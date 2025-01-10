import os
import sys
from dotenv import load_dotenv

from auth import *
from pocketcasts import get_history

import sqlite3
import json

def create_database(db_name='pocketcasts.db'):
    table_schema = """
        CREATE TABLE IF NOT EXISTS PocketCasts_Listening_History (
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
            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
    """

    try:
        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        cursor.execute(table_schema)
        connection.commit()
        print('Table created successfully.')
        return connection
    except sqlite3.Error as e:
        print(f'Something happened: {e}')
        if connection:
            connection.rollback()
        return None

def insert_data(connection, data):
    if not connection:
        print("Error: No Database connection.")
        return
    
    sql_insert_command = """
        INSERT INTO PocketCasts_Listening_History (
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

if __name__ == "__main__":

    # load credentials
    load_dotenv()
    if not 'USERNAME' in os.environ:
        print('USERNAME environment variable does not exist.')
        sys.exit()
    if not 'PASSWORD' in os.environ:
        print('PASSWORD environment variable does not exist.')
        sys.exit()

    # http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
    # token = do_login(http, user=os.environ.get('USERNAME'), pw=os.environ.get('PASSWORD'))
    # history = get_history(http, token)
    # with open('data3.json', 'w', encoding='utf-8') as file:
    #     json.dump(history, file)

    # read sample json into memory
    with open('data3.json', 'r', encoding='utf-8') as file:
        history = json.load(file)   

    # - Create the SQLite database
    connection = create_database('pocketcasts2.db')
    if connection:
        episode_history = history['episodes']
        for episode in episode_history.reverse():
            insert_data(connection, (
                episode['uuid'],
                episode['url'],
                episode['published'],
                episode['duration'], 
                episode['title'],
                episode['size'],
                episode['starred'],
                episode['podcastUuid'],
                episode['podcastTitle'],
                episode['author'])
            )
        
    #     connection.close()