import structlog
import uvicorn

from app import app

logger = structlog.get_logger()


if __name__ == '__main__':
    logger.info('Starting SDX Deliver')
    uvicorn.run(app, host="0.0.0.0", port=5000)
