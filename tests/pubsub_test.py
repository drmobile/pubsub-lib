# coding=utf-8
#
import os
import time
import docker
import pytest
import logging
import unittest

from google.api_core.exceptions import ServiceUnavailable
from soocii_pubsub_lib import pubsub_client

# ========== Initial Logger ==========
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)-15s][%(levelname)-5s][%(filename)s][%(funcName)s#%(lineno)d] %(message)s')
logger = logging.getLogger(__name__)
# ====================================

container = None


@pytest.fixture()
def no_emulator(request):
    # export PUBSUB_EMULATOR_HOST=127.0.0.1:8538
    os.environ["PUBSUB_EMULATOR_HOST"] = "127.0.0.1:8538"


@pytest.fixture()
def start_emulator(request):
    # export PUBSUB_EMULATOR_HOST=127.0.0.1:8538
    os.environ["PUBSUB_EMULATOR_HOST"] = "127.0.0.1:8538"

    # start pubsub emulator
    client = docker.from_env()
    container = client.containers.run(
        'bigtruedata/gcloud-pubsub-emulator',
        'start --host-port=0.0.0.0:8538 --data-dir=/data',
        ports={'8538/tcp': 8538},
        detach=True,
        auto_remove=True)

    def stop_emulator():
        container.stop()

    request.addfinalizer(stop_emulator)
    return container


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

    def __on_received(self, payload):
        pass

    def test_publish_bytes_data(self):
        # prepare publisher
        publisher = pubsub_client.PublisherClient(self.project, self.cred)
        publisher.create_topic(self.topic)

        # # prepare subscriber
        # subscriber = pubsub_client.SubscribeClient(self.project, self.cred)
        # subscription = subscriber.create_subscription(self.topic, 'fake-subscription')

        # get configuration of the topic before sending request
        exception_caughted = False
        try:
            publisher.get_topic(self.topic)
        except Exception as e:
            exception_caughted = True
            logger.exception('unexpected exception is caughted: {}'.format(e))
        self.assertFalse(exception_caughted)
        # publish bytes
        publisher.publish(self.topic, b'bytes data', callback=lambda message_id: self.__on_published(message_id))
        # wait for callback
        time.sleep(1)
        # verify if message has been published
        self.assertTrue(self.published_message_id is not None)

    def test_publish_string(self):
        # prepare publisher
        publisher = pubsub_client.PublisherClient(self.project, self.cred)
        publisher.create_topic(self.topic)
        # get configuration of the topic before sending request
        exception_caughted = False
        try:
            publisher.get_topic(self.topic)
        except Exception as e:
            exception_caughted = True
            logger.exception('unexpected exception is caughted: {}'.format(e))
        self.assertFalse(exception_caughted)
        # publish string
        publisher.publish(self.topic, 'string data', callback=lambda message_id: self.__on_published(message_id))
        # wait for callback
        time.sleep(1)
        # verify if message has been published
        self.assertTrue(self.published_message_id is not None)

    def test_publish_dict(self):
        # prepare publisher
        publisher = pubsub_client.PublisherClient(self.project, self.cred)
        publisher.create_topic(self.topic)
        # get configuration of the topic before sending request
        exception_caughted = False
        try:
            publisher.get_topic(self.topic)
        except Exception as e:
            exception_caughted = True
            logger.exception('unexpected exception is caughted: {}'.format(e))
        self.assertFalse(exception_caughted)
        # publish dict
        data = {
            'f1': 1,
            'f2': '2',
            'f3': [3, 4, 5]
        }
        publisher.publish(self.topic, data, callback=lambda message_id: self.__on_published(message_id))
        # wait for callback
        time.sleep(1)
        # verify if message has been published
        self.assertTrue(self.published_message_id is not None)

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
            logger.exception('unexpected exception is caughted: {}'.format(e))
        self.assertFalse(exception_caughted)
        # publish to the topic in sync way
        message_id, _ = publisher.publish(self.topic, b'bytes data')
        # verify if message_id is returned
        self.assertTrue(message_id is not None)


@pytest.mark.usefixtures("start_emulator")
class NonExistTopicTests(unittest.TestCase):
    def setUp(self):
        self.project = 'fake-project'
        self.cred = None
        self.topic = 'fake-topic'
        self.published_message_id = None

    def tearDown(self):
        pass

    def test_non_exist_topic(self):
        # prepare publisher
        publisher = pubsub_client.PublisherClient(self.project, self.cred)
        # get configuration of an non-exist topic without retry policy
        with self.assertRaises(ServiceUnavailable):
            publisher.get_topic('non-exist', retry=None)


@pytest.mark.usefixtures("no_emulator")
class NoEmulatorTests(unittest.TestCase):
    def setUp(self):
        self.project = 'fake-project'
        self.cred = None
        self.topic = 'fake-topic'
        self.published_message_id = None

    def tearDown(self):
        pass

    def test_no_emulator(self):
        # prepare publisher
        publisher = pubsub_client.PublisherClient(self.project, self.cred)
        # get configuration of an non-exist topic without retry policy
        with self.assertRaises(ServiceUnavailable):
            publisher.get_topic(self.topic, retry=None)
