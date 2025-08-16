import json

ADDITIONAL_PARAMS_NAME = 'additionalParams'


def create_custom_request(request):
    params = request.parameters['params']
    cloud = params['cloud']

    if not params.get('Count'):
        params['Count'] = 1

    if not params.get('Key Pair Name') and cloud != 'AZURE':
        raise AssertionError(f"The '--key-name' parameter is required "
                             f"for {cloud} cloud")

    if (params.get('Additional Storage (GB)')
            and cloud not in ["AWS", "AZURE", "GOOGLE", "YANDEX"]):
        raise AssertionError(f"The '--additional-storage' parameter is not "
                             f"allowed with {cloud} cloud")

    if params.get('Shape Alias') and params.get('Instance type'):
        raise AssertionError(f"The \'Shape\' and \'Instance Type\' "
                             f"parameters cannot be specified simultaneously")

    if not params.get('Shape Alias') and not params.get('Instance type'):
        raise AssertionError(f"Please, specify one of the following "
                             f"parameters: \'Shape\' or \'Instance Type\'")

    stop_after = params.get('Stop after')
    terminate_after = params.get('Terminate after')

    if stop_after and terminate_after:
        if stop_after >= terminate_after:
            raise AssertionError(f"The '--stop-after' param should not be "
                                 f"equal or greater than '--terminate-after' "
                                 f"param value.")

    additional_param_names = {'cloud', 'tenantDisplayName'}
    request.parameters[ADDITIONAL_PARAMS_NAME] = {
        each: params.pop(each, None)
        for each in additional_param_names
    }
    request.parameters['actionName'] = 'Run Instance'
    request.parameters['quotaAction'] = True
    return request


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    return [response]
