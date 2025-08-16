import json
import os
from copy import copy
from os.path import expanduser
from typing import Any

from tabulate import tabulate

from m3cli.services.environment_service import (
    get_configuration_folder_path, CONFIGURATION_FOLDER_PATH,
)
from m3cli.services.interactive_options_service import (
    INTERACTIVE_OPTIONS_ATTRIBUTE,
)
from m3cli.services.request_service import mask_params
from m3cli.services.validation_service import (
    COMMANDS_KEY, HELP_FILE_KEY, VALIDATION_KEY, HELP_KEY, PARAMS_KEY,
    ALIAS_KEY, REQUIRED_KEY, SECURE_KEY, DOMAIN_PARAMETERS_KEY, GROUPS_KEY,
    VALIDATION_TYPE, DATE_PATTERN, AUXILIARY_GROUP_PREFIX, EMAIL_GROUP_SUFFIX,
    AUXILIARY_GROUP_SUFFIX, EMAIL_GROUP_PREFIX,
)
from m3cli.utils import (
    CREDENTIALS_FILE, M3_CLI_RESOURCES_DIR, M3_PROPERTIES_FILE,
    RESERVED_KEYWORDS,
)
from m3cli.utils.decorators import SECURED_VALUES
from m3cli.utils.logger import get_logger
from m3cli.utils.utilities import load_properties_file, inherit_dict

_LOG = get_logger('commands_service')
COMMAND_STUB = '<command>'
HELP_STUB = 'Here are the commands supported by the current version ' \
            'of Maestro CLI. \nIMPORTANT: The scope of commands you ' \
            'can execute depends on your user permissions. \n\nOutput:'

COMMANDS_DEF_FILE_NAME = 'commands_def.json'

GENERAL_HELP_STRING = """
--------------------------------------------------------------------------------
Description: {0}

Usage: m3 {1} [parameters]

{2}

{3}
"""
SHORT_HELP_STRING = """
{4}

Usage: m3 {0} [parameters]

Use {1} parameter for all available options

{2}

{3}
"""
HELP_WITH_RELATED_COMMANDS_STRING = """
{0}


Related commands:

{1}
"""
RELATED_COMMAND_STRING = """{0}:
        {1}

"""
HELP_MESSAGE_HELP = 'Shows the detailed help for the command'
SHORT_HELP_MESSAGE_HELP = 'Shows the short help for the command'
HELP_MESSAGE_KEY = '--full-help'
SHORT_HELP_MESSAGE_KEY = '--help'
TABLE_HELP = 'Returns the server response in the table form (default)'
TABLE_KEY = '--table'
JSON_HELP = 'Returns the server response in the JSON format'
JSON_KEY = '--json'
VERBOSE_HELP = 'Controls the verbosity of command output'
VERBOSE_KEY = '--verbose'
FULL_HELP = 'Shows the full response from the server without any specific ' \
            'formatting (can be used with --json)'
FULL_KEY = '--full'
RAW_HELP = 'Shows raw response from the server (can be used with --json)'
RAW_KEY = '--raw'
CASE_KEY = 'case'
UPPER = 'upper'
LIST = 'list'
LOWER = 'lower'
API_PARAM_NAME = 'api_param_name'
ACCESS_CMD_ALIAS = 'access'
ACCESS_HELP = f"Set up all needed settings. You can use the command in " \
              f"non-interactive mode by specifying parameters: {os.linesep}" \
              f"--access_key, --secret_key, --api_address"
TABLE_HEADER_COMMAND = 'COMMAND'
TABLE_HEADER_ALIAS = 'ALIAS'
TABLE_HEADER_DESCRIPTION = 'DESCRIPTION'


def _resolve_parameter_case(case_identifier, parameter_value, parameter_type):
    """
    Resolve the case parameter
    """
    if case_identifier == UPPER:
        parameter_value = [value.upper() for value in parameter_value] if \
            parameter_type == LIST else parameter_value.upper()
    if case_identifier == LOWER:
        parameter_value = [value.lower() for value in parameter_value] if \
            parameter_type == LIST else parameter_value.lower()

    return parameter_value


def _resolve_commands_def_path(default_path, env_path, file_name):
    return os.path.join(env_path, file_name) \
        if env_path else os.path.join(
        default_path, file_name)


def _resolve_default_cr_path(file_name):
    """
    Set path to file default.cr.

    :param file_name: name of file
    """
    home_directory = expanduser("~")
    return os.path.join(home_directory, M3_CLI_RESOURCES_DIR, file_name)


def load_parameters_from_json(file_path):
    try:
        with open(file_path, 'r') as file:
            config = json.loads(file.read())
            parameter_set = {}
            for key, value in config.items():
                if key not in RESERVED_KEYWORDS:
                    parameter_set.update({key: value})
    except json.JSONDecodeError:
        raise SyntaxError(
            f'{file_path} contains an invalid JSON')
    return parameter_set


def load_parameters_from_properties(file_path):
    parameters = load_properties_file(file_path)
    for keyword in RESERVED_KEYWORDS:
        parameters.pop(keyword, None)
    return parameters


def get_help_key(cmd_def, cmd_name=None):
    help_string = cmd_def.get(HELP_KEY)
    if not help_string:
        _LOG.debug(f'Definition of the help command \"{cmd_name}\" '
                   f'is broken: absent help message')
        help_string = " "
    return help_string


class CommandsService:
    def __init__(self, m3cli_path, validation_service):
        path_env_commands_def = get_configuration_folder_path()
        commands_def_file_path = _resolve_commands_def_path(
            default_path=m3cli_path,
            env_path=path_env_commands_def,
            file_name=COMMANDS_DEF_FILE_NAME)
        _LOG.debug(f'Resolved path to {COMMANDS_DEF_FILE_NAME}: '
                   f'{commands_def_file_path}')
        self.params_file_path = _resolve_default_cr_path(
            file_name=CREDENTIALS_FILE)
        _LOG.debug(f'Resolved path to {CREDENTIALS_FILE}: '
                   f'{self.params_file_path}')
        self.default_params = self._load_default_parameters()
        if not os.path.isfile(commands_def_file_path):
            raise FileExistsError(
                f'File with commands configuration is absent. '
                f'Provided path: {commands_def_file_path}'
                f'\nPlease set environment variable '
                f'{CONFIGURATION_FOLDER_PATH} to specify the folder '
                f'containing m3cli configuration files.')
        self.commands_file_path = commands_def_file_path
        self.commands_def = self.__load_commands_def()
        self.validation_service = validation_service

    def __load_commands_def(self):
        try:
            with open(file=self.commands_file_path, mode='r') as cmd_file:
                commands_def = json.loads(cmd_file.read())
            _LOG.debug(
                f'{COMMANDS_DEF_FILE_NAME} has been successfully loaded')
            for name, definition in commands_def.get('commands').items():
                definition['name'] = name
        except json.JSONDecodeError:
            raise SyntaxError(
                f'{COMMANDS_DEF_FILE_NAME} contains invalid JSON')
        return commands_def

    def __get_help_from_file(self, command):
        import m3cli.commands_help as commands_help
        # Replaced hyphen to underscore in the command for full-help
        command = command.replace('-', '_')
        if command in [item for item in dir(commands_help) if
                       not item.startswith("__")]:
            return getattr(commands_help, command)

    def validate_meta(self):
        return self.validation_service.validate_meta(meta=self.commands_def)

    def get_help(self, command, compact=False):
        all_commands = self.commands_def.get(COMMANDS_KEY)
        if command:
            cmd_name, cmd_def = self.__resolve_command_def(command)
            if not cmd_def:
                raise AssertionError(f'Command \"{command}\" is unknown')
            current_help = cmd_def.get(HELP_KEY) if not cmd_def.get(
                HELP_FILE_KEY) else self.__get_help_from_file(cmd_name)
            if not current_help:
                raise AssertionError(
                    f'Definition of the command \"{cmd_name}\" '
                    f'is broken: absent help message')
            if not compact:
                t_data = [
                    ['\t', '\t', SHORT_HELP_MESSAGE_KEY, '', '',
                     SHORT_HELP_MESSAGE_HELP],
                    ['\t', '\t', HELP_MESSAGE_KEY, '', '', HELP_MESSAGE_HELP],
                    ['\t', '\t', VERBOSE_KEY, '', '', VERBOSE_HELP],
                    ['\t', '\t', JSON_KEY, '', '', JSON_HELP],
                    ['\t', '\t', TABLE_KEY, '', '', TABLE_HELP],
                    ['\t', '\t', FULL_KEY, '', '', FULL_HELP],
                    ['\t', '\t', RAW_KEY, '', '', RAW_HELP],
                    ['\t', '\t', '', '', '', '']
                ]
            else:
                t_data = []

            command_params = cmd_def[PARAMS_KEY].items()
            if not cmd_def.get("keep-params-order"):
                command_params = sorted(
                    command_params, key=lambda x: (-x[1]['required'], x[0])
                )

            for each_param, each_param_value in command_params:
                param_alias = each_param_value.get(ALIAS_KEY)
                t_data.append([
                    '\t',
                    '\t',
                    '--' + str(each_param) + ',',
                    '-' + str(param_alias) + ',' if param_alias else '',
                    str('*' if each_param_value.get(REQUIRED_KEY) else ""),
                    each_param_value.get(HELP_KEY)
                ])
            table_item = tabulate(tabular_data=t_data,
                                  tablefmt="plain")
            # Checking for empty parameters in commands
            if not table_item:
                table_item = "There are no parameters in the command"
            cmd_name_alias = f'{cmd_name}'
            cmd_alias = cmd_def.get(ALIAS_KEY)
            if cmd_alias:
                cmd_name_alias += f'({cmd_alias})'
            if compact:
                return SHORT_HELP_STRING.format(f'{cmd_name_alias}',
                                                HELP_MESSAGE_KEY,
                                                'Parameters:', table_item,
                                                get_help_key(cmd_def,
                                                             cmd_name))
            related_commands = self._find_related_commands(cmd_name, cmd_def)
            if related_commands:
                current_help = self._append_related_commands_help(
                    help_content=current_help,
                    related_commands=related_commands)
            return GENERAL_HELP_STRING.format(current_help,
                                              f'{cmd_name_alias}',
                                              'Parameters:', table_item)
        else:
            table_headers = [each.upper() for each in [
                TABLE_HEADER_COMMAND, TABLE_HEADER_ALIAS,
                TABLE_HEADER_DESCRIPTION]]
            t_data = [[ACCESS_CMD_ALIAS, ACCESS_CMD_ALIAS, ACCESS_HELP]]
            for each_group_name, each_group_desc in sorted(
                    all_commands.items()):
                each_group_desc[
                    TABLE_HEADER_DESCRIPTION] = each_group_desc.get(
                    HELP_KEY) \
                    if not each_group_desc.get(HELP_FILE_KEY) \
                    else self.__get_help_from_file(each_group_name)
                t_data.append([each_group_name,
                               each_group_desc.get(ALIAS_KEY),
                               each_group_desc.get(HELP_KEY).split(
                                   '\nExamples:')[0]
                               ])
            table_item = tabulate(tabular_data=t_data,
                                  headers=table_headers,
                                  tablefmt='grid')
            return GENERAL_HELP_STRING.format(HELP_STUB, COMMAND_STUB,
                                              '', table_item)

    def _find_related_commands(self, cmd_name, cmd_def):
        all_commands = self.commands_def.get(COMMANDS_KEY)
        related_commands = []
        auxiliary_commands = []
        groups = cmd_def.get(GROUPS_KEY, [])
        for other_cmd_name, other_cmd_def in all_commands.items():
            if other_cmd_name == cmd_name:
                continue
            other_cmd_groups = other_cmd_def.get(GROUPS_KEY, [])
            auxiliary_group = f'{AUXILIARY_GROUP_PREFIX}' \
                              f'{cmd_name}{AUXILIARY_GROUP_SUFFIX}'
            other_cmd_main_groups = \
                self.filter_main_command_groups(other_cmd_groups)
            if auxiliary_group in other_cmd_groups:
                auxiliary_commands.append(other_cmd_def)
            elif any(group in other_cmd_main_groups for group in groups):
                related_commands.append(other_cmd_def)
        related_commands.sort(key=lambda cmd: cmd['name'])
        auxiliary_commands.sort(key=lambda cmd: cmd['name'])
        related_commands.extend(auxiliary_commands)
        return related_commands

    @staticmethod
    def filter_main_command_groups(other_cmd_groups):
        return [_ for _ in other_cmd_groups
                if not _.startswith(AUXILIARY_GROUP_PREFIX)
                and not _.endswith(AUXILIARY_GROUP_SUFFIX)
                and not _.startswith(EMAIL_GROUP_PREFIX)
                and not _.endswith(EMAIL_GROUP_SUFFIX)]

    def _format_command_example(self, command):
        cmd_params = command.get(PARAMS_KEY, {})
        default_params = []
        generic_params = []
        for p_name, p_def in cmd_params.items():
            if not p_def.get(REQUIRED_KEY):
                continue
            if p_name in self.default_params:
                p_value = self.default_params[p_name]
                default_params.append(self._format_example_parameter(
                    p_name, p_value, p_def.get(ALIAS_KEY)))
            else:
                p_type = p_def[VALIDATION_KEY][VALIDATION_TYPE]
                p_value = self._get_parameter_placeholder(p_name, p_type)
                generic_params.append(self._format_example_parameter(
                    p_name, p_value, p_def.get(ALIAS_KEY)))
        all_params = [*default_params, *generic_params]
        return f'm3 {command["name"]} {" ".join(all_params)}'.rstrip()

    @staticmethod
    def _format_example_parameter(p_name, p_value, p_alias=None):
        if p_alias:
            parameter = f'-{p_alias} {p_value}'
        else:
            parameter = f'--{p_name} {p_value}'
        return parameter

    @staticmethod
    def _get_parameter_placeholder(param_name, param_type):
        if param_type == 'date':
            return f'<{DATE_PATTERN}>'
        elif param_type == LIST:
            truncated_p_name = param_name[:-len('-list')] if param_name.\
                endswith('-list') else param_name  # remove suffix
            formatted_p_name = truncated_p_name.replace('-', '_')
            return f'<{formatted_p_name}1>,<{formatted_p_name}N>'
        else:
            return f'<{param_name}>'.replace('-', '_')

    def _append_related_commands_help(self, help_content, related_commands):
        for index, cmd in enumerate(related_commands):
            cmd_example = self._format_command_example(cmd)
            related_commands[index] = RELATED_COMMAND_STRING.format(
                cmd.get(HELP_KEY), cmd_example)
        related_commands.sort()
        related_commands = [f'{i + 1}. {_}'
                            for i, _ in enumerate(related_commands)]
        help_content = HELP_WITH_RELATED_COMMANDS_STRING.format(
            help_content.rstrip(), ''.join(related_commands).rstrip())
        return help_content

    # Replacing alias names with parameter names
    @staticmethod
    def __replace_parameters_aliases(incoming_parameters, parameter_def):
        for parameter, definition in parameter_def.items():
            alias_name = definition.get(ALIAS_KEY)
            if alias_name:
                alias_name = f'-{alias_name}'
            if alias_name in incoming_parameters:
                incoming_parameters[parameter] = incoming_parameters.pop(
                    alias_name)
        return incoming_parameters

    def __resolve_command_def(self, command_name):
        commands_def = self.commands_def.get(COMMANDS_KEY)
        cmd_def = commands_def.get(command_name)
        if cmd_def:
            return command_name, cmd_def
        for cmd_name, cmd_def in commands_def.items():
            alias = cmd_def.get(ALIAS_KEY)
            if alias and command_name == alias:
                command_name = cmd_name
                return command_name, cmd_def
        return command_name, None

    def get_secure_params(
            self,
            command: str,
    ) -> list[str | Any]:
        """
        Look for parameters to be encrypted.

        :param command: inputted command name
        """
        cmd_def = self.commands_def
        domain_parameters = cmd_def.get(DOMAIN_PARAMETERS_KEY)
        _, cmd_desc = self.__resolve_command_def(command)
        secure_params = []
        if cmd_desc:
            command_params = cmd_desc.get(PARAMS_KEY)

            if command_params:
                for param_name, param_def in command_params.items():
                    parent_param_name = param_def.get('parent')
                    if parent_param_name and domain_parameters:
                        inherit_dict(
                            domain_parameters.get(parent_param_name),
                            param_def)

            for key in command_params:
                if command_params[key].get(SECURE_KEY):
                    secure_params.append(
                        f"-{command_params[key].get(ALIAS_KEY)}"
                    )
                    secure_params.append(key)
        return secure_params

    def validate_request(self, request):
        """
        Validates request.

        Checks that specified in cli group name is present in commands
            definition file;
        Checks that specified command exists in group;
        Checks parameters against rules defined in file;

        NOTE: Also the method modifies the request.parameters that were not
            specified via CLI with default values - API specifics.
            + returns definition of the command to format output
        :param request:
        :return: error message if only one error occurred,
            list of messages if many or None if everything is ok
        """
        _LOG.debug(f'Request: {mask_params(request, SECURED_VALUES)}')
        commands_def = self.commands_def.get(COMMANDS_KEY)
        cmd_name, cmd_def = self.__resolve_command_def(request.command)
        incoming_command_name = cmd_name
        if not cmd_def:
            return (
                None, [f'Command \"{incoming_command_name}\" is invalid or '
                       f'is not available.\n'
                       f'Available commands: {list(commands_def.keys())};'])
        api_action = cmd_def.get('api_action')
        if api_action:
            request.api_action = api_action

        parameters_errors = []
        params_def = cmd_def.get(PARAMS_KEY)
        incoming_params = self.__replace_parameters_aliases(request.parameters,
                                                            params_def)
        # check required params
        required_params_names = [param_name for param_name, value in
                                 params_def.items() if
                                 value.get('required')]

        missing_required = set(required_params_names) - set(incoming_params)
        for each_missed in missing_required:
            default_param_value = self.default_params.get(each_missed)
            if default_param_value:
                _LOG.debug(f'Value for the required parameter '
                           f'\'{each_missed}\' has been resolved from '
                           f'file: {self.params_file_path}')
                incoming_params[each_missed] = default_param_value
        missing_required = set(required_params_names) - set(incoming_params)
        invalid_params = []
        for each_invalid in incoming_params:
            common_view_param = each_invalid.replace('-', '')
            if each_invalid.startswith(
                    '-') and common_view_param in missing_required:
                invalid_params.append('-' + each_invalid)
                missing_required -= {common_view_param}

        if invalid_params:
            _pretty_list = ', '.join(invalid_params)
            parameters_errors.append(
                f'The command {incoming_command_name} requires parameters '
                f'in the following form: {_pretty_list};')

        if missing_required:
            changed_params = []
            for parameter in missing_required:
                # changed_params.append('--' + parameter)
                changed_params.append(parameter)

            for p_name, p_def in params_def.items():
                for index, parameter in enumerate(changed_params):
                    if parameter == p_name:
                        parameter += ' (-' + p_def.get('alias') + ')'
                        changed_params[index] = '--' + parameter

            missing_required = set(changed_params)
            _pretty_list = ', '.join(sorted(list(missing_required)))
            parameters_errors.append(
                f'The command {incoming_command_name} requires the following '
                f'parameter: {_pretty_list};')
            if not incoming_params:
                pretty_help = self.get_help(
                    command=cmd_name,
                    compact=True)
                if isinstance(pretty_help, str):
                    pretty_help = pretty_help.split('\n')[5:]
                    pretty_help = '\n'.join(pretty_help)
                    parameters_errors.append(pretty_help)

        # check extra params
        extra_parameters = set(incoming_params) - set(params_def)

        # crunch for `m3 report --type hourly` to ignore `-R/--report`
        if api_action == 'GET_HOURLY_BILLING_REPORT':
            extra_parameters.discard('--report')
            extra_parameters.discard('-R')

        if extra_parameters:
            _pretty_list = ', '.join(list(extra_parameters))
            parameters_errors.append(
                f'The command {incoming_command_name} obtains unexpected '
                f'params: {_pretty_list};')

        # check parameters using validation attr
        for p_name, p_def in params_def.items():
            if isinstance(incoming_params.get(p_name), list):
                if not p_def.get("multiple_values"):
                    parameters_errors.append(
                        f'Can specify option only once: {p_name};')
                incoming_params[p_name] = ",".join(incoming_params.get(p_name))

            validation_rules = p_def.get(VALIDATION_KEY)
            if not validation_rules:
                continue
            parameter_type = validation_rules.get('type')
            is_param_present = p_name in incoming_params
            if parameter_type == 'bool':
                if incoming_params.get(p_name):
                    parameters_errors.append(
                        f'Unexpected value after the flag parameter: {p_name};')
                else:
                    incoming_params[p_name] = is_param_present
            actual_value = incoming_params.get(p_name)
            if is_param_present:
                errors = self.validation_service.validate_value(
                    param_name=p_name,
                    param_value=actual_value,
                    validation_rules=validation_rules
                )
                if errors:
                    parameters_errors.extend(errors)

        if parameters_errors:
            return None, parameters_errors
        _LOG.debug(f'The validation of parameters {list(params_def.keys())} '
                   f'has succeeded')

        # adopt values
        resulting_params = {}
        for p_name, p_def in params_def.items():
            actual_value = incoming_params.get(p_name)
            if not actual_value:
                continue
            validation_rules = p_def.get(VALIDATION_KEY)
            actual_value = self.validation_service.adapt_actual_value(
                param_value=actual_value,
                validation_rules=validation_rules)
            _LOG.debug(f'Adopted param \'{p_name}\' value:'
                       f' {mask_params(actual_value, SECURED_VALUES)}')
            resulting_params[p_name] = actual_value
        request.parameters = resulting_params

        # fill not specified request.parameters via CLI with default values.
        missing_all = set(params_def) - set(incoming_params)
        default_values = {}
        for param in missing_all:
            default_value = self.validation_service.get_default_value_for_param(
                params_def.get(param).get(VALIDATION_KEY))
            _LOG.debug(
                f'Setting default value for missing param '
                f'{param}: {default_value}')
            default_values[param] = default_value
        request.parameters.update(default_values)

        return cmd_def, parameters_errors

    def get_commands_def_version(self):
        return self.commands_def.get('version')

    def resolve_parameters_case(self, request):
        cmd_name, cmd_def = self.__resolve_command_def(request.command)
        if not cmd_def:
            return request

        # Processing the values of the "parameter" field
        params_def = cmd_def.get(PARAMS_KEY)
        incoming_params = self.__replace_parameters_aliases(request.parameters,
                                                            params_def)
        resulting_params = {}
        for p_name, p_def in params_def.items():
            actual_value = incoming_params.get(p_name)
            if not actual_value:
                continue
            case_identifier = p_def.get(CASE_KEY)
            actual_value = _resolve_parameter_case(
                case_identifier, actual_value,
                p_def['validation'].get('type'))
            # Replacing original parameters name with server
            # parameters API_PARAM_NAME
            if not p_def.get('no_api'):
                p_name = p_def.get(API_PARAM_NAME)

            resulting_params[p_name] = actual_value
        request.parameters = resulting_params
        return request

    @staticmethod
    def resolve_parameters_batch_processing(cmd_def, request):
        batch_param = None
        is_batch = False
        command_params = cmd_def.get('parameters')
        for param_name, values in command_params.items():
            if values.get('batch_param') is True:
                param_type = values['validation']['type']
                if not LIST == param_type:
                    raise AssertionError('Only parameter with type \'list\' '
                                         'can be used as batch parameter')
                interactive_mode = cmd_def.get(INTERACTIVE_OPTIONS_ATTRIBUTE)
                if interactive_mode:
                    raise AssertionError('Batch requests are not allowed'
                                         ' for interactive mode')
                batch_param = values['api_param_name']
                is_batch = True
                break
        if not batch_param:
            return [request], is_batch
        batch_request = []
        request_params = request.parameters
        batch_params = request_params.pop(batch_param)
        for param in batch_params:
            req = copy(request)
            params = copy(request_params)
            params[batch_param] = param
            req.parameters = params
            batch_request.append(req)
        return batch_request, is_batch

    def _load_default_parameters(self):
        """
        Get default parameters from default.cr, and m3.properties in CWD
        (excluding credentials)
        """
        parameter_set = {}
        if os.path.exists(self.params_file_path):
            parameter_set = load_parameters_from_json(self.params_file_path)
        m3_properties_path = os.path.join(os.getcwd(), M3_PROPERTIES_FILE)
        if os.path.exists(m3_properties_path):
            cwd_parameters = load_parameters_from_properties(
                m3_properties_path)
            parameter_set.update(cwd_parameters)
        return parameter_set
