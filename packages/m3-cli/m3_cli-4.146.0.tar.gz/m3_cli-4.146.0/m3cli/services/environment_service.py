import json
import os

from m3cli.utils import (ACCESS_KEY, SECRET_KEY, ADDRESS, SDK_VERSION,
                         CONFIGURATION_FOLDER_PATH,
                         DEBUG_MODE, M3_CLI_RESOURCES_PATH,
                         CREDENTIALS_FILE_PATH, CUSTOM_LOG_PATH,
                         CREDENTIALS_FILE)
from m3cli.utils.utilities import get_user_access


def _get_credentials_from_file(secret_name):
    secret_value = None
    dir_creds = os.path.join(os.getcwd(), CREDENTIALS_FILE)
    if os.path.isfile(dir_creds):
        with open(dir_creds, 'r') as f:
            secret_value = json.load(f).get(secret_name)

    elif os.path.isdir(M3_CLI_RESOURCES_PATH) and os.path.isfile(
            CREDENTIALS_FILE_PATH):
        with open(CREDENTIALS_FILE_PATH, 'r') as f:
            secret_value = json.load(f).get(secret_name)
    return secret_value


def _get_certain_credential(secret_name):
    key = _get_credentials_from_file(secret_name)
    if not key:
        key = os.getenv(secret_name)
    if not key:
        get_user_access()
        key = os.getenv(secret_name)
    return key if key else os.getenv(secret_name)


def get_access_key():
    return _get_certain_credential(ACCESS_KEY)


def get_secret_key():
    return _get_certain_credential(SECRET_KEY)


# todo move agent_address and sdk_version to setup.conf file

def get_agent_address():
    return _get_certain_credential(ADDRESS)


def get_sdk_version():
    return os.getenv(SDK_VERSION, "3.2.80")


def get_configuration_folder_path():
    return os.getenv(CONFIGURATION_FOLDER_PATH)


def get_debug_mode():
    debug_mode = os.getenv(DEBUG_MODE)
    return debug_mode == 'True'


def get_log_path():
    log_path = os.getenv(CUSTOM_LOG_PATH)
    return log_path
