"""
The custom logic for the command m3 report.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import datetime as dt
import json
from datetime import datetime, timedelta

from m3cli.services.validation_service import ValidationService
from m3cli.plugins.utils.plugin_utilities import processing_report_format


def create_custom_request(
        request,
        view_type: str | None = None,
):
    """ Transform 'hourly-report' command parameters from the Human
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
    validation_service = ValidationService()
    params = request.parameters

    use_date = 'date' in params
    use_year_month_day = 'year' in params and 'month' in params and 'day' in params

    if use_date and any(p in params for p in ('year', 'month', 'day')):
        raise ValueError("Cannot mix 'date' with 'year'/'month'/'day'")
    if not (use_date or use_year_month_day):
        raise ValueError("Requires 'date' or 'year', 'month', 'day' parameters")

    if use_date:
        from_date = params.pop('date')
        to_date = datetime.timestamp(
            datetime.fromtimestamp(from_date / 1000) + dt.timedelta(days=1)
        ) * 1000
    else:
        year = params.pop('year')
        month = params.pop('month')
        day = params.pop('day')

        try:
            year_int = int(year)
            month_int = int(month)
            day_int = int(day)
            datetime(year_int, month_int, day_int)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid date parameters: {e}") from e

        from_date_str = f'{int(day):02d}.{month_int:02d}.{year_int}'
        from_date = validation_service.adapt_date(from_date_str)

        next_day_date = \
            datetime(year_int, month_int, int(day)) + timedelta(days=1)
        to_date_str = (
            f'{next_day_date.day:02d}.{next_day_date.month:02d}'
            f'.{next_day_date.year}'
        )
        to_date = validation_service.adapt_date(to_date_str)

        params['from'] = from_date
        params['to'] = to_date

    params['target'] = {
        'tenantGroup': params.pop('tenantGroup'),
        'reportUnit': 'TENANT_GROUP'
    }
    target = params['target']
    if params.get('region'):
        target.update({
            'region': params.pop('region'),
        })
    params['from'] = from_date
    params['to'] = to_date
    return request


def create_custom_response(
        request,
        response,
        view_type: str,
):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    if response.get('message') and response.get('s3ReportLink'):
        return f"{response.get('message')} Link: `{response.get('s3ReportLink')}`"
    return response
