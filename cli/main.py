#!/var/www/pool-controller/venv/bin/python3

import requests
import time
from discordwebhook import Discord
import os
from dotenv import load_dotenv

load_dotenv()

upload_seconds = 0
upload_errors = 0
errors = 0
upload_flag = True

# TODO Remove seconds cal from config?

DEBUG = os.environ.get("FLASK_DEBUG")
DISCORD_POOL_URL = os.environ.get("DISCORD_POOL_URL")
DISCORD = Discord(url=DISCORD_POOL_URL)

def logging(string=None):
        DISCORD.post(content=string)

while True:
    try:

        # Call the API
        response = requests.put("http://127.0.0.1/refresh-valve")
        if response.status_code != 201:
            logging("Pool controller offline!")
            break
        
        # Response is standard response
        data = response.json()

        if upload_seconds >= 60 and upload_flag:
            # Upload the data to server
            try:
                if DEBUG:
                    print(data)
                else:
                    response = requests.post("http://192.168.86.205/pool/status", json={"data":data['data']})
                upload_seconds = -1
            except OSError:
                logging("Pool could not connect to RASPI server!\n")
                upload_errors += 1
                if upload_errors > 20:
                    upload_flag = False
            else:
                if upload_errors > 0:
                    upload_errors -= 1

        upload_seconds += 1

    except Exception as error:
        errors += 1
        logging(f"Problem with the auto program: {error}")
        if errors > 20:
            logging(f'Too many errors, auto closing.')
            break
    else:
        if errors > 0:
            errors -= 1
    finally:
        time.sleep(1)
