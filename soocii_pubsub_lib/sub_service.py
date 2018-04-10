# coding=utf-8
#
import json
import signal
import logging
import threading

logger = logging.getLogger(__name__)


class SubscriptionService():
    def __init__(self, subscription):
        logger.info('init instance of SubscriptionService')
        self.subscription = subscription
        # create service stop event
        self.stop = threading.Event()
        self.stop.clear()    # default false

    def __exit(self, signalnum, frame):
        logger.info('got signal {} {}: exit.'.format(signalnum, frame))
        self.shutdown()

    def run(self, callback=None):
        logger.info('start running SubscriptionService')
        try:
            # add signal handler to stop the service.
            # NOTED: signal only works in main thread.
            if isinstance(threading.current_thread(), threading._MainThread) is True:
                for signame in ('SIGINT', 'SIGTERM'):
                    logger.info('register signal handler for {}'.format(signame))
                    signal.signal(getattr(signal, signame), lambda signalnum, frame: self.__exit(signalnum, frame))
            else:
                logger.warn('skip signal handler registration, due to this is not in main thread.')
            # open subscription channel
            logger.info('open subscription channel.')
            self.subscription_future = self.subscription.open(callback)
            logger.info('subscription service is running forever, press CTRL+C to interrupt.')
            self.stop.wait()
        except Exception as e:
            logger.error('unexpected exception was caughted: {}.'.format(e))

    def shutdown(self):
        logger.info('stop running SubscriptionService')
        self.stop.set()
        # close subscription channel
        logger.info('close subscription channel.')
        self.subscription.close()
        # wait for pending tasks to clean up
        self.subscription_future.result()
