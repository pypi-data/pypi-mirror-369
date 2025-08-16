"""
The custom logic for the command m3 backup.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json
from typing import Dict, Any, List


def create_custom_request(
        request: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Transforms the command parameters if necessary for M3 SDK API request.

    :param request: Dictionary with command information.
    :return: Transformed or original request for M3 SDK API.
    """
    return request


def create_custom_response(
        request: Dict[str, Any],
        response: str,
) -> List[Dict[str, Any]]:
    """
    Makes the response from the M3 SDK API more human-readable.

    :param request: Dictionary with command information.
    :param response: Server response as a stringified JSON array.
    :return: A list of dictionaries with readable instance status.
    """
    try:
        response_list = json.loads(response)
        return response_list
    except json.decoder.JSONDecodeError:
        return [{"error": "Invalid JSON response"}]
