"""
The custom logic for the command m3 health-check.
This logic is created to convert M3 SDK API response to the Human readable
format.
"""
import json
from datetime import datetime

from m3cli.utils.utilities import open_creds_file, SERVER_UNAVAILABLE_TIMESTAMP


def create_custom_response(request, response):
    """ Transform the command 'health-check' response from M3 SDK API
    to the more human readable format.

    :param response: Server response with data as a string representation
    of a dictionary
    """
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response

    creds_file = open_creds_file()
    with open(creds_file, 'r+') as file:
        try:
            data = json.load(file)
            data.update({'cliLatestVersion': response.get('cliLatestVersion'),
                         'cliDistributionLatestVersionUrl': response.get(
                             'cliDistributionLatestVersionUrl'),
                         'last_visit': datetime.timestamp(datetime.now()),
                         'cliWindowsDistributionUrl': response.get(
                             'cliWindowsDistributionUrl'),
                         'cliLinuxDistributionUrl': response.get(
                             'cliLinuxDistributionUrl'),
                         'cliMacOsDistributionUrl': response.get(
                             'cliMacOsDistributionUrl')})
            data.pop(SERVER_UNAVAILABLE_TIMESTAMP, None)
        except json.decoder.JSONDecodeError:
            data = {}

    with open(creds_file, 'w') as write_file:
        json.dump(data, write_file)

    if response.get('additionalData'):
        data = response.pop('additionalData')
        response['mails'] = data.get('mails')
        response['ownership'] = data.get('ownership')
        response['terraform'] = data.get('terraform')
    return response
