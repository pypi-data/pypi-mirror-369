"""
The custom logic for the command m3 delete-terraform-template.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    if response.get('cause'):
        response['status'] = response.pop('cause')
    if response.get('success'):
        response.pop('success')
        response['status'] = 'Success'
    return response
