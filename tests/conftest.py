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
    
@pytest.fixture
def dataset2():
    with open('tests/data1.json') as file:
        return json.load(file)