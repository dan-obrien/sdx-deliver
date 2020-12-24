import logging
from flask import request, jsonify
from structlog import wrap_logger

from app import app
from app.deliver import deliver

logger = wrap_logger(logging.getLogger(__name__))

DELIVER_NAME = 'zip'


@app.route('/deliver/dap', methods=['POST'])
def deliver_dap():
    dataset = request.args.get("survey_id")
    return process(dataset, "surveys")


@app.route('/deliver/survey', methods=['POST'])
def deliver_survey():
    return process("EDCSurvey", "surveys")


@app.route('/deliver/feedback', methods=['POST'])
def deliver_feedback():
    return process("EDCFeedback", "feedback")


@app.route('/deliver/comments', methods=['POST'])
def deliver_comments():
    return process("EDCComments", "comments")


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


def process(dataset, directory):
    try:
        logger.info(f"processing request")
        files = request.files
        file_bytes = files[DELIVER_NAME].read()
        logger.info(f"file_bytes: {file_bytes}")
        # filename = files[DELIVER_NAME].filename
        filename = request.args.get("filename")
        logger.info(f"filename: {filename}")
        tx_id = request.args.get("tx_id")
        logger.info(f"tx_id: {tx_id}")
        description = request.args.get("description")
        logger.info(f"description: {description}")
        iteration = request.args.get("iteration")
        logger.info(f"iteration: {iteration}")
        deliver(file_bytes=file_bytes,
                filename=filename,
                tx_id=tx_id,
                dataset=dataset,
                description=description,
                iteration=iteration,
                directory=directory)
        return jsonify(success=True)
    except Exception as e:
        return server_error(e)
