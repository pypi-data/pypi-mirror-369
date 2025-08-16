"""
The custom logic for the command m3 destroy-terraform-stack.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json


def create_custom_request(request):
    request.parameters['task'] = 'DESTROY'
    if request.parameters.get('variables'):
        variables = request.parameters.pop('variables')
        request.parameters['variables'] = json.loads(variables)
    else:
        request.parameters['variables'] = dict()
    return request


def create_custom_response(request, response):
    return f'Destroy Terraform stack is initiated'
