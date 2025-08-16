"""The custom logic for the command m3 describe-platform-services."""
from operator import xor, or_


def create_custom_request(request):
    params = request.parameters
    service_name = bool(params.get('serviceName'))
    cloud = bool(params.get('cloud'))
    tenant_name = bool(params.get('tenantName'))

    if not xor(service_name, (or_(cloud, tenant_name))):
        raise AssertionError(
            "Specify only one of the following groups of the parameters: "
            "1. '--cloud' and '--tenant'; 2. '--service' ")

    if xor(cloud, tenant_name):
        raise AssertionError(
            "The '--cloud' and '--tenant' parameters are required if "
            "'--service' is empty and vice versa")

    return request
