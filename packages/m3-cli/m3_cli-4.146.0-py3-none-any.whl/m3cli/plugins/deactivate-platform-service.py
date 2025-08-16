"""
The custom logic for the command m3 deactivate-platform-service.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""


def create_custom_response(request, response):
    """Prettify None response"""
    return "The request to deactivate platform service was successfully sent"
