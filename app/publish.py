import structlog

from app import dap_publisher, dap_topic_path, BUCKET_NAME, PROJECT_ID
import json
from datetime import datetime
from app.meta_wrapper import MetaWrapper
from app.output_type import OutputType

logger = structlog.get_logger()


def send_message(meta_data: MetaWrapper, path: str):
    message_str = create_message_data(meta_data)
    publish_data(message_str, meta_data.tx_id, path)


def create_message_data(meta_data: MetaWrapper) -> str:
    if meta_data.output_type == OutputType.COMMENTS:
        dataset = "comments"
        iteration1 = None
    else:
        dataset = meta_data.survey_id
        iteration1 = meta_data.period

    message_data = {
        'version': '1',
        'files': [{
            'name': meta_data.filename,
            'sizeBytes': meta_data.sizeBytes,
            'md5sum': meta_data.md5sum
        }],
        'sensitivity': 'High',
        'sourceName': PROJECT_ID,
        'manifestCreated': get_formatted_current_utc(),
        'description': meta_data.get_description(),
        'dataset': dataset,
        'schemaversion': '1'
    }

    if iteration1 is not None:
        message_data['iterationL1'] = iteration1

    if meta_data.output_type == OutputType.FEEDBACK:
        message_data['iterationL2'] = "feedback"

    logger.info("Created dap data")
    str_dap_message = json.dumps(message_data)
    return str_dap_message


def get_formatted_current_utc():
    """
    Returns a formatted utc date with only 3 milliseconds as opposed to the usual 6 that python provides.
    Additionally, we provide the Zulu time indicator (Z) at the end to indicate it being UTC time. This is
    done for consistency with timestamps provided in other languages.
    The format the time is returned is YYYY-mm-ddTHH:MM:SS.fffZ (e.g., 2018-10-10T08:42:24.737Z)
    """
    date_time = datetime.utcnow()
    milliseconds = date_time.strftime("%f")[:3]
    return f"{date_time.strftime('%Y-%m-%dT%H:%M:%S')}.{milliseconds}Z"


def publish_data(message_str: str, tx_id: str, path: str):
    # Data must be a byte-string
    message = message_str.encode("utf-8")
    attributes = {
        'gcs.bucket': BUCKET_NAME,
        'gcs.key': path,
        'tx_id': tx_id
    }
    future = dap_publisher.publish(dap_topic_path, message, **attributes)
    logger.info(f"published message with tx_id={tx_id} to dap")
    return future.result()
