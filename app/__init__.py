import os
import gnupg
import structlog

from google.cloud import pubsub_v1, storage
from flask import Flask
from app.logger import logging_config
from app.secret_manager import get_secret


logging_config()
logger = structlog.get_logger()
project_id = os.getenv('PROJECT_ID', 'ons-sdx-sandbox')


class Config:

    def __init__(self, proj_id) -> None:
        self.PROJECT_ID = proj_id
        self.BUCKET_NAME = f'{proj_id}-outputs'
        self.BUCKET = None
        self.DAP_TOPIC_PATH = None
        self.DAP_PUBLISHER = None
        self.ENCRYPTION_KEY = None
        self.GPG = None
        if proj_id == "ons-sdx-preprod":
            data_sensitivity = "Low"
        else:
            data_sensitivity = "High"
        self.DATA_SENSITIVITY = data_sensitivity


CONFIG = Config(project_id)


def cloud_config():
    """
    The cloud_config method gives us control over GCP Connections. It can be omitted when these connections are not
    needed such as UnitTesting
    """
    logger.info("Loading Cloud Config")
    dap_publisher = pubsub_v1.PublisherClient()
    CONFIG.DAP_TOPIC_PATH = dap_publisher.topic_path(CONFIG.PROJECT_ID, "dap-topic")
    CONFIG.DAP_PUBLISHER = dap_publisher

    gpg = gnupg.GPG()
    encryption_key = get_secret(CONFIG.PROJECT_ID, 'dap-public-gpg')
    gpg.import_keys(encryption_key)
    CONFIG.ENCRYPTION_KEY = encryption_key
    CONFIG.GPG = gpg

    storage_client = storage.Client(CONFIG.PROJECT_ID)
    CONFIG.BUCKET = storage_client.bucket(CONFIG.BUCKET_NAME)


app = Flask(__name__)
from app import routes
