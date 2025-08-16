"""
The custom logic for the command m3 activate-service.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json

from m3cli.utils.utilities import timestamp_to_iso


def create_custom_response(request, response):
    """
    Transform the command 'activate-platform-service' response from M3 SDK
    API to the more human readable format.

    :param response: Server response with data as a string representation
    of a dictionary
    """
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    if response.get('id'):
        response.update({'serviceId': response.pop('id')})
    if response.get('creationDate'):
        response['creationDate'] = timestamp_to_iso(response.get('creationDate'))
    return response
