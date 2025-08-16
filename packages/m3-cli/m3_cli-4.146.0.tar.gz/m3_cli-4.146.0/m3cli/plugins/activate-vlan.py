"""
The custom logic for the command m3 activate-vlan.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json


def create_custom_request(request):
    tenant_name = request.parameters['tenantName']
    request.parameters['tenantNames'] = [tenant_name]
    return request


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    return response.get('messages')[0].get('key')
