def create_custom_response(request, response):
    return 'Instance termination protection state was successfully changed' \
        if response == 'null' else response
