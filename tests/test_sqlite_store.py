import pytest
from src.sqlite_store import SQLiteStore

def test_sqlite_store():
    store = SQLiteStore(':memory:')
    cursor = store.db_connection.cursor()

    cursor.execute(f'PRAGMA table_info(Listening_History)')
    columns = cursor.fetchall()

    # column[1] contains the string names of the columns in the table.
    column_names = [ column[1] for column in columns ]
    assert len(column_names) == 12