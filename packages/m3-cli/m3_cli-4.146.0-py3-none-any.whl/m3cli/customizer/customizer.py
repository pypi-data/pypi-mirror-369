import argparse
import json
import os.path

from m3cli.services.validation_service import ValidationService

COMMANDS_DEF_FILE_NAME = 'commands_def.json'


def remove_required_options_from_schema(schema: dict):
    if 'required' in schema.keys():
        del schema['required']
    return schema


def validate_mutation_errors(validation_service, json_to_be_validated,
                             validation_schema):
    schema_validation_errors = validation_service.validate_with_json_schema(
        instance=json_to_be_validated,
        json_schema=validation_schema)
    if schema_validation_errors:
        raise SyntaxError(schema_validation_errors)


def inherit_action_handler(validation_service, command_meta: dict,
                           mutation_info: dict):
    # validate mutation command schema
    validate_mutation_errors(
        validation_service=validation_service,
        json_to_be_validated=mutation_info,
        validation_schema=remove_required_options_from_schema(
            schema=validation_service.command_schema))

    for mutation, info in mutation_info.items():
        if mutation == 'parameters':
            for parameter, parameter_mutation in info.items():
                # validate mutation parameter schema

                validate_mutation_errors(
                    validation_service=validation_service,
                    json_to_be_validated=parameter_mutation,
                    validation_schema=remove_required_options_from_schema(
                        schema=validation_service.param_schema))

                # create parameter fields if they are not exists in command
                if not command_meta.get('parameters'):
                    command_meta['parameters'] = {}
                if not command_meta['parameters'].get(parameter):
                    command_meta['parameters'][parameter] = {}

                # add or update parameter options due to instructions in
                # mutation file
                for param_config_name, param_config_value in \
                        parameter_mutation.items():
                    command_meta['parameters'][parameter][
                        param_config_name] = param_config_value

        elif mutation == 'output_configuration':
            for output, output_mutation in info.items():
                # create output config fields if they are not exists in command
                if not command_meta.get('output_configuration'):
                    command_meta['output_configuration'] = {}
                if not command_meta['output_configuration'].get(output):
                    command_meta['output_configuration'][output] = {}

                # add or update output config options due to instructions in
                # mutation file
                command_meta['output_configuration'][output] = output_mutation

        else:
            # add or update top level command options due to instructions in
            # mutation file
            command_meta[mutation] = info
    return command_meta


def override_action_handler(validation_service, command_meta: dict,
                            mutation_info: dict):
    # validate mutation command schema
    validate_mutation_errors(
        validation_service=validation_service,
        json_to_be_validated=mutation_info,
        validation_schema=validation_service.command_schema)

    # fully replace command options due to instructions in mutation file
    return mutation_info


mutation_actions_handlers_mapping = {
    'inherit': inherit_action_handler,
    'override': override_action_handler
}


def get_file_content(path_to_file):
    try:
        if not os.path.isfile(path_to_file):
            raise AssertionError('There is no file by path: {}.'.
                                 format(path_to_file))
        with open(path_to_file) as file:
            file_content = json.load(file)
        return file_content
    except json.JSONDecodeError:
        raise SyntaxError(f'{path_to_file} contains an invalid JSON')


def save_mutated_commands_def_meta(path_to_file, modified_command_def_content,
                                   commands_def_file_path):
    if not path_to_file:
        path_to_file = os.path.join(os.path.split(commands_def_file_path)[0],
                                    COMMANDS_DEF_FILE_NAME)
    with open(path_to_file, 'w') as new_file:
        new_file.write(json.dumps(modified_command_def_content, indent=2))


def generate_meta(commands_def_file_path, mutation_file_path,
                  output_file_path):
    command_def_content = get_file_content(path_to_file=commands_def_file_path)
    mutations_file_content = get_file_content(path_to_file=mutation_file_path)

    # process commands meta depends on mutation action
    mutations = mutations_file_content.get('mutations')
    if mutations:
        validation_service = ValidationService()
        for command, mutation_info in mutations.items():
            action = mutation_info.pop('action', None)
            mutation_handler = mutation_actions_handlers_mapping.get(action)
            if not mutation_handler:
                raise AssertionError('Invalid mutation action. Allowed values:'
                                     ' "override", "inherit"')

            command_meta = command_def_content.get('commands', {}).get(command)
            modified_command_meta = mutation_handler(
                validation_service=validation_service,
                command_meta=command_meta,
                mutation_info=mutation_info)

            command_def_content['commands'][command] = modified_command_meta

    # delete commands meta which marked as "exclusions"
    exclusions = mutations_file_content.get('exclusions')
    if exclusions:
        for command_to_be_excluded in exclusions:
            command_def_content['commands'].pop(command_to_be_excluded, None)

    save_mutated_commands_def_meta(
        path_to_file=output_file_path,
        modified_command_def_content=command_def_content,
        commands_def_file_path=commands_def_file_path)


parser = argparse.ArgumentParser(
    description='Customize commands_def.json meta due to predefined rules')
parser.add_argument('--commands_def_file_path', type=str, required=True,
                    help='Path to root commands_def.json file')
parser.add_argument('--mutation_file_path', type=str, required=True,
                    help='Path to file with predefined mutation rules')
parser.add_argument('--output_file_path', type=str,
                    help='Path to file where processed file will be '
                         'saved')
try:
    kwargs = vars(parser.parse_args())
    generate_meta(**kwargs)
except Exception as ex:
    print(ex)
