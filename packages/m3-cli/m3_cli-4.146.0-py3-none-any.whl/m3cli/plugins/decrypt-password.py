import base64
import json

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding


def create_custom_request(request):
    params = request.parameters
    region = params['region']
    cloud = region.split('-')[0]
    if cloud not in ['AWS', 'GCP', 'GGL']:
        raise AssertionError('It is possible to decrypt password just'
                             ' for AWS and GOOGLE instances')
    if cloud == 'GCP' or cloud == 'GGL':
        availability_zone = params.get('availabilityZone')
        if not availability_zone:
            raise AssertionError(
                'Parameter availability-zone is required for GOOGLE cloud')
        params['availabilityZone'] = availability_zone
    return request


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response

    encrypted_password = response['password']

    params = request.parameters
    file_path = params.pop('privatePart')
    with open(file_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    rec_data = base64.b64decode(encrypted_password)

    region = params['region']
    cloud = region.split('-')[0]
    if cloud == 'GCP' or cloud == 'GGL':
        decrypted_password = private_key.decrypt(rec_data, padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(), label=None))
    else:
        decrypted_password = private_key.decrypt(
            rec_data,
            padding.PKCS1v15()
        )
    password_string = decrypted_password.decode("utf-8")
    return {"decrypted_password": password_string}
