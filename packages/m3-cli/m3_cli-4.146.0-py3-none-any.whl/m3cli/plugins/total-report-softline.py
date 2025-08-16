"""
The custom logic for the command m3 report.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json

from m3cli.plugins.utils.plugin_utilities import processing_report_format
from m3cli.utils.utilities import timestamp_to_iso


def create_custom_request(request):
    """ Transform 'total-report' command parameters from the Human
    readable format to appropriate for M3 SDK API request.

    :param request: Dictionary with command name, api action, method and
    parameters
    :type request: BaseRequest
    """
    processing_report_format(request)
    params = request.parameters
    from_date = params.get('from')
    to_date = params.get('to')
    if from_date >= to_date:
        raise AssertionError('Parameter "from" can not be equal or greater '
                             'than parameter "to"')
    request.parameters['target'] = {'tenant': params.pop('tenant'),
                                    'reportUnit': 'TENANT'}
    target = params['target']
    if params.get('clouds'):
        target.update({
            'clouds': params.pop('clouds'),
            'reportUnit': 'TENANT_AND_CLOUD'
        })
    elif params.get('region'):
        target.update({
            'region': params.pop('region'),
        })
    return request


def create_custom_response(request, response):
    """ Transform the command 'total-report' response from M3 SDK API
    to the more human readable format.

    :param response: Server response with data as a string representation
    of a dictionary
    """
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    response_processed = []
    grand_total = response.get('grandTotal')
    if isinstance(grand_total, (float, int)):
        for each_row in response.get('records'):
            if each_row.get('billingPeriodStartDate'):
                each_row['billingPeriodStartDate'] = \
                    timestamp_to_iso(each_row.get('billingPeriodStartDate'))
            if each_row.get('billingPeriodEndDate'):
                each_row['billingPeriodEndDate'] = \
                    timestamp_to_iso(each_row.get('billingPeriodEndDate'))
            response_processed.append(each_row)

        currency_code = response.get('currencyCode') or 'USD'
        response_processed.append({
            'recordType': 'grandTotal',
            'totalPrice': grand_total,
            'currencyCode': currency_code,
        })
        return response_processed
    if response.get('message'):
        return response.get('message')
    return response
