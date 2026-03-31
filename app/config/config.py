from app.db.sqlite.config import SQLiteConfig


class BackendConfig:
    def __init__(self):
        self.db = SQLiteConfig()
        self.auth = None
