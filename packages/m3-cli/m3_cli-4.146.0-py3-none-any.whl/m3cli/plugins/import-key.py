"""The custom logic for the command m3 import-key."""
import os


def create_custom_request(request):
    params = request.parameters
    tenant_name = params.get('tenantName')
    all_tenants = params.get('allTenants')
    region = params.get('region')
    parameters_specified_together = {'cloud', 'tenantName', 'region'}

    file_path = request.parameters.pop('filepath')
    if not os.path.isfile(file_path):
        raise FileExistsError(f'File {file_path} absent.')
    try:
        with open(file_path, 'r') as f:
            public_key = f.read()
    except UnicodeDecodeError:
        import codecs
        with codecs.open(file_path, 'r', encoding='utf-8',
                         errors='ignore') as fdata:
            public_key = fdata.read()
    request.parameters['publicKey'] = public_key.split('==')[0]

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
                                 f"{separator.join(lack_params)}")
    elif not tenant_name and not all_tenants:
        raise AssertionError("Please specify at least one of the following "
                             "parameters: '--tenant' or '--all-tenants'")
    elif all_tenants and region:
        raise AssertionError("The '--region' parameter is not allowed "
                             "when '--all-tenants' specified")

    return request
