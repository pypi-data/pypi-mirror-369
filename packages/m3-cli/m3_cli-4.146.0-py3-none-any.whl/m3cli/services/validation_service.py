import imghdr
import math
import os
import re
from datetime import datetime
from datetime import timezone
from pathlib import Path

import jsonschema
from jsonschema import ValidationError

from m3cli.utils.decorators import human_readable_list
from m3cli.utils.logger import get_logger
from m3cli.utils.utilities import inherit_dict

_LOG = get_logger('validation_service')

ROOT_DEFAULT = ''
LIST_SEPARATOR = ','
LIST_REGEX_PATTERN = r'''(?:"[^"]+"|[^,\s]+)\s*:\s*(?:"[^"]+"|[^,\s]+)|[^,]+'''

VALIDATION_TYPE = 'type'
VALIDATION_ALLOWED_VALUES = 'allowed_values'
VALIDATION_REGEX = 'regex'
VALIDATION_REGEX_ERROR = 'regex_error'
VALIDATION_MAX_FILE_SIZE = 'max_size_bytes'
VALIDATION_ALLOWED_FILE_EXTENSIONS = 'file_extensions'

DEFAULT_MAX_FILE_SIZE = 3.5 * 1024 * 1024  # 3.5 MB
DATE_PATTERN = 'dd.mm.yyyy'
SUPPORTED_IMAGE_TYPES = {'.png', '.jpeg'}

AUXILIARY_GROUP_PREFIX = 'cli-'
AUXILIARY_GROUP_SUFFIX = '-help'
EMAIL_GROUP_PREFIX = 'email-'
EMAIL_GROUP_SUFFIX = '-group'

COMMANDS_KEY = 'commands'
GROUPS_KEY = 'groups'
DOMAIN_PARAMETERS_KEY = 'domain_parameters'
PARAMS_KEY = 'parameters'
HELP_KEY = 'help'
HELP_FILE_KEY = 'help_file'
VALIDATION_KEY = 'validation'
ALIAS_KEY = 'alias'
REQUIRED_KEY = 'required'
SECURE_KEY = 'secure'


class ValidationService:

    def __init__(self):
        self.command_schema = {
            'type': 'object',
            'properties': {
                'api_action': {'type': 'string'},
                'help_file': {'type': 'boolean'},
                'help': {'type': 'string'},
                'alias': {'type': 'string'},
                'integration_request': {'type': 'boolean'},
                'integration_response': {'type': 'boolean'},
                'integration_suffix': {'type': 'string'},
                'groups': {'type': 'array'},
                'parameters': {'type': 'object'},
                'output_configuration': {
                    'type': 'object',
                    'properties': {
                        'response_table_headers': {'type': 'array'},
                        'none': {'type': 'boolean'},
                        'nullable': {'type': 'boolean'},
                        'multiple_table': {'type': 'boolean'},
                        'headers_customization': {
                            'type': 'object',
                            'properties': {
                                'the_name_of_header': {
                                    'type': 'object',
                                    'properties': {
                                        'header_display_name': {
                                            'type': 'string'
                                        },
                                        'disable_numparse': {
                                            'type': 'boolean'
                                        },
                                        'prevent_list_formatting': {
                                            'type': 'boolean'
                                        }
                                    }
                                }
                            }
                        },
                        'unmap_key': {'type': 'string'}
                    },
                    'required': ['response_table_headers']
                }
            },
            'required': ['output_configuration']
        }
        self.param_schema = {
            'type': 'object',
            'properties': {
                'parent': {'type': 'string'},
                'alias': {'type': 'string'},
                'api_param_name': {'type': 'string'},
                'help': {'type': 'string'},
                'required': {'type': 'boolean'},
                'secure': {'type': 'boolean'},
                'validation': {
                    'type': 'object',
                    'properties': {
                        'type': {
                            'type': 'string',
                            'enum': ['string', 'number', 'list', 'object',
                                     'date', 'bool', 'file']
                        },
                        'allowed_values': {'type': 'array'},
                        'regex': {'type': 'string'},
                        'regex_error': {'type': 'string'},
                        'properties': {'type': 'object'},
                        'min_value': {'type': 'number'},
                        'max_value': {'type': 'number'},
                        'max_size_bytes': {'type': 'number'},
                        'file_extensions': {'type': 'array'}
                    },
                    'required': ['type']
                },
                'case': {'type': 'string'}
            },
            'required': ['validation', 'help']
        }

        self.types_handler_mapping = {
            'string': self.check_string,
            'number': self.check_number,
            'list': self.check_list,
            'object': self.check_object,
            'date': self.check_date,
            'bool': self.check_bool,
            'file': self.check_file
        }
        self.default_values_mapping = {
            'string': ROOT_DEFAULT,
            'number': ROOT_DEFAULT,  # no value in str type
            'list': [],
            'object': {},
            'date': ROOT_DEFAULT,
            'bool': False
        }
        self.adapt_values_mapping = {
            'list': self.adapt_list,
            'object': self.adapt_object,
            'date': self.adapt_date
        }

    @staticmethod
    def validate_with_json_schema(instance, json_schema):
        try:
            jsonschema.validate(instance=instance,
                                schema=json_schema)
        except ValidationError as ex:
            if 'None is not of type' in ex.message:
                return 'description is missed in meta'
            return ex.message

    def validate_meta(self, meta):
        commands = meta.get(COMMANDS_KEY)
        groups = meta.get(GROUPS_KEY, [])
        errors = []
        if not commands:
            errors.append(
                'File with commands configuration must contain \'commands\' '
                'attribute')
        for cmd_name, cmd_meta in commands.items():
            try:
                cmd_groups = cmd_meta.get(GROUPS_KEY, [])
                for group in cmd_groups:
                    if (group.startswith(AUXILIARY_GROUP_PREFIX)
                            and group.endswith(AUXILIARY_GROUP_SUFFIX)):
                        continue
                    if (group.startswith(EMAIL_GROUP_PREFIX)
                            and group.endswith(EMAIL_GROUP_SUFFIX)):
                        continue
                    if group not in groups:
                        errors.append(f'Command \'{cmd_name}\': \'{group}\' '
                                      f'command group is not defined')
                error = self.validate_with_json_schema(
                    instance=cmd_meta,
                    json_schema=self.command_schema)
                if error:
                    errors.append(f'Command \'{cmd_name}\': {error}')
                params_dict = cmd_meta.get(PARAMS_KEY)
                if params_dict:
                    domain_params = meta.get(DOMAIN_PARAMETERS_KEY)
                    for param_name, param_def in params_dict.items():
                        parent_param_name = param_def.get('parent')
                        if parent_param_name and domain_params:
                            param_def = inherit_dict(
                                domain_params.get(parent_param_name),
                                param_def)
                        error = self.validate_with_json_schema(
                            instance=param_def,
                            json_schema=self.param_schema
                        )
                        if error:
                            errors.append(f'Command \'{cmd_name}\': parameter '
                                          f'\'{param_name}\' - {error}')
            except ValidationError as ex:
                errors.append(
                    f'The definition of the command \'{cmd_name}\' is '
                    f'invalid. Reason: {ex.message}')
        _LOG.debug(f'Meta validation has been finished. '
                   f'Amount of errors: {len(errors)}')
        return errors

    def validate_value(self, param_name, param_value, validation_rules):
        if param_value is None:
            raise AssertionError(
                f'Expected a value after parameter {param_name}')
        if not validation_rules:
            return
        _LOG.debug(f'Validating \'{param_name}\' with {validation_rules}')
        type_rule = self.__assert_type_specified(validation_rules)
        handler = self.types_handler_mapping.get(type_rule)
        return handler(param_name=param_name, value=param_value,
                       validation_rules=validation_rules)

    def get_default_value_for_param(self, validation_rules):
        if not validation_rules:
            return ROOT_DEFAULT  # root default
        type_rule = self.__assert_type_specified(validation_rules)
        default_value = self.default_values_mapping.get(type_rule)
        return default_value if default_value is not None else ROOT_DEFAULT

    def adapt_actual_value(self, param_value, validation_rules):
        if not validation_rules:
            return param_value
        type_rule = self.__assert_type_specified(validation_rules)
        adapter = self.adapt_values_mapping.get(type_rule)
        if not adapter:
            return param_value
        return adapter(actual_value=param_value)

    @staticmethod
    def __assert_type_specified(validation_rules):
        type_rule = validation_rules.get('type')
        if not validation_rules.get('type'):
            raise AssertionError('Attribute \'type\' is mandatory in '
                                 'parameter validation section')
        return type_rule

    @staticmethod
    def check_string(param_name, value, validation_rules):
        if not type(value) == str:
            return [f"Type of parameter '{param_name}' is not str"]
        regex = validation_rules.get(VALIDATION_REGEX)
        if regex:
            pattern = re.compile(regex)
            if not pattern.match(value):
                error_msg = validation_rules.get(
                    VALIDATION_REGEX_ERROR,
                    f'The value of {param_name} does not match the '
                    f'RegExp value "{regex}"')
                return [error_msg]
        allowed_values = validation_rules.get(VALIDATION_ALLOWED_VALUES)
        if not allowed_values:
            return
            # Case conversion is required for more accurate check of list entry
        if value.lower() not in [each.lower() for each in allowed_values]:
            return [f'The value of {param_name} should be one of allowed '
                    f'values: {allowed_values}. Actual value: {value}']

    @staticmethod
    def check_number(param_name, value, validation_rules):
        try:
            float_value = float(value)
            errors = []
            min_value = validation_rules.get('min_value')
            if isinstance(min_value, (int, float)) and min_value > float_value:
                errors.append(f'The value of {param_name} should be '
                              f'greater or equal than {min_value}. '
                              f'Actual: {value}')
            max_value = validation_rules.get('max_value')
            if not max_value:
                _LOG.debug(f"The Max_value: {max_value} doesn't exist. "
                           f"This value up to 10 digits long by default. "
                           f"Use 0 to restrict resource creation")
                max_value = 10000000000
            if isinstance(min_value, (int, float)) and float_value > max_value:
                errors.append(f'The value of {param_name} should be '
                              f'less than {max_value}. Actual: {value}')
            return errors
        except ValueError:
            return [f'Type of {param_name} is not number.']

    @staticmethod
    def check_list(param_name, value, validation_rules):
        list_values = value.split(LIST_SEPARATOR)
        list_values = [value.strip() for value in list_values]
        allowed_values = validation_rules.get(VALIDATION_ALLOWED_VALUES)

        if allowed_values:
            # Case conversion is required for more accurate check of list entry
            unknown_values = [param for param in list_values
                              if param.lower()
                              not in [each.lower() for each in allowed_values]]
            if unknown_values:
                return [
                    f'Range of values for list {param_name} is '
                    f'limited by these values: '
                    f'{human_readable_list(allowed_values)}. '
                    f'The following values are unknown: '
                    f'{human_readable_list(unknown_values)}'
                ]

    @staticmethod
    def check_object(param_name, value, validation_rules):
        try:
            dict_ = ValidationService.adapt_object(value)
            properties = validation_rules.get('properties')
            if properties:
                import jsonschema
                try:
                    jsonschema.validate(instance=dict_,
                                        schema=validation_rules)
                except ValidationError as e:
                    return [
                        f'The {param_name} value does not corresponds to '
                        f'the schema; Reason: {e.message}']
        except Exception:
            return [f'Type of {param_name} is not object.']

    @staticmethod
    def check_date(param_name, value, validation_rules):
        try:
            datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            return [f'Expected date format for parameter {param_name}: '
                    f'{DATE_PATTERN}. Given value: {value}']

    @staticmethod
    def check_bool(param_name, value, validation_rules):
        if not (value != 'True' or value != 'true'):
            return [f'Expected boolean format for parameter \'{param_name}\': '
                    f'"True" or "true" Given value: {value}']

    @staticmethod
    def check_file(param_name, value, validation_rules):
        if not os.path.exists(value):
            return [f'The "{value}" file does not exist']
        errors = []
        path = Path(value)

        errors.extend(ValidationService.check_file_type(
            path=path, validation_rules=validation_rules))

        regex = validation_rules.get(VALIDATION_REGEX)
        if regex and not re.match(regex, path.stem):
            error_msg = validation_rules.get(
                VALIDATION_REGEX_ERROR,
                f'The name of the file does not match the '
                f'RegExp value "{regex}"')
            errors.append(error_msg)

        max_size = validation_rules.get(VALIDATION_MAX_FILE_SIZE)
        if max_size is None or max_size > DEFAULT_MAX_FILE_SIZE:
            max_size = DEFAULT_MAX_FILE_SIZE
        if os.path.getsize(value) > max_size:
            # round megabytes down with precision of 1 digit.
            max_size_mb = math.floor(max_size / 1024 ** 2 * 10) / 10
            errors.append(f'The file exceeds the maximum '
                          f'allowed size ({max_size_mb:g}MB).')
        return errors

    @staticmethod
    def check_file_type(path, validation_rules):
        errors = []
        allowed_extensions = \
            validation_rules.get(VALIDATION_ALLOWED_FILE_EXTENSIONS)
        if allowed_extensions:
            file_suffix = path.suffix.lower()
            file_suffix = ValidationService.standardize_extension(file_suffix)
            if file_suffix not in allowed_extensions:
                errors.append('The file must have one of these extensions — '
                              + ', '.join(allowed_extensions))
            elif file_suffix in SUPPORTED_IMAGE_TYPES and \
                    imghdr.what(path) != file_suffix[1:]:
                types = set(allowed_extensions) \
                    .intersection(SUPPORTED_IMAGE_TYPES)
                errors.append(
                    f'The "{path}" image is corrupted. Please, provide a '
                    f'valid image of one of these types: '
                    f'{", ".join((t[1:].upper() for t in types))}')
        return errors

    @staticmethod
    def standardize_extension(extension):
        mapping = {
            '.jpg': '.jpeg'
        }
        return mapping.get(extension, extension)

    @staticmethod
    def adapt_list(actual_value):
        list_values = actual_value.split(LIST_SEPARATOR)
        return [value.strip() for value in list_values]

    @staticmethod
    def adapt_object(actual_value):
        values = re.findall(LIST_REGEX_PATTERN, actual_value)
        object_dict = {}
        for v in values:
            key, val = v.replace('"', '').split(':')
            object_dict[key] = val
        return object_dict

    @staticmethod
    def adapt_date(actual_value):
        return datetime.strptime(actual_value, '%d.%m.%Y').replace(
            tzinfo=timezone.utc).timestamp() * 1000
