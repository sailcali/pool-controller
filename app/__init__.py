from flask import Flask
import os
from discordwebhook import Discord
from .utils.sensors import Sensor
from .utils.solarvalve import Valve
from .utils.config import Config

DISCORD_POOL_URL = os.environ.get("DISCORD_POOL_URL")
DISCORD = Discord(url=DISCORD_POOL_URL)

# Roof is ADC ch 0 and water is ADC ch 7
ROOF_CH = 0
WATER_CH = 7

CONFIG = Config()
SENSORS = {"roof": Sensor(ROOF_CH), "water": Sensor(WATER_CH)}
SOLAR_VALVE = Valve(CONFIG)

def create_app():
    app = Flask(__name__)
    DISCORD.post(content="Server running")

    from .routes import pool_bp

    app.register_blueprint(pool_bp)

    return app