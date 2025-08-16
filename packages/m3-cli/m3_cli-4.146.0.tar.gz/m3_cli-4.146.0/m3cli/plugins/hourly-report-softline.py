"""
The custom logic for the command m3 report.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import datetime as dt
from datetime import datetime


def create_custom_request(request):
    """ Transform 'hourly-report' command parameters from the Human
    readable format to appropriate for M3 SDK API request.

    :param request: Dictionary with command name, api action, method and
    parameters
    :type request: BaseRequest
    """
    params = request.parameters
    from_date = params.pop('date')
    to_date = datetime.timestamp(
        datetime.fromtimestamp(from_date / 1000) + dt.timedelta(days=1)) * 1000
    params['target'] = {'tenant': params.pop('tenant'),
                        'reportUnit': 'TENANT'}
    target = params['target']
    if params.get('region'):
        target.update({
            'region': params.pop('region'),
        })
    params['from'] = from_date
    params['to'] = to_date
    return request
