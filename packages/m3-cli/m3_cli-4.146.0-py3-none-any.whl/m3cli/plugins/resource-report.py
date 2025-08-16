"""
The custom logic for the command m3 report.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json

from m3cli.plugins.utils.plugin_utilities import processing_report_format
from m3cli.utils.utilities import timestamp_to_iso
from m3cli.plugins import parse_and_set_date_range


def create_custom_request(
        request,
        view_type: str | None = None,
):
    """ Transform 'resource-report' command parameters from the Human
    readable format to appropriate for M3 SDK API request.

    :param request: Dictionary with command name, api action, method and
    parameters
    :type request: BaseRequest
    """
    if view_type in ('json', 'full'):
        raise AssertionError(
            "This command doesn't support the '--json' or '--full' "
            "flags"
        )

    processing_report_format(request, report_format='EMAIL')
    parse_and_set_date_range(request.parameters)
    params = request.parameters
    if params.get('onlyAdjustments'):
        raise AssertionError(
            "The flag `--adjustment` is not supported for this report type"
        )
    params['target'] = {
        'tenantGroup': params.pop('tenantGroup'),
        'reportUnit': 'TENANT_GROUP'
    }
    target = params['target']
    if params.get('clouds') and params.get('region'):
        raise AssertionError(
            'Parameters "clouds" and "regions" can not be specified together'
        )
    elif params.get('clouds'):
        target.update({
            'reportUnit': 'TENANT_GROUP_AND_CLOUD',
            'clouds': params.pop('clouds'),
        })
    elif params.get('region'):
        target.update({'region': params.pop('region')})
    return request


def create_custom_response(
        request,
        response,
        view_type: str | None = None,
):
    """ Transform the command 'resource-report' response from M3 SDK API
    to the more human readable format.

    :param response: Server response with data as a string representation
    of a dictionary
    """
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response

    if response.get('message') and response.get('s3ReportLink'):
        return f"{response.get('message')} Link: `{response.get('s3ReportLink')}`"

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
            # Rename
            if 'totalPrice' in each_row:
                each_row['total'] = each_row.pop('totalPrice')
            if 'recordType' in each_row:
                each_row['type'] = each_row.pop('recordType')
            if 'zone' in each_row:
                each_row['region'] = each_row.pop('zone')
            response_processed.append(each_row)

        currency_code = response.get('currencyCode') or 'USD'
        response_processed.append({
            'type': 'grandTotal',
            'total': grand_total,
            'currencyCode': currency_code,
        })
        return response_processed
    if response.get('message'):
        return response.get('message')
    return response
