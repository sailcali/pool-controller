#!/var/www/pool-controller/venv/bin/python3

import requests
import time as timer
from discordwebhook import Discord
import os
from dotenv import load_dotenv
from datetime import datetime, time

load_dotenv()

UPLOAD_SECONDS = 0
UPLOAD_ERRORS = 0
CONTROLLER_ERRORS = 0
ERRORS = 0
UPLOAD_FLAG = True

# TODO Remove seconds cal from config?

DEBUG = os.environ.get("FLASK_DEBUG")
if DEBUG == "True":
    DEBUG = True
else:
    DEBUG = False

DISCORD_POOL_URL = os.environ.get("DISCORD_POOL_URL")
DISCORD = Discord(url=DISCORD_POOL_URL)

def logging(string=None):
        DISCORD.post(content=string)

while True:
    try:
        # Call API to update valve and get current values
        response = requests.put("http://127.0.0.1/refresh-valve")
        if response.status_code != 201:
            logging("Pool controller offline!")
            CONTROLLER_ERRORS += 1
        else:
            if CONTROLLER_ERRORS > 0:
                CONTROLLER_ERRORS -= 1
        if CONTROLLER_ERRORS > 10:
            break
        
        # Response is standard response
        data = response.json()['data']

        # Guard clause to NOT upload if pump is not running
        if not data['pump_on']:
            timer.sleep(1)
            continue
    
        if UPLOAD_SECONDS >= 60 and UPLOAD_FLAG:
            # Upload the data to server
            try:
                if DEBUG:
                    print(data)
                else:
                    response = requests.post("http://192.168.86.205/pool/status", json={"data":data})
                UPLOAD_SECONDS = -1
            except OSError:
                logging("Pool could not connect to RASPI server!\n")
                UPLOAD_ERRORS += 1
                if UPLOAD_ERRORS > 20:
                    UPLOAD_FLAG = False
            else:
                if UPLOAD_ERRORS > 0:
                    UPLOAD_ERRORS -= 1

        UPLOAD_SECONDS += 1

    except Exception as error:
        ERRORS += 1
        logging(f"Problem with the auto program: {error}")
        if ERRORS > 20:
            break
    else:
        if ERRORS > 0:
            ERRORS -= 1
    finally:
        timer.sleep(1)

logging(f'Too many errors, auto closing.')
