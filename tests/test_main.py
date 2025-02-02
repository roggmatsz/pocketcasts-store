from typing import Any
from src.main import diff_records
from src.sqlite_store import SQLiteStore

def test_diff_records(data_store: SQLiteStore, dataset2: dict, dataset3: dict):
    data_store.save_records(dataset2['episodes'])
    existing_records = data_store.get_records()

    # value comes from diff of dataset2 and 3 based on working code.
    assert len(diff_records(dataset3['episodes'], existing_records)) == 22