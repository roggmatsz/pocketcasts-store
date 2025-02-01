import sqlite3

class SQLiteStore():
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.db_connection = self.create_database()

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
        if not self.db_connection:
            print("Error: No Database connection.")
            return

        with self.db_connection:
            cursor = self.db_connection.cursor()
            cursor.execute(f'''
                SELECT Episode_UUID, URL, Published_Date, Duration, Title, Size, Is_Starred, Podcast_UUID, Podcast_Title, Author, Date_Saved
                FROM Listening_History
                ORDER BY Date_Saved DESC
                LIMIT {count}
            ''')
            return cursor.fetchall()

    def get_records_by_uuid(self, records: list) -> list:
        if not self.db_connection:
            print("Error: No Database connection.")
            return
        
        cursor = self.db_connection.cursor()
        cursor.execute(f'''
            SELECT Episode_UUID
            FROM Listening_History
            WHERE episode_uuid IN ({ ','.join(['?'] * len(records)) })
        ''', [ record['uuid'] for record in records ])
        
        return cursor.fetchall()

    def save_records(self, records: list[dict]) -> int:
        if not records:
            return 0
        
        if not self.db_connection:
            print("Error: No Database connection.")
            return
        
        cursor = self.db_connection.cursor()
        cursor.executemany('''
            INSERT INTO Listening_History (
                Episode_UUID,
                URL,
                Published_Date,
                Duration,
                Title,
                Size,
                Is_Starred,
                Podcast_UUID,
                Podcast_Title,
                Author
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', [(
                record['uuid'],
                record['url'],
                record['published'],
                record['duration'],
                record['title'],
                record['size'],
                record['starred'],
                record['podcastUuid'],
                record['podcastTitle'],
                record['author']
            ) for record in reversed(records)
        ])
        
        return len(records)