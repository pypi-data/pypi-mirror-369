import json
import os
import re

import yaml
from tabulate import tabulate
from collections.abc import KeysView

from m3cli.services.request_service import mask_params
from m3cli.services.response_utils import contains_empty_data, \
    contains_string_data, \
    contains_dict_data
from m3cli.utils.decorators import FULL_VIEW, JSON_VIEW, TABLE_VIEW, \
    SECURED_VALUES
from m3cli.utils.logger import get_logger
from m3cli.utils.utilities import format_floats_in_data

STATUS = 'status'

DATA_FIELD = 'data'
READABLE_ERROR_FILED = 'readableError'
ERROR_FILED = 'error'
HEADER_DISPLAY_NAME = 'header_display_name'
NO_RECORDS_INFO_MESSAGE = 'There are no records to display'

_LOG = get_logger('response_processor_service')

MULTIPLE_TABLE_FIELD = 'multiple_table'
HEADERS_FIELD = 'headers'
TABLE_NAME_FIELD = 'name'
TABLE_DISPLAY_NAME_FIELD = 'display_name'
HEADERS_CUSTOMIZATION = 'headers_customization'


def _process_table_headers(responses: list, output_conf: dict):
    if not output_conf:
        return
    response_table_headers = output_conf.get('response_table_headers')
    if output_conf.get(MULTIPLE_TABLE_FIELD):
        tables = _build_multiple_table(
            response=responses,
            response_table_headers=response_table_headers)
    else:
        headers_config = output_conf.get(HEADERS_CUSTOMIZATION, {})
        tables = [_build_single_table(responses=responses,
                                      headers=response_table_headers,
                                      headers_config=headers_config)]
    return tables


def _format_lists(responses, headers_config):
    for each_response in responses:
        if not isinstance(each_response, list):
            each_response = [each_response]
        for item in each_response:
            for attr_name, value in item.items():
                if not isinstance(value, list) or \
                        any(v for v in value if not isinstance(v, str)):
                    continue
                h_config = headers_config.get(attr_name, {})
                if not h_config.get('prevent_list_formatting'):
                    item[attr_name] = '\n'.join(sorted(value))
    return responses


def _configure_table_response(responses, response_table_headers: list):
    """Process the displaying headers in the table format.

    Keyword arguments:
    responses               -- current responses from the server
    response_table_headers  -- the list of the headers specified in a
    response_table_headers
    """
    title_headers = {}
    if isinstance(responses, list):
        for val in response_table_headers:
            title_headers[val] = _camel_to_title(val)
            response_table_headers[
                response_table_headers.index(val)] = _camel_to_title(
                val)
        for header, custom_header_name in title_headers.items():
            responses = _change_header_display_name(
                responses=responses,
                header=header,
                custom_header=custom_header_name)

    return responses, response_table_headers


def _change_header_display_name(responses, header: str, custom_header: str):
    """Returns response with headers were replaced with the custom header name.

    Keyword arguments:
    responses       -- current response from server
    header          -- the list of the header specified in response_table_headers
    custom_header   -- the list of the headers are specified in headers_config
    """
    if isinstance(responses, list):
        for resp in responses:
            if isinstance(resp, list):
                _change_header_display_name(responses=resp, header=header,
                                            custom_header=custom_header)
            elif resp.get(header.strip()) \
                    or isinstance(resp.get(header.strip()), (bool, float, int)):
                resp[custom_header] = resp.pop(header)
    elif responses.get(header.strip()) \
            or isinstance(responses.get(header.strip()), (bool, float, int)):
        responses[custom_header] = responses.pop(header)

    return responses


def _camel_to_title(name):
    """Returns the converted headers from the "camelCase" to the "Title Case".

    Keyword arguments:
    name -- the name of the header
    """
    if not name.istitle():
        name = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', name).title()


def _resolve_disable_numparse_indices(response_table_headers, headers_config):
    return [response_table_headers.index(header)
            for header, config_dict in headers_config.items()
            if config_dict.get('disable_numparse')]


def _resolve_header_display_name(response, response_table_headers,
                                 headers_config):
    """
    Returns the list of replaced headers and response with headers were
    replaced with the custom header name.

    Keyword arguments:
    response                -- current response from server
    response_table_headers  -- the list of the header specified in
                                a response_table_headers
    headers_config          -- the list of the headers are specified
                                in headers_config
    """
    headers = []
    for header, config_dict in headers_config.items():
        custom_header_name = config_dict.get(HEADER_DISPLAY_NAME)
        if custom_header_name:
            response = _change_header_display_name(
                response, header, custom_header_name)
            if header in response_table_headers:
                response_table_headers[
                    response_table_headers.index(header)] = custom_header_name

    return headers, response


def _build_single_table(
        responses: list,
        headers: KeysView[str],
        display_name: str | None = None,
        headers_config: dict | None = None,
):
    responses = [responses] if isinstance(responses, dict) else responses
    """
    Such logic is needed because by default 'responses' param is the list
    of responses which consists of one response or amount
    of responses (in case of batch requests), each response, in turn, can be
    a list of elements or dict, so in case if our response consists of the
    list of dictionaries, we should iterate over each item, otherwise, we
    should iterate over each list and each item of the corresponding list.
    """
    responses = _format_lists(
        responses=responses,
        headers_config=headers_config,
    )

    _resolve_header_display_name(
        response=responses,
        response_table_headers=headers,
        headers_config=headers_config,
    )

    responses, headers = _configure_table_response(responses, headers)
    headers, data = _build_tabulate_data(responses=responses, headers=headers)

    data = [
        [
            "0" if cell == 0 else str(cell) if cell is not None else ''
            for cell in row
        ]
        for row in data
    ]

    table = tabulate(
        tabular_data=data,
        headers=headers,
        tablefmt='grid',
        disable_numparse=True,
    )
    return TableView(table=table, display_name=display_name)


def _build_multiple_table(response, response_table_headers):
    tables = []
    response_data = response[0]
    for table_config in response_table_headers:
        title = table_config.get(TABLE_NAME_FIELD)
        response_item = response_data.get(title)
        if not response_item:
            continue

        headers_config = table_config.get(HEADERS_CUSTOMIZATION, {})
        headers = table_config.get(HEADERS_FIELD)
        display_name = table_config.get(TABLE_DISPLAY_NAME_FIELD)
        table = _build_single_table(responses=response_item, headers=headers,
                                    display_name=display_name,
                                    headers_config=headers_config)
        tables.append(table)
    return tables


def _build_tabulate_data(responses, headers):
    table_data = TableDataContainer(headers=headers)
    for each_response in responses:
        if isinstance(each_response, list):
            for item in each_response:
                table_data.aggregate_values(response_item=item)
        else:
            table_data.aggregate_values(response_item=each_response)
    return table_data.get_table_data()

def flatten(obj, parent_key='', sep='.', list_sep=','):
    """Recursively flattens a dict/list into key = value lines"""
    items = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.extend(flatten(v, new_key, sep, list_sep))
    elif isinstance(obj, list):
        if all(isinstance(x, (str, int, float, bool, type(None))) for x in obj):
            # List of primitives: join as comma-separated
            items.append(f"{parent_key} = {list_sep.join(str(x) for x in obj)}")
        else:
            # List of dicts or lists: index as key[i]
            for i, v in enumerate(obj):
                items.extend(flatten(v, f"{parent_key}[{i}]", sep, list_sep))
    else:  # primitive
        items.append(f"{parent_key} = {obj}")
    return items

def general_full_view(responses):
    # Flatten top-level if needed
    if isinstance(responses, list) \
            and len(responses) == 1 and isinstance(responses[0], list):
        responses = responses[0]
    lines = []
    if isinstance(responses, list):
        for obj in responses:
            lines.extend(flatten(obj))
            lines.append('')  # blank line between items
    else:
        lines = flatten(responses)
    return '\n'.join(lines)

class TableDataContainer:
    def __init__(self, headers):
        super().__init__()
        self.headers = headers
        self.items = self.__aggregate_initial_data(self.headers)

    @staticmethod
    def __aggregate_initial_data(headers):
        items = {}
        for h in headers:
            items[h] = []
        return items

    def __add_value(self, header, val):
        self.items[header].append(val)

    def aggregate_values(self, response_item):
        for header in self.headers:
            item_value = self.__item_value(
                item_value=response_item.get(header))
            self.__add_value(header=header, val=item_value)

    @staticmethod
    def __item_value(item_value):
        if isinstance(item_value, str) and '\n' not in item_value:
            valid_string_length = 70
            if len(item_value) > valid_string_length:
                splited_string = [item_value[idx:idx + valid_string_length]
                                  for idx in range(0, len(item_value),
                                                   valid_string_length)]
                item_value = f'{os.linesep}'.join(splited_string)
        return item_value

    def get_table_data(self):
        """
        Define which of 'headers' columns contains full empty data,
        such columns should be removed.
        """
        items = self.items
        for value in self.headers:
            val = items[value]
            if all(x is None for x in val):
                items.pop(value)

        all_rows = []
        if items:
            values = items.values()
            repeat = True
        else:
            repeat = False

        """
         To tabulate the data we need next data structure: 
         Example:
         headers = ['tenant', 'region', 'cloud'] 
         data = [['tenant1', 'region1', 'cloud1'],
                 ['tenant2', 'region2', 'cloud2']]

         table = tabulate(tabular_data=data, headers=headers,
                             tablefmt='grid', floatfmt='.2f')

         Current items has the structure:
          {
            'tenant' : ['tenant1', 'tenant2', 'tenant3'],
            'region' : ['region1', 'region2', 'region3'],
            'cloud' : ['cloud1', 'cloud2', 'cloud3']
          }
         Current logic need to transform current items to required view.
         The 'items' is a dict which keys will be used as a keys.
        """
        while repeat:
            row = []
            for value in values:
                if not value:
                    repeat = False
                    break
                row.append(value.pop(0))
            if row:
                all_rows.append(row)
        return items.keys(), all_rows


class TableView:
    def __init__(self, table, display_name=None):
        super().__init__()
        self.table = table
        self.display_name = display_name

    def get_view(self):
        if not self.display_name:
            return self.table
        return '\n'.join([self.display_name, self.table])


class ResponseProcessorService:
    def __init__(self, cmd_def, view_type, detailed):
        super().__init__()
        self.cmd_def = cmd_def
        self.view = view_type
        self.detailed = detailed
        self.available_view_types = {
            FULL_VIEW: self.__full_view,
            JSON_VIEW: self.__json_view,
            TABLE_VIEW: self.__table_view
        }

    def process_response(self, response, fail_safe):
        _LOG.debug(f'Response: {mask_params(response, SECURED_VALUES)}')
        try:
            ResponseProcessorService.check_errors(response=response)
        except AssertionError as e:
            if not fail_safe:
                raise AssertionError(e)
            # TODO to design the flow for case if fail_safe will be applied
            #  for non batch requests
            return json.dumps({'error': str(e)})

        if self.cmd_def.get('output_configuration') and self.cmd_def.get(
                'output_configuration').get('none'):
            return 'The command has been executed successfully'
        return response.get(DATA_FIELD)

    @staticmethod
    def check_errors(response):
        # todo user always should be informed about the command result.
        # todo no AssertionErrors should be thrown by logic
        if response.get(READABLE_ERROR_FILED):
            try:
                error = json.loads(response.get(READABLE_ERROR_FILED))
            except json.decoder.JSONDecodeError:
                raise AssertionError(response.get(READABLE_ERROR_FILED))
            raise AssertionError(error.get('message'))
        if response.get(ERROR_FILED):
            raise AssertionError(response.get(ERROR_FILED))
        if response.get(STATUS) == 'FAILED':
            raise AssertionError(
                'The service has failed to handle the request')

    def prettify_response(self, response: list):
        response = ResponseProcessorService.format_response(response=response)
        nullable = self.cmd_def.get('output_configuration').get('nullable')
        custom_full_view = self.cmd_def.get('output_configuration') \
                               .get('custom_full_view') or False
        mutated_yaml = self.cmd_def.get('output_configuration') \
                               .get('mutated_yaml') or False
        view_printer = self.available_view_types.get(self.view)
        if not view_printer:
            raise AssertionError(
                f'The view type {self.view} is not currently supported')
        return view_printer(
            responses=response,
            detailed=self.detailed,
            nullable=nullable,
            custom_full_view=custom_full_view,
            mutated_yaml=mutated_yaml,
        )

    @staticmethod
    def format_response(response):
        result = []
        for each in response:
            if not isinstance(each, (dict, list)):
                try:
                    each = json.loads(each)
                except (json.decoder.JSONDecodeError, TypeError):
                    each = str(each)
            result.append(each)
        return result

    def __full_view(
            self,
            responses,
            detailed=None,
            nullable=None,
            custom_full_view: bool = False,
            mutated_yaml: bool = False,
    ):
        if custom_full_view:
            return "\n\n" + general_full_view(responses)
        elif mutated_yaml:
            yaml_str = yaml.dump(responses)
            lines = yaml_str.split('\n')
            # Remove list markers from top-level items
            processed_lines = [
                line[2:] if line.startswith('- ') else line for line in lines
            ]
            # Detect top-level keys dynamically
            final_lines = []
            for line in processed_lines:
                # Calculate current indentation
                curr_indent = len(line) - len(line.lstrip())
                # Add blank line before new root-level objects
                if curr_indent == 0 and line.strip().endswith(':'):
                    if final_lines and final_lines[-1] != '':
                        final_lines.append('')
                final_lines.append(line)
            # Format key-value pairs
            formatted_response = '\n'.join(final_lines).replace(': ', ' = ')
            return f'\n\n{formatted_response}'
        else:
            formatted_response = yaml.dump(responses)
            return f'\n\n{formatted_response}'.replace(': ', ' = ')

    def __json_view(
            self,
            responses: list,
            detailed: bool,
            nullable: bool,
            custom_full_view: bool = False,
            mutated_yaml: bool = False,
    ) -> json:
        responses = self.__remove_none(responses, nullable)
        # It is possible to take empty data after removing none values,
        # need to check
        if contains_empty_data(responses):
            return NO_RECORDS_INFO_MESSAGE

        if not detailed:
            responses = self.__unmap_response(responses)

        if contains_string_data(responses):
            return responses[0]
        # response after sending report via email
        if contains_dict_data(responses) and responses[0].get('message'):
            return responses
        if contains_empty_data(responses):
            return NO_RECORDS_INFO_MESSAGE

        _output_conf = self.cmd_def.get('output_configuration')
        if _output_conf and not detailed and \
                _output_conf.get('response_table_headers'):
            headers = _output_conf.get('response_table_headers')
            multiple_table = _output_conf.get('multiple_table')
            self._compose_json_items(
                responses=responses,
                response_table_headers=headers,
                multiple_table=multiple_table,
            )

        # Format all float values to avoid scientific notation
        responses = format_floats_in_data(responses)

        return json.dumps(responses, indent=4)

    def _compose_json_items(self, responses, response_table_headers,
                            multiple_table=None):
        if multiple_table:
            response_items = []
            for res_headers in response_table_headers:
                headers = res_headers.get('headers')
                response_processed = self._single_json_view(responses,
                                                            headers)
                response_items.append(response_processed)
            return json.dumps(response_items, indent=4) if \
                response_items else json.dumps(responses, indent=4)
        else:
            response_processed = self._single_json_view(responses,
                                                        response_table_headers)
            return json.dumps(response_processed, indent=4) if \
                response_processed else json.dumps(responses, indent=4)

    @staticmethod
    def _single_json_view(responses, headers):
        """
           Such logic is need because by default 'responses' param is the
           list of responses which consists of one response or amount
           of responses(in case of batch requests), each response, in turn,
           can be a list of elements or dict, so in case if our response
           consists of the list of dictionaries, we should iterate over
           each item, otherwise, we should iterate over each list and each
           item of the corresponding list.
        """
        response_processed = []
        for each_item in responses:
            if isinstance(each_item, list):
                for each in each_item:
                    response_processed.append(
                        {k: v for (k, v) in each.items()
                         if k in headers})
            else:
                response_processed.append(
                    {k: v for (k, v) in each_item.items()
                     if k in headers})
        return response_processed

    def __table_view(
            self,
            responses,
            detailed=None,
            nullable=None,
            custom_full_view: bool = False,
            mutated_yaml: bool = False,
    ):
        # Format all float values to avoid scientific notation
        responses = format_floats_in_data(responses)
        responses = self.__unmap_response(responses)
        responses = self.__remove_none(responses, nullable)
        # It is possible to take empty data after removing none values,
        # need to check
        if contains_empty_data(response=responses):
            return NO_RECORDS_INFO_MESSAGE

        if contains_string_data(responses):
            return responses[0]
        if contains_dict_data(responses) and responses[0].get('message'):
            # response after sending report via email
            return responses[0].get('message')

        output_conf = self.cmd_def.get('output_configuration')
        tables = _process_table_headers(responses=responses,
                                        output_conf=output_conf)
        if tables:
            return self.__compose_table(tables)
        else:
            if isinstance(responses, list):
                return responses[0] if len(responses) == 1 else responses
            return str(responses)

    @staticmethod
    def __compose_table(tables):
        return '\n\n'.join([x.get_view() for x in tables])

    def __remove_none(self, obj, retain_zeros=False):
        if isinstance(obj, (list, tuple, set)):
            return type(obj)(self.__remove_none(x, retain_zeros)
                             for x in obj if x is not None)
        elif isinstance(obj, dict):
            return {
                k: self.__remove_none(v, retain_zeros)
                for k, v in obj.items()
                if (k and v
                    or retain_zeros and isinstance(v, (int, float)))
            }
        else:
            return obj

    def __unmap_response(self, response):
        output_configuration = self.cmd_def.get('output_configuration', {})
        unmap_key = output_configuration.get('unmap_key')
        if unmap_key:
            return [each[unmap_key] for each in response
                    if each.get(unmap_key)]
        return response
