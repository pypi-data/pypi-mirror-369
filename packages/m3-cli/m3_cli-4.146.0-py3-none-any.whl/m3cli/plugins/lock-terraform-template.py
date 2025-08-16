"""
The custom logic for the command m3 lock-terraform-template.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json
from datetime import datetime, timedelta


def create_custom_request(request):
    params = request.parameters
    expiration_in_hours = params.pop('expirationHours')
    expiration_date = datetime.now() + timedelta(hours=int(expiration_in_hours))
    params['expirationInMillis'] = int(expiration_date.timestamp() * 1e3)
    template_name = params.get('templateName')
    params['description'] = f"Template '{template_name}' is locked"
    return request


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    return [response]
