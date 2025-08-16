import json
import os
import sys
from datetime import datetime, date, timezone, timedelta
from decimal import Decimal
from getpass import getpass
from pathlib import Path
from typing import Any

import click
from packaging import version

from m3cli.utils import (ACCESS_KEY, SECRET_KEY, ADDRESS, FOLDERS_SEPARATOR,
                         CREDENTIALS_FILE, POSITIVE_ANSWERS,
                         HOME_DIRECTORY, M3_CLI_RESOURCES_DIR,
                         M3_CLI_RESOURCES_PATH, CREDENTIALS_FILE_PATH,
                         HEALTH_CHECK_CMD_NAME)

WINDOWS_SYSTEM = 'win'
HEALTH_CHECK_LAST_VISIT = 'last_visit'
SERVER_UNAVAILABLE_TIMESTAMP = 'server_unavailable'
CLI_LATEST_VERSION = 'cliLatestVersion'
CLI_WINDOWS_DISTRIBUTION_URL = 'cliWindowsDistributionUrl'
CLI_LINUX_DISTRIBUTION_URL = 'cliLinuxDistributionUrl'
CLI_MAC_OS_DISTRIBUTION_URL = 'cliMacOsDistributionUrl'

CONFIRMATION_MESSAGE = 'Maestro CLI credentials have been already set.\n' \
                       'Do you want to set a new credentials? [y/n]: '
DEFAULT_API_ADDRESS = 'https://api-mcc.cloud.epam.com/maestro/api/v3'
SECRET_KEY_ERROR = (
    "Error: Secret Key must be 128, 192, or 256 bits (16, 24, or 32 bytes)\n"
    "Credentials were NOT saved. Please run the command again and enter a valid"
    " key"
)
TIP_MESSAGE_FOR_ACCESS = (
    '\nTip: You can also set credentials non-interactively using:\n'
    '  m3 access --access_key <ACCESS_KEY> --secret_key <SECRET_KEY> '
    '--api_address <API_ADDRESS>'
)


def inherit_dict(root_dict, child_dict):
    child_dict.update({**root_dict, **child_dict})
    return child_dict


def _set_credentials_interactively(credentials_path: str) -> bool:
    print('Please enter your Maestro CLI credentials')
    m3sdk_access_key = input('M3 SDK Access key: ')
    if sys.platform.startswith(WINDOWS_SYSTEM):
        print('Use right-click anywhere in the body of the window to paste '
              'M3 SDK Secret key instead of using Ctrl+V')
    m3sdk_secret_key = getpass('M3 SDK Secret key: ')
    key_len = len(m3sdk_secret_key.encode('utf-8'))
    if key_len not in (16, 24, 32):
        print(SECRET_KEY_ERROR)
        print(TIP_MESSAGE_FOR_ACCESS)
        return False

    print(f'Default API link: {DEFAULT_API_ADDRESS}')
    api_link = input(
        'Press Enter to use the default API link above, or paste a custom '
        'API link: '
    ).strip()
    if api_link == '':
        m3sdk_api_address = DEFAULT_API_ADDRESS
        print(f'Using default API link: {DEFAULT_API_ADDRESS}')
    else:
        m3sdk_api_address = api_link
        print(f'Using custom API link: {m3sdk_api_address}')

    os.environ[ACCESS_KEY] = m3sdk_access_key
    os.environ[SECRET_KEY] = m3sdk_secret_key
    os.environ[ADDRESS] = m3sdk_api_address
    __write_credentials_to_file(
        credentials_path=credentials_path,
        access_key=m3sdk_access_key,
        secret_key=m3sdk_secret_key,
        api_address=m3sdk_api_address,
    )
    print("Credentials have been successfully saved")
    print(f"Location: {credentials_path}")
    print(TIP_MESSAGE_FOR_ACCESS)
    return True


def _set_credentials_by_params(
        credentials_path,
        access_key: str = None,
        secret_key: str = None,
        api_address: str = None,
):
    api_address = DEFAULT_API_ADDRESS if not api_address else api_address
    os.environ[ACCESS_KEY] = access_key
    os.environ[SECRET_KEY] = secret_key
    os.environ[ADDRESS] = api_address
    __write_credentials_to_file(
        credentials_path, access_key, secret_key, api_address,
    )


def __write_credentials_to_file(
        credentials_path: str,
        access_key: str,
        secret_key: str,
        api_address: str,
):
    data = {}
    if os.path.exists(credentials_path):
        with open(credentials_path, 'r') as file:
            try:
                data = json.load(file)
            except json.decoder.JSONDecodeError:
                raise SyntaxError(
                    f'{credentials_path} contains invalid JSON'
                )
    with open(credentials_path, 'w') as file:
        data.update({ACCESS_KEY: access_key,
                     SECRET_KEY: secret_key,
                     ADDRESS: api_address})
        file.write(json.dumps(data))


def _get_credentials_file_path():
    """
    Get filepath for default.cr.
    """
    creds_path = os.path.join(HOME_DIRECTORY, M3_CLI_RESOURCES_DIR)
    if not os.path.isdir(creds_path):
        os.makedirs(creds_path)
    return creds_path + FOLDERS_SEPARATOR + CREDENTIALS_FILE


def get_non_interactive_access(
        access_key: str,
        secret_key: str,
        api_address=None,
        path=None,
) -> str:
    if path:
        creds_filepath = Path(path)
        creds_filepath.mkdir(parents=True, exist_ok=True)
        creds_filepath = creds_filepath / CREDENTIALS_FILE
    else:
        creds_filepath = _get_credentials_file_path()
    _set_credentials_by_params(
        creds_filepath, access_key, secret_key, api_address,
    )
    return f'Credentials have been successfully saved in: \n{creds_filepath}'


def get_user_access() -> bool:
    creds_filepath = _get_credentials_file_path()
    if (check_credentials_in_file(creds_filepath)
            and input(CONFIRMATION_MESSAGE).lower().strip() not
            in POSITIVE_ANSWERS):
        return False
    return _set_credentials_interactively(creds_filepath)


def check_credentials_in_file(file_path):
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            if data.get(ACCESS_KEY) and data.get(SECRET_KEY) and \
                    data.get(ADDRESS):
                return True
    return False


def open_creds_file():
    #  no ./.creds folder
    if not os.path.exists(M3_CLI_RESOURCES_PATH):
        os.mkdir(M3_CLI_RESOURCES_PATH)
        open(CREDENTIALS_FILE_PATH, 'w').close()
    #  no ./.creds/default.cr file
    if not os.path.exists(CREDENTIALS_FILE_PATH):
        open(CREDENTIALS_FILE_PATH, 'w').close()

    return CREDENTIALS_FILE_PATH


def check_update():
    """
    Checks the latest version of m3cli. If the version is not up to date,
    then a warning message will be displayed.
    """
    creds_file = open_creds_file()
    data = __load_creds_contents(creds_file)
    latest_version = data.get(CLI_LATEST_VERSION)
    if not latest_version:
        return 'Please run command "m3 health-check" to check the ' \
               'latest version of m3cli.'

    current_version = get_current_cli_version()
    if version.parse(latest_version) > version.parse(current_version):
        return __get_warning_message(latest_version=latest_version,
                                     current_version=current_version,
                                     creds_data=data)


def get_current_cli_version():
    from importlib.metadata import version as lib_version
    return lib_version('m3-cli')


def perform_version_check(invoked_command, is_help_invoked,
                          view_type, detailed):
    """
    Updates the latest version and distribution links of m3cli in the
    /.creds/default.cr file. If there is no such file, it will be created.

    The update is performed once a day or when the 'health-check' is invoked
    explicitly. The up-to-date version and distribution links are stored
    locally to avoid accessing the remote file with each request.
    """
    creds_file = open_creds_file()
    data = __load_creds_contents(creds_file)
    health_check_explicitly = (not is_help_invoked
                               and invoked_command == HEALTH_CHECK_CMD_NAME)
    try:
        if health_check_explicitly or __should_perform_health_check(data):
            return execute_health_check(view_type=view_type,
                                        detailed=detailed)
    except ConnectionError:
        data.update({
            SERVER_UNAVAILABLE_TIMESTAMP: datetime.timestamp(datetime.now())
        })
        with open(creds_file, 'w') as write_file:
            json.dump(data, write_file)
        from m3cli.utils.decorators import decorate_as_warning
        click.echo(decorate_as_warning(
            'Server is temporary unavailable. '
            'Could not retrieve available updates. The version of CLI you '
            'use may be outdated.'))
    except AssertionError as e:
        if health_check_explicitly:
            raise e
        from m3cli.utils.decorators import decorate_as_warning
        click.echo(decorate_as_warning(
            f'WARNING. Can not check the latest m3-cli updates. '
            f'Reason: "{e}" while performing a health-check. '
            f'{os.linesep}Please contact Maestro Support Team.'
        ))
    finally:
        data = __load_creds_contents(creds_file)
        if not data.get(SERVER_UNAVAILABLE_TIMESTAMP):
            from m3cli.utils.decorators import check_version
            outdated_cli_warning = check_version()
            if outdated_cli_warning:
                click.echo(outdated_cli_warning)


def execute_health_check(view_type, detailed):
    if not view_type:
        from m3cli.utils.decorators import JSON_VIEW
        view_type = JSON_VIEW
    from m3cli.m3 import execute_command
    return execute_command(
        command='health-check', parameters={},
        view_type=view_type, detailed=detailed)


def __load_creds_contents(creds_file):
    with open(creds_file, "r+") as file:
        try:
            data = json.load(file)
        except json.decoder.JSONDecodeError:
            data = {}
            __write_json_to_file(creds_file, data)
    return data


def __should_perform_health_check(data: dict):
    server_unavailable_time = datetime.fromtimestamp(
        data.get(SERVER_UNAVAILABLE_TIMESTAMP, 0))
    health_check_timeout = server_unavailable_time + timedelta(hours=1)
    if datetime.now() < health_check_timeout:
        return False
    return (HEALTH_CHECK_LAST_VISIT not in data
            or __has_the_day_passed(data[HEALTH_CHECK_LAST_VISIT])
            or not data.get(CLI_LATEST_VERSION)
            or not data.get(CLI_WINDOWS_DISTRIBUTION_URL)
            or not data.get(CLI_LINUX_DISTRIBUTION_URL)
            or not data.get(CLI_MAC_OS_DISTRIBUTION_URL))


def __get_warning_message(latest_version: str, current_version: str,
                          creds_data: dict):
    linux_url = creds_data.get(CLI_LINUX_DISTRIBUTION_URL)
    mac_url = creds_data.get(CLI_MAC_OS_DISTRIBUTION_URL)
    win_url = creds_data.get(CLI_WINDOWS_DISTRIBUTION_URL)
    return \
        (f'You are using an outdated version of m3-cli ({current_version}). '
         f'Version {latest_version} is now available. '
         f'\nPlease use the next link to download cli for Linux - {linux_url}'
         f'\nTo upgrade cli on macOS run the '
         f'following command: pip install {mac_url},'
         f'\nFor windows run: pip install {win_url}')


def __has_the_day_passed(timestamp: float):
    received_date = date.fromtimestamp(timestamp)
    return received_date < date.today()


def __write_json_to_file(filename, data):
    with open(filename, 'w') as write_file:
        json.dump(data, write_file)


def load_file_contents(file_path):
    if not os.path.isfile(file_path):
        raise FileExistsError(f'File {file_path} is absent.')
    try:
        with open(file_path, 'r') as f:
            contents = f.read()
    except UnicodeDecodeError:
        import codecs
        with codecs.open(file_path, 'r', encoding='utf-8',
                         errors='ignore') as fdata:
            contents = fdata.read()
    return contents


def load_properties_file(file_path):
    """
    Reads a properties file into a dictionary.
    Allowed lines in the properties file are:
        a key=value pair;
        a blank line;
        a comment starting with '#'.
    """
    parameters = {}
    with open(file_path, 'r') as file:
        for line in file:
            if '=' not in line or line.startswith('#'):
                continue
            key, value = line.split('=', maxsplit=1)
            parameters[key.strip()] = value.strip()
    return parameters


def is_not_empty_file(file_path):
    return file_path and os.path.isfile(file_path) and os.path.getsize(
        file_path) > 0


def timestamp_to_iso(timestamp):
    return datetime.fromtimestamp(int(timestamp / 1000),
                                  tz=timezone.utc).isoformat()


def get_var_type_value_console(value: Any) -> tuple[str, Any]:
    match value:
        case str(value) if ',' in value and '=' in value:
            value = value.replace(' ', '')
            map_values = value.split(',')
            if not all('=' in item for item in map_values):
                raise AssertionError(
                    "Non key-value element found in map variable."
                )
            value = dict(item.split('=') for item in map_values)
            if not all(key for key in value.keys()):
                raise AssertionError("Empty key found in map variable.")
            return 'MAP', value
        case str(value) if ',' in value:
            value = value.replace(' ', '').strip('][').split(',')
            return 'LIST', value
        case str(value) if '=' in value:
            temp = value.replace(' ', '').split('=')
            if not temp[0]:
                raise AssertionError("Empty key found in map variable.")
            value = {temp[0]: temp[-1]}
            return 'MAP', value
        case str(value):
            return 'STRING', value
        case _:
            raise AssertionError(
                "Unsupported variable type, please contact the administrator. "
                "Supported types for console: LIST, MAP, STRING"
            )


def get_var_type_value_file(value: Any) -> tuple[str, Any]:
    match value:
        case str(value):
            return 'STRING', value
        case list(value):
            return 'LIST', value
        case dict(value):
            return 'MAP', value
        case bool(value):
            return 'BOOL', value
        case int(value):
            return 'NUMBER', value
        case _:
            raise AssertionError(
                "Unsupported variable type, please contact the administrator. "
                "Supported types for JSON file: LIST, MAP, STRING, BOOL, NUMBER"
            )


def handle_variables(
        variables: str | None,
        path_to_file: str | None,
) -> dict:
    if variables and path_to_file:
        raise AssertionError(
            'Cannot use the "--variables" and "--variables-file" parameters '
            'together'
        )
    if path_to_file:
        if not os.path.isfile(path_to_file):
            raise AssertionError(f'There is no file by path: "{path_to_file}"')
        try:
            with open(path_to_file, 'r') as file:
                variables = json.load(file)
        except json.JSONDecodeError:
            raise ValueError(f'Invalid JSON format in file: "{path_to_file}"')

    result = {}
    for name, value in variables.items():
        var_type, value = (
            get_var_type_value_file(value) if path_to_file
            else get_var_type_value_console(value)
        )
        result[name] = {
            'type': var_type,
            'value': value,
            'sensitive': True,
            'name': name,
        }
    return result


def format_floats_in_data(data):
    if isinstance(data, dict):
        return {k: format_floats_in_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [format_floats_in_data(item) for item in data]
    elif isinstance(data, float):
        return format(Decimal(str(data)), 'f').rstrip('0').rstrip('.') or '0'
    elif isinstance(data, int):
        return str(data)
    else:
        return data
