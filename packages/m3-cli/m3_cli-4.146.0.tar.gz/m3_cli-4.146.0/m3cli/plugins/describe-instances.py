"""
The custom logic for the command m3 describe-instances.
This logic is created to convert M3 SDK API response to the Human readable
format.
"""
import json

from m3cli.utils.utilities import timestamp_to_iso


def create_custom_request(request):
    params = request.parameters
    running = params.get('running')
    stopped = params.get('stopped')
    insights = params.get('insights')
    group = params.get('group')
    risk_factor = params.get('riskFactor')
    tags = params.get('resourceTag')

    if tags:
        if len(tags) > 1:
            raise AssertionError(
                'Only one value allowed for \'tag\' parameter, '
                'could not process more')
        for key, value in tags.items():
            params['resourceTag'] = {"key": key, "value": value}

    if not insights:
        params['insights'] = False

    if group:
        groups_if_insights = ['ALL', 'INSTANCE_COSTS', 'SCHEDULES', 'TAGS',
                              'LIFE_TIME', 'OWNERSHIP', 'VULNERABLE']
        groups_if_not_insights = ['ALL', 'UNTAGGED']
        if insights:
            if group not in groups_if_insights:
                raise AssertionError(
                    f'Please check \'group\' parameter. '
                    f'Allowed values: {groups_if_insights}')
        if not insights:
            if group not in groups_if_not_insights:
                raise AssertionError(
                    f'Please check \'group\' parameter. '
                    f'Allowed values: {groups_if_not_insights}')

    if risk_factor and not insights:
        raise AssertionError(
            'Please specify \'insights\' flag. '
            'It is required for \'risk-factor\' parameter')

    if running and stopped:
        raise AssertionError(
            '\'running\' and \'stopped\' flags cannot be both specified'
        )

    if running:
        params['instanceStates'] = ['running']
        return request
    if stopped:
        params['instanceStates'] = ['stopped']
        return request
    return request


def create_custom_response(
        request,
        response,
        view_type: str | None = None,
):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    instances = response.get('instances')
    if instances:
        for instance in instances:
            if instance.get('instanceType'):
                instance['shape'] = instance.pop('instanceType')
            if instance.get('nativeInstanceType'):
                instance['instanceType'] = instance.pop('nativeInstanceType')
            if instance.get('instanceStopDate'):
                instance['instanceStopDate'] = \
                    timestamp_to_iso(instance.get('instanceStopDate'))
            if instance.get('instanceTerminationDate'):
                instance['instanceTerminationDate'] = \
                    timestamp_to_iso(instance.get('instanceTerminationDate'))
            if instance.get('memoryMb'):
                instance['memoryGb'] = round(instance.pop('memoryMb') / 1024, 2)

    if view_type == 'full':
        instances = response.get('instances', [])
        response = [{"instance": instance} for instance in instances]

    return response
