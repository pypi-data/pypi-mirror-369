"""
The custom logic for the command m3 upload-terraform-template.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import os
import json

from m3cli.utils.utilities import load_file_contents, handle_variables


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
        parameters["needReview"] = True
    file_path = parameters.pop('filepath')
    parameters['templateContent'] = load_file_contents(file_path)
    parameters['templateActivity'] = 'UPLOAD'
    variables = parameters.pop('variables', None)
    path_to_file = parameters.pop('variables-file', None)
    if variables or path_to_file:
        parameters['variables'] = handle_variables(variables, path_to_file)
    return request


def create_custom_response(request, response):
    response = json.loads(response)
    if response['success']:
        template_id = response.get('templateUUID')
        return f'The template was uploaded with the identifier "{template_id}"'
    else:
        error = response.get('errorMessage')
        return f'The template failed to upload. Reason: "{error}"'
