from app.db.sqlite.config import SQLitePlate
from app.db.abstract_plate import DatabasePlate


class BackendConfig:
    def __init__(self):
        self.db: DatabasePlate = SQLitePlate()
        self.auth = None
