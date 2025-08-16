"""
The custom logic for the command m3 upload-script.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json
from pathlib import Path

from m3cli.utils.utilities import load_file_contents


def create_custom_request(request):
    file_path = request.parameters.pop('filepath')
    extension = Path(file_path).suffix
    request.parameters['fileName'] += extension
    request.parameters['content'] = load_file_contents(file_path)
    return request


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    return response
