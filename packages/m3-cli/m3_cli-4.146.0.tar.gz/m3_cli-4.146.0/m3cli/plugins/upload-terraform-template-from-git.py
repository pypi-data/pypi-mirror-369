"""The custom logic for the command m3 upload-terraform-template-from-git."""
import json
import os

from m3cli.utils.utilities import handle_variables


def create_custom_request(request):
    parameters = request.parameters
    approval_params = ['reviewers', 'approvalRule']
    approval_values = [
        p for p in approval_params if parameters.get(p) is not None
    ]
    approval_len = len(approval_values)
    if approval_len != 0:
        if approval_len != len(approval_params):
            raise AssertionError(
                'Parameters: "--approver", "--approval-policy" are required if '
                'the template needs review'
            )
        parameters['needReview'] = True
    parameters['gitUsername'] = 'TOKEN'
    variables = parameters.pop('variables', None)
    path_to_file = parameters.pop('variables-file', None)
    if variables or path_to_file:
        parameters['variables'] = handle_variables(variables, path_to_file)
    return request


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    if response.get('success'):
        return 'Specified template was successfully uploaded'
    error_message = response.get('errorMessage')
    if error_message:
        return (
            f'Some error happened during template uploading, reason - '
            f'"{error_message}"'
        )
    return response
