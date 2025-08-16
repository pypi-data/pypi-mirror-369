"""
The custom logic for the command m3 plan-terraform-template.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import os
import json

from m3cli.utils.utilities import handle_variables


def create_custom_request(request):
    parameters = request.parameters
    parameters['task'] = 'PLAN'
    variables = parameters.pop('variables', None)
    path_to_file = parameters.pop('variables-file', None)
    if variables or path_to_file:
        parameters['variables'] = handle_variables(variables, path_to_file)
    return request
