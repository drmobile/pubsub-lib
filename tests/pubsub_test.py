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
    container = client.containers.run('bigtruedata/gcloud-pubsub-emulator',
                                            'start --host-port=0.0.0.0:8538 --data-dir=/data',
                                            ports = {'8538/tcp': 8538},
                                            detach = True,
                                            auto_remove = True)
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

        message_id = publisher.publish(self.topic, b'bytes data')
        # verify if message_id is returned
        self.assertTrue(message_id is not None)

# abnormal publish
@pytest.mark.usefixtures("start_emulator")
class AbnormalPublishTests(unittest.TestCase):
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

    def test_publish_to_non_exist_topic(self):
        # prepare publisher
        publisher = pubsub_client.PublisherClient(self.project, self.cred)

        publisher.publish('non-exist', b'bytes data', callback=lambda message_id: self.__on_published(message_id))
        # wait for callback
        time.sleep(1)
        # verify if message has NOT been published
        self.assertTrue(self.published_message_id is None)

@pytest.mark.usefixtures("no_emulator")
class NoEmulatorPublishTests(unittest.TestCase):
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

    def test_publish_without_emulator(self):
        # prepare publisher
        publisher = pubsub_client.PublisherClient(self.project, self.cred)

        publisher.publish(self.topic, b'bytes data', callback=lambda message_id: self.__on_published(message_id))
        # wait for callback
        time.sleep(1)
        # verify if message has NOT been published
        self.assertTrue(self.published_message_id is None)

