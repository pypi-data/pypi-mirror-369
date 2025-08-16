"""The custom logic for the command m3 delete-storage."""


def create_custom_request(request):
    params = request.parameters
    region = params['region']
    cloud = region.split('-')[0]

    additional_params = {}
    if cloud == 'GCP' or cloud == 'GGL':
        availability_zone = params.get('availabilityZone')
        if not availability_zone:
            raise AssertionError(
                'Parameter availability-zone is required for GOOGLE cloud')
        additional_params['availabilityZone'] = availability_zone
    params['params'] = additional_params

    return request


def create_custom_response(request, response):
    return 'The specified volume was successfully deleted' \
        if response == 'null' else response
