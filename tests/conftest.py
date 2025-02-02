import pytest
import json

from src.sqlite_store import SQLiteStore

@pytest.fixture
def data_store(scope='module'):
    store = SQLiteStore(':memory:')
    yield store
    store.close()

@pytest.fixture
def dataset1(scope='session'):
    with open('tests/data.json') as file:
        return json.load(file)
    
@pytest.fixture
def dataset2(scope='session'):
    with open('tests/data1.json') as file:
        return json.load(file)