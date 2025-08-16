import json


# TODO: redesign plugins to use OOP, move common logic to abstract class
def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response

    if isinstance(response, dict):
        error = response.get('error')
        if error:
            parameters = request.parameters
            instance_id = parameters.get('instanceId')
            tenant_name = parameters.get('tenantName')
            region_name = parameters.get('region')
            cloud = region_name.split('-')[0]
            return {
                'cloud': cloud,
                'instanceId': instance_id,
                'region': region_name,
                'tenant': tenant_name,
                'errorMessage': error
            }
    return response.get('instances')
