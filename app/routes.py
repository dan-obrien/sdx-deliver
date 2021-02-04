import json
import logging
from flask import request, jsonify
from structlog import wrap_logger

from app import app
from app.deliver import deliver
from app.output_type import OutputType

logger = wrap_logger(logging.getLogger(__name__))

ZIP_FILE = 'zip'
SUBMISSION_FILE = 'submission'
TRANSFORMED_FILE = 'transformed'


@app.route('/deliver/dap', methods=['POST'])
def deliver_dap():
    return process(OutputType.DAP)


@app.route('/deliver/legacy', methods=['POST'])
def deliver_legacy():
    return process(OutputType.LEGACY)


@app.route('/deliver/feedback', methods=['POST'])
def deliver_feedback():
    return process(OutputType.FEEDBACK)


@app.route('/deliver/comments', methods=['POST'])
def deliver_comments():
    return process(OutputType.COMMENTS)


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


def process(output_type: OutputType) -> str:
    try:
        logger.info(f"processing request")
        files = request.files

        submission_bytes = b""
        survey_dict = {}

        if not output_type == OutputType.COMMENTS:
            submission_bytes = files[SUBMISSION_FILE].read()
            survey_dict = json.loads(submission_bytes.decode())

        if output_type == OutputType.DAP or output_type == OutputType.FEEDBACK:
            data_bytes = submission_bytes

        elif output_type == OutputType.COMMENTS:
            logger.info('Reading comments')
            data_bytes = files[ZIP_FILE].read()

        else:
            logger.info('else')
            data_bytes = files[TRANSFORMED_FILE].read()

        filename = request.args.get("filename")
        logger.info(f"filename: {filename}")

        deliver(filename=filename,
                data_bytes=data_bytes,
                survey_dict=survey_dict,
                output_type=output_type)

        return jsonify(success=True)
    except Exception as e:
        return server_error(e)
