"""
The custom logic for the command m3 create-key.
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json
import os
from pathlib import Path

from m3cli.plugins.utils.plugin_utilities import create_files


def create_custom_request(request):
    global PATH_FROM_REQUEST
    global ALL_TENANTS
    params = request.parameters
    tenant_name = params.get('tenantName')
    all_tenants = params.get('allTenants')
    region = params.get('region')
    parameters_specified_together = {'cloud', 'tenantName', 'region'}

    if request.parameters.get('allTenants'):
        ALL_TENANTS = 'All available tenants'
    else:
        ALL_TENANTS = ''

    if request.parameters.get('path'):
        PATH_FROM_REQUEST = request.parameters.pop('path')
    else:
        PATH_FROM_REQUEST = ''

    intersection_params = set(request.parameters).intersection(
        parameters_specified_together)
    if intersection_params and not all_tenants:
        lack_params = parameters_specified_together.difference(
            intersection_params)
        if lack_params:
            separator = ', '
            raise AssertionError(f"The {separator.join(intersection_params)} "
                                 f"parameter(s) should be specified with "
                                 f"the following parameter(s): "
                                 f"{separator.join(sorted(lack_params))}")
    elif not tenant_name and not all_tenants:
        raise AssertionError("Please specify at least one of the following "
                             "parameters: '--tenant' or '--all-tenants'")
    elif all_tenants and region:
        raise AssertionError("The '--region' parameter is not allowed "
                             "when '--all-tenants' specified")

    return request


def create_custom_response(request, response):
    default_path = os.path.join(Path.home(), '.m3cli', 'keys')
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    if not PATH_FROM_REQUEST:
        # Creating full name of the path to the log directory
        path_files = default_path
    else:
        path_files = os.path.join(PATH_FROM_REQUEST, '.m3cli', 'keys')

    file_name_dict = {
        (response.get('name') + '.pem'): response.get('privatePart'),
        response.get('name'): response.get('publicPart')
    }

    path_to_the_file = create_files(
        file_name_dict, path_files, default_path
    )
    if ALL_TENANTS:
        response['region'] = 'All regions'
        response['tenant'] = 'All tenants'
    response['path'] = path_to_the_file
    return response
