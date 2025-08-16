import os

from m3cli.services.validation_service import ValidationService
from m3cli.utils.decorators import cli_response
from m3cli.services.commands_service import CommandsService


@cli_response(no_output=True)
def init_commands_service():
    cmd_service = CommandsService(
        m3cli_path=get_root_dir_path(),
        validation_service=ValidationService(),
    )
    return cmd_service


def get_root_dir_path():
    root_dir = os.path.dirname(__file__)
    if root_dir.split(os.sep)[-1] != 'm3cli':
        root_dir = os.path.join(root_dir, 'm3cli')
    return root_dir


CMD_SERVICE = init_commands_service()
