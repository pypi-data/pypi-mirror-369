import base64
import json
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

UTF_8 = 'utf-8'


class AESCipherService(object):

    def __init__(self, key):
        self.key = key.encode() if key else None
        self.backend = default_backend()
        self.iv = os.urandom(12)

    def encrypt(self, data):
        """
        Encrypt data, add initialization vector ("iv") at beginning of encrypted
        message and encode entire data in Base64 format
        """
        iv = self.iv
        plain_text = data if isinstance(data, str) else json.dumps(data)
        data_in_bytes = plain_text.encode(UTF_8)
        try:
            cipher = AESGCM(key=self.key)
        except ValueError as e:
            raise ValueError(str(e).replace('AESGCM key', 'Secret Key'))
        encrypted_data = cipher.encrypt(
            nonce=iv, data=data_in_bytes, associated_data=None)
        encrypted_data_with_iv = bytes(iv) + encrypted_data
        base64_request = base64.b64encode(encrypted_data_with_iv)
        return base64_request.decode(UTF_8)

    def decrypt(self, data):
        """
        Decode received message from Base64 format, cut initialization
        vector ("iv") from beginning of the message, decrypt message
        """
        decoded_data = base64.b64decode(data)
        iv = decoded_data[:12]
        encrypted_data = decoded_data[12:]
        cipher = Cipher(
            algorithms.AES(key=self.key),
            modes.GCM(initialization_vector=iv)
        ).decryptor()
        origin_data_with_iv = cipher.update(encrypted_data)
        return origin_data_with_iv
