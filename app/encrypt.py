import structlog
from app import CONFIG

logger = structlog.get_logger()

DAP_RECIPIENT = 'dap@ons.gov.uk'


def encrypt_output(data_bytes: bytes) -> str:
    """
    Encrypts data using DAP public key (GPG)
    """

    encrypted_data = CONFIG.GPG.encrypt(data_bytes, recipients=[DAP_RECIPIENT], always_trust=True)

    if encrypted_data.ok:
        logger.info("Successfully encrypted output")
    else:
        logger.error("Failed to encrypt output")
        logger.error(encrypted_data.status)

    return str(encrypted_data)
