import os
import sys
from dotenv import load_dotenv
import json

from .auth import *
from .pocketcasts import get_history
from .sqlite_store import SQLiteStore
    
def diff_records(incoming: list[dict], existing: tuple) -> list:
    if not incoming:
        return 0
    
    existing_uuids = { record[0] for record in existing }
    records_to_insert = [
        record for record in incoming if record['uuid'] not in existing_uuids
    ]

    return records_to_insert

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

    store = SQLiteStore('pocketcasts.db')
    saved_records = store.get_records()
    new_records = diff_records(history['episodes'], saved_records)
    store.save_records(new_records)
    print(len(new_records))
    store.close()