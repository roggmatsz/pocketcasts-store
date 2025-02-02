import pytest

from src.sqlite_store import SQLiteStore

@pytest.fixture
def data_store():
    store = SQLiteStore(':memory:')
    yield store
    store.close()
    

def test_table_creation(data_store):
    cursor = data_store.db_connection.cursor()

    cursor.execute(f'PRAGMA table_info(Listening_History)')
    columns = cursor.fetchall()

    # column[1] contains the string names of the columns in the table.
    column_names = [ column[1] for column in columns ]
    assert len(column_names) == 12

def test_save_records():
    
    pass