from app import app, cloud_config
import structlog

logger = structlog.get_logger()

if __name__ == '__main__':
    logger.info('Starting SDX Deliver')
    cloud_config()
    app.run(debug=True, host='0.0.0.0', port=5000)
