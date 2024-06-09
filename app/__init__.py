from flask import Flask
import os
from discordwebhook import Discord
from .utils.config import Config

DISCORD_POOL_URL = os.environ.get("DISCORD_POOL_URL")
DEBUG = os.environ.get("FLASK_DEBUG")
DISCORD = Discord(url=DISCORD_POOL_URL)

# Roof is ADC ch 0 and water is ADC ch 7
ROOF_CH = 0
WATER_CH = 7

CONFIG = Config()
if DEBUG:
    from .utils.testclass.testvalve import TestValve
    from .utils.testclass.testsensor import TestSensor
    SENSORS = {"roof": TestSensor(ROOF_CH), "water": TestSensor(WATER_CH)}
    SOLAR_VALVE = TestValve(CONFIG.min_cycle_time)
else:
    from .utils.sensor import Sensor
    from .utils.valve import Valve
    SENSORS = {"roof": Sensor(ROOF_CH), "water": Sensor(WATER_CH)}
    SOLAR_VALVE = Valve(CONFIG.min_cycle_time)

def create_app():
    app = Flask(__name__)
    DISCORD.post(content="Server running")
    from .routes import pool_bp
    app.register_blueprint(pool_bp)

    return app
