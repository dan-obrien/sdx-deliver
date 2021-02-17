import structlog

from app.encrypt import encrypt_output
from app.meta_wrapper import MetaWrapper
from app.output_type import OutputType
from app.publish import send_message
from app.store import write_to_bucket

logger = structlog.get_logger()


def deliver(meta_data: MetaWrapper, data_bytes: bytes):
    if meta_data.output_type == OutputType.SEFT:
        encrypted_output = data_bytes
    else:
        logger.info("encrypting")
        encrypted_output = encrypt_output(data_bytes)

    logger.info("storing")
    path = write_to_bucket(encrypted_output, filename=meta_data.filename, output_type=meta_data.output_type)

    logger.info("sending dap notification")
    send_message(meta_data, path)
