"""
The custom logic for the command m3 describe-resources.
This logic is created to convert M3 SDK API response to the Human readable
format.
"""
import json


def create_custom_request(request):
    params = request.parameters
    cloud = params.get('cloud')
    params['resourceType'] = 'INSTANCE'

    # todo remove
    params['categories'] = []
    availability_zone = params.get('availabilityZone')
    resource_group = params.get('resourceGroup')
    if cloud == 'GOOGLE' and not availability_zone:
        raise AssertionError(
            "Parameter 'availability-zone' is required for GOOGLE cloud.")
    if cloud == 'AZURE' and not resource_group:
        raise AssertionError(
            "Parameter 'resource-group' is required for AZURE cloud.")
    return request


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    response = response.get('sections', {})
    if not response:
        return {}

    result = []
    for section_value in response.values():
        result.append({
            "Category": section_value.get('title'),
            "Risk status": section_value.get('riskStatus'),
            "Risk priority": section_value.get('riskPriority')
        })
    return result
