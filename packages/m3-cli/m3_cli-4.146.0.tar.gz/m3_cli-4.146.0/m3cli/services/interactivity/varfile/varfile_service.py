import json
import os
from typing import TextIO, List

import click

from m3cli.models.interactive_parameter import InteractiveParameter
from m3cli.services.interactivity import (
    STRING_TYPE, LIST_TYPE, MAP_TYPE, COMPLEX_TYPE)
from m3cli.utils.utilities import is_not_empty_file

VARFILE_PARAMETER = 'variables-file'
VARFILE_FORMAT_PARAMETER = 'variables-file-format'

JSON_FORMAT = 'JSON'
HCL_FORMAT = 'HCL'


class VarfileService:

    def __init__(self, interactive_options):
        self.interactive_options = interactive_options
        self.placeholders = {
            STRING_TYPE: None,
            LIST_TYPE: [],
            MAP_TYPE: {},
            COMPLEX_TYPE: None
        }
        self.io_adapters = {
            JSON_FORMAT: VarfileJsonAdapter,
            HCL_FORMAT: VarfileHclAdapter
        }

    def generate_varfile_template(self, request,
                                  parameters: List[InteractiveParameter]):
        request_params = request.parameters if request.parameters else {}
        if not parameters:
            click.echo("There are no additional parameters. "
                       "The variables file was not generated.")
            return
        varfile_model = {
            param.name: self._resolve_parameter_value(param)
            for param in parameters
        }
        varfile_path = self._save_varfile(
            model=varfile_model,
            request_parameters=request_params)
        click.echo(f"The variables file is generated "
                   f"by the path: {varfile_path}")

    def read_varfile(self, request_params) -> dict:
        """
        :returns: A key-value mapping of varfile variables.
        """
        varfile_parameters = {}
        varfile_path = request_params.get(VARFILE_PARAMETER)
        if is_not_empty_file(varfile_path):
            with open(varfile_path, 'r') as varfile:
                io_adapter = self._get_io_adapter(request_params)
                try:
                    varfile_parameters = io_adapter.load(varfile)
                except ValueError as error:
                    click.echo(f'Variables file by the path "{varfile_path}" '
                               f'cannot be parsed as JSON.{os.linesep}'
                               f'Reason: {error}')
                    raise click.exceptions.Exit()
        return varfile_parameters

    @staticmethod
    def is_varfile_invalid(invalid_parameters: List[InteractiveParameter]):
        return any(param.type != STRING_TYPE
                   for param in invalid_parameters)

    def _resolve_parameter_value(self, parameter: InteractiveParameter):
        if parameter.value:
            return parameter.value
        return self.placeholders.get(parameter.type)

    def _save_varfile(self, model, request_parameters):
        varfile_path = self._resolve_varfile_path(request_parameters)
        with open(varfile_path, 'w') as varfile:
            self._get_io_adapter(request_parameters).dump(model, varfile)
        return varfile_path

    def _resolve_varfile_path(self, request_parameters):
        varfile_path = request_parameters.get(VARFILE_PARAMETER)
        if varfile_path:
            return varfile_path
        service_name = request_parameters.get('serviceName')
        default_varfile_name = \
            self._get_io_adapter(request_parameters).default_varfile_name
        file_name = f'{service_name}.{default_varfile_name}' \
            if service_name else default_varfile_name
        return os.path.join(os.getcwd(), file_name)

    def _get_io_adapter(self, request_parameters):
        fmt = request_parameters.get(VARFILE_FORMAT_PARAMETER, JSON_FORMAT)
        io_adapter = self.io_adapters.get(fmt)
        if not io_adapter:
            raise ValueError(f'{fmt} variables file format is not supported')
        return io_adapter()


class VarfileJsonAdapter:

    @staticmethod
    def dump(tfvars: dict, varfile: TextIO):
        json.dump(tfvars, varfile, indent=2)

    @staticmethod
    def load(varfile: TextIO):
        return json.load(varfile)

    @property
    def default_varfile_name(self):
        return 'varfile.tfvars.json'


class VarfileHclAdapter:

    @staticmethod
    def dump(tfvars: dict, varfile: TextIO):
        pass

    @staticmethod
    def load(varfile: TextIO):
        pass

    @property
    def default_varfile_name(self):
        return 'varfile.tfvars'

