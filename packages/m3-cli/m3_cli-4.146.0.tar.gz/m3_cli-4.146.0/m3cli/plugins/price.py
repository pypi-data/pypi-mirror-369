import json

SUPPORTED_PRICE_MODEL_TYPES = ['instancePriceModel',
                               'storagePriceModel',
                               'machineImagePriceModel',
                               'checkpointPriceModel']


def create_custom_request(request):
    params = request.parameters

    inactive = params.get('inactive')
    is_resource_state_active = False if inactive else True
    params['isResourceStateActive'] = is_resource_state_active
    params['zoneName'] = params.pop('region')

    date_from = params.get('from')
    date_to = params.get('to')
    if not date_from and date_to or not date_to and date_from:
        raise AssertionError('Both from and to parameters should be specified'
                             ' if at least one of them specified')
    return request


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response

    result = {}
    price_model = response.get('priceModel')
    for price_model_type, data in price_model.items():
        if price_model_type not in SUPPORTED_PRICE_MODEL_TYPES or not data:
            continue

        if price_model_type == 'instancePriceModel':
            entries = data.get('entries')
            if not entries:
                continue

            entries = sorted(entries,
                             key=lambda k: (k['osType'], k['totalPrice']),
                             reverse=True)
            result[price_model_type] = entries
        else:
            result[price_model_type] = data
    return result
