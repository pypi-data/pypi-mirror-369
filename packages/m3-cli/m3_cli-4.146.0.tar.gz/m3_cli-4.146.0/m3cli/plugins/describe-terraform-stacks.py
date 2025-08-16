"""
The custom logic for the command m3 describe-terraform-stack.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json

from m3cli.utils.utilities import timestamp_to_iso


def create_custom_request(request):
    if not request.parameters.get('stacksId'):
        request.parameters['stacksId'] = []
    return request


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    for each in response:
        creation_date = each.get('stackCreationTimestamp')
        if creation_date:
            each['creationDate'] = timestamp_to_iso(creation_date)
        mod_date = each.get('stackModificationTimestamp')
        if creation_date:
            each['lastModificationDate'] = timestamp_to_iso(mod_date)
    return response
