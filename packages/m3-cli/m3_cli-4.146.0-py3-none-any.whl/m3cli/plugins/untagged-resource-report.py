"""
The custom logic for the command m3 untagged-resource-report.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json

from m3cli.plugins.utils.plugin_utilities import processing_report_format
from m3cli.utils.utilities import timestamp_to_iso


def create_custom_request(request):
    """ Transform 'untagged-resource-report' command parameters from the Human
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
                                    'reportUnit': 'TENANT_AND_RESOURCES_UNTAGGED',
                                    'clouds': [] if not params.get('clouds')
                                    else params.pop('clouds')}
    target = request.parameters['target']
    if params.get('region'):
        target.update({
            'region': params.pop('region'),
        })
    return request


def create_custom_response(request, response):
    """ Transform the command 'untagged-resource-report' response from
    M3 SDK API to the more human-readable format.

    :param response: Server response with data as a string representation
    of a dictionary
    """
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    response_processed = []
    grand_total = response.get('grandTotal')
    if grand_total is not None:
        for each_row in response.get('records'):
            # TODO to investigate how to replace projectCode with
            #  tenantName on api side
            project_code = each_row.get('projectCode')
            if project_code:
                each_row['tenantName'] = each_row.pop('projectCode')
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
