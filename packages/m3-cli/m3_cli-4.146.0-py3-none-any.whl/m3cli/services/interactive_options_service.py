import json
import os
from typing import List, Mapping

import click

from m3cli.models.interactive_parameter import InteractiveParameter
from m3cli.services.interactivity import (
    STRING_TYPE, RemoteValidationService, ParametersProvider, VarfileService,
    InteractiveInputService,
)
from m3cli.utils.interactivity_utils import (
    unavailable_values_detector, get_interactivity_option,
)
from m3cli.utils.logger import get_logger
from m3cli.services.request_service import BaseRequest

_LOG = get_logger('interactive_options_service')

INTERACTIVE_OPTIONS_ATTRIBUTE = 'interactive_options'
VARFILE_PARAMETER = 'variables-file'
OPTION_NAME_ATTRIBUTE = 'option_name'
GENERATE_VARFILE_ATTRIBUTE = 'generate_varfile'


class InteractiveOptionsService:
    def __init__(self, cmd_def):
        self.interactive_options = cmd_def.get(INTERACTIVE_OPTIONS_ATTRIBUTE)
        self.parameters_provider = ParametersProvider(self.interactive_options)
        self.varfile_service = VarfileService(self.interactive_options)
        self.remote_validation_service = \
            RemoteValidationService(self.interactive_options)
        self.input_service = InteractiveInputService(self.interactive_options)

    def process_request(self, data):
        """
        Entry point for processing of interactive options.
        """
        if not self.interactive_options:
            return data

        request = data[0] if isinstance(data, list) else data
        interactive_params = self._collect_interactive_parameters(request)
        if self._varfile_generation_requested():
            self.varfile_service.generate_varfile_template(
                request=request,
                parameters=interactive_params)
            raise click.exceptions.Exit()
        else:
            filled_params = self._fill_parameter_values(
                request=request,
                interactive_parameters=interactive_params)
            return self.add_parameters_to_request(request, filled_params)

    def add_parameters_to_request(
            self,
            request,
            filled_params: List[InteractiveParameter]
    ):
        request_parameters = request.parameters if request.parameters else {}
        variables_param_name = get_interactivity_option(
            interactive_options=self.interactive_options,
            option_name=OPTION_NAME_ATTRIBUTE)
        raw_parameters = {
            param.name: param.to_raw_parameter() for param in filled_params
        }
        request_parameters.update({
            variables_param_name: raw_parameters
        })
        return request

    def _varfile_generation_requested(self):
        return bool(get_interactivity_option(
            interactive_options=self.interactive_options,
            option_name=GENERATE_VARFILE_ATTRIBUTE,
            required=False))

    def _collect_interactive_parameters(self, request):
        request_params = request.parameters if request.parameters else {}
        interactive_params = self.parameters_provider \
            .fetch_interactive_parameters(request_params)
        if not interactive_params:
            return []
        varfile_params = self.varfile_service.read_varfile(request_params)
        return self._integrate_varfile_parameters(
            parameters=interactive_params,
            varfile_parameters=varfile_params)

    @staticmethod
    def _integrate_varfile_parameters(parameters: List[InteractiveParameter],
                                      varfile_parameters: dict):
        if varfile_parameters:
            for param in parameters:
                if param.name in varfile_parameters:
                    varfile_value = varfile_parameters[param.name]
                    if param.type == STRING_TYPE \
                            and not isinstance(varfile_value, str):
                        varfile_value = json.dumps(varfile_value)
                    param.value = varfile_value
        return parameters

    def _fill_parameter_values(self, request, interactive_parameters):
        self._check_parameters_presence(interactive_parameters, request)
        filled_params = self._run_user_prompts(request, interactive_parameters)
        if not self.input_service.approve_parameters(filled_params):
            raise click.exceptions.Exit()
        return filled_params

    def _run_user_prompts(
            self,
            request: BaseRequest,
            interactive_parameters: List[InteractiveParameter],
    ):
        filled_params = []
        while interactive_parameters:
            collected_params = self.input_service.collect_user_input(
                interactive_parameters=interactive_parameters, request=request,
            )
            invalid_items = self.remote_validation_service.validate_parameters(
                collected_params,
                request.parameters.get("serviceName"),
            )
            if invalid_items:
                self._show_validation_errors(invalid_items)
                if self.varfile_service.is_varfile_invalid(
                        list(invalid_items.keys())
                ):
                    raise click.exceptions.Exit()
            filled_params.extend(
                param for param in interactive_parameters
                if param not in invalid_items
            )
            interactive_parameters = list(invalid_items.keys())
            for param in interactive_parameters:
                param.force_prompt()
        return filled_params

    @staticmethod
    def _check_parameters_presence(interactive_params, request):
        request_params = request.parameters if request.parameters else {}
        varfile_path = request_params.get(VARFILE_PARAMETER)
        errors = [f"Parameter '{param.name}' of type "
                  f"{param.type}: Value is absent"
                  for param in unavailable_values_detector(interactive_params)]
        if errors:
            if varfile_path and os.path.exists(varfile_path):
                click.echo(
                    f'The variables file is invalid: {os.linesep}'
                    f'{os.linesep.join(errors)}'
                    f'{os.linesep}'
                    'You may use the "generate-platform-service-varfile" '
                    'command to fill your file with the missing variables.')
            else:
                click.echo(
                    f'This service requires a variables file.{os.linesep}'
                    'Use the "generate-platform-service-varfile" command to '
                    'create a template of the variables file.')
            raise click.exceptions.Exit()

    def _show_validation_errors(
            self,
            errors: Mapping[InteractiveParameter, str],
    ):
        click.echo('----------------------------')
        click.echo('Invalid parameters! Errors: ')
        for param, message in errors.items():
            click.echo(f'Parameter \'{param.name}\' '
                       f'of type {param.type}: '
                       f'{message}')
        if self.varfile_service.is_varfile_invalid(list(errors.keys())):
            click.echo('Please provide a varfile with valid parameters.')
        else:
            click.echo('Please enter valid values...')
        click.echo('----------------------------')
