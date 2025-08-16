import copy
import os
from functools import wraps
from shutil import get_terminal_size

import click

from m3cli.services.help_client import EnableAutocompleteCommandHandler, \
    DisableAutocompleteCommandHandler
from m3cli.utils.logger import get_logger
from m3cli.utils.logger import write_logs
from m3cli.utils.utilities import (get_user_access, check_update,
                                   get_non_interactive_access)

HELP_COMMAND = 'full_help'
SHORT_HELP_COMMAND = 'help'
JSON_VIEW = 'json'
TABLE_VIEW = 'table'
FULL_VIEW = 'full'
COMMAND_KEY = 'command'
COMMAND_OUTPUT_PATTERN = '{0} command output:\n{1}'
COMMAND_INPUT_PATTERN = '{0} command input: {1}'
SECURED_PARAM_VALUE = '*****'
VERBOSE_MODE = 'verbose'
RAW_RESPONSE = 'raw'
SECURED_VALUES = []
ACCESS_HELP = '\nUsage: m3 access [parameters]\n\nParameters:\n\n     ' \
              '--access_key,   Access key associated with the Maestro user' \
              ' user\n     ' \
              '--secret_key,   Secret key associated with access key specified' \
              ' in the commands' \
              ' key\n     ' \
              '--api_address,  Address of the Maestro environment. ' \
              ' Please set the custom one if you want to change environment.' \
              '\n     ' \
              '--path,  Path to the file where the user credentials will be ' \
              'stored. Should be used to store credentials for different ' \
              'Maestro environment.'


class TextColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def __extract_parameters(parameters_list):
    parameters_dict = {}
    param_pfx = '-'
    full_param_pfx = '--'

    for index in range(len(parameters_list)):
        if not parameters_list[index].startswith(param_pfx):
            continue
        key = parameters_list[index].replace(full_param_pfx, "")
        if index < len(parameters_list)-1 and not parameters_list[index+1].startswith(param_pfx):
            val = parameters_list[index+1]
        else:
            val = None
        if key in parameters_dict:
            if isinstance(parameters_dict[key], list):
                parameters_dict[key].append(val)
            else:
                parameters_dict[key] = [parameters_dict[key], val]
        else:
            parameters_dict[key] = val
    return parameters_dict


def __prettify_error(action, error):
    width, _ = get_terminal_size()
    action = action if action[-1:] == '.' else f'{action}!'
    divider = "=" * (width - 1)
    return f'{TextColors.FAIL}' \
           f'{divider}{os.linesep}' \
           f'{action}' \
           f'{os.linesep}{os.linesep}Reason: {error}' \
           f'{os.linesep}{divider}' \
           f'{TextColors.ENDC}'


def human_readable_list(values):
    return ', '.join(values)


CONFIG_COMMAND_HANDLER_MAPPING = {
    'enable-autocomplete': EnableAutocompleteCommandHandler,
    'disable-autocomplete': DisableAutocompleteCommandHandler
}


def configuration_executor(config_command, config_command_help, config_params):
    config_command_class = CONFIG_COMMAND_HANDLER_MAPPING[config_command]
    initiate_appropriate_command = config_command_class(
        config_command_help=config_command_help,
        config_params=config_params)
    return initiate_appropriate_command.process_passed_command()


def dynamic_dispatcher(func):
    @wraps(func)
    def wrapper(ctx, *args, **kwargs):
        # var to determine whether to call the command health-check after the
        # 'm3 access' command
        check_health = False

        if kwargs.get(VERBOSE_MODE):
            write_logs()

        raw_response = kwargs.get(RAW_RESPONSE)

        if ctx.args and ctx.args[0] in ['enable-autocomplete',
                                        'disable-autocomplete']:
            try:
                response = configuration_executor(
                    config_command=ctx.args[0],
                    config_command_help=ctx.params['help'],
                    config_params=ctx.args)
                return response
            except AssertionError as e:
                action = f'The command \"{ctx.args[0]}\" failed'
                response = __prettify_error(action=action,
                                            error=e)
                click.echo(response, err=True)
                raise e
        if len(ctx.args) > 0 and ctx.args[0] == 'access':
            if ctx.params['help']:
                click.echo(ACCESS_HELP)
                return
            elif ('--access_key' or '--secret_key' or '--api_address' or
                  '--path') in ctx.args:
                try:
                    access = get_non_interactive_access(
                        *check_args_for_non_interactive_access(ctx)
                    )
                    click.echo(access)
                except AssertionError as e:
                    action = f'The command \"{ctx.args[0]}\" failed'
                    response = __prettify_error(
                        action=action, error=e,
                    )
                    click.echo(response, err=True)
                    raise e
            else:
                access = get_user_access()

            # if the user has entered credits then switch check_health
            # flag to True
            if access:
                check_health = True
            # if user entered "no" then just stop the execution of
            # 'm3 access' command
            else:
                return

        if not ctx.args or kwargs.get(HELP_COMMAND):
            params = {HELP_COMMAND: True}
            if len(ctx.args) >= 1:
                params[COMMAND_KEY] = ctx.args[0]
            return func(**params)
        elif kwargs.get(SHORT_HELP_COMMAND):
            params = {SHORT_HELP_COMMAND: True}
            if len(ctx.args) >= 1:
                params[COMMAND_KEY] = ctx.args[0]
            return func(**params)

        view_type = TABLE_VIEW
        detailed = False
        if kwargs.get(FULL_VIEW) and (
                kwargs.get(JSON_VIEW) or kwargs.get(TABLE_VIEW)):
            detailed = True
            kwargs[FULL_VIEW] = False
        if kwargs.get(JSON_VIEW):
            view_type = JSON_VIEW
        elif kwargs.get(FULL_VIEW):
            view_type = FULL_VIEW
        try:
            parameters = __extract_parameters(ctx.args[1:])
        except AssertionError as e:
            action = f'The command \"{ctx.args[0]}\" failed'
            response = __prettify_error(action=action,
                                        error=e)
            click.echo(response, err=True)
            raise e
        command = ctx.args[0]

        if check_health:  # user entered new credentials
            command = 'health-check'
            parameters = {}

        response = func(
            *args, command=command, parameters=parameters, view_type=view_type,
            detailed=detailed, raw_response=raw_response
        )
        return response

    return wrapper


def cli_response(stdout=click.echo, params_to_be_secured=None, no_output=None):
    """
    Wrapper for formatting cli command response
    :param stdout: function which prints response to the end user
    :param params_to_be_secured: function which returns parameters to be
    secured.
    :param no_output: makes off wrapped command output, only returns the value
    :return:
    """

    def real_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _FUNC_LOG = get_logger(func.__name__)
            try:
                parameter_to_log = copy.deepcopy(kwargs)
                if kwargs:
                    secured_params = params_to_be_secured(
                        kwargs.get(COMMAND_KEY)
                    )
                    if secured_params and not (kwargs.get(HELP_COMMAND) or
                                               kwargs.get(SHORT_HELP_COMMAND)):
                        global SECURED_VALUES
                        for param in secured_params:
                            param_to_be_hidden = \
                                parameter_to_log.get('parameters').get(param)
                            if param_to_be_hidden:
                                SECURED_VALUES.append(param_to_be_hidden)
                                parameter_to_log['parameters'][param] = \
                                    SECURED_PARAM_VALUE
                    _FUNC_LOG.debug(COMMAND_INPUT_PATTERN.format(
                        func.__name__, parameter_to_log)
                    )
                function_result = func(*args, **kwargs)
                if no_output:
                    return function_result
                if function_result:
                    response_word = 'Response:\n' if not kwargs.get(
                        'view_type') == JSON_VIEW else ''
                    response = f'{TextColors.OKGREEN}' \
                               f'{response_word}{function_result}' \
                               f'{TextColors.ENDC}'
                    stdout(response)
            except Exception as e:
                action = f'The command \"{kwargs.get(COMMAND_KEY)}\" failed'
                response = __prettify_error(action=action,
                                            error=e)
                stdout(response, err=True)
                _FUNC_LOG.exception(COMMAND_INPUT_PATTERN.format(
                    func.__name__, e))

        return wrapper

    return real_wrapper


def check_version():
    needs_update = check_update()
    if needs_update:
        return decorate_as_warning(needs_update)
    return None


def decorate_as_warning(text):
    terminal_width, _ = get_terminal_size()
    divider = "=" * (terminal_width - 1)
    return f'{TextColors.WARNING}' \
           f'{divider}{os.linesep}' \
           f'{text}' \
           f'{os.linesep}{divider}' \
           f'{TextColors.ENDC}\n'


def check_args_for_non_interactive_access(ctx):
    access_args = {
        '--access_key': True,
        '--secret_key': True,
        '--api_address': False,
        '--path': False
    }
    result = []
    for arg, required in access_args.items():
        if arg in ctx.args:
            result.append(ctx.args[ctx.args.index(arg) + 1])
        else:
            if required:
                raise AssertionError(f'The parameter "{arg}" is missing')
    return result
