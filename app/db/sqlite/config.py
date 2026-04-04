import aiosqlite
import logging
from pathlib import Path
from pydantic_settings import BaseSettings

from app.db.abstract_plate import DatabasePlate

logger = logging.getLogger(__name__)


class SQLiteConfig(BaseSettings):
    db_path: str = "db.sqlite3"


class SQLitePlate(DatabasePlate):
    def __init__(self):
        self.config = SQLiteConfig()
        self.conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        logger.info("Connecting to sqlite file...")
        resolved = str(Path(self.config.db_path).resolve())
        self.conn = await aiosqlite.connect(resolved)
        self.conn.row_factory = aiosqlite.Row

    async def disconnect(self) -> None:
        if self.conn:
            logger.info("Disconnecting from sqlite file...")
            await self.conn.close()
            self.conn = None

    async def ping(self) -> bool:
        if self.conn is None:
            logger.warning("Ping failed, connection is None")
            return False
        try:
            await self.conn.execute("SELECT 1")
            logger.info("PONG")
            return True
        except Exception:
            logger.exception("Ping failed")
            return False

    async def get_session(self):
        return self.conn
