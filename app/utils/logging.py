# import requests
from discordwebhook import Discord
from dotenv import load_dotenv
import os

load_dotenv()

DISCORD_POOL_URL = os.environ.get("DISCORD_POOL_URL")
DISCORD = Discord(url=DISCORD_POOL_URL)

def logging(string=None):
        DISCORD.post(content=string)
        
        # DEPRECATED
        # result = requests.post("http://192.168.86.205/pool/notification", json={"message":string})
        # result.close()