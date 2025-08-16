"""The custom logic for the command m3 describe-tags."""
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

        request.api_action = 'DESCRIBE_TAGS'
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
        res['instanceId'] = instance_id
        tag = res['tag']
        res['key'] = tag.pop('key', None)
        res['value'] = tag.pop('value', None)
    return response
