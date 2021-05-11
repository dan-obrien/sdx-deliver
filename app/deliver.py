import hashlib

import structlog

from app.encrypt import encrypt_output
from app.meta_wrapper import MetaWrapper
from app.output_type import OutputType
from app.publish import send_message
from app.store import write_to_bucket

logger = structlog.get_logger()


def deliver(meta_data: MetaWrapper, data_bytes: bytes):
    """
    Encrypts any unencrypted data, writes to the appropriate location within the outputs GCP bucket and notifies DAP
    via PubSub
    """
    if meta_data.output_type == OutputType.SEFT:
        encrypted_output = data_bytes
    else:
        logger.info("Encrypting output")
        encrypted_output = encrypt_output(data_bytes)
        encrypted_bytes = encrypted_output.encode()
        meta_data.md5sum = hashlib.md5(encrypted_bytes).hexdigest()
        meta_data.sizeBytes = len(encrypted_bytes)

    logger.info("Storing to bucket")
    path = write_to_bucket(encrypted_output, filename=meta_data.filename, output_type=meta_data.output_type)

    logger.info("Sending DAP notification")
    send_message(meta_data, path)
