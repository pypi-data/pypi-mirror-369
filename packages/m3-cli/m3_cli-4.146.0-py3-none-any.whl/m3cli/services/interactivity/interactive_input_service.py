import json
import os
from typing import List

import click

from m3cli.models.interactive_parameter import InteractiveParameter
from m3cli.services.interactivity import STRING_TYPE

INTERACTIVE_MODE_PARAMETER = 'interactive-mode'


class InteractiveInputService:

    def __init__(self, interactive_options):
        self.interactive_options = interactive_options

    def collect_user_input(self, interactive_parameters, request):
        request_parameters = request.parameters if request.parameters else {}
        interactive_mode = \
            bool(request_parameters.get(INTERACTIVE_MODE_PARAMETER))
        parameters = self._select_parameters_to_ask(interactive_parameters)
        self._ask_parameter_values(
            parameters=parameters,
            force_interactive_mode=interactive_mode)
        return interactive_parameters

    @staticmethod
    def approve_parameters(interactive_parameters: List[InteractiveParameter]):
        click.echo(f'{os.linesep}Please review the parameters:{os.linesep}')
        for param in interactive_parameters:
            if param.sensitive:
                display_value = '(sensitive)'
            else:
                display_value = json.dumps(param.value, indent=2)
            click.echo(f'{param.name}: {display_value}')
        return click.confirm(f'{os.linesep}Approve parameters')

    @staticmethod
    def _select_parameters_to_ask(interactive_parameters):
        return [param for param in interactive_parameters
                if param.type == STRING_TYPE]

    @staticmethod
    def _ask_parameter_values(parameters: List[InteractiveParameter],
                              force_interactive_mode: bool):
        for param in parameters:
            if not param.value and not param.value_provided_by_user \
                    or force_interactive_mode or param.is_prompt_forced():
                param_name = param.name if not param.sensitive \
                    else f'{param.name} (sensitive)'
                param.value = click.prompt(
                    text=param_name,
                    hide_input=param.sensitive,
                    default=param.value,
                    show_default=not param.sensitive)
        return parameters
