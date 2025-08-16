"""
The custom logic for the command m3 add-service-section.
"""
from m3cli.utils.utilities import load_file_contents


def create_custom_request(request):
    parameters = request.parameters
    if not (('blockValue' in parameters)
            ^ ('blockValuePath' in parameters)):
        raise AssertionError(
            "One of the 'block-value' and 'block-value-path' "
            "parameters must be specified")
    if 'blockValuePath' in parameters:
        filepath = parameters.pop('blockValuePath')
        block_value = load_file_contents(filepath)
        parameters['blockValue'] = block_value
    return request
