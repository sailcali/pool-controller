from flask import Blueprint, jsonify, request
from discordwebhook import Discord
import os
import time

from . import SENSORS, SOLAR_VALVE, CONFIG
from .utils.maintainer import Maintainer

pool_bp = Blueprint('pool_bp', __name__, url_prefix='/')

MAINTAINER = Maintainer(SENSORS, SOLAR_VALVE)
MAINTAINER.start()
DISCORD_POOL_URL = os.environ.get("DISCORD_POOL_URL")
DISCORD = Discord(url=DISCORD_POOL_URL)

def standard_response():
    return {"roof_temp": SENSORS['roof'].temp(), "water_temp": SENSORS['water'].temp(), **SOLAR_VALVE.data(), **CONFIG.data(), "auto_running":MAINTAINER.is_alive()}

@pool_bp.route('/', methods=['GET'])
def get_status():
    """Returns the current pool status"""
    return jsonify({'data': standard_response()}), 200

@pool_bp.route('/valve', methods=['POST'])
def change_valve():
    """Manually opens or closes the solar valve"""
    body = request.get_json()
    try:
        delay = int(body['delay'])
    except KeyError:
        delay = 90
    if body['valve'] == True:
        if SOLAR_VALVE.position == 1:
            return jsonify({'error': 'valve already open'}), 400
        elif SOLAR_VALVE.last_valve_change < SOLAR_VALVE.config.min_cycle_time:
            return jsonify({'error': 'last valve change was too recent'}), 400
        else:
            SOLAR_VALVE.position = 1
            SOLAR_VALVE.delay = delay

    elif body['valve'] == False:
        if SOLAR_VALVE.position == 0:
            return jsonify({'error': 'valve already closed'}), 400
        elif SOLAR_VALVE.last_valve_change < SOLAR_VALVE.config.min_cycle_time:
            return jsonify({'error': 'last valve change was too recent'}), 400
        else:
            SOLAR_VALVE.position = 0
            SOLAR_VALVE.delay = delay

    return jsonify({'data': standard_response()}), 201

@pool_bp.route('/temp', methods=['POST'])
def set_temp():
    body = request.get_json()
    SOLAR_VALVE.config.change_setting("max_water_temp", int(body['setting']))
    return jsonify({'data': standard_response()}), 201

@pool_bp.route('/start-auto', methods=['POST'])
def start_timer():
    """This allows the user to request auto valve control. User may pass -upload- param as False to not upload to DB every second"""
    global MAINTAINER
    MAINTAINER = Maintainer(SENSORS, SOLAR_VALVE)
    body = request.get_json()
    try:
        MAINTAINER.upload_flag = body['upload']
    except KeyError:
        pass

    MAINTAINER.start()
    DISCORD.post(content="Auto running")
    return jsonify({'data': standard_response()}), 201

@pool_bp.route('/stop-auto', methods=['POST'])
def stop_timer():
    """This will STOP execution of the auto thread and reset the function"""
    global MAINTAINER

    MAINTAINER.stop_sign = True
    time.sleep(2)
    MAINTAINER = Maintainer(SENSORS, SOLAR_VALVE)
    return jsonify({'data': standard_response()}), 201

@pool_bp.route('/config', methods=['POST'])
def update_config():
    """Updates any of the config values. Params must include key and setting values"""
    body = request.get_json()
    try:
        SOLAR_VALVE.config.change_setting(body['key'], int(body['setting']))
    except KeyError:
        return jsonify({'error': 'Must include [key] and [setting] params!'}), 401
    return jsonify({'data': standard_response()}), 201