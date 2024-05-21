from flask import Flask
from dotenv import load_dotenv
from .utils.sensors import Sensors
from .utils.solarvalve import SolarValve
from .utils.maintainer import Maintainer

load_dotenv()

sensors = Sensors()
valve = SolarValve()

def create_app():
    app = Flask(__name__)

    maintainer = Maintainer(sensors, valve)

    maintainer.start()

    from .routes import pool_bp

    app.register_blueprint(pool_bp)

    return app