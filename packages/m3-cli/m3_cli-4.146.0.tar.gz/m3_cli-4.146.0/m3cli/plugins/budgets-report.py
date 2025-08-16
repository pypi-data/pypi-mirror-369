"""
The custom logic for the command m3 budgets-report
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json
import datetime

from m3cli.services.request_service import BaseRequest


def compute_month_epoch_ms(year, month):
    return int(
        datetime.datetime(
            year, month, 1, tzinfo=datetime.timezone.utc).timestamp()
    ) * 1000


def create_custom_request(
        request: BaseRequest,
        view_type: str | None = None,
) -> BaseRequest:
    params = request.parameters
    if params.get('URL'):
        raise AssertionError(
            'The flag `--url` is not supported for this report type'
        )
    if params.get('reportFormat'):
        raise AssertionError(
            'The flag `--report` is not supported for this report type'
        )
    if params.get('instanceId'):
        raise AssertionError(
            'The parameter `--instance-id` is not supported for this report type'
        )
    if params.get('onlyAdjustments'):
        raise AssertionError(
            'The flag `--adjustment` is not supported for this report type'
        )
    if params.get('day'):
        raise AssertionError(
            'The parameter `--day` is not supported for this report type'
        )

    if not params.get('criteria'):
        params['criteria'] = 'ALL'
    if not params.get('compressEachQuota'):
        params['compressEachQuota'] = False
    params['tenantNames'] = [params.pop('tenantGroup')]
    if 'region' in params:
        params['regionName'] = params.pop('region')
    if params.get('year'):
        year = int(params['year'])
        if not isinstance(year, int):
            raise AssertionError("Year must be an integer")
        current_year = datetime.datetime.now().year
        if not (2020 <= year <= current_year):
            raise AssertionError(
                f"Year must be between 2020 and {current_year}"
            )

        if params.get('month'):
            month = int(params['month'])
            if not isinstance(month, int):
                raise AssertionError("Month must be an integer")
            if not (1 <= month <= 12):
                raise AssertionError("Month must be between 1 and 12")

            current_month = datetime.datetime.now().month
            if year == current_year and month > current_month:
                raise AssertionError(
                    f"Month {month}/{year} is in the future. Current month is "
                    f"{current_month}/{current_year}"
                )
    return request


def create_custom_response(
        request: BaseRequest,
        response,
        view_type: str | None = None,
):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    if isinstance(response, dict) and response.get('message') \
            and response.get('s3ReportLink'):
        return f"{response.get('message')} Link: `{response.get('s3ReportLink')}`"
    params = getattr(request, 'parameters', None)
    if view_type in ('json', 'table', 'full'):
        year = \
            int(params.get('year')) if params and params.get('year') else None
        month = \
            int(params.get('month')) if params and params.get('month') else None
        month_epoch_ms = \
            compute_month_epoch_ms(year, month) if year and month else None

        table_rows = []
        for item in response:
            month_usages = item.get('monthUsages', [])
            month_usage = None
            if month_epoch_ms:
                for usage in month_usages:
                    if int(usage.get("month", 0)) == month_epoch_ms:
                        month_usage = usage
                        break

            if month_usage:
                percent_used = month_usage.get('percentUsed')
                utilization = ""
                if percent_used is not None:
                    utilization = \
                        "less than 1%" if percent_used < 1 else f"{percent_used}"
                monthly_budget = month_usage.get("value")
                current_chargeback = month_usage.get("used")
            else:
                utilization = monthly_budget = current_chargeback = ''

            daily_usages = item.get('dailyUsages', [])
            daily_usage = None
            if isinstance(daily_usages, list) and daily_usages:
                daily_usage = max(
                    daily_usages,
                    key=lambda d: int(d.get('date') or 0)
                )

            if daily_usage:
                d_percent_used = daily_usage.get('percentUsed')
                daily_utilization = ""
                if d_percent_used is not None:
                    daily_utilization = \
                        "less than 1%" if d_percent_used < 1 else f"{d_percent_used}"
                daily_budget = daily_usage.get("value")
                current_daily_chargeback = daily_usage.get("used")
            else:
                daily_utilization = daily_budget = current_daily_chargeback = ''

            thresholds = item.get('thresholds', [])
            actions = item.get('actions', [])
            threshold_strs = [
                f"{int(th['value'])} %" for th in thresholds if 'value' in th
            ]
            action_plan = None
            if thresholds:
                action_plan = f"Notify on ({', '.join(threshold_strs)})"
                show_action_plan = [a for a in actions if a != 'NOTHING']
                if show_action_plan:
                    action_plan += ", " + ", ".join(show_action_plan)

            row = {
                "tenant": item.get("tenantDisplayName", ""),
                "type": item.get("type", ""),
                "monthlyBudget": monthly_budget,
                "currentMonthlyChargeback": current_chargeback,
                "monthlyUtilization %": utilization,
                "dailyBudget": daily_budget,
                "currentDailyChargeback": current_daily_chargeback,
                "dailyUtilization %": daily_utilization,
                "status": "enabled" if item.get("active") else "disabled",
                "tag": item.get("tag", ""),
                "affectedRegions": item.get("regionName", "")
            }
            if action_plan:
                row["actionPlan"] = action_plan
            table_rows.append(row)

            if params and params.get('tag'):
                desired_tag = params['tag']
                table_rows = [
                    row for row in table_rows if row.get('tag') == desired_tag
                ]

        def get_sort_key(row):
            # Try monthly utilization first, then daily
            utilization = row.get('monthlyUtilization %', '') \
                          or row.get('dailyUtilization %', '')

            # Convert to numeric value for sorting (descending order)
            if utilization == 'less than 1%':
                return -0.5  # Treat as 0.5% for sorting
            elif utilization:
                try:
                    return -float(str(utilization).replace('%', '').strip())
                except ValueError:
                    return float('inf')  # Invalid values go to end
            else:
                return float('inf')  # Empty values go to end

        if view_type == 'full':
            return [{"budget": item} for item in response]

        return sorted(
            table_rows,
            key=get_sort_key
        )

    return response
