"""
The custom logic for the command m3 describe-shapes.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""

import json


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response

    for item in response:
        memory = item.get('memory')
        if memory:
            item['memoryGb'] = memory
    return response
