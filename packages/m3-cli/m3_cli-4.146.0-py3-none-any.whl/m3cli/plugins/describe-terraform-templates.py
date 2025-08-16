"""
The custom logic for the command m3 describe-terraform-template.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json


def create_custom_request(request):
    if not request.parameters.get('templateNames'):
        request.parameters['templateNames'] = []
    return request


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    if not response:
        return 'Specified templates were not found'
    response = sorted(response, key=lambda k: k['templateName'].upper())
    return response
