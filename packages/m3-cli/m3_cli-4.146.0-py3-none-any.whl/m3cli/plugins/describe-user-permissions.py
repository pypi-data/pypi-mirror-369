import json


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    response.pop('message', None)
    if response.get('permissionGroups'):
        response = response['permissionGroups']
    elif response.get('cloudServiceAccessDto'):
        response = response['cloudServiceAccessDto']
    return response
