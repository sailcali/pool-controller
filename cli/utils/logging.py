# import requests
from discordwebhook import Discord
import os

DISCORD_POOL_URL = os.environ.get("DISCORD_POOL_URL")
DISCORD = Discord(url=DISCORD_POOL_URL)

def logging(string=None):
        
        try:
                DISCORD.post(content=string)
        except ConnectionError:
                pass
        
        # DEPRECATED
        # result = requests.post("http://192.168.86.205/pool/notification", json={"message":string})
        # result.close()