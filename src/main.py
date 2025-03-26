import os
import sys
from dotenv import load_dotenv
import json
import logging

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
        logger.error(f"Permission denied when trying to write to {os.path.dirname(path)}")
        raise

    return path 

def configure_logging() -> logging.Logger:
    logger = logging.getLogger('app')
    logger.setLevel(logging.DEBUG)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stdout_handler.setFormatter(stdout_formatter)
    logger.addHandler(stdout_handler)

    return logger

if __name__ == "__main__":
    CALL_API = False
    LOAD_SAMPLE = True

    logger = configure_logging()

    # look for flag to load sample data
    if 'DEBUG_MODE' in os.environ and os.environ.get('DEBUG_MODE') == 'True':
        LOAD_SAMPLE = True
        CALL_API = False
        logger.debug('DEBUG_MODE is set to True. Loading sample data.')

    # load credentials
    load_dotenv()
    if not 'USERNAME' in os.environ:
        logger.error('USERNAME environment variable was not found.')
        sys.exit()
    if not 'PASSWORD' in os.environ:
        logger.error('PASSWORD environment variable was not found.')
        sys.exit()

    if CALL_API:
        http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
        token = do_login(http, user=os.environ.get('USERNAME'), pw=os.environ.get('PASSWORD'))
        history = get_history(http, token)
    
    if LOAD_SAMPLE: # read sample json into memory
        logger.debug('Loading sample data.')
        with open('tests/data7.json', 'r', encoding='utf-8') as file:
            history = json.load(file)

    store = SQLiteStore(getDB_path())
    saved_records = store.get_records()
    new_records = diff_records(history['episodes'], saved_records)
    store.save_records(new_records)
    logger.info(f'{len(saved_records)} records added.')
    store.close()