import logging

from structlog import wrap_logger

from app.encrypt import encrypt_data
from app.publish import notify_dap
from app.store import write_to_bucket


logger = wrap_logger(logging.getLogger(__name__))


def deliver(file_bytes: bytes,
            filename: str,
            tx_id: str,
            dataset: str,
            description: str,
            iteration: str,
            directory: str):

    logger.info("encrypting")
    encrypted_payload = encrypt_data(file_bytes)

    logger.info("storing")
    write_to_bucket(file_bytes, filename=filename, directory=directory)

    logger.info("sending dap notification")
    notify_dap(data=encrypted_payload,
               filename=filename,
               tx_id=tx_id,
               dataset=dataset,
               description=description,
               iteration=iteration)
