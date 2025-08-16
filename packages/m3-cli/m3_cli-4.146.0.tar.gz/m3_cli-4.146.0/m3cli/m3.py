import os
import sys

import click

from m3cli.services.commands_service import CommandsService
from m3cli.services.interactive_options_service import (
    InteractiveOptionsService,
)
from m3cli.services.plugin_service import (
    INTEGRATION_REQUEST_ATTRIBUTE_NAME, INTEGRATION_RESPONSE_ATTRIBUTE_NAME,
    PluginService, REQUEST_KEY, RESPONSE_KEY, VIEW_TYPE_KEY,
)
from m3cli.services.request_service import (
    BaseRequest, POST, SdkClient, wrap_request,
)
from m3cli.services.response_processor_service import ResponseProcessorService
from m3cli.services.validation_service import ValidationService
from m3cli.utils import HEALTH_CHECK_CMD_NAME
from m3cli.utils.decorators import (cli_response, dynamic_dispatcher)
from m3cli.utils.logger import exception_handler_formatter
from m3cli.utils.utilities import perform_version_check

sys.excepthook = exception_handler_formatter

CONTEXT_SETTINGS = dict(allow_extra_args=True, ignore_unknown_options=True)


@cli_response(no_output=True)
def init_commands_service():
    cmd_service = CommandsService(m3cli_path=get_root_dir_path(),
                                  validation_service=ValidationService())
    return cmd_service


def print_version(ctx, value):
    if not value or ctx.resilient_parsing:
        return

    from importlib.metadata import version as lib_version

    version_m3 = lib_version('m3-cli')
    click.echo(f'Maestro CLI version: {version_m3}')
    commands_meta_version = CMD_SERVICE.get_commands_def_version()
    click.echo(f'Commands version: {commands_meta_version}')
    ctx.exit()


def get_root_dir_path():
    root_dir = os.path.dirname(__file__)
    if root_dir.split(os.sep)[-1] != 'm3cli':
        root_dir = os.path.join(root_dir, 'm3cli')
    return root_dir


CMD_SERVICE = init_commands_service()


@click.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.option('--verbose', is_flag=True, default=False)
@click.option('--raw', is_flag=True, default=False)
@click.option('--full-help', is_flag=True, default=False)
@click.option('--help', is_flag=True, default=False)
@click.option('--json', is_flag=True, default=False)
@click.option('--full', is_flag=True, default=False)
@click.option('--table', is_flag=True, default=False)
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
@dynamic_dispatcher
@cli_response(params_to_be_secured=CMD_SERVICE.get_secure_params)
def m3(
        help: bool = False,
        full_help: bool = False,
        command: str | None = None,
        parameters: dict | None = None,
        view_type: str | None = None,
        detailed: bool = False,
        raw_response: bool = False,
):
    health_check_response = perform_version_check(
        invoked_command=command,
        is_help_invoked=help or full_help,
        view_type=view_type,
        detailed=detailed,
    )
    errors = CMD_SERVICE.validate_meta()
    if errors:
        _pretty_errors = '\n'.join(errors)
        raise AssertionError(f'Invalid commands meta. \n{_pretty_errors}')
    if help:
        click.echo(CMD_SERVICE.get_help(command=command, compact=True))
        return
    if full_help or not command and not parameters:
        click.echo(CMD_SERVICE.get_help(command=command))
        return

    if command == HEALTH_CHECK_CMD_NAME:
        return health_check_response

    return execute_command(
        command=command,
        parameters=parameters,
        view_type=view_type,
        detailed=detailed,
        raw_response=raw_response,
    )


def execute_command(
        command: str | None = None,
        parameters: dict | None = None,
        view_type: str | None = None,
        detailed: bool = False,
        raw_response: bool = False,
):
    # Forming an incoming request from cli
    requests = BaseRequest(command=command,
                           parameters=parameters, method=POST)
    cmd_def, errors = CMD_SERVICE.validate_request(request=requests)
    if errors:
        _pretty_errors = '\n'.join(errors)
        raise AssertionError(f'Invalid request. \n{_pretty_errors}')

    # Substitution of values to form the original query
    requests = CMD_SERVICE.resolve_parameters_case(requests)
    requests, is_batch = CMD_SERVICE.resolve_parameters_batch_processing(
        cmd_def=cmd_def,
        request=requests)

    plugin_service = PluginService(m3cli_path=get_root_dir_path(),
                                   cmd_def=cmd_def,
                                   command_name=cmd_def.get('name'))

    requests_list = []
    for req in requests:
        applied_request = plugin_service.apply_plugin(
            data=build_plugin_data(
                request=wrap_request(cmd_def=cmd_def, request=req),
                view_type=view_type,
            ),
            method_type=INTEGRATION_REQUEST_ATTRIBUTE_NAME,
        )
        check_required_parameters(request=applied_request)
        requests_list.append(applied_request)

    interactive_options_service = InteractiveOptionsService(cmd_def=cmd_def)
    try:
        requests_list = \
            interactive_options_service.process_request(requests_list)
    except click.exceptions.Exit:
        return

    # Initializing the connection to the server in SdkClient
    request_mapping, responses = SdkClient().execute(request=requests_list)
    if raw_response:
        return responses

    response_service = ResponseProcessorService(
        cmd_def=cmd_def,
        view_type=view_type,
        detailed=detailed
    )
    fail_safe = is_batch
    applied_responses = []
    for resp in responses:
        related_request = request_mapping[resp['id']]
        processed_response = response_service.process_response(resp, fail_safe)

        response = plugin_service.apply_plugin(
            data=build_plugin_data(
                request=related_request,
                response=processed_response,
                view_type=view_type,
            ),
            method_type=INTEGRATION_RESPONSE_ATTRIBUTE_NAME
        )
        if isinstance(response, list):
            applied_responses.extend(response)
        else:
            applied_responses.append(response)
    return response_service.prettify_response(applied_responses)


def check_required_parameters(request):
    api_action = request.api_action
    if not api_action:
        incoming_command_name = request.command
        raise AssertionError(
            f'The command meta for \'{incoming_command_name}\' does not have '
            f'the required \'api_action\' attribute.')


def build_plugin_data(
        request,
        response=None,
        view_type: str | None = None,
) -> dict:
    return {
        REQUEST_KEY: request,
        RESPONSE_KEY: response,
        VIEW_TYPE_KEY: view_type,
    }


if __name__ == '__main__':
    # redirects cli arguments to click handler
    m3(sys.argv[1:])
