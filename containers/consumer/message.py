#!/usr/bin/env python3

import json
import requests

class Message():
    """ Class for handling Messages """
    # Dict translating debezium_op to a corresponding integer value. c = Create, r = Read (insert from initial snapshot)
    # u = Upadte, d = Delete, t = Tombstone (empty event sent after a deleted row)
    operations_dict = {
        'c': 1,
        'r': 1,
        'u': 0,
        'd': -1,
        't': 999
        }

    def __init__(self, msg, api_endpoint):
        """ Instantiate a Message object """
        # Message class documentation:
        # https://docs.confluent.io/4.1.2/clients/confluent-kafka-python/index.html#confluent_kafka.Message

        self.api_endpoint = api_endpoint
        self.msg_header_topic = msg.topic()
        self.msg_header_offset = msg.offset()
        self.msg_header_partition = msg.partition()
        self.msg_header = {
            'topic': self.msg_header_topic,
            'offset': self.msg_header_offset,
            'partition': self.msg_header_partition
            }

        self.operation, self.request_body = self._set_message_properties(msg)

    def _set_message_properties(self, msg):
        """ Set operation and request_body properties for the message """

        # If the previous message was a delete event, the message is empty ('tombstone' message).
        # Accordingly, set operation to 't' (for 'tombstone')
        operation = 't'
        request_body = {
            'Operation': 999,
            'UnterkunftTermin': {}
        }
    
        if not msg.value() is None:
            # Convert byte-string to string:
            data_string = msg.value().decode('UTF-8')

            data_dict = json.loads(data_string)
            payload = data_dict['payload']
            operation = payload['op']

            # Depending on operation, the relevant data is stored in either 'after' or 'before' property
            request_body['UnterkunftTermin'] = payload['after'] if operation != 'd' else payload['before']

            # Save operation integer representation 
            request_body['Operation'] = Message.operations_dict[operation]

        return operation, request_body


    def handle_message(self):
        """ Public method. Send request to API or do nothing """

        # Unless operation is a tombstone operation, send event to API in request body
        if self.operation != 't':
            return self._send_request(self.request_body)

        return self._handle_tombstone()

    def _send_request(self, request_body):
        """ Send POST request to API """

        print(f'msg_header:{self.msg_header}')
        print(f'msg request_body before post request:{self.request_body}')

        request_headers = {'Content-Type': 'application/json; charset=utf-8'}

        print(f'\nsending request to url: {self.api_endpoint}')

        response = requests.post(self.api_endpoint, headers=request_headers, json=request_body)

        print(f'\nresponse.status_code:{response.status_code}')
        print(f'\nresponse.text:{response.text}')
        input('press enter')

        return response
        

    def _handle_tombstone(self):
        """ Handle empty message ('tombstone') - do nothing """
        # Do nothing
        print('No request sent: tombstone message')
        return