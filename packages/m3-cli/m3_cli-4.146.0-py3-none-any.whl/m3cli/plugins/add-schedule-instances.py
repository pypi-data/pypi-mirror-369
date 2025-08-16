"""
The custom logic for the command m3 add-schedule-instances.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
from m3cli.plugins.common.schedule_instances import format_response


def create_custom_response(request, response):
    return format_response(response, 'added', 'to')
