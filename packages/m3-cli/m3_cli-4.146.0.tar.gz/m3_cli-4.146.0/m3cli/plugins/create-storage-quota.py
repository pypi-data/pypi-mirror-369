"""
The custom logic for the command m3 create-volume-quota.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""


def create_custom_request(request):
    request.parameters['volumeQuota'] = {
        'creationIntervalHours':
            request.parameters.pop('creationIntervalHours'),
        'creationIntervalCount':
            request.parameters.pop('creationIntervalCount'),
        'maxSize':
            request.parameters.pop('maxSize')
    }
    return request

