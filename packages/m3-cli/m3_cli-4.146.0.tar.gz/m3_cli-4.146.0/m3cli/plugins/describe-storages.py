"""The custom logic for the command m3 describe-storages."""
import json


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    for each in response:
        cloud = each.get('cloud')
        if not cloud:
            continue
        if cloud == 'AZURE':
            params = each.get('parameters')
            if params:
                res_group_name = params.get('resourceGroupName')
                if res_group_name:
                    each['resourceGroup'] = res_group_name
        elif cloud == 'GOOGLE':
            params = each.get('parameters')
            if params:
                availability_zone = params.get('availabilityZone')
                if availability_zone:
                    each['googleAvailabilityZone'] = availability_zone
    return response
