#!/usr/bin/env python
# coding=utf-8
#
import os
import time
import logging

from soocii_pubsub_lib import pubsub_client, sub_service

# ========== Initial Logger ==========
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)-15s][%(levelname)-5s][%(filename)s][%(funcName)s#%(lineno)d] %(message)s')
logger = logging.getLogger(__name__)
# ====================================


if __name__ == '__main__':
    project = os.environ['PUBSUB_PROJECT_ID'] if 'PUBSUB_PROJECT_ID' in os.environ else 'pubsub-trial-198610'
    cred = os.environ['GOOGLE_APPLICATION_CREDENTIALS'] if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ else './pubsub-trial.json'
    logger.info('project: {}, cred: {}'.format(project, cred))

    # prepare publisher
    publisher = pubsub_client.PublisherClient(project, cred)
    topic = publisher.create_topic('test-topic')

    # publish message
    logger.info('start publishing messages')
    for _ in range(5):
        message = 'publish message {}'.format(time.time())
        logger.info(message)
        publisher.publish('test-topic', message)
    logger.info('stop publishing messages')
