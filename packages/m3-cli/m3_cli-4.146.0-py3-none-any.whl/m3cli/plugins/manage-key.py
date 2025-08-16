"""
The custom logic for the command m3 manage-key
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""


def create_custom_request(request):
    params = request.parameters
    if params.get('region') and params.get('allRegions'):
        raise AssertionError('The --region parameter cannot be passed '
                             'along with the --all-region flag')

    if not params.get('region') and not params.get('allRegions'):
        raise AssertionError('Please specified one of the following '
                             'parameters: --region or --all-region')
    # Todo Refactor loop. Make request assembly
    final_params = request.parameters.copy()
    if params.get('region'):
        regions = params.get('region')
        final_params['keys'] = []
        for region in regions:
            final_params['keys'].append(
                {
                    "tenantName": params.get('tenantName'),
                    "state": params.get('state'),
                    "cloud": params.get('cloud'),
                    "region": region,
                })
        del final_params['tenantName']
        del final_params['state']
        del final_params['cloud']
        del final_params['region']
    else:
        final_params['keys'] = [{
            "tenantName": final_params.pop('tenantName'),
            "state": final_params.pop('state'),
            "cloud": final_params.pop('cloud')
        }]

    request.parameters = final_params
    return request
