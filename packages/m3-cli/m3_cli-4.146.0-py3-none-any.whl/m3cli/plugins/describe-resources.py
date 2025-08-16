"""
The custom logic for the command m3 describe-resources.
This logic is created to convert M3 SDK API response to the Human readable
format.
"""


def create_custom_request(request):
    params = request.parameters
    tags = params.get('tag')
    group = params.get('group')

    if not group:
        params['group'] = 'ALL'

    if tags:
        for key, value in tags.items():
            params['tag'] = {"key": key, "value": value}
    return request


def create_custom_response(request, response):
    return response
