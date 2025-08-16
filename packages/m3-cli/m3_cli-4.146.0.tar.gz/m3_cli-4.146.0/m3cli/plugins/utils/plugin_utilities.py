import os

from m3cli.utils.logger import get_custom_terminal_logger
from m3cli.utils.__init__ import SUPPORTED_OS
from logging import (WARNING)
from base64 import b64encode
from PIL import Image


def create_files(files_dict, path_for_files=None, reserve_path=None):
    """
    Initializing the path for the log file

      This function determines the type of system and, based on it,
      returns the path to the files, where keys were saved and
      creates the log file
    """

    global full_path
    os_name = os.name
    _LOG = get_custom_terminal_logger(__name__, WARNING)
    _LOG.propagate = False

    # Determining the type of operating system
    if os_name not in SUPPORTED_OS or not path_for_files:
        _LOG.warning(
            f'The {os_name} OS is not supported or the {path_for_files} '
            f'environment variable is not set. The file will be stored by '
            f'the {reserve_path} path'
        )
        path_for_files = reserve_path

    for key, value in files_dict.items():
        if not os.path.exists(path_for_files):
            try:
                os.makedirs(path_for_files)
            except OSError as exp:
                _LOG.warning(
                    f'{exp} The {key} file cannot be created. '
                    f'The file will be stored by the {reserve_path} path'
                )
                path_for_files = reserve_path

        full_path = os.path.join(path_for_files, key)
        try:
            with open(rf"{full_path}", "w") as file:
                file.write(value)
        except OSError:
            _LOG.exception(
                f'Unfortunately, it had not been possible to create '
                f'the files to the following {os.getcwd()} path'
            )

    return full_path


def encoding_image(icon):
    img = Image.open(icon)
    wid, hgt = img.size
    if wid >= 190 or hgt >= 130:
        raise AssertionError(
            f'The size of the image should be: width less than 190px, '
            f'height less than 130px. The size of the image that has '
            f'been provided: width={wid}px, height={hgt}px')
    encoded_str = str(
        b64encode(open(icon, 'rb').read()))[2:-1]

    return encoded_str


def processing_report_format(request, report_format: str | None = None):
    params = request.parameters
    if params.get('reportFormat') and params.get('URL'):
        raise AssertionError(
            'The flags `--url` (`-U`) and `--report` (`-R`) cannot be specified'
            ' together'
        )

    if params.get("URL"):
        params.update({'reportFormat': 'S3'})
        params.pop("URL")
        return request

    if params.get("reportFormat"):
        params.update({'reportFormat': 'EMAIL'})
    elif report_format == 'EMAIL':
        params.update({'reportFormat': 'EMAIL'})
    else:
        params.update({'reportFormat': 'JSON'})
    return request
