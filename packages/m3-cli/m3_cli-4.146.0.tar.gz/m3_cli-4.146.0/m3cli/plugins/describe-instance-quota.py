"""
The custom logic for the command m3 describe-instance-quota.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json


def create_custom_response(request, response):
    if not response or response == 'null':
        return 'There are no records to display'

    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response

    response['creationIntervalCount'] = \
        str(response.get('creationIntervalCount'))
    response['creationIntervalHours'] = \
        str(response.get('creationIntervalHours'))
    return response
