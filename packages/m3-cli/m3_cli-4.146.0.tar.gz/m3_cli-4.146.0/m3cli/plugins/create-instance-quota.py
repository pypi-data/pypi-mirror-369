"""
The custom logic for the command m3 create-instance-quota.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""


def create_custom_request(request):
    request.parameters['instanceQuota'] = {
        'creationIntervalCount':
            request.parameters.pop('creationIntervalCount'),
        'creationIntervalHours':
            request.parameters.pop('creationIntervalHours')
    }
    return request

