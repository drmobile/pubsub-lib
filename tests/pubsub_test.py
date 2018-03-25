# coding=utf-8
#
import os
import time
import docker
import pytest
import logging
import unittest

from soocii_pubsub_lib import pubsub_client

########## Initial Logger ##########
# Logger
logging.basicConfig(level=logging.DEBUG,
            format='[%(asctime)-15s][%(levelname)-5s][%(filename)s][%(funcName)s#%(lineno)d] %(message)s')
logger = logging.getLogger(__name__)
########################################

class PubSubTests(unittest.TestCase):
    def setUp(self):
        self.project = 'fake-project'
        self.cred = None
        self.topic = 'fake-topic'
        self.published_message_id = None

        # start pubsub emulator
        client = docker.from_env()
        self.container = client.containers.run('bigtruedata/gcloud-pubsub-emulator', 
                                                'start --host-port=0.0.0.0:8538 --data-dir=/data',
                                                ports = {'8538/tcp': 8538},
                                                detach = True,
                                                auto_remove = True)
        # export PUBSUB_EMULATOR_HOST=127.0.0.1:8538
        os.environ["PUBSUB_EMULATOR_HOST"] = "127.0.0.1:8538"

    def tearDown(self):
        self.container.stop()

    def __on_published(self, message_id):
        logger.info('message is published with message id: {}'.format(message_id))
        self.published_message_id = message_id

    def __on_received(self, payload):
        pass

    #@pytest.mark.first
    def test_publish(self):
        # prepare publisher
        publisher = pubsub_client.PublisherClient(self.project, self.cred)
        topic = publisher.create_topic(self.topic)

        # # prepare subscriber
        # subscriber = pubsub_client.SubscribeClient(self.project, self.cred)
        # subscription = subscriber.create_subscription(self.topic, 'fake-subscription')

        # publish bytes
        publisher.publish(self.topic, b'bytes data', callback=lambda message_id: self.__on_published(message_id))
        # wait for callback
        time.sleep(1)
        # verify if message has been published
        self.assertTrue(self.published_message_id is not None)

# TODO: publish to non-exist topic
# TODO: test publish with timeout when PubSub service is not available