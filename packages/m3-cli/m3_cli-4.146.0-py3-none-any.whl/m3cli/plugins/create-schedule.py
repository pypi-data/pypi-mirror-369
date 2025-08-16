"""
The custom logic for the command m3 create-schedule.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request; wraps tag key
"""
import json

from m3cli.utils.utilities import timestamp_to_iso


def create_custom_request(request):
    instances = []
    schedule = request.parameters['schedule']
    schedule['whenToExecute'] = "By cron expression"
    region = request.parameters['schedule']['region']
    if schedule.get('instances'):
        for each_instance_id in schedule['instances']:
            instances.append({
                "instanceId": each_instance_id,
                "instanceLocationInfo": {
                    "region": region
                }
            })
    schedule['instances'] = instances

    display_name = schedule.get('displayName')
    schedule_name = (display_name + '::' + region).lower()
    schedule['scheduleName'] = schedule_name

    schedule_type = schedule.get('scheduleType')
    tag_key = schedule.get('tagKey')
    tag_value = schedule.get('tagValue')
    if schedule_type == 'My instances with tag' \
            and (tag_key is None or tag_value is None):
        raise AssertionError('Parameters "tagKey" and "tagValue" are required '
                             'for schedule type "My instances with tag"')
    if tag_key or tag_value:
        schedule['tag'] = {
            'key': tag_key,
            'value': tag_value
        }
        del schedule['tagKey']
        del schedule['tagValue']
    return request


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    if response.get('nextRun'):
        response['nextRun'] = timestamp_to_iso(response.get('nextRun'))
    return response
