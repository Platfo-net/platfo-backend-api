import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from tenacity import (after_log, before_log, retry, stop_after_attempt,
                      wait_fixed)

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init() -> None:
    try:
        url = "postgresql://{}:{}@{}:{}/{}".format(
            settings.POSTGRES_USER,
            settings.POSTGRES_PASSWORD,
            settings.DB_HOST,
            settings.DB_PORT,
            settings.POSTGRES_DB
        )
        engine = create_engine(url, pool_pre_ping=True)
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = Session()
        # Try to create session to check if DB is awake
        db.execute(text('SELECT 1'))
    except Exception as e:
        logger.error(e)
        raise e


def main() -> None:
    logger.info('Initializing service')
    init()
    logger.info('Service finished initializing')


if __name__ == '__main__':
    main()
