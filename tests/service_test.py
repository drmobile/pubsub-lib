# coding=utf-8
#
import time
import pytest
import logging
import unittest
import concurrent.futures

from soocii_pubsub_lib import pubsub_client, sub_service

# ========== Initial Logger ==========
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)-15s][%(levelname)-5s][%(filename)s][%(funcName)s#%(lineno)d] %(message)s')
logger = logging.getLogger(__name__)
# ====================================


# normal subscribe
@pytest.mark.usefixtures("start_emulator")
class NormalSubscribeTests(unittest.TestCase):
    def setUp(self):
        self.project = 'fake-project'
        self.cred = None
        self.topic = 'fake-topic'
        self.published_message_id = None
        self.received_message = None
        self.received_message_count = 0
        self.service = None

    def tearDown(self):
        pass

    def __on_published(self, message_id):
        logger.info('message is published with message id: {}'.format(message_id))
        self.published_message_id = message_id

    def __on_received(self, message):
        logger.info('message is received with payload: {}'.format(message))
        self.received_message = message
        self.received_message_count = self.received_message_count + 1
        # ack message
        return True

    def __publisher(self):
        # prepare publisher
        publisher = pubsub_client.PublisherClient(self.project, self.cred)
        # get configuration of the topic before sending request
        exception_caughted = False
        try:
            publisher.get_topic(self.topic)
        except Exception as e:
            exception_caughted = True
            logger.exception('unexpected exception was caughted: {}'.format(e))
        self.assertFalse(exception_caughted)
        # publish bytes
        logger.info('start publishing message')
        for i in range(5):
            publisher.publish(self.topic, b'bytes data', callback=lambda message_id: self.__on_published(message_id))

    def __subscriber(self):
        # prepare subscriber
        subscriber = pubsub_client.SubscribeClient(self.project, self.cred)
        self.subscription = subscriber.create_subscription(self.topic, 'fake-subscription')
        self.service = sub_service.SubscriptionService(self.subscription)
        logger.info('start subscribing message')
        self.service.run(callback=lambda message: self.__on_received(message))

    def __waitter(self):
        # wait for callback
        time.sleep(5)
        self.service.shutdown()

    def test_subscribe_message(self):
        # prepare publisher
        publisher = pubsub_client.PublisherClient(self.project, self.cred)
        publisher.create_topic(self.topic)
        # prepare subscriber
        subscriber = pubsub_client.SubscribeClient(self.project, self.cred)
        self.subscription = subscriber.create_subscription(self.topic, 'fake-subscription')

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            executor.submit(lambda: self.__waitter())
            executor.submit(lambda: self.__publisher())
            # subscriber service is running in main thread
            self.__subscriber()

        # verify if message has been received
        self.assertTrue(self.received_message is not None)
        self.assertEqual(self.published_message_id, self.received_message['message_id'])
        self.assertEqual(self.received_message['data'], 'bytes data')
        self.assertEqual(self.received_message['attributes'], {})
        self.assertEqual(self.received_message_count, 5)

    # def test_subscribe_message2(self):
    #     # prepare publisher
    #     publisher = pubsub_client.PublisherClient(self.project, self.cred)
    #     publisher.create_topic(self.topic)
    #     # prepare subscriber
    #     subscriber = pubsub_client.SubscribeClient(self.project, self.cred)
    #     self.subscription = subscriber.create_subscription(self.topic, 'fake-subscription')

    #     with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    #         # subscriber service is NOT running in main thread
    #         executor.submit(lambda: self.__subscriber())
    #         executor.submit(lambda: self.__publisher())
    #         # wait for callback
    #         time.sleep(5)
    #         self.service.shutdown()

    #     # verify if message has been received
    #     self.assertTrue(self.received_message is not None)
    #     self.assertEqual(self.published_message_id, self.received_message['message_id'])
    #     self.assertEqual(self.received_message['data'], 'bytes data')
    #     self.assertEqual(self.received_message['attributes'], {})
    #     self.assertEqual(self.received_message_count, 5)
