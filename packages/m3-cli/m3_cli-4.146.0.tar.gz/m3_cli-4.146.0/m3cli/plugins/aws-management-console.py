"""
The custom logic for the command m3 aws-management-console.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""


def create_custom_request(request):
    request.parameters['cloud'] = 'AWS'
    return request


def create_custom_response(request, response):
    return 'The letter with console credentials was successfully sent' \
        if response == 'null' else response
