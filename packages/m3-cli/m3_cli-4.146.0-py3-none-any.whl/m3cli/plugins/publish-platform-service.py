"""
The custom logic for the command m3 publish-platform-service.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json
from m3cli.plugins.utils.plugin_utilities import encoding_image


def create_custom_request(request):
    parameters = request.parameters
    platform_service = parameters['platformService']

    parameters['tenantDisplayName'] = platform_service. \
        pop('tenantDisplayName', None)
    parameters['cloud'] = platform_service.pop('cloud', None)

    if not platform_service.get('deliveryMethod'):
        platform_service['deliveryMethod'] = 'Maestro'

    icon = platform_service.get('icon')
    if icon:
        platform_service['icon'] = encoding_image(icon)
    parameters['allTenants'] = platform_service.pop('allTenants', None)
    return request


def create_custom_response(request, response):
    """
    Transform the command 'activate-platform-service' response from M3 SDK
    API to the more human-readable format.

    :param request:
    :param response: Server response with data as a string representation
    of a dictionary
    """
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        pass
    return response
