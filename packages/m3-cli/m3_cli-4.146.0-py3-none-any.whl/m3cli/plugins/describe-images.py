"""
The custom logic for the command m3 describe-images.
This logic is created to convert M3 SDK API response to the Human readable
format.
"""
import json

from m3cli.utils.utilities import timestamp_to_iso


def create_custom_response(request, response):
    """ Transform the command 'describe-images' response from M3 SDK API
    to the more human readable format.

    :param response: Server response with data as a string representation
    of a dictionary
    """
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response

    for each_row in response:
        if each_row.get('createdDate'):
            each_row['createdDate'] = timestamp_to_iso(
                each_row.get('createdDate'))
    return response
