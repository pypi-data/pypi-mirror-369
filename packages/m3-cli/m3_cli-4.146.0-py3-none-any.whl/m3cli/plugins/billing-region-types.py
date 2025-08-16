"""Custom logic for the M3 billing-region-types command"""

import json
from typing import List, Union, Dict, Any


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
) -> Union[List[Dict[str, Any]], str]:
    """
    Makes the response from the M3 SDK API more human-readable.

    :param request: Dictionary with command information.
    :param response: Server response as a stringified dictionary.
    :return: Processed response in a more human-readable format or error message.
    """
    try:
        response_dict = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    response_processed = []
    billing_region_types = response_dict.get('billingRegionTypes', [])
    if isinstance(billing_region_types, list):
        for region_type in billing_region_types:
            region_type_value = region_type.get('regionType')
            regions = ", ".join(region_type.get('regions', []))
            response_processed.append(
                {'regionType': region_type_value, 'regions': regions}
            )
        return response_processed
    return response_dict.get('message', response)
