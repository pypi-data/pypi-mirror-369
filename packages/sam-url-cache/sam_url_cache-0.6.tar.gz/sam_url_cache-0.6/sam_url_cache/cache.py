import sqlite3
import logging
import os
from datetime import date

CACHE_DEFINITION = """
CREATE TABLE IF NOT EXISTS cache (
    URL TEXT PRIMARY KEY,
    LAST_UPDATED TEXT NOT NULL,
    BLOB TEXT NOT NULL
);
"""

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, 
    format='%(levelname)s: %(name)s: %(message)s'
)

class _URLCacheDB:
    def __init__(self, database_path) -> None:
        os.makedirs(os.path.dirname(database_path), exist_ok=True)
        self.connection = sqlite3.connect(database_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self._ensure_table()

    def _ensure_table(self) -> None:
        self.cursor.execute(CACHE_DEFINITION)
        self.connection.commit()
        logger.info("Cache started.")

    def put(self, url: str, text: str) -> None:
        query = "INSERT OR REPLACE INTO cache (URL, LAST_UPDATED, BLOB) VALUES (?, ?, ?)"
        last_updated = date.today().strftime("%Y-%m-%d")
        try:
            self.cursor.execute(query, (url, last_updated, text))
            self.connection.commit()
            logger.info(f"Cache Miss. Added: {url}")
        except Exception:
            logger.exception(f"Error putting: {url}")
            raise

    def get(self, url: str) -> str | None:
        query = "SELECT BLOB FROM cache WHERE URL = ?"
        try:
            self.cursor.execute(query, (url,))
            result = self.cursor.fetchone()
            logger.info(f"Cache Hit: {url}")
            if result is None:
                logger.info(f"Cache Miss: {url}")
                return None
            else:
                logger.info(f"Cache Hit: {url}")
                return result[0]
        except Exception:
            logger.exception(f"Error getting: {url}")
            raise

if __name__ == "__main__":
    raise RuntimeError("Do not run this directly.")