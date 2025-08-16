"""The custom logic for the command m3 describe-service-section."""
import json

from bs4 import BeautifulSoup


def create_custom_response(
        request,
        response: str,
) -> list | str:
    try:
        response_data = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response  # Return the raw response if it's not a valid JSON

    if isinstance(response_data, list):
        for res in response_data:
            block_value = res.get('blockValue')
            if not block_value:
                res['blockValue'] = "No content for the section is available"
            else:
                html = bool(BeautifulSoup(block_value, "html.parser").find())
                if html:
                    res['blockValue'] = '<HTML content>'
    return response_data
