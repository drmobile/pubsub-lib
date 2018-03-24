#!/usr/bin/env python
# coding=utf-8
#
import time
import pytest
import logging
import unittest

from pubsub_client import PublisherClient, SubscribeClient

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
        pass

    def tearDown(self):
        pass

    def __on_published(self, message_id):
        logger.info('message is published with message id: {}'.format(message_id))
        self.published_message_id = message_id

    def __on_received(self, payload):
        pass

    #@pytest.mark.first
    def test_publish(self):
        # prepare publisher
        publisher = PublisherClient(self.project, self.cred)
        topic = publisher.create_topic(self.topic)

        # # prepare subscriber
        # subscriber = SubscribeClient(self.project, self.cred)
        # subscription = subscriber.create_subscription(self.topic, 'fake-subscription')

        # publish bytes
        publisher.publish(self.topic, b'bytes data', callback=lambda message_id: self.__on_published(message_id))
        # wait for callback
        time.sleep(1)
        # verify if message has been published
        self.assertTrue(self.published_message_id is not None)

        pass

# TODO: publish to non-exist topic
# TODO: test publish with timeout when PubSub service is not available