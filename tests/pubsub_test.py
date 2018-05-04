# coding=utf-8
#
import time
import pytest
import logging
import unittest

from google.api_core.exceptions import ServiceUnavailable
from google.api_core.exceptions import NotFound
from soocii_pubsub_lib import pubsub_client

# ========== Initial Logger ==========
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)-15s][%(levelname)-5s][%(filename)s][%(funcName)s#%(lineno)d] %(message)s')
logger = logging.getLogger(__name__)
# ====================================


# normal publish
@pytest.mark.usefixtures("start_emulator")
class NormalPublishTests(unittest.TestCase):
    def setUp(self):
        self.project = 'fake-project'
        self.cred = None
        self.topic = 'fake-topic'
        self.published_message_id = None

    def tearDown(self):
        pass

    def __on_published(self, message_id):
        logger.info('message is published with message id: {}'.format(message_id))
        self.published_message_id = message_id

    def test_publish_bytes_data(self):
        # prepare publisher
        publisher = pubsub_client.PublisherClient(self.project, self.cred)
        publisher.create_topic(self.topic)
        # get configuration of the topic before sending request
        exception_caughted = False
        try:
            publisher.get_topic(self.topic)
        except Exception as e:
            exception_caughted = True
            logger.exception('unexpected exception was caughted: {}'.format(e))
        assert exception_caughted is False
        # publish bytes
        publisher.publish(self.topic, b'bytes data', callback=lambda message_id: self.__on_published(message_id))
        # wait for callback
        time.sleep(1)
        # verify if message has been published
        assert self.published_message_id is not None

    def test_publish_with_attributes(self):
        # prepare publisher
        publisher = pubsub_client.PublisherClient(self.project, self.cred)
        publisher.create_topic(self.topic)
        # get configuration of the topic before sending request
        exception_caughted = False
        try:
            publisher.get_topic(self.topic)
        except Exception as e:
            exception_caughted = True
            logger.exception('unexpected exception was caughted: {}'.format(e))
        assert exception_caughted is False
        # publish dict
        publisher.publish(self.topic, b'bytes data', callback=lambda message_id: self.__on_published(message_id), addition1='test1', addition2='test2')
        # wait for callback
        time.sleep(1)
        # verify if message has been published
        assert self.published_message_id is not None

    def test_sync_publish(self):
        # prepare publisher
        publisher = pubsub_client.PublisherClient(self.project, self.cred)
        publisher.create_topic(self.topic)
        # get configuration of the topic before sending request
        exception_caughted = False
        try:
            publisher.get_topic(self.topic)
        except Exception as e:
            exception_caughted = True
            logger.exception('unexpected exception was caughted: {}'.format(e))
        assert exception_caughted is False
        # publish to the topic in sync way
        message_id, _ = publisher.publish(self.topic, b'bytes data')
        # verify if message_id is returned
        assert message_id is not None


# normal subscribe
@pytest.mark.usefixtures("start_emulator")
class NormalSubscribeTests(unittest.TestCase):
    def setUp(self):
        self.project = 'fake-project'
        self.cred = None
        self.topic = 'fake-topic'
        self.published_message_id = None
        self.received_message = None

    def tearDown(self):
        # close subscription channel
        if self.subscription is not None:
            self.subscription.close()
        if self.future is not None:
            self.future.result()

    def __on_published(self, message_id):
        logger.info('message is published with message id: {}'.format(message_id))
        self.published_message_id = message_id

    def __on_received(self, message):
        logger.info('message is received with payload: {}'.format(message))
        self.received_message = message
        # ack message
        return True

    def test_subscribe_non_dict_message(self):
        # prepare publisher
        publisher = pubsub_client.PublisherClient(self.project, self.cred)
        publisher.create_topic(self.topic)
        # get configuration of the topic before sending request
        exception_caughted = False
        try:
            publisher.get_topic(self.topic)
        except Exception as e:
            exception_caughted = True
            logger.exception('unexpected exception was caughted: {}'.format(e))
        assert exception_caughted is False
        # prepare subscriber
        subscriber = pubsub_client.SubscribeClient(self.project, self.cred)
        self.subscription = subscriber.create_subscription(self.topic, 'fake-subscription')
        # publish bytes
        publisher.publish(self.topic, b'bytes data', callback=lambda message_id: self.__on_published(message_id))
        # open subscription channel, and start receiving message
        self.future = self.subscription.open(callback=lambda message: self.__on_received(message))
        # wait for callback
        time.sleep(1)
        # verify if message has been received
        assert self.received_message is not None
        assert self.published_message_id == self.received_message['message_id']
        assert self.received_message['data'] == b'bytes data'
        assert self.received_message['attributes'] == {}

    def test_subscribe_message_with_attributes(self):
        # prepare publisher
        publisher = pubsub_client.PublisherClient(self.project, self.cred)
        publisher.create_topic(self.topic)
        # get configuration of the topic before sending request
        exception_caughted = False
        try:
            publisher.get_topic(self.topic)
        except Exception as e:
            exception_caughted = True
            logger.exception('unexpected exception was caughted: {}'.format(e))
        assert exception_caughted is False
        # prepare subscriber
        subscriber = pubsub_client.SubscribeClient(self.project, self.cred)
        self.subscription = subscriber.create_subscription(self.topic, 'fake-subscription')
        # publish dict
        publisher.publish(self.topic, b'bytes data', callback=lambda message_id: self.__on_published(message_id), addition1='test1', addition2='test2')
        # open subscription channel, and start receiving message
        self.future = self.subscription.open(callback=lambda message: self.__on_received(message))
        # wait for callback
        time.sleep(1)
        # verify if message has been received
        assert self.received_message is not None
        assert self.published_message_id == self.received_message['message_id']
        assert self.received_message['data'] == b'bytes data'
        assert self.received_message['attributes']['addition1'] == 'test1'
        assert self.received_message['attributes']['addition2'] == 'test2'

    def test_subscribe_message_without_callback(self):
        # prepare publisher
        publisher = pubsub_client.PublisherClient(self.project, self.cred)
        publisher.create_topic(self.topic)
        # get configuration of the topic before sending request
        exception_caughted = False
        try:
            publisher.get_topic(self.topic)
        except Exception as e:
            exception_caughted = True
            logger.exception('unexpected exception was caughted: {}'.format(e))
        assert exception_caughted is False
        # prepare subscriber
        subscriber = pubsub_client.SubscribeClient(self.project, self.cred)
        self.subscription = subscriber.create_subscription(self.topic, 'fake-subscription')
        # publish bytes
        publisher.publish(self.topic, b'bytes data', callback=lambda message_id: self.__on_published(message_id))
        # open subscription channel, and start receiving message
        self.future = self.subscription.open()
        # wait for callback
        time.sleep(1)
        # close subscription channel, and open again with callback
        self.subscription.close()
        self.future = self.subscription.open(callback=lambda message: self.__on_received(message))
        # wait for callback
        time.sleep(1)
        # verify if message has been processed in previous channel
        assert self.received_message is None


@pytest.mark.usefixtures("start_emulator")
class NonExistTopicTests(unittest.TestCase):
    def setUp(self):
        self.project = 'fake-project'
        self.cred = None
        self.topic = 'fake-topic'

    def tearDown(self):
        pass

    def test_get_non_exist_topic(self):
        # prepare publisher
        publisher = pubsub_client.PublisherClient(self.project, self.cred)
        # get configuration of an non-exist topic without retry policy
        with self.assertRaises(ServiceUnavailable):
            publisher.get_topic(self.topic, retry=None)

    def test_subscribe_non_exist_topic(self):
        # prepare subscriber
        subscriber = pubsub_client.SubscribeClient(self.project, self.cred)
        with self.assertRaises(NotFound):
            subscriber.create_subscription(self.topic, 'fake-subscription')


@pytest.mark.usefixtures("start_emulator")
class UnsupportedDataTypeTests(unittest.TestCase):
    def setUp(self):
        self.project = 'fake-project'
        self.cred = None
        self.topic = 'fake-topic'

    def tearDown(self):
        pass

    def test_unsupported_data_type(self):
        # prepare publisher
        publisher = pubsub_client.PublisherClient(self.project, self.cred)
        publisher.create_topic(self.topic)
        # get configuration of the topic before sending request
        exception_caughted = False
        try:
            publisher.get_topic(self.topic)
        except Exception as e:
            exception_caughted = True
            logger.exception('unexpected exception was caughted: {}'.format(e))
        self.assertFalse(exception_caughted)
        # publish to the topic in sync way
        with self.assertRaises(ValueError):
            publisher.publish(self.topic, 12345)


@pytest.mark.usefixtures("start_emulator")
class DuplicatedTopicTests(unittest.TestCase):
    def setUp(self):
        self.project = 'fake-project'
        self.cred = None
        self.topic = 'fake-topic'

    def tearDown(self):
        pass

    def test_create_topic_twice(self):
        # prepare publisher
        publisher = pubsub_client.PublisherClient(self.project, self.cred)
        publisher.create_topic(self.topic)
        publisher.create_topic(self.topic)
        # get configuration of the topic before sending request
        exception_caughted = False
        try:
            publisher.get_topic(self.topic)
        except Exception as e:
            exception_caughted = True
            logger.exception('unexpected exception was caughted: {}'.format(e))
        assert exception_caughted is False
        # publish to the topic in sync way
        message_id, _ = publisher.publish(self.topic, b'bytes data')
        # verify if message_id is returned
        assert message_id is not None


@pytest.mark.usefixtures("start_emulator")
class DuplicatedSubscriptionTests(unittest.TestCase):
    def setUp(self):
        self.project = 'fake-project'
        self.cred = None
        self.topic = 'fake-topic'

    def tearDown(self):
        pass

    def __on_published(self, message_id):
        logger.info('message is published with message id: {}'.format(message_id))
        self.published_message_id = message_id

    def __on_received(self, message):
        logger.info('message is received with payload: {}'.format(message))
        self.received_message = message
        # ack message
        return True

    def test_create_subscription_twice(self):
        # prepare publisher
        publisher = pubsub_client.PublisherClient(self.project, self.cred)
        publisher.create_topic(self.topic)
        # get configuration of the topic before sending request
        exception_caughted = False
        try:
            publisher.get_topic(self.topic)
        except Exception as e:
            exception_caughted = True
            logger.exception('unexpected exception was caughted: {}'.format(e))
        assert exception_caughted is False
        # prepare subscriber
        subscriber = pubsub_client.SubscribeClient(self.project, self.cred)
        self.subscription = subscriber.create_subscription(self.topic, 'fake-subscription')
        self.subscription = subscriber.create_subscription(self.topic, 'fake-subscription')
        # publish bytes
        publisher.publish(self.topic, b'bytes data', callback=lambda message_id: self.__on_published(message_id))
        # open subscription channel, and start receiving message
        self.future = self.subscription.open(callback=lambda message: self.__on_received(message))
        # wait for callback
        time.sleep(1)
        # verify if message has been received
        assert self.received_message is not None
        assert self.published_message_id == self.received_message['message_id']
        assert self.received_message['data'] == b'bytes data'
        assert self.received_message['attributes'] == {}


@pytest.mark.usefixtures("no_emulator")
class NoEmulatorTests(unittest.TestCase):
    def setUp(self):
        self.project = 'fake-project'
        self.cred = None
        self.topic = 'fake-topic'
        self.published_message_id = None

    def tearDown(self):
        pass

    def test_get_topic_without_emulator(self):
        # prepare publisher
        publisher = pubsub_client.PublisherClient(self.project, self.cred)
        # get configuration of an non-exist topic without retry policy
        with self.assertRaises(ServiceUnavailable):
            publisher.get_topic(self.topic, retry=None)

    def test_subscribe_without_emulator(self):
        # prepare subscriber
        subscriber = pubsub_client.SubscribeClient(self.project, self.cred)
        with self.assertRaises(ServiceUnavailable):
            subscriber.create_subscription(self.topic, 'fake-subscription', retry=None)
