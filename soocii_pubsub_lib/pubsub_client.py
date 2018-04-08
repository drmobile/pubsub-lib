# coding=utf-8
#
import abc
import six
import json
import logging
# Imports the Google Cloud client library
from google.cloud import pubsub_v1
from google.oauth2 import service_account as sa

from google.api_core.exceptions import AlreadyExists

logger = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class PubSubBase():
    def __init__(self, project, cred_json):
        self.project = project
        self.cred = None if cred_json is None else sa.Credentials.from_service_account_file(cred_json)

    def topic_path(self, client, topic):
        # The resource path for the new topic contains the project ID
        # and the topic name.
        return client.topic_path(self.project, topic)

    def subscription_path(self, client, subscription_name):
        return client.subscription_path(self.project, subscription_name)


class PublisherClient(PubSubBase):
    def __init__(self, project, cred_json):
        """A wrapped publisher client for Google Cloud Pub/Sub.

        This creates an object that is capable of publishing messages. Generally, you can instantiate this client with no arguments, and you get sensible defaults.

        Arguments:
            project {str} -- Project id
            cred_json {str} -- Full path to credential file in json format
        """
        super(PublisherClient, self).__init__(project, cred_json)
        # Instantiates a client
        self.client = pubsub_v1.PublisherClient(credentials=self.cred)

    def create_topic(self, topic, **kwargs):
        """Creates the given topic with the given name.

        Arguments:
            topic {str} -- The topic name to create.

        Keyword Arguments:
            retry {google.api_core.retry.Retry]} -- An optional retry object used to retry requests. If None is specified, requests will not be retried.

        Returns:
            str -- A topic name
        """
        topic = self.topic_path(self.client, topic)
        try:
            return self.client.create_topic(topic, **kwargs).name
        except AlreadyExists:
            logger.debug('topic {} already exists.'.format(topic))

    def get_topic(self, topic, **kwargs):
        """Gets the configuration of a topic.

        Arguments:
            topic {str} -- The topic name to get.

        Keyword Arguments:
            retry {google.api_core.retry.Retry]} -- An optional retry object used to retry requests. If None is specified, requests will not be retried.

        Raises:
            google.api_core.exceptions.GoogleAPICallError -– If the request failed for any reason.
            google.api_core.exceptions.RetryError –- If the request failed due to a retryable error and retry attempts failed.
            ValueError -– If the parameters are invalid.

        Returns:
            str -- A topic name
        """
        topic = self.topic_path(self.client, topic)
        return self.client.get_topic(topic, **kwargs).name

    def __on_published(self, future, callback):
        logger.debug('callback for publish message')
        message_id = None
        if future.cancelled():
            logger.warn('{}: canceled'.format(future.arg))
        elif future.done():
            error = future.exception()
            if error:
                logger.error('{}: error returned: {}'.format(future.arg, error))
            else:
                message_id = future.result()
                logger.info('data has been publised with message id {}.'.format(message_id))

        if callback is not None:
            callback(message_id)

    #
    def publish(self, topic, payload, callback=None, **kwargs):
        """To publish a message, use the publish() method. This method accepts two positional arguments:
        the topic to publish to, and the payload of the message.
        It also accepts arbitrary keyword arguments, which are passed along as attributes of the message.
        If callback is provided, this method invoke in async way and return message_id through callback.
        If callback is NOT provided, this method invoke in sync way and return message_id.
        Either async or sync way invokation, this method return tuple (message_id, future)

        Arguments:
            topic {str} -- The topic name to publish messages to.
            payload -- A bytestring, string, or dictionary representing the message body.

        Keyword Arguments:
            callback -- An optional callback (default: {None})

        Raises:
            ValueError -- If payload is not a bytestring, string, or dictionary.
            Exception -- If unexpected exception is caughted

        Returns:
            (str, concurrent.futures.Future) -- A tuple of message id and future instance
        """
        try:
            logger.debug('publish message to {}'.format(topic))
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
                raise ValueError('unexpected data type which is {}.'.format(dtype))
            topic = self.topic_path(self.client, topic)
            future = self.client.publish(topic, msg, **kwargs)
            # async call
            if callback is not None:
                future.add_done_callback(lambda future: self.__on_published(future, callback))
                return (None, future)
            # sync call
            else:
                message_id = future.result()
                logger.info('data has been publised with message id {}.'.format(message_id))
                return (message_id, future)
        except Exception as e:
            logger.error('unexpected exception is caughted: {}'.format(e))
            raise e


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
