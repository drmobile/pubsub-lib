# coding=utf-8
#
import json
import signal
import asyncio
import logging

logger = logging.getLogger(__name__)

class SubscriptionService():
    def __init__(self, subscription):
        self.subscription = subscription
        self.ev_loop = asyncio.get_event_loop()
        # create service stop event
        self.stop = asyncio.Event(loop=self.ev_loop)
        self.stop.clear()    # default false

    async def __exit(self, signame):
        logger.info('got signal {}: exit.'.format(signame))
        self.stop.set()
        this = asyncio.Task.current_task()
        tasks = asyncio.Task.all_tasks()
        # signal pending tasks to clean up except itself
        for task in tasks:
            if task is not this:
                task.cancel()
        # close subscription channel
        logger.info('close subscription channel.')
        self.subscription.close()
        # wait for pending tasks to clean up
        self.subscription_future.result()
        # await asyncio.sleep(3)
        self.ev_loop.stop()

    def __on_received(self, message, callback):
        # A message data and its attributes. 
        # The message payload must not be empty; it must contain either a non-empty data field, or at least one attribute.
        # https://googlecloudplatform.github.io/google-cloud-python/latest/pubsub/types.html#google.cloud.pubsub_v1.types.PubsubMessage
        logger.info('message has been received, which is published at {}.'.format(message.publish_time))
        logger.debug('message content is {}.'.format(message))
        # callback custom
        try:
            if callback is not None:
                # convert data into appropriate python data type
                payload = message.data.decode('utf-8')
                # try to convert into dict type
                try:
                    payload = json.loads(payload)
                except:
                    pass
                # convert attributes into dict type
                attributes = {attr: message.attributes[attr] for attr in message.attributes}
                dup_msg = {
                    'message_id': message.message_id,
                    'data': payload,
                    'attributes': attributes
                }
                callback(dup_msg)
            message.ack()
        except Exception as e:
            logger.error('unexpected exception was caughted {}.'.format(e))

    def run(self, callback = None):
        # add signal handler to stop the service
        for signame in ('SIGINT', 'SIGTERM'):
            self.ev_loop.add_signal_handler(getattr(signal, signame),
                                        lambda: asyncio.ensure_future(self.__exit(signame)))    
        try:
            # open subscription channel
            logger.info('open subscription channel.')
            self.subscription_future = self.subscription.open(lambda message: self.__on_received(message, callback))            
            logger.info('Event loop running forever, press CTRL+C to interrupt.')
            self.ev_loop.run_forever()
        except Exception as e:
            logger.error('unexpected exception was caughted {}.'.format(e))
        finally:
            self.ev_loop.close()