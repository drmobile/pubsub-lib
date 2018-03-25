# coding=utf-8
#
import abc, six
import json
import logging
# Imports the Google Cloud client library
from google.cloud import pubsub_v1
from google.oauth2 import service_account

from google.api_core.exceptions import AlreadyExists

logger = logging.getLogger(__name__)

@six.add_metaclass(abc.ABCMeta)
class PubSubBase():
    def __init__(self, project, cred_json):
        self.project = project
        self.cred = None if cred_json is None else service_account.Credentials.from_service_account_file(cred_json)

    def topic_path(self, client, topic):
        # The resource path for the new topic contains the project ID
        # and the topic name.
        return client.topic_path(self.project, topic)
    
    def subscription_path(self, client, subscription_name):
        return client.subscription_path(self.project, subscription_name)
            
class PublisherClient(PubSubBase):
    def __init__(self, project, cred_json):
        super(PublisherClient, self).__init__(project, cred_json)
        # Instantiates a client
        self.client = pubsub_v1.PublisherClient(credentials=self.cred)

    # Create the topic.
    def create_topic(self, topic):
        topic = self.topic_path(self.client, topic)
        try:
            return self.client.create_topic(topic)
        except AlreadyExists:
            logger.debug('topic {} already exists.'.format(topic))

    def on_published(self, future, callback):
        message_id = future.result()
        logger.info('data has been publised with message id {}.'.format(message_id))
        if callback is not None:
            callback(message_id)

    # To publish a message, use the publish() method. 
    # This method accepts two positional arguments: the topic to publish to, 
    # and the body of the message. It also accepts arbitrary keyword arguments, 
    # which are passed along as attributes of the message.
    def publish(self, topic, payload, callback=None, **kwargs):
        try:
            dtype = type(payload)
            if dtype is bytes:
                # good to go head
                msg = payload
            elif dtype is str:
                msg = payload.encode('utf-8')
            elif dtype is dict:
                # convert dict into JSON
                msg = json.dumps(payload).encode('utf-8')
            else:
                raise ValueError('unexpected data type which is {}.'.format(type(data)))
            topic = self.topic_path(self.client, topic)
            future = self.client.publish(topic, msg, **kwargs)
            future.add_done_callback(lambda future: self.on_published(future, callback))
        except ValueError as e:
            logger.error(e)


class SubscribeClient(PubSubBase):
    def __init__(self, project, cred_json):
        super(SubscribeClient, self).__init__(project, cred_json)
        self.client = pubsub_v1.SubscriberClient(credentials=self.cred)
    
    def create_subscription(self, topic, subscription_name):
        topic = self.topic_path(self.client, topic)
        subscription_name = self.subscription_path(self.client, subscription_name)
        try:
            self.client.create_subscription(subscription_name, topic)
        except AlreadyExists:
            logger.debug('subscription {} already exists.'.format(subscription_name))
        finally:
            return self.client.subscribe(subscription_name)

            