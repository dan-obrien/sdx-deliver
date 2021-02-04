import logging
from structlog import wrap_logger

from app import gpg

logger = wrap_logger(logging.getLogger(__name__))

DAP_RECIPIENT = 'dap@ons.gov.uk'


def encrypt_output(data_bytes: bytes) -> str:

    encrypted_data = gpg.encrypt(data_bytes, recipients=[DAP_RECIPIENT], always_trust=True)

    if encrypted_data.ok:
        logger.info("successfully encrypted output")
    else:
        logger.info("failed to encrypt output")
        logger.info(encrypted_data.status)

    return str(encrypted_data)
