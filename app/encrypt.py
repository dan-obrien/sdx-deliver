import logging

# import yaml
# from sdc.crypto.key_store import KeyStore
# from sdc.crypto.encrypter import encrypt
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))

KEY_PURPOSE_SUBMISSION = 'submission'


def encrypt_data(data: bytes) -> str:
    # data_str = str(data)
    # with open("./keys.yml") as file:
    #     secrets_from_file = yaml.safe_load(file)
    # key_store = KeyStore(secrets_from_file)
    # encrypted_payload = encrypt(data_str, key_store, KEY_PURPOSE_SUBMISSION)
    # logger.info("successfully encrypted payload")
    encrypted_payload = str(data)
    print(encrypted_payload)
    return encrypted_payload
