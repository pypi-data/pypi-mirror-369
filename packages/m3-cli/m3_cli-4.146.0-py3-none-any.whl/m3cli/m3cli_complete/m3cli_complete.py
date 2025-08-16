import json
import os
import re
import sys
import pathlib

PARAMETERS = 'parameters'
NO_DESCRIPTION = 'No description'
NAME = 'name'
COMMANDS = 'commands'
M3CLI_RUNNABLE = 'm3'
M3CLI = 'm3cli'
DESCRIPTION = 'description'
HELP = 'help'
PARENT_ATTR = 'parent'
DOMAIN_PARAMETERS = 'domain_parameters'
REQUIRED = 'required'
BASH_INTERPRETER = 'bash'
ZSH_INTERPRETER = 'zsh'
M3CLI_COMPLETE_DIR = 'm3cli_complete'
FOLDERS_SEPARATOR = os.sep
M3CLI_DIR2 = '/'.join(os.path.join(os.path.realpath(__file__)).split('/')[:-1])
M3CLI_DIR = FOLDERS_SEPARATOR.join(os.path.realpath(__file__).split(
    FOLDERS_SEPARATOR)[:-2])
M3CLI_HELP_FILE = 'm3cli_help.txt'
COMMANDS_DEF_FILE = 'commands_def.json'
ACCESS_META_FILE = 'access_meta.json'
M3CLI_CMD_DEF_PATH = os.path.join(M3CLI_DIR, COMMANDS_DEF_FILE)
M3CLI_ACCESS_META_PATH = os.path.join(M3CLI_DIR, M3CLI_COMPLETE_DIR,
                                      ACCESS_META_FILE)

RELATIVE_PATH_TO_COMPLETE = 'm3cli/m3cli_complete'


m3_home_path = pathlib.Path(__file__).parent.parent.parent.resolve()
HELP_FILE = os.path.join(m3_home_path,
                         RELATIVE_PATH_TO_COMPLETE,
                         M3CLI_HELP_FILE)


def load_meta_file(file_name=M3CLI_CMD_DEF_PATH,
                   access_meta=M3CLI_ACCESS_META_PATH):
    if not os.path.exists(file_name):
        sys.exit(1)
    with open(file_name) as meta_file:
        meta_file = json.loads(meta_file.read())
    with open(access_meta) as access_f:
        access_f = json.loads(access_f.read())
    meta_file['commands'].update(access_f)
    return meta_file


def process_command_start(request, meta):
    is_command_start = False
    command_start = request[-1]
    pretoken = request[-2]
    if pretoken != M3CLI_RUNNABLE:
        return is_command_start, {}

    suggestions = {}
    commands_meta = meta.get(COMMANDS)
    for command, attr in commands_meta.items():
        if command.startswith(command_start) and command != command_start:
            is_command_start = True
            command_description = attr.get(HELP).split(os.linesep)[0]
            suggestions[command] = command_description \
                if command_description else NO_DESCRIPTION
    return is_command_start, suggestions


def process_command(request, meta):
    is_command = False
    command_name = request[-1]
    pretoken = request[-2]
    if pretoken != M3CLI_RUNNABLE:
        return is_command, {}

    commands_meta = meta.get(COMMANDS)
    command = commands_meta.get(command_name)
    if not command:
        return is_command, {}

    is_command = True
    parameters = command.get(PARAMETERS)
    for parameter, attr in parameters.items():
        param_description = attr.get(HELP)
        param_required = attr.get(REQUIRED)
        if not param_description or PARENT_ATTR in attr:
            for key, value in meta.get(DOMAIN_PARAMETERS).items():
                if parameter == key:
                    param_description = value.get(HELP)
                    param_required = value.get(REQUIRED)
        if param_required:
            param_description = f'* {param_description}'
        suggestions[f'--{parameter}'] = param_description if param_description \
            else NO_DESCRIPTION
    return is_command, suggestions


def process_command_parameter(request, meta):
    index_of_first_param = 0
    for index, token in enumerate(request):
        if '--' in token:
            index_of_first_param = index
            break
    if not index_of_first_param:
        return False, {}
    no_params_request = request[:index_of_first_param]
    params_request = [param for param in
                      list(set(request) - set(no_params_request))
                      if re.match(r'^--[a-z]', param)]
    is_command, suggestions = process_command(request=no_params_request,
                                              meta=meta)
    updated_suggestions = {}
    for specified_param in params_request:
        if specified_param not in suggestions:
            for suggested_param in suggestions:
                if suggested_param.startswith(specified_param) \
                        and not specified_param == suggested_param:
                    updated_suggestions[suggested_param] = suggestions.get(
                        suggested_param)
        else:
            del suggestions[specified_param]
    if updated_suggestions:
        suggestions = updated_suggestions
    return True, suggestions


def format_response(suggestions):
    if isinstance(suggestions, list):
        with open(HELP_FILE, 'w+') as result_file:
            result_file.write(f'{os.linesep}'.join(sorted(suggestions)))
        exit(0)
    if isinstance(suggestions, str):
        with open(HELP_FILE, 'w+') as result_file:
            for each in suggestions:
                result_file.write(each)
        exit(0)
    suggestions = dict(sorted(suggestions.items()))
    response_array = []
    for key, value in suggestions.items():
        response_array.append(key)
        response_array.append(value)
    response_str = f'{os.linesep}'.join(response_array)
    with open(HELP_FILE, 'w+') as result_file:
        result_file.write(response_str)
    sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        sys.exit()
    interpreter = sys.argv[1]
    meta = load_meta_file()
    request = sys.argv[2:]
    response_str = ''

    if len(request) == 1:
        commands_meta = meta.get(COMMANDS)
        suggestions = ''
        if interpreter == BASH_INTERPRETER:
            suggestions = [key for key in commands_meta]
        if interpreter == ZSH_INTERPRETER:
            suggestions = {key: value.get(HELP).split(os.linesep)[0]
                           for key, value in commands_meta.items()}
        format_response(suggestions=suggestions)

    global_suggestion = {}

    is_command_start, suggestions = process_command_start(request=request,
                                                          meta=meta)

    if is_command_start:
        global_suggestion.update(suggestions)

    is_command, suggestions = process_command(request=request,
                                              meta=meta)
    if is_command:
        global_suggestion.update(suggestions)

    is_command_parameter, suggestions = process_command_parameter(
        request=request,
        meta=meta)
    if is_command_parameter:
        global_suggestion.update(suggestions)

    if interpreter == BASH_INTERPRETER:
        global_suggestion = [key for key in global_suggestion]
    format_response(suggestions=global_suggestion)
