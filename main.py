import os
import sys
from dotenv import load_dotenv

from auth import *
from pocketcasts import get_history
from listen_record import ListenRecord

import sqlite3
import json
from collections import deque

def create_database(db_name='pocketcasts.db'):
    with sqlite3.connect(db_name) as connection:
        cursor = connection.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS Listening_History (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Episode_UUID TEXT NOT NULL,
                URL TEXT NOT NULL,
                Published_Date TEXT NOT NULL,
                Duration INTEGER,
                Title TEXT NOT NULL,
                Size INTEGER NOT NULL,
                Is_Starred BOOLEAN DEFAULT 0 CHECK (Is_Starred IN (0, 1)),
                Podcast_UUID TEXT NOT NULL,
                Podcast_Title TEXT NOT NULL,
                Author TEXT NOT NULL,
                Date_Saved DATETIME DEFAULT CURRENT_TIMESTAMP)
        ''')

    return connection

def get_saved_data(db_connection: sqlite3.Connection, count=100):
    if not db_connection:
        print("Error: No Database connection.")
        return

    with db_connection:
        cursor = db_connection.cursor()
        cursor.execute(f'''
            SELECT Episode_UUID, URL, Published_Date, Duration, Title, Size, Is_Starred, Podcast_UUID, Podcast_Title, Author, Date_Saved
            FROM Listening_History
            ORDER BY Date_Saved DESC
            LIMIT {count}
        ''')
        return cursor.fetchall()
    
def diff_records(db_connection, incoming, saved):
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

def insert_data(connection, data):
    if not connection:
        print("Error: No Database connection.")
        return
    
    sql_insert_command = """
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
    """
    try:
        cursor = connection.cursor()
        cursor.execute(sql_insert_command, data)
        connection.commit()
        print('Data inserted successfully.')
    except sqlite3.Error as e:
        print(f'{e}')
        if connection:
            connection.rollback()

def diff_history(incoming_history, saved_history):
    saved_deque = deque(saved_history)
    overlap = 0
    min_length = min(len(saved_history), len(incoming_history))

    for i in range(1, min_length + 1):
        if incoming_history[-i] == incoming_history[i - 1]:
            overlap = i
        else:
            break

    new_records = incoming_history[:len(incoming_history) - overlap]
    saved_deque.extendleft(new_records)

    while len(saved_deque) > 100:
        saved_deque.pop()

    return list(saved_deque)

if __name__ == "__main__":
    CALL_API = False
    LOAD_SAMPLE = True
    CREATE_DB = False
    TRY_DIFF = True

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
        with open('data4.json', 'w', encoding='utf-8') as file:
            json.dump(history, file)
    
    if LOAD_SAMPLE:
         # read sample json into memory
        with open('data4.json', 'r', encoding='utf-8') as file:
            history = json.load(file)

    connection = create_database('pocketcasts.db')
    print(diff_records(connection, history['episodes'], get_saved_data(connection)))
    # for episode in history['episodes'][::-1]:
    #     insert_data(connection, (
    #         episode['uuid'],
    #         episode['url'],
    #         episode['published'],
    #         episode['duration'], 
    #         episode['title'],
    #         episode['size'],
    #         episode['starred'],
    #         episode['podcastUuid'],
    #         episode['podcastTitle'],
    #         episode['author']))

    # if CREATE_DB:
    #     # - Create the SQLite database
    #     connection = create_database('pocketcasts.db')
    #     if connection:
    #         for episode in history['episodes'][::-1]:
    #             insert_data(connection, (
    #                 episode['uuid'],
    #                 episode['url'],
    #                 episode['published'],
    #                 episode['duration'], 
    #                 episode['title'],
    #                 episode['size'],
    #                 episode['starred'],
    #                 episode['podcastUuid'],
    #                 episode['podcastTitle'],
    #                 episode['author']))
                
    #     connection.close()

    # if TRY_DIFF:
    #     # fetch the last 100 items stored in the db
    #     connection = sqlite3.connect('pocketcasts.db')
    #     cursor = connection.cursor()
    #     cursor.execute('SELECT * FROM PocketCasts_Listening_History ORDER BY ID LIMIT 100')
    #     saved_history = cursor.fetchall()
    #     packaged_saved_history = ListenRecord.Convert_List(saved_history)

    #     # get latest data
    #     latest_history = []
    #     with open('data3.json', 'r', encoding='utf-8') as file:
    #         latest_history = json.load(file)

    #     pkgd_latest_history = []
    #     for item in latest_history['episodes']:
    #         pkgd_latest_history.append(ListenRecord.From_Dictionary(item))

    #     # diff here
    #     results = diff_history(pkgd_latest_history, packaged_saved_history)
    #     print('fo')