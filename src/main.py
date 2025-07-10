import os
import sys
from dotenv import load_dotenv
import json

from .auth import *
from .pocketcasts import get_history
from .sqlite_store import SQLiteStore
    
def diff_records(incoming: list[dict], existing: tuple) -> list:
    if not incoming:
        return [] # Return empty list instead of 0
    
    existing_uuids = { record[0] for record in existing }
    records_to_insert = [
        record for record in incoming if record['uuid'] not in existing_uuids
    ]

    return records_to_insert

def getDB_path():
    path = ''
    if os.path.exists('/.dockerenv'):
        # Path when running in Docker container
        path = '/app/data/pockecasts.db'
    else:
        # Path when running locally
        path = 'data/pocketcasts.db'

    # confirm directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        # Attempt to create a file to test write permissions
        test_file = os.path.join(os.path.dirname(path), 'test_write.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
    except PermissionError:
        print(f"Permission denied when trying to write to {os.path.dirname(path)}")
        raise

    return path 

if __name__ == "__main__":
    CALL_API = True
    LOAD_SAMPLE = False

    # load credentials
    load_dotenv()
    if not 'USERNAME' in os.environ:
        print('USERNAME environment variable does not exist.')
        sys.exit()
    if not 'PASSWORD' in os.environ:
        print('PASSWORD environment variable does not exist.')
        sys.exit()

    if CALL_API:
        http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
        token = do_login(http, user=os.environ.get('USERNAME'), pw=os.environ.get('PASSWORD'))
        history = get_history(http, token)
    
    if LOAD_SAMPLE: # read sample json into memory
        with open('tests/data7.json', 'r', encoding='utf-8') as file:
            history = json.load(file)

    store = SQLiteStore(getDB_path())
    saved_records = store.get_records()
    new_records = diff_records(history['episodes'], saved_records)
    store.save_records(new_records)
    print(len(new_records))
    store.close()