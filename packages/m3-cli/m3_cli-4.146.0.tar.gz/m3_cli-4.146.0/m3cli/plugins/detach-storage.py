def create_custom_response(request, response):
    return 'The specified volume was detached successfully' \
        if response == 'null' else response
