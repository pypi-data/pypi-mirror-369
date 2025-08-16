"""
The custom logic for the command m3 unlock-terraform-template.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json


def create_custom_request(request):
    parameters = request.parameters
    template_name = parameters.get('templateName')
    parameters['description'] = f"Template '{template_name}' has been unlocked"
    return request


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    return [response]
