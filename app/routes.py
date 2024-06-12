from flask import Blueprint, jsonify, request
from discordwebhook import Discord
import os
from datetime import datetime, time

from . import SENSORS, SOLAR_VALVE, CONFIG

pool_bp = Blueprint('pool_bp', __name__, url_prefix='/')

DISCORD_POOL_URL = os.environ.get("DISCORD_POOL_URL")
DISCORD = Discord(url=DISCORD_POOL_URL)
PUMP_START = time(10, 0, 0)
PUMP_STOP = time(16, 0, 0)

def standard_response():
    if SOLAR_VALVE.current_state() == 0:
        temp_range = CONFIG.temp_range_for_open
    else:
        temp_range = CONFIG.temp_range_for_close
    if CONFIG.max_temp_today():
        max_hit_delay = 1
    else:
        max_hit_delay = 0
    pump_on = datetime.now().time() >= PUMP_START and datetime.now().time() < PUMP_STOP
    return {"pump_on": pump_on, "max_hit_delay": max_hit_delay, "temp_range": temp_range, "roof_temp": SENSORS['roof'].get_temp(), 
            "water_temp": SENSORS['water'].get_temp(), "valve": SOLAR_VALVE.current_state(), **CONFIG.data()}

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
        if SOLAR_VALVE.current_state() == 1:
            return jsonify({'error': 'valve already open'}), 400
        else:
            SOLAR_VALVE.open_valve(delay)

    elif body['valve'] == False:
        if SOLAR_VALVE.current_state() == 0:
            return jsonify({'error': 'valve already closed'}), 400
        elif SOLAR_VALVE.last_valve_change < CONFIG.min_cycle_time:
            return jsonify({'error': 'last valve change was too recent'}), 400
        else:
            SOLAR_VALVE.close_valve()
            SOLAR_VALVE.delay = delay

    return jsonify({'data': standard_response()}), 201

@pool_bp.route('/temp', methods=['POST'])
def set_temp():
    body = request.get_json()
    CONFIG.change_setting("max_water_temp", int(body['setting']))
    return jsonify({'data': standard_response()}), 201

@pool_bp.route('/config', methods=['POST'])
def update_config():
    """Updates any of the config values. Params must include key and setting values"""
    body = request.get_json()
    try:
        CONFIG.change_setting(body['key'], int(body['setting']))
    except KeyError:
        return jsonify({'error': 'Must include [key] and [setting] params!'}), 401
    return jsonify({'data': standard_response()}), 201