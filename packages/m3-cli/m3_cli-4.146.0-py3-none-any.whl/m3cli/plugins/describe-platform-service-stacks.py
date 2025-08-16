"""The custom logic for the command m3 describe-platform-service-stacks.py"""
import json

from m3cli.utils.utilities import timestamp_to_iso


def create_custom_request(request):
    params = request.parameters
    if params.get('serviceName') and params.get('serviceId'):
        raise AssertionError("The `--service` and `--service-id` parameters "
                             "cannot be specified together")

    return request


def create_custom_response(request, response):
    """
    Transform the command 'describe-platform-service-stacks' response from M3 SDK
    API to the more human readable format.

    :param response: Server response with data as a string representation
    of a dictionary
    """
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    for each in response:
        if each.get('id'):
            each.update({'serviceId': each.pop('id')})
        if each.get('creationDate'):
            each['creationDate'] = timestamp_to_iso(each.get('creationDate'))
    return response
