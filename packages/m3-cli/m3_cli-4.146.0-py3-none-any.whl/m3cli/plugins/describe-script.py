"""
The custom logic for the command m3 describe-script.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    for each in response:
        # return null if there is no script with given name. Status "Success"
        if not each:
            return 'There is no script with such name'
        if not each.get('content'):
            each['content'] = 'Describe this item separately to get ' \
                              'the content.'
    return response

