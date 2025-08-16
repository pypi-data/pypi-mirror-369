import json
import uuid

from pika import exceptions

from m3cli.utils.logger import get_logger

RESPONSE_NOT_RECEIVED_ERROR = 'Response was not received.'

SYNC_HEADER = 'sync'
APPLICATION_JSON = 'application/json'

_LOG = get_logger('RabbitMqService')


def build_message(id, command_name, parameters):
    result = {'id': id,
              'type': command_name,
              'parameters': parameters}
    return json.dumps(result)


def _generate_id():
    return str(uuid.uuid4())


class RabbitMqService:
    def __init__(self, rabbit_connection, request_queue, response_queue):
        self.rabbit = rabbit_connection
        self.request_queue = request_queue
        self.response_queue = response_queue

    def execute_async(self, command_name, parameters):
        _LOG.debug('Command info:\n'
                   'command name: {0}\n'
                   'parameters: {1}'.format(command_name, parameters))

        message = build_message(command_name=command_name,
                                parameters=parameters,
                                id=_generate_id())

        _LOG.debug('Going to execute async command: {0}\nCommand format: {1}'
                   .format(command_name, message))

        return self.rabbit.publish(routing_key=self.request_queue,
                                   message=message,
                                   headers={SYNC_HEADER: False},
                                   content_type=APPLICATION_JSON)

    def execute_sync(self, command_name, parameters):
        request_id = _generate_id()
        message = build_message(command_name=command_name,
                                parameters=parameters,
                                id=request_id)

        _LOG.debug('Going to execute sync command: {0}\nCommand format: {1}'
                   .format(command_name, message))

        self.rabbit.publish_sync(routing_key=self.request_queue,
                                 callback_queue=self.response_queue,
                                 correlation_id=request_id,
                                 message=message,
                                 headers={SYNC_HEADER: True},
                                 content_type=APPLICATION_JSON)
        try:
            response_json = self.rabbit.consume_sync(queue=self.response_queue,
                                                     correlation_id=request_id)
        except exceptions.ConnectionWrongStateError as e:
            return str(e), True

        if response_json:
            response = json.loads(response_json).get('response')
            _LOG.info('Return response of executed command: {0}. Response: {1}'
                      .format(command_name, response))
            return response
        else:
            return RESPONSE_NOT_RECEIVED_ERROR + '\nTimeout: {0} seconds.'.format(
                self.rabbit.timeout), True
