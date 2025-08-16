import importlib

from m3cli import CMD_SERVICE
from m3cli.services.request_service import BaseRequest, POST


ACTIONS_MAP = {
    "total": importlib.import_module("m3cli.plugins.total-report"),
    "subtotal": importlib.import_module("m3cli.plugins.subtotal-report"),
    "resource": importlib.import_module("m3cli.plugins.resource-report"),
    "hourly": importlib.import_module("m3cli.plugins.hourly-report"),
    "budgets": importlib.import_module("m3cli.plugins.budgets-report"),
}

COMMANDS_MAP = {
    "total": "total-report",
    "subtotal": "subtotal-report",
    "resource": "resource-report",
    "hourly": "hourly-report",
    "budgets": "budgets-report",
}

TYPES_MAP = {
    "total-report": "total",
    "subtotal-report": "subtotal",
    "resource-report": "resource",
    "hourly-report": "hourly",
    "budgets-report": "budgets",
}

REQUEST_MAP = {}
HEADERS_MAP = {}
for param_type, command_name in COMMANDS_MAP.items():
    _, cmd_def = CMD_SERVICE._CommandsService__resolve_command_def(command_name)
    REQUEST_MAP[param_type] = {
        "command": command_name,
        "method": POST,
        "api_action": cmd_def["api_action"],
    }
    HEADERS_MAP[param_type] = \
        cmd_def["output_configuration"].get("response_table_headers") or []


def create_custom_request(
        request: BaseRequest,
        view_type: str | None = None,
) -> BaseRequest:
    report_type = request.parameters.pop("types", "total")
    request_kwargs = REQUEST_MAP.get(report_type)
    if not request_kwargs:
        raise AssertionError(
            f"No such type: '{report_type}' in command 'm3 report'. "
            f"Valid options: {tuple(COMMANDS_MAP.keys())}"
        )
    new_request = BaseRequest(**request_kwargs, parameters=request.parameters)
    new_request = ACTIONS_MAP[report_type].create_custom_request(
        new_request, view_type,
    )
    return new_request


def create_custom_response(
        request: BaseRequest,
        response,
        view_type: str | None = None,
):
    report_type = TYPES_MAP[request.command]
    new_response = ACTIONS_MAP[report_type].create_custom_response(
        request, response, view_type,
    )
    if view_type == 'table' and isinstance(new_response, list):
        new_headers = HEADERS_MAP[report_type]
        new_response = [
            {k: v for k, v in i.items() if k in new_headers}
            for i in new_response
        ]
    return new_response
