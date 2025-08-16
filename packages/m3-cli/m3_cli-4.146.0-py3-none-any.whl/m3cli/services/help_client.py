import os
from abc import ABC, abstractmethod

import click

from m3cli.m3cli_complete.autocomplete_setup import enable_autocomplete_handler, \
    disable_autocomplete_handler


class AbstractStaticCommands(ABC):
    def __init__(self, config_command_help, config_params):
        self.config_command_help = config_command_help
        self.config_params = config_params

    @abstractmethod
    def define_description(self):
        pass

    def validate_params(self, configure_args):
        pass

    @abstractmethod
    def execute_command(self):
        pass

    def process_passed_command(self):
        if self.config_command_help:
            self.define_description()
        return self.execute_command()


class EnableAutocompleteCommandHandler(AbstractStaticCommands):
    def define_description(self):
        enable_autocomplete_command_help = f'{os.linesep}Usage: m3 (then' \
                                           f' press tab)' \
                                           f'{os.linesep}{os.linesep} Gives' \
                                           f' you suggestions ' \
                                           f'to complete your command.'
        click.echo(enable_autocomplete_command_help)
        exit()

    def execute_command(self):
        response = enable_autocomplete_handler()
        click.echo(response)


class DisableAutocompleteCommandHandler(AbstractStaticCommands):
    def define_description(self):
        disable_autocomplete_command_help = f'{os.linesep}Usage: none' \
                                            f'{os.linesep}{os.linesep} Disable' \
                                            f'autocomplete'
        click.echo(disable_autocomplete_command_help)
        exit()

    def execute_command(self):
        response = disable_autocomplete_handler()
        click.echo(response)
