"""
The custom logic for the command m3 update-platform-service.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
from m3cli.plugins.utils.plugin_utilities import encoding_image


def create_custom_request(request):
    platform_service = request.parameters['platformService']
    icon = platform_service.get('icon')
    if icon:
        platform_service['icon'] = encoding_image(icon)
    return request


def create_custom_response(request, response):
    """
    Transform the command 'update-platform-service' response from M3 SDK
    API to the more human readable format.

    :param response: Server response with data as a string representation
    of a dictionary
    """
    import json
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    return response
