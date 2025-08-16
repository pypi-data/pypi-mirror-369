"""
The custom logic for the command m3 cost-usage-report.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json
from m3cli.plugins.utils.plugin_utilities import processing_report_format


def create_custom_request(request):
    """ Transform the command 'cost-usage-report' request for M3 SDK API.
        """
    # ToDo redesign and support a new format of the response from BE.
    processing_report_format(request)

    request.parameters.update({'reportType': 'COST_AND_USAGE_OPTIMIZATION'})
    request.parameters.update({'cloud': 'AWS'})
    if request.parameters.get("reportFormat") == "JSON":
        raise AssertionError(
            f"The cost and usage report is temporarily unavailable in JSON "
            f"view. Use the \"report\" flag to receive the report by email")
    return request


def create_custom_response(request, response):
    """ Transform the command 'cost-usage-report' response from M3 SDK API
    to the more human readable format.
    """
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response

    if response.get('table') and not response.get('message') and \
            not response["table"].get('headers'):
        return "There are no records to display"

    return response
