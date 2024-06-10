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
PUMP_START = time(10, 0, 0)
PUMP_STOP = time(16, 0, 0)

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
    pump_on = datetime.now().time() >= PUMP_START and datetime.now().time() < PUMP_STOP
    if not pump_on:
        response = requests.put("http://127.0.0.1/refresh-valve")
        if response.status_code != 201:
            logging("Pool controller offline!")
            CONTROLLER_ERRORS += 1
        else:
            if CONTROLLER_ERRORS > 0:
                CONTROLLER_ERRORS -= 1
        if CONTROLLER_ERRORS > 10:
            break
        timer.sleep(1)
        continue

    try:
        # Call the API
        response = requests.put("http://127.0.0.1/refresh-valve")
        if response.status_code != 201:
            logging("Pool controller offline!")
            break
        
        # Response is standard response
        data = response.json()

        if UPLOAD_SECONDS >= 60 and UPLOAD_FLAG:
            # Upload the data to server
            try:
                if DEBUG:
                    print(data)
                else:
                    response = requests.post("http://192.168.86.205/pool/status", json={"data":data['data']})
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
