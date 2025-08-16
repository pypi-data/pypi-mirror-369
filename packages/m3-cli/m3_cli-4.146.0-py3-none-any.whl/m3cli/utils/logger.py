import getpass
import traceback
import os
from pathlib import Path
from logging import (DEBUG, getLogger, Formatter, StreamHandler, INFO,
                     NullHandler, FileHandler, WARNING)

from m3cli.services.environment_service import get_debug_mode, get_log_path
from m3cli.utils.__init__ import SUPPORTED_OS

USERNAME = getpass.getuser()
LOG_FILE_NAME = 'm3cli.log'
LOG_FORMAT_FOR_FILE = ('%(asctime)s [%(levelname)s] USER:{} %(filename)s:'
                       '%(lineno)d:%(funcName)s LOG: %(message)s'
                       .format(USERNAME))
LOG_FORMAT_FOR_VERBOSE_MODE = ('%(asctime)s [%(levelname)s] USER:{} LOG: '
                               '%(message)s'.format(USERNAME))


def get_file_handler(level=INFO):
    file_handler = FileHandler(LOG_FILE_NAME)
    file_handler.setLevel(level)
    file_handler.setFormatter(Formatter(LOG_FORMAT_FOR_FILE))

    return file_handler


def get_stream_handler(level=WARNING):
    stream_handler = StreamHandler()
    stream_handler.setLevel(level)
    log_formatter = Formatter('%(message)s')
    stream_handler.setFormatter(log_formatter)

    return stream_handler


def get_custom_file_logger(name, log_level_for_file=DEBUG,
                           log_level_logger=None):
    module_logger = getLogger(name)
    if not log_level_logger:
        log_level_logger = log_level_for_file
    module_logger.setLevel(log_level_logger)
    module_logger.addHandler(get_file_handler(log_level_for_file))

    return module_logger


def get_custom_terminal_logger(name, log_level_for_terminal=INFO,
                               log_level_logger=None):
    module_logger = getLogger(name)
    if not log_level_logger:
        log_level_logger = log_level_for_terminal
    module_logger.setLevel(log_level_logger)
    module_logger.addHandler(get_stream_handler(log_level_for_terminal))

    return module_logger


def create_path_for_logs():
    """
    Initializing the path for the log file

      This function determines the type of system and, based on it,
      returns the path to create the log file.
    """

    os_name = os.name
    path_home = Path.home()
    _LOG = get_custom_terminal_logger(__name__, WARNING)
    _LOG.propagate = False

    # Determining the type of operating system
    if os_name not in SUPPORTED_OS or not path_home:
        _LOG.warning(
            f"Current OS:[{os_name}] is not supported or environment variable"
            f" ${path_home} is not set. The log file will be stored by path "
            f"{os.getcwd()}"
        )
        return LOG_FILE_NAME

    # Creating full name of the path to the log directory
    custom_log_path = get_log_path()
    if custom_log_path:
        path = os.path.join(custom_log_path, 'm3cli', USERNAME)
    elif os_name == 'posix':
        path = os.path.join('/var/log', 'm3cli', USERNAME)
    else:
        path = os.path.join(path_home, '.m3cli', 'log')
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError:
            _LOG.warning(
                f"No access: {path}. To find the log file, check the directory"
                f" from which you called the command"
            )
            return LOG_FILE_NAME
    full_path = os.path.join(path, LOG_FILE_NAME)
    return full_path


# basicConfig(filename='m3cli.log', filemode='w', level=DEBUG)
m3cli_logger = getLogger('m3cli')
m3cli_logger.propagate = False

debug_mode = get_debug_mode()
if debug_mode:
    debug_path = create_path_for_logs()
    file_handler = FileHandler(debug_path)
    file_handler.setLevel(DEBUG)
    logFormatter = Formatter(LOG_FORMAT_FOR_FILE)
    file_handler.setFormatter(logFormatter)
    m3cli_logger.addHandler(file_handler)
else:
    m3cli_logger.addHandler(NullHandler())


# For --verbose
def write_logs():
    console_handler = StreamHandler()
    console_handler.setLevel(DEBUG)
    formatter = Formatter(LOG_FORMAT_FOR_VERBOSE_MODE)
    console_handler.setFormatter(formatter)
    m3cli_logger.addHandler(console_handler)


# define user logger to print messages
m3cli_user_logger = getLogger('m3cli.user')
# console output
console_handler = StreamHandler()
console_handler.setLevel(INFO)
console_handler.setFormatter(Formatter('%(message)s'))

m3cli_user_logger.addHandler(console_handler)


def get_logger(log_name, level=DEBUG):
    module_logger = m3cli_logger.getChild(log_name)
    if level:
        module_logger.setLevel(level)
    return module_logger


def get_user_logger(log_name, level=INFO):
    module_logger = m3cli_user_logger.getChild(log_name)
    if level:
        module_logger.setLevel(level)
    return module_logger


def exception_handler_formatter(exception_type, exception, exc_traceback):
    if debug_mode:
        m3cli_logger.error('%s: %s', exception_type.__name__, exception)
        traceback.print_tb(tb=exc_traceback, limit=15)
