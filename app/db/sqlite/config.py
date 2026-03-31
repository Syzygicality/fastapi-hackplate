import sqlite3
from pathlib import Path


class SQLiteConfig:
    def __init__(self, path: str = "db.sqlite3"):
        self.path = Path(path)
        self.conn: sqlite3.Connection | None = None

    def connect(self) -> None:
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def disconnect(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

    def cursor(self) -> sqlite3.Cursor:
        if self.conn is None:
            raise RuntimeError("SQLiteDB is not connected")
        return self.conn.cursor()
