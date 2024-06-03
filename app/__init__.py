from flask import Flask
# from dotenv import load_dotenv
import os
from discordwebhook import Discord
from .utils.sensors import Sensors
from .utils.solarvalve import SolarValve
from .utils.maintainer import Maintainer

# load_dotenv()

DISCORD_POOL_URL = os.environ.get("DISCORD_POOL_URL")
DISCORD = Discord(url=DISCORD_POOL_URL)

sensors = Sensors()
valve = SolarValve()

def create_app():
    app = Flask(__name__)
    print(DISCORD_POOL_URL)
    DISCORD.post(content="Server running")
    # maintainer = Maintainer(sensors, valve)
    # maintainer.start()
    DISCORD.post(content="Maintainer running")

    from .routes import pool_bp

    app.register_blueprint(pool_bp)

    return app