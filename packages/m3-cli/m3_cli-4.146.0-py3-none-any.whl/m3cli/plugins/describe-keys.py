"""The custom logic for the command m3 describe-keys."""
import json


def create_custom_request(request):
    """ Transform 'describe-keys' command parameters from the Human
    readable format to appropriate for M3 SDK API request.

    :param request: Dictionary with command name, api action, method and
    parameters
    :type request: BaseRequest
    """
    params = request.parameters

    if not params.get('name') and not params.get('cloud') and \
            not params.get('tenantName') and not params.get('region'):
        raise AssertionError('Please specified one of the following '
                             'parameters: region, tenant, cloud or key name')

    return request


def create_custom_response(request, response):
    """
    Transform the command 'describe-keys' response from M3 SDK API to
    the more humanreadable format.

    :param response: Server response with data as a string representation
    of a dictionary
    """
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response

    emails = set([each['email'] for each in response])
    if len(emails) <= 1:
        for each in response:
            each['email'] = None
    return response
