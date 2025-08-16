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
    """ Transform 'subtotal-report' command parameters from the Human
    readable format to appropriate for M3 SDK API request.

    :param request: Dictionary with command name, api action, method and
    parameters
    :type request: BaseRequest
    """
    processing_report_format(request)
    parse_and_set_date_range(request.parameters)

    params = request.parameters
    if params.get('instanceId'):
        raise AssertionError(
            'The parameter `--instance-id` is not supported for this report type'
        )

    tenant_group = params.pop('tenantGroup')
    clouds = params.pop('clouds', None) or None
    region = params.pop('region', None) or None
    params['target'] = {
        'tenantGroup': tenant_group,
        'reportUnit': 'TENANT_GROUP',
    }
    if region and clouds:
        raise AssertionError(
            'Can not get subtotal report using --clouds and --region filters '
            'together.'
        )
    if clouds:
        params['target'].update({
            'clouds': clouds,
            'reportUnit': 'TENANT_GROUP_AND_CLOUD',
        })
    if params.get('onlyAdjustments'):
        params['target'].update({
            'onlyAdjustments': params.pop('onlyAdjustments'),
        })
    if region:
        params['target'].update({'region': region})

    if params['target'].get('region') in {'AWS_UNREACHABLE', 'AZURE_NATIVE'}:
        params['nativeCurrency'] = True

    return request


def create_custom_response(
        request,
        response,
        view_type: str | None = None,
):
    """ Transform the command 'subtotal-report' response from M3 SDK API
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
    if grand_total:
        for each_row in response.get('records'):
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
            if 'projectCode' in each_row:
                each_row['tenant'] = each_row.pop('projectCode')
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
