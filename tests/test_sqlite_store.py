import pytest
import json

from src.sqlite_store import SQLiteStore

@pytest.fixture
def data_store():
    store = SQLiteStore(':memory:')
    yield store
    store.close()

@pytest.fixture
def dataset1():
    with open('tests/data.json') as file:
        return json.load(file)
    

def test_table_creation(data_store):
    cursor = data_store.db_connection.cursor()

    cursor.execute(f'PRAGMA table_info(Listening_History)')
    columns = cursor.fetchall()

    # column[1] contains the string names of the columns in the table.
    column_names = [ column[1] for column in columns ]
    assert len(column_names) == 12

def test_save_records(data_store, dataset1):
    records_saved: int = data_store.save_records(dataset1['episodes'])

    cursor = data_store.db_connection.cursor()
    cursor.execute('SELECT * FROM Listening_History')
    records = cursor.fetchall()

    assert records_saved == len(dataset1['episodes'])
    assert len(records) == len(dataset1['episodes'])