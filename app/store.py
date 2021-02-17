import structlog

from google.cloud import storage
from app import PROJECT_ID, BUCKET_NAME
from app.output_type import OutputType

logger = structlog.get_logger()


def write_to_bucket(data: str, filename: str, output_type: OutputType) -> str:
    """Uploads a string to the bucket."""
    directory = {OutputType.DAP: "dap",
                 OutputType.LEGACY: "survey",
                 OutputType.FEEDBACK: "feedback",
                 OutputType.COMMENTS: "comments",
                 OutputType.SEFT: "seft"}.get(output_type)

    path = f"{directory}/{filename}"
    storage_client = storage.Client(PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(path)
    blob.upload_from_string(data)
    logger.info(f"Successfully uploaded: {filename} to {directory}")
    return path
