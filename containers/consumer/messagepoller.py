#!/usr/bin/env python3

from confluent_kafka import Consumer, KafkaException, KafkaError

from message import Message

class MessagePoller():
    """ Singleton class for polling messages """

    def __init__(self, params):
        """ Instantiate a MessagePoller object """

        self.running = True
        self.topics = params['topics']
        self.api_endpoint = params['api_endpoint']
        self.config = {
            'bootstrap.servers': params['bootstrap_broker_servers'],
            'group.id': params['group_id'],
            'auto.offset.reset': params['auto_offset_reset']
            }
        self.consumer = Consumer(self.config)        

    def loop_poll_messages(self):
        """ Poll loop listening to messages from topic(s) """
        try:
            self.consumer.subscribe(self.topics)

            i = 0
            while self.running:
                i += 1
                print(f"Polling ({i})...")
                # Maybe increase this to near infinity? Why not simply wait until something happens instead of polling again?
                # timeout (float) – Maximum time to block waiting for message, event or callback (default: infinite (None translated into -1 in the library)). (Seconds)
                msg = self.consumer.poll(timeout=5.0)
                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                        (msg.topic(), msg.partition(), msg.offset()))
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    message = Message(msg, self.api_endpoint)
                    message.handle_message()

        finally:
            # Close down consumer to commit final offsets.
            self._shutdown()
            return

    def _shutdown(self):
        # Close down consumer to commit final offsets.
        print("close consumer, set 'running' to False")
        self.consumer.close()
        self.running = False