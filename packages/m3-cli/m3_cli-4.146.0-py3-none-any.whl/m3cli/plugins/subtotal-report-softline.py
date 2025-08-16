"""
The custom logic for the command m3 report.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json

from m3cli.plugins.utils.plugin_utilities import processing_report_format
from m3cli.utils.utilities import timestamp_to_iso


def create_custom_request(request):
    """ Transform 'subtotal-report' command parameters from the Human
    readable format to appropriate for M3 SDK API request.

    :param request: Dictionary with command name, api action, method and
    parameters
    :type request: BaseRequest
    """
    processing_report_format(request)
    from_date = request.parameters.get('from')
    to_date = request.parameters.get('to')
    if from_date >= to_date:
        raise AssertionError('Parameter "from" can not be equal or greater '
                             'than parameter "to"')

    tenant = request.parameters.pop('tenant')
    clouds = request.parameters.pop('clouds') if \
        request.parameters.get('clouds') else None
    region = request.parameters.pop('region') if \
        request.parameters.get('region') else None
    request.parameters['target'] = {'tenant': tenant, 'reportUnit': 'TENANT'}
    if region and clouds:
        raise AssertionError('Can not get subtotal report using '
                             '--clouds and --region filters together.')
    if clouds:
        request.parameters['target'].update({
            'clouds': clouds,
            'reportUnit': 'TENANT_AND_CLOUD'
        })
    if region:
        request.parameters['target'].update({
            'region': region
        })
    return request


def create_custom_response(request, response):
    """ Transform the command 'subtotal-report' response from M3 SDK API
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
    if grand_total:
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
