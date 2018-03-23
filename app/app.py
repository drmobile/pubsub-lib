#!/usr/bin/env python
# coding=utf-8
#
import os
import logging

from pubsub_client import PublisherClient, SubscribeClient
from sub_service import SubscriptionService

########## Initial Logger ##########
# Logger
logging.basicConfig(level=logging.INFO,
            format='[%(asctime)-15s][%(levelname)-5s][%(filename)s][%(funcName)s#%(lineno)d] %(message)s')
logger = logging.getLogger(__name__)
########################################

def callback(payload):
    logger.info(payload)
    # raise Exception if any error occur    

if __name__ == '__main__':
    project = 'pubsub-trial-198610'
    cred = None if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ else './pubsub-trial-f5e6dbba824c.json'

    # prepare publisher
    publisher = PublisherClient(project, cred)
    topic = publisher.create_topic('test-topic')

    # prepare subscriber
    subscriber = SubscribeClient(project, cred)
    subscription = subscriber.create_subscription('test-topic', 'test-sub2')

    # publish bytes
    publisher.publish('test-topic', b'bytes data', callback=lambda message_id: logger.info(message_id))
    # publish string
    publisher.publish('test-topic', 'string data')
    # publish dict
    data = {
        'f1': 1,
        'f2': '2',
        'f3': [3, 4, 5]
    }
    publisher.publish('test-topic', data, addition1='test1', addition2='test2')

    service = SubscriptionService(subscription)
    service.run(callback)
