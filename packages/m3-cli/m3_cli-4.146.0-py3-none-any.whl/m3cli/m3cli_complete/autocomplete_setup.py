import os
import subprocess
import sys

from m3cli.m3cli_complete import BASH_COMPLETE_SCRIPT, ZSH_COMPLETE_SCRIPT, \
    PROFILE_D_PATH, RELATIVE_PATH_TO_COMPLETE, COMPLETE_PROCESS_FILE, \
    TEMP_HELP_FILE, PROFILE_ZSH_COMPLETE_SCRIPT, PROFILE_BASH_COMPLETE_SCRIPT
from m3cli.m3cli_complete.m3cli_complete import (BASH_INTERPRETER,
                                                 ZSH_INTERPRETER)
from m3cli.utils.logger import get_logger

_LOG = get_logger('autocomplete_handler')

PYTHON_SYMLINK = 'PYTHON_SYMLINK'
SCRIPT_PATH = 'SCRIPT_PATH'
HELP_FILE = 'HELP_FILE'
COMMAND_TO_CHECK_INTERPRETER = "echo $SHELL"
SHRC_AUTOCOMPLETE_MARKER = 'm3cli_autocomplete_system_settings'


def _get_appropriate_script_name(stdout):
    if BASH_INTERPRETER in stdout:
        return BASH_INTERPRETER, BASH_COMPLETE_SCRIPT
    if ZSH_INTERPRETER in stdout:
        return ZSH_INTERPRETER, ZSH_COMPLETE_SCRIPT
    return None, None


def _add_str_to_rc_file(interpreter, script, m3_home_path,
                        installed_python_link):
    script_path = os.path.join(m3_home_path,
                               RELATIVE_PATH_TO_COMPLETE, script)
    source_string = f'\nsource {script_path} "{installed_python_link}" ' \
                    f'"{m3_home_path}"'
    rc_file_path = os.path.expanduser('~') + f'/.{interpreter}rc'
    with open(rc_file_path, 'r+') as f:
        if SHRC_AUTOCOMPLETE_MARKER not in f.read():
            f.write(f'\n# {SHRC_AUTOCOMPLETE_MARKER}')
            f.write(source_string)
            _LOG.info(f'm3 autocomplete have been '
                      f'successfully injected to the RC file. '
                      f'Path to the RC file: {rc_file_path}')
    return source_string


def _delete_str_from_rc_file(interpreter):
    rc_file_path = os.path.expanduser('~') + f'/.{interpreter}rc'
    with open(rc_file_path, 'r+') as f:
        lines = f.readlines()

    first_string_found = False
    with open(rc_file_path, 'w') as f:
        for line in lines:
            if SHRC_AUTOCOMPLETE_MARKER in line.strip("\n"):
                first_string_found = True
                continue
            if first_string_found:
                first_string_found = False
                continue
            f.write(line)
    _LOG.info(f'm3 autocomplete have been '
              f'successfully removed from the RC file. ')


def _get_interpreter_and_appropriate_script():
    if sys.platform not in ['darwin', 'linux']:
        raise AssertionError(
            f'The OS is not applicable for autocompletion '
            f'setup. Current OS is {sys.platform}')
    stdout = subprocess.check_output(COMMAND_TO_CHECK_INTERPRETER,
                                     shell=True).decode('utf-8').strip()
    _LOG.info(f'Current interpreter: {stdout}')
    if not stdout:
        raise AssertionError(
            f'The interpreter can not be checked. M3 '
            f'autocomplete installation will be skipped...')
    interpreter, script = _get_appropriate_script_name(stdout)
    if not interpreter:
        raise AssertionError(
            f'Unsupported interpreter {stdout}. M3admin '
            f'autocomplete installation will be skipped...')
    return interpreter, script


def enable_autocomplete_handler():
    interpreter, script = _get_interpreter_and_appropriate_script()
    import pathlib
    m3_home_path = pathlib.Path(__file__).parent.parent.parent.resolve()
    from platform import python_version
    installed_python_link = 'python' + '.'.join(
        python_version().lower().split('.')[0:-1])
    try:
        if not os.path.exists(PROFILE_D_PATH):
            _LOG.info(f'Going to edit RC file')
            source_string = _add_str_to_rc_file(interpreter, script,
                                                m3_home_path,
                                                installed_python_link)
            return f'Autocomplete has been successfully installed and ' \
                   f'will start work after the current terminal session ' \
                   f'reload. If you want to manually activate ' \
                   f'autocomplete without reloading the terminal session, ' \
                   f'please run the following command \n {source_string}'

        _LOG.info(f'Going to copy autocomplete files to '
                  f'{PROFILE_D_PATH}')
        init_profile_script_path = os.path.join(m3_home_path,
                                                RELATIVE_PATH_TO_COMPLETE,
                                                script)
        python_script = os.path.join(m3_home_path,
                                     RELATIVE_PATH_TO_COMPLETE,
                                     COMPLETE_PROCESS_FILE)
        help_file_path = os.path.join(m3_home_path,
                                      RELATIVE_PATH_TO_COMPLETE,
                                      TEMP_HELP_FILE)
        script = 'profile_' + script
        processed_profile_script_path = os.path.join(PROFILE_D_PATH, script)
        with open(init_profile_script_path, 'r+') as f:
            lines = f.readlines()
        script_was_found = False
        help_was_found = False
        with open(processed_profile_script_path, 'w') as f:
            for line in lines:
                if SCRIPT_PATH in line.strip(
                        "\n") and not script_was_found:
                    line = f'SCRIPT_PATH={python_script}\n'
                    script_was_found = True
                if HELP_FILE in line.strip(
                        "\n") and not help_was_found:
                    line = f'HELP_FILE={help_file_path}'
                    help_was_found = True
                f.write(line)
        _LOG.info(f'm3cli autocomplete have been '
                  f'successfully set up. Path to the "profile.d" file: '
                  f'{processed_profile_script_path}')
        return f'm3admin autocomplete have been ' \
               f'successfully set up. Path to the "profile.d" file: ' \
               f'{processed_profile_script_path}'
    except AssertionError:
        _LOG.info(f'Autocomplete installation is not available')
        raise AssertionError(f'Autocomplete installation is not '
                             f'available')
    except Exception as e:
        _LOG.info(f'Something happen while setup autocomplete. Reason: {e}')
        raise AssertionError(f'Something happen while setup '
                             f'autocomplete. Reason: {e}')


def disable_autocomplete_handler():
    interpreter, script = _get_interpreter_and_appropriate_script()
    try:
        _delete_str_from_rc_file(interpreter)
        if os.path.exists(PROFILE_D_PATH):
            for each in os.listdir(PROFILE_D_PATH):
                if each in [ZSH_COMPLETE_SCRIPT,
                            BASH_COMPLETE_SCRIPT,
                            PROFILE_ZSH_COMPLETE_SCRIPT,
                            PROFILE_BASH_COMPLETE_SCRIPT]:
                    os.remove(os.path.join(PROFILE_D_PATH, each))
        return 'm3cli autocomplete have been ' \
               'successfully deleted'
    except Exception as e:
        _LOG.info(f'Something happen while removing autocomplete. Reason: {e}')
        raise AssertionError(f'Something happen while removing '
                             f'autocomplete. Reason: {e}')
