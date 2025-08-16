"""
The custom logic for the command m3 report.

This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""


def create_custom_request(request):
    params = request.parameters
    if params.get('reportProjectType') != 'ACCOUNT' and params.get('eoAccount'):
        raise AssertionError(
            "The 'account-id' parameter may be specified only in case ACCOUNT "
            "report-type is set. Account-id is not applicable with other values"
            " of report-type"
        )
    if params.get('reportProjectType') == 'ACCOUNT' \
            and not params.get('eoAccount'):
        raise AssertionError(
            "Please, specified the 'account-id' parameter for the ACCOUNT "
            "report-type parameter"
        )

    params['format'] = 'EMAIL'

    if params.get('reportZoneType') in {'AWS_UNREACHABLE', 'AZURE_NATIVE'}:
        params['nativeCurrency'] = True

    return request
