import json
import threading
import structlog

from flask import request, jsonify
from structlog.contextvars import bind_contextvars

from app import app
from app.deliver import deliver
from app.meta_wrapper import MetaWrapper

logger = structlog.get_logger()

ZIP_FILE = 'zip'
SUBMISSION_FILE = 'submission'
TRANSFORMED_FILE = 'transformed'
METADATA_FILE = 'metadata'
SEFT_FILE = 'seft'


@app.route('/deliver/dap', methods=['POST'])
def deliver_dap():
    """
    Endpoint for submissions only intended for DAP. POST request requires the submission JSON to be uploaded as "submission" and
    the filename passed in the query parameters.
    """
    logger.info('Processing DAP submission')
    filename = request.args.get("filename")
    meta = MetaWrapper(filename)
    files = request.files
    submission_bytes = files[SUBMISSION_FILE].read()
    survey_dict = json.loads(submission_bytes.decode())
    data_bytes = submission_bytes
    meta.set_dap(survey_dict, data_bytes)
    return process(meta, data_bytes)


@app.route('/deliver/legacy', methods=['POST'])
def deliver_legacy():
    """
    Endpoint for submissions intended for legacy systems. POST request requires the submission JSON to be uploaded as
    "submission", the zipped transformed artifact as "transformed", and the filename passed in the query
    parameters.
    """
    logger.info('Processing Legacy submission')
    filename = request.args.get("filename")
    meta = MetaWrapper(filename)
    files = request.files
    submission_bytes = files[SUBMISSION_FILE].read()
    survey_dict = json.loads(submission_bytes.decode())
    data_bytes = files[TRANSFORMED_FILE].read()
    meta.set_legacy(survey_dict, data_bytes)
    return process(meta, data_bytes)


@app.route('/deliver/feedback', methods=['POST'])
def deliver_feedback():
    """
    Endpoint for feedback submissions only. POST request requires the feedback JSON to be uploaded as
    "submission", and the filename passed in the query parameters.
    """
    logger.info('Processing Feedback submission')
    filename = request.args.get("filename")
    meta = MetaWrapper(filename)
    files = request.files
    submission_bytes = files[SUBMISSION_FILE].read()
    survey_dict = json.loads(submission_bytes.decode())
    data_bytes = survey_dict
    meta.set_feedback(survey_dict, data_bytes)
    return process(meta, data_bytes)


@app.route('/deliver/comments', methods=['POST'])
def deliver_comments():
    """
    Endpoint for delivering daily comment report. POST request requires the zipped up comments to be uploaded as
    "zip", and the filename passed in the query parameters.
    """
    logger.info('Processing Comments submission')
    filename = request.args.get("filename")
    meta = MetaWrapper(filename)
    files = request.files
    data_bytes = files[ZIP_FILE].read()
    meta.set_comments(data_bytes)
    return process(meta, data_bytes)


@app.route('/deliver/seft', methods=['POST'])
def deliver_seft():
    """
    Endpoint for delivering SEFT submissions. POST request requires the encrypted SEFT to be uploaded as
    "seft", metadata JSON as "metadata", and the filename passed in the query parameters.
    Metadata file is required to provide information about the submissions to construct the PubSub message.
    """
    logger.info('Processing SEFT submission')
    filename = request.args.get("filename")
    meta = MetaWrapper(filename)
    files = request.files
    meta_bytes = files[METADATA_FILE].read()
    meta_dict = json.loads(meta_bytes.decode())
    data_bytes = files[SEFT_FILE].read()
    meta.set_seft(meta_dict)
    return process(meta, data_bytes)


@app.errorhandler(500)
def server_error(error=None):
    logger.error("Server error", error=repr(error))
    message = {
        'status': 500,
        'message': "Internal server error: " + repr(error),
    }
    resp = jsonify(message)
    resp.status_code = 500
    return resp


def process(meta_data: MetaWrapper, data_bytes: bytes) -> str:
    """
    Binds submission data to logger and begins deliver process
    """
    try:
        bind_contextvars(app="SDX-Deliver")
        bind_contextvars(tx_id=meta_data.tx_id)
        bind_contextvars(survey_id=meta_data.survey_id)
        bind_contextvars(output_type=meta_data.output_type)
        bind_contextvars(thread=threading.currentThread().getName())
        logger.info("Processing request")
        deliver(meta_data, data_bytes)
        logger.info("Process completed successfully")
        return jsonify(success=True)
    except Exception as e:
        return server_error(e)
