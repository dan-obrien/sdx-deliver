import logging

from structlog import wrap_logger

from app import dap_publisher, dap_topic_path, BUCKET_NAME, PROJECT_ID
import hashlib
import json
from datetime import datetime

from app.output_type import OutputType

logger = wrap_logger(logging.getLogger(__name__))


def send_message(data_bytes: bytes,
                 filename: str,
                 path: str,
                 survey_dict: dict,
                 output_type: OutputType):

    if output_type == OutputType.COMMENTS:
        tx_id = filename
        description = "Comments zip"
        dataset = "comments"
        message_str = create_message_data(data_bytes=data_bytes,
                                          filename=filename,
                                          description=description,
                                          dataset=dataset)
    else:
        tx_id = survey_dict['tx_id']
        description = get_description(survey_dict)
        dataset = survey_dict['survey_id']
        iteration1 = survey_dict['collection']['period']
        iteration2 = None

        if output_type == OutputType.FEEDBACK:
            iteration2 = "feedback"

        message_str = create_message_data(data_bytes=data_bytes,
                                          filename=filename,
                                          description=description,
                                          dataset=dataset,
                                          iteration1=iteration1,
                                          iteration2=iteration2)

    publish_data(message_str, tx_id, path)


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


def create_message_data(data_bytes: bytes,
                        filename: str,
                        description: str,
                        dataset: str,
                        iteration1: str = None,
                        iteration2: str = None) -> str:

    md5_hash = hashlib.md5(data_bytes).hexdigest()

    message_data = {
        'version': '1',
        'files': [{
            'name': filename,
            'sizeBytes': len(data_bytes),
            'md5sum': md5_hash
        }],
        'sensitivity': 'High',
        'sourceName': PROJECT_ID,
        'manifestCreated': get_formatted_current_utc(),
        'description': description,
        'iterationL1': iteration1,
        'dataset': dataset,
        'schemaversion': '1'
    }

    if iteration1 is not None:
        message_data['iterationL1'] = iteration1

    if iteration2 is not None:
        message_data['iterationL2'] = iteration2

    logger.info("Created dap data")
    str_dap_message = json.dumps(message_data)
    return str_dap_message


def get_description(survey_dict: dict) -> str:
    return "{} survey response for period {} sample unit {}".format(
        survey_dict['survey_id'],
        survey_dict['collection']['period'],
        survey_dict['metadata']['ru_ref']
    )


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
