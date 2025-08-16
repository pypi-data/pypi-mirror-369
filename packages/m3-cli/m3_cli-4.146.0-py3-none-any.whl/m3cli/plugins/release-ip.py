"""
The custom logic for the command m3 release-ip.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    if response:
        return "Success"
    else:
        return "Failed"
