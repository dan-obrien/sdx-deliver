import structlog

from app import CONFIG
from app.output_type import OutputType

logger = structlog.get_logger()


dir_dict = {OutputType.DAP: "dap",
            OutputType.LEGACY: "survey",
            OutputType.HYBRID: "survey",
            OutputType.FEEDBACK: "feedback",
            OutputType.COMMENTS: "comments",
            OutputType.SEFT: "seft"}


def write_to_bucket(data: str, filename: str, output_type: OutputType) -> str:
    """
    Uploads a string submission to the correct folder within the GCP outputs bucket.
    """
    logger.info("Uploading to bucket")
    directory = dir_dict.get(output_type)
    # remove destination suffix
    name = filename.split(":")[0]
    path = f"{directory}/{name}"
    logger.info(f"Storing as {path}")
    blob = CONFIG.BUCKET.blob(path)
    blob.upload_from_string(data)
    logger.info(f"Successfully uploaded: {filename} to {directory}")
    return path
