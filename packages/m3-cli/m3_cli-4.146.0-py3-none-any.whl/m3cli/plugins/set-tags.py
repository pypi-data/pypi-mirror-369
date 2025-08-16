import json


def create_custom_request(request):
    params = request.parameters

    cloud = params['cloud']

    if cloud == 'AZURE':
        if not params.get('resourceGroup'):
            raise AssertionError(
                'Parameter resource-group is required for AZURE cloud')
    if cloud == 'GOOGLE':
        if not params.get('availabilityZone'):
            raise AssertionError(
                'Parameter availability-zone is required for GOOGLE cloud')
    if params.get('volumeIds'):
        raise AssertionError(
            '\'volumeIds\' parameter is not allowed for public clouds')

    return request


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response

    parameters = request.parameters
    instance_id = parameters.get('instanceId')

    if isinstance(response, dict):
        error = response.get('error')
        if error:
            return {
                'instanceId': instance_id,
                'errorMessage': error
            }

    for res in response:
        tag = res['tag']
        res['key'] = tag.pop('key', None)
        res['value'] = tag.pop('value', None)
        res['instanceId'] = instance_id
    return response
