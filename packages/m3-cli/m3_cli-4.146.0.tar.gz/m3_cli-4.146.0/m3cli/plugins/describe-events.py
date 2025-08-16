"""
The custom logic for the command m3 describe-events.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json

from m3cli.utils.utilities import timestamp_to_iso


def create_custom_request(request):
    params = request.parameters
    if not params.get('searchType'):
        params['searchType'] = 'ALL'
    if not params.get('count'):
        params.update({'count': 10})
    if params.get('searchType') == "RELATED" and not params.get('resourceId'):
        raise AssertionError(
            "The `--resource-id` parameter is required in case the RELATED "
            "search-type is specified"
        )

    return request


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except (IndexError, json.decoder.JSONDecodeError):
        return response
    for item in response:
        if item.get('timestamp'):
            item['timestamp'] = timestamp_to_iso(item.get('timestamp'))
    return response
