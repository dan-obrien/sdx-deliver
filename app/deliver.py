import logging

from structlog import wrap_logger

from app.encrypt import encrypt_output
from app.output_type import OutputType
from app.publish import send_message
from app.store import write_to_bucket


logger = wrap_logger(logging.getLogger(__name__))


def deliver(filename: str, data_bytes: bytes, survey_dict: dict, output_type: OutputType):

    logger.info("encrypting")
    encrypted_output = encrypt_output(data_bytes)

    logger.info("storing")
    path = write_to_bucket(encrypted_output, filename=filename, output_type=output_type)

    logger.info("sending dap notification")
    send_message(encrypted_output.encode(), filename, path, survey_dict, output_type)
