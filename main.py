import os
import json
import sys
import urllib3
from dotenv import load_dotenv

from auth import *
from pocketcasts import get_history

if __name__ == "__main__":

    # load credentials
    load_dotenv()
    if not 'USERNAME' in os.environ:
        print('USERNAME environment variable does not exist.')
        sys.exit()
    if not 'PASSWORD' in os.environ:
        print('PASSWORD environment variable does not exist.')
        sys.exit()

    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
    token = do_login(http, user=os.environ.get('USERNAME'), pw=os.environ.get('PASSWORD'))
    history = get_history(http, token)

    # save file 
    
    with open('data1.json', 'w', encoding='utf-8') as file:
        json.dump(history, file)
        
    print(history)