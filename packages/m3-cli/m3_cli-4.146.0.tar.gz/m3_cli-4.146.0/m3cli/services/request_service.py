import hashlib
import hmac
import json
import socket
import uuid
from datetime import datetime

import requests

from m3cli.services.aes_cipher_service import AESCipherService, UTF_8
from m3cli.services.environment_service import (
    get_access_key, get_agent_address, get_sdk_version, get_secret_key,
)
from m3cli.utils.decorators import SECURED_VALUES
from m3cli.utils.logger import get_logger
from m3cli.utils.utilities import open_creds_file, __load_creds_contents

RESPONSE_ENDING_CHARS = b'}]}'

_LOG = get_logger('request_service')

USER_UNKNOWN = 'UNKNOWN'
CLIENT_IDENTIFIER = "api-server"

POST = 'POST'

HEADER_ENCRYPTED_ACCESS = 'maestro-accesskey'
HEADER_DATE = 'maestro-date'
HEADER_ENCRYPTED_DATE = 'maestro-authentication'

HTTP_PROTOCOL = 'http://'
HTTPS_PROTOCOL = 'https://'

EXECUTORS = {
    POST: requests.post
}

MISSED_KEY_EXCEPTION = 'Missed {0} key for M3 SDK API. Please create ' \
                       'environment variable with name "M3SDK_{0}_KEY" and ' \
                       'value that contains your valid SDK {0} Key.'
INVALID_URL_PROTOCOL = 'Invalid URL: {0}. Please specify protocol.'


def wrap_request(cmd_def, request):
    if cmd_def.get('request_wrapper'):
        request.parameters = {
            cmd_def.pop('request_wrapper'): request.parameters
        }
    return request


def verify_response(response):
    status_code = response.status_code
    if status_code == 404:
        raise AssertionError(f'[{status_code}] Requested resource not found. '
                             f'{response.raw.reason}')
    if status_code == 401:
        creds_file = open_creds_file()
        data = __load_creds_contents(creds_file)
        error_msg = f'[{status_code}] Bad credentials. Please use the command ' \
                    f'"m3 access" to set up a valid credentials.'
        if not data.get('cliWindowsDistributionUrl'):
            error_msg += ' Or try to install the latest version of m3 tool.'
        raise AssertionError(error_msg)
    if status_code == 413:
        message = response.json().get('message', 'Payload Too Large')
        raise AssertionError(f'[{status_code}] {message}')
    if status_code == 500:
        raise AssertionError(
            f'[{status_code}] Error during executing request. '
            f'{response.raw.reason}')
    if not status_code:
        raise AssertionError(f'[{204}] Empty response received. '
                             f'{response.raw.reason}')
    if status_code != 200:
        raise AssertionError(
            f'[{status_code}] Error during executing request.'
            f'Message: {response.text}')
    return response.content.decode()


def find_item(obj, key):
    if isinstance(obj, dict):
        for each_key in obj:
            if key in each_key:
                return obj
    for k, v in obj.items():
        if isinstance(v, dict):
            item = find_item(v, key)
            if item is not None:
                return item


def mask_pass(obj, key, replace_value, replace_now=False):
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(
            mask_pass(x, key, replace_value) for x in obj if x is not None)
    elif isinstance(obj, dict):
        response = {}
        for k, v in obj.items():
            response[k] = mask_pass(v, key, replace_value, True) \
                if key in k else mask_pass(v, key, replace_value)
        return response
    elif replace_now:
        return replace_value
    else:
        return obj


def mask_params(obj, secured_params, replace_value='*****'):
    params_to_log = str(obj)
    for param in secured_params:
        params_to_log = params_to_log.replace(param, replace_value)
    return params_to_log


def get_host():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    primary_ip_addr = s.getsockname()[0]
    s.close()
    return primary_ip_addr


class BaseRequest:
    def __init__(
            self,
            command: str,
            method: str = POST,
            parameters: dict | None = None,
            api_action=None,
            metadata=None,
    ) -> None:
        self.command = command
        self.api_action = api_action
        self.parameters = parameters
        self.method = method
        self.metadata = metadata

    def __repr__(self) -> str:
        return json.dumps(self.get_request())

    def get_request(self):
        return {
            'command': self.command,
            'api_action': self.api_action,
            'parameters': self.parameters,
            'method': self.method
        }


class SdkClient:
    def __init__(self, signer=None):
        secret_key = get_secret_key()
        if not secret_key:
            raise KeyError(MISSED_KEY_EXCEPTION.format('SECRET'))
        self.signer = AESCipherService(secret_key) if not signer else signer
        self.base_address = get_agent_address()
        if not self.base_address.startswith(HTTP_PROTOCOL) \
                and not self.base_address.startswith(HTTPS_PROTOCOL):
            raise AssertionError(
                INVALID_URL_PROTOCOL.format(self.base_address))

    @staticmethod
    def request_params(request):
        request_mapping = {}
        unencrypted_object = []
        for req in request:
            request_id = str(uuid.uuid4())
            unencrypted_object.append(
                {
                    'id': request_id,
                    'type': req.api_action.upper(),
                    'params': {
                        'body': json.dumps(
                            req.parameters) if req.parameters else None
                    }
                }
            )
            request_mapping[request_id] = req
        return unencrypted_object, request_mapping

    def execute(self, request):
        request = [request] if isinstance(request, BaseRequest) else request
        access_key = get_access_key()
        if not access_key:
            raise KeyError(MISSED_KEY_EXCEPTION.format('ACCESS'))
        unencrypted_object, request_mapping = SdkClient.request_params(
            request=request)

        _LOG.debug(f'Request which will be submitted to server: '
                   f'{mask_params(request, SECURED_VALUES)}')
        encrypted_raw_object = self.signer.encrypt(
            json.dumps(unencrypted_object))
        _LOG.debug('Request body has been encrypted')
        date = int(datetime.now().timestamp()) * 1000
        signature = hmac.new(
            key=bytearray(f'{get_secret_key()}{date}'.encode(UTF_8)),
            msg=bytearray(
                f'M3-POST:{access_key}:{date}:{USER_UNKNOWN}'.encode(UTF_8)
            ),
            digestmod=hashlib.sha256
        ).hexdigest()
        n = 2
        signature_resolved = ''
        for each in [signature[i:i + n] for i in range(0, len(signature), n)]:
            signature_resolved += '1' + each
        new_request = {
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "maestro-authentication": signature_resolved,
                "maestro-request-identifier": CLIENT_IDENTIFIER,
                "maestro-user-identifier": USER_UNKNOWN,
                "maestro-date": str(date),
                "maestro-accesskey": access_key,
                "maestro-sdk-version": get_sdk_version(),
                "maestro-sdk-async": 'false',
                "X-App": "m3-cli",
                "X-Client-Id": get_host()
            },
            'data': encrypted_raw_object,
            'url': self.base_address
        }
        _LOG.debug('Request body has been signed')
        executor = EXECUTORS.get(self.request_method(request=request))
        try:
            response = executor(**new_request)
        except requests.ConnectionError:
            raise ConnectionError('Failed to establish new connection')

        response_raw = verify_response(response)
        _LOG.debug('Response has been obtained')
        response = self.signer.decrypt(response_raw)
        # Due to Initialization vector in decrypting method
        # there is need to split useful and useless parts of the
        # server response.
        splitter = response.rindex(RESPONSE_ENDING_CHARS)
        response = response[:splitter] + RESPONSE_ENDING_CHARS
        _LOG.debug('Response has been decrypted')
        try:
            results = json.loads(response).get('results')
            return request_mapping, results
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(
                f'There are some troubles with response decryption: {e.reason}')

    @staticmethod
    def request_method(request):
        return request[0].method
