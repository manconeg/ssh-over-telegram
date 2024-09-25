import logging
import os

import paramiko
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from paramiko.ssh_exception import BadHostKeyException, SSHException

PUBLIC_KEY = 'public.key'
PRIVATE_KEY = 'private.key'
logger = logging.getLogger()


def get_public_save_private_key(path_to_keys):
    key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=65537,
        key_size=2048
    )

    public_key = key.public_key().public_bytes(
        crypto_serialization.Encoding.OpenSSH,
        crypto_serialization.PublicFormat.OpenSSH
    )

    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.TraditionalOpenSSL,
        crypto_serialization.NoEncryption())

    with open(path_to_keys + PUBLIC_KEY, 'wb') as f:
        f.write(public_key)

    with open(path_to_keys + PRIVATE_KEY, 'wb') as f:
        f.write(private_key)

    # Set read and write permission for user only
    os.chmod(path_to_keys + PUBLIC_KEY, 0o0600)
    os.chmod(path_to_keys + PRIVATE_KEY, 0o0600)

    return public_key


def get_client(connection_info) -> paramiko.SSHClient:
    username, hostname, port, path_to_keys = connection_info
    if not os.path.exists(path_to_keys):
        os.mkdir(path_to_keys)
    key_path = path_to_keys + PRIVATE_KEY
    if not os.path.exists(key_path):
        raise Exception(f'No keys at: {key_path}')
    client = paramiko.SSHClient()

    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # TODO change it in future updates

    try:
        client.connect(username=username, hostname=hostname, port=port, key_filename=key_path, allow_agent=False, look_for_keys=False)
    except (BadHostKeyException, SSHException):
        raise Exception(f'Cannot establish connection: {key_path}')
    return client
