import sqlite3

class SQLiteStore():
    def __init__(self, db_path: str):
        pass

    def create_database(self) -> sqlite3.Connection:
        pass

    def get_records(self, count=100) -> list:
        pass

    def get_records_by_uuid(self, uuids: list) -> list:
        pass

    def save_records(self, records: list[dict]) -> int:
        pass