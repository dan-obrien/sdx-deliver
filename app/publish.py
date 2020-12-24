import logging

from structlog import wrap_logger

from app import dap_publisher, dap_topic_path
import hashlib
import json
from datetime import datetime


logger = wrap_logger(logging.getLogger(__name__))


def notify_dap(data: str,
               filename: str,
               tx_id: str,
               dataset: str,
               description: str,
               iteration: str):

    data_bytes = data.encode("utf-8")
    message_str = create_dap_message(data_bytes,
                                     filename=filename,
                                     dataset=dataset,
                                     description=description,
                                     iteration=iteration)
    publish_data(message_str, tx_id, filename)


def publish_data(message_str: str, tx_id: str, filename: str):
    # Data must be a byte-string
    message = message_str.encode("utf-8")
    # When you publish a message, the client returns a future.
    future = dap_publisher.publish(dap_topic_path, message, tx_id=tx_id, filename=filename)
    logger.info(f"published message with tx_id={tx_id} to dap")
    return future.result()


def create_dap_message(data_bytes: bytes,
                       filename: str,
                       dataset: str,
                       description: str,
                       iteration: str) -> str:

    md5_hash = hashlib.md5(data_bytes).hexdigest()

    dap_message = {
        'version': '1',
        'files': [{
            'name': filename,
            'URL': f"http://sdx-store:5000/responses/{filename}",
            'sizeBytes': len(data_bytes),
            'md5sum': md5_hash
        }],
        'sensitivity': 'High',
        'sourceName': 'sdx-development',
        'manifestCreated': get_formatted_current_utc(),
        'description': description,
        'iterationL1': iteration,
        'dataset': dataset,
        'schemaversion': '1'
    }

    logger.info("Created dap data")
    str_dap_message = json.dumps(dap_message)
    return str_dap_message


def get_formatted_current_utc():
    """
    Returns a formatted utc date with only 3 milliseconds as opposed to the ususal 6 that python provides.
    Additionally, we provide the Zulu time indicator (Z) at the end to indicate it being UTC time. This is
    done for consistency with timestamps provided in other languages.
    The format the time is returned is YYYY-mm-ddTHH:MM:SS.fffZ (e.g., 2018-10-10T08:42:24.737Z)
    """
    date_time = datetime.utcnow()
    milliseconds = date_time.strftime("%f")[:3]
    return f"{date_time.strftime('%Y-%m-%dT%H:%M:%S')}.{milliseconds}Z"
