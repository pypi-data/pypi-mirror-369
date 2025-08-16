"""
The custom logic for the command m3 prolong-terraform-template-lock.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json
from datetime import datetime, timedelta

from m3cli.services.request_service import SdkClient, BaseRequest


def create_custom_request(request):
    parameters = request.parameters
    terraform_request = BaseRequest(
        command='get_parameters',
        api_action='GET_TERRAFORM_TEMPLATE_LOCK',
        parameters=parameters,
        method='POST',
    )
    request_map, response = SdkClient().execute(request=terraform_request)
    response = response[0]
    if not response.get('data'):
        error_msg = 'An error has occurred while processing the request'
        if response.get('readableError'):
            error_msg += response.get('readableError')
        else:
            error_msg += response.get('error')
        raise AssertionError(error_msg)
    raw_params = json.loads(response.get('data'))
    expiration_timestamp = raw_params.get('expiration')
    expiration_date = datetime.fromtimestamp(expiration_timestamp / 1e3)
    expiration_hours = parameters.pop('expirationHours')
    new_exp_date = expiration_date + timedelta(hours=int(expiration_hours))
    parameters['expirationInMillis'] = int(new_exp_date.timestamp() * 1e3)
    template_name = parameters.get('templateName')
    parameters['description'] = (
        f"Lock on template '{template_name}' has been updated"
    )
    return request


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    return [response]
