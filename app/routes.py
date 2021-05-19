import json
import threading
import structlog

from structlog.contextvars import bind_contextvars
from fastapi import File, UploadFile, HTTPException
from app import app
from app.deliver import deliver
from app.meta_wrapper import MetaWrapper
logger = structlog.get_logger()

ZIP_FILE = 'zip'
SUBMISSION_FILE = 'submission'
TRANSFORMED_FILE = 'transformed'
METADATA_FILE = 'metadata'
SEFT_FILE = 'seft'


@app.post('/deliver/legacy')
async def deliver_legacy(filename: str,
                         transformed: UploadFile = File(...),
                         submission: UploadFile = File(...)
                         ):
    """
    Endpoint for submissions intended for legacy systems. POST request requires the submission JSON to be uploaded as
    "submission", the zipped transformed artifact as "transformed", and the filename passed in the query
    parameters.
    """
    logger.info('Processing Legacy submission')
    meta = MetaWrapper(filename)
    submission_bytes = submission.file.read()
    survey_dict = json.loads(submission_bytes.decode())
    data_bytes = transformed.file.read()
    meta.set_legacy(survey_dict, data_bytes)
    return process(meta, data_bytes)


@app.post('/deliver/dap')
def deliver_dap(filename: str, submission: UploadFile = File(...)):
    """
    Endpoint for submissions only intended for DAP. POST request requires the submission JSON to be uploaded
    as "submission" and the filename passed in the query parameters.
    """
    logger.info('Processing DAP submission')
    meta = MetaWrapper(filename)
    submission_bytes = submission.file.read()
    survey_dict = json.loads(submission_bytes.decode())
    data_bytes = submission_bytes
    meta.set_dap(survey_dict, data_bytes)
    return process(meta, data_bytes)


@app.post('/deliver/hybrid')
def deliver_hybrid(filename: str,
                   transformed: UploadFile = File(...),
                   submission: UploadFile = File(...)):
    """
    Endpoint for submissions intended for dap and legacy systems. POST request requires the submission JSON to be
    uploaded as "submission", the zipped transformed artifact as "transformed", and the filename passed in the
    query parameters.
    """
    logger.info('Processing Hybrid submission')
    meta = MetaWrapper(filename)
    submission_bytes = submission.file.read()
    survey_dict = json.loads(submission_bytes.decode())
    data_bytes = transformed.file.read()
    meta.set_hybrid(survey_dict, data_bytes)
    return process(meta, data_bytes)


@app.post('/deliver/feedback')
def deliver_feedback(filename: str,
                     submission: UploadFile = File(...)):
    """
    Endpoint for feedback submissions only. POST request requires the feedback JSON to be uploaded as
    "submission", and the filename passed in the query parameters.
    """
    logger.info('Processing Feedback submission')
    meta = MetaWrapper(filename)
    submission_bytes = submission.file.read()
    survey_dict = json.loads(submission_bytes.decode())
    data_bytes = submission_bytes
    meta.set_feedback(survey_dict, data_bytes)
    return process(meta, data_bytes)


@app.post('/deliver/comments')
def deliver_comments(filename: str,
                     zip: UploadFile = File(...)):
    """
    Endpoint for delivering daily comment report. POST request requires the zipped up comments to be uploaded as
    "zip", and the filename passed in the query parameters.
    """
    logger.info('Processing Comments submission')
    meta = MetaWrapper(filename)
    data_bytes = zip.file.read()
    meta.set_comments(data_bytes)
    return process(meta, data_bytes)


@app.post('/deliver/seft')
def deliver_seft(filename: str,
                 metadata: UploadFile = File(...),
                 seft: UploadFile = File(...)):
    """
    Endpoint for delivering SEFT submissions. POST request requires the encrypted SEFT to be uploaded as
    "seft", metadata JSON as "metadata", and the filename passed in the query parameters.
    Metadata file is required to provide information about the submissions to construct the PubSub message.
    """
    logger.info('Processing SEFT submission')

    meta = MetaWrapper(filename)
    metadata_bytes = metadata.file.read()
    meta_dict = json.loads(metadata_bytes.decode())
    data_bytes = seft.file.read()
    meta.set_seft(meta_dict)
    return process(meta, data_bytes)


@app.get('/healthcheck')
def healthcheck():
    return {'status': 'OK'}


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
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
