import os
import sys
from dotenv import load_dotenv

from auth import *
from pocketcasts import get_history

import sqlite3
import json
    
def process_new_records(db_connection: sqlite3.Connection, incoming: list[dict]) -> int:
    if not incoming:
        return 0
    
    with db_connection:
        cursor = db_connection.cursor()
        cursor.execute(f'''
            SELECT Episode_UUID
            FROM Listening_History
            WHERE episode_uuid IN ({ ','.join(['?'] * len(incoming)) })
        ''', [ record['uuid'] for record in incoming ])

        existing_uuids = { row[0] for row in cursor.fetchall() }

        records_to_insert = [
            record for record in incoming if record['uuid'] not in existing_uuids
        ]

        if records_to_insert:
            cursor.executemany('''
                INSERT INTO Listening_History (
                    Episode_UUID,
                    URL,
                    Published_Date,
                    Duration,
                    Title,
                    Size,
                    Is_Starred,
                    Podcast_UUID,
                    Podcast_Title,
                    Author
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', [(
                    record['uuid'],
                    record['url'],
                    record['published'],
                    record['duration'],
                    record['title'],
                    record['size'],
                    record['starred'],
                    record['podcastUuid'],
                    record['podcastTitle'],
                    record['author']
                ) for record in reversed(records_to_insert)
            ])
        return len(records_to_insert)

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
        with open('data7.json', 'r', encoding='utf-8') as file:
            history = json.load(file)

    connection = create_database('pocketcasts.db')
    print(process_new_records(connection, history['episodes']))