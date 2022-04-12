#!/usr/bin/env python3

import os
import avro.io
from confluent_kafka.admin import AdminClient

from messagepoller import MessagePoller

class TopicConsumer():
    """ Singleton class for TopicConsumer """

    def __init__(self):
        """ Instantiate a TopicConsumer object """

        params = {
            'topics': [],
            'bootstrap_broker_servers': '',
            'group_id': '3',
            'auto_offset_reset': 'smallest'
        }

        try:
            # Use docker compose environment variables. Will exist if started from docker-compose.
            params['topics'] = [os.environ['TOPIC']]
            params['bootstrap_broker_servers'] = os.environ['BOOTSTRAP_BROKER_SERVER'] + ':' + os.environ['BOOTSTRAP_BROKER_PORT']
            params['api_endpoint'] = "http://" + os.environ['API_ENDPOINT_SERVER'] + ":" + os.environ['API_ENDPOINT_PORT'] + "/Werbemittel/api/Importer"
            print("Using environment parameters")

        except:
            # Otherwise use the following
            params['topics'] = ['MSSQLSERVER.dbo.persons']
            params['bootstrap_broker_servers'] = 'localhost:9093'
            params['api_endpoint'] = 'http://host.docker.internal:5000' + "/Werbemittel/api/Importer"
            print("Failed to get environment params: fallback to default params")

        self._params = params

    def display_initial_broker_data(self):
        """ Display internal and external bootstrap server addresses """
        admin_client = AdminClient({'bootstrap.servers': self._params['bootstrap_broker_servers']})
        md=admin_client.list_topics(timeout=10)

        print(f"bootstrap_broker_servers: {self._params['bootstrap_broker_servers']}")
        print(f"brokers: {md.brokers}")


    def start_polling(self):
        """ Instantiate MessagePoller and start polling for messages """
        poller = MessagePoller(self._params)
        poller.loop_poll_messages()

if __name__ == '__main__':
    topic_consumer = TopicConsumer()
    topic_consumer.display_initial_broker_data()
    topic_consumer.start_polling()

