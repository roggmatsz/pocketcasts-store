import sqlite3

class SQLiteStore():
    def __init__(self, db_name: str):
        self.db_name = db_name
        return self.create_database()

    def create_database(self) -> sqlite3.Connection:
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS Listening_History (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Episode_UUID TEXT NOT NULL,
                    URL TEXT NOT NULL,
                    Published_Date TEXT NOT NULL,
                    Duration INTEGER,
                    Title TEXT NOT NULL,
                    Size INTEGER NOT NULL,
                    Is_Starred BOOLEAN DEFAULT 0 CHECK (Is_Starred IN (0, 1)),
                    Podcast_UUID TEXT NOT NULL,
                    Podcast_Title TEXT NOT NULL,
                    Author TEXT NOT NULL,
                    Date_Saved DATETIME DEFAULT CURRENT_TIMESTAMP)
            ''')
        return connection

    def get_records(self, count=100) -> list:
        pass

    def get_records_by_uuid(self, uuids: list) -> list:
        pass

    def save_records(self, records: list[dict]) -> int:
        pass