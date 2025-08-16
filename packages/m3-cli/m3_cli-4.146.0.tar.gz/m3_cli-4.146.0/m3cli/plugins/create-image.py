"""
The custom logic for the command m3 create-image.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json

from m3cli.utils.utilities import timestamp_to_iso


def create_custom_response(request, response):
    try:
        response = json.loads(response)[0]
    except (IndexError, json.decoder.JSONDecodeError):
        return response
    if response.get('createdDate'):
        response['createdDate'] = timestamp_to_iso(response.get('createdDate'))
    return response
