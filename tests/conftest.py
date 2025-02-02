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
    
@pytest.fixture
def dataset3(scope='session'):
    with open('tests/data3.json') as file:
        return json.load(file)
    
@pytest.fixture
def dataset4(scope='session'):
    with open('tests/data4.json') as file:
        return json.load(file)

@pytest.fixture
def dataset5(scope='session'):
    with open('tests/data5.json') as file:
        return json.load(file)
    
@pytest.fixture
def dataset6(scope='session'):
    with open('tests/data6.json') as file:
        return json.load(file)