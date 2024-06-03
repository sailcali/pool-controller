from flask import Blueprint, jsonify, request
from discordwebhook import Discord
import os

from . import sensors, valve
from .utils.maintainer import Maintainer

pool_bp = Blueprint('pool_bp', __name__, url_prefix='/')

MAINTAINER = None

DISCORD_POOL_URL = os.environ.get("DISCORD_POOL_URL")
DISCORD = Discord(url=DISCORD_POOL_URL)

def standard_response():
    if MAINTAINER != None:
        maint = MAINTAINER.is_alive()
    return {**sensors.data(), **valve.data(), "auto_running":maint}

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
        if valve.position == 1:
            return jsonify({'error': 'valve already open'}), 400
        elif valve.last_valve_change < valve.config['min_cycle_time']:
            return jsonify({'error': 'last valve change was too recent'}), 400
        else:
            valve.position = 1
            valve.delay = delay

    elif body['valve'] == False:
        if valve.position == 0:
            return jsonify({'error': 'valve already closed'}), 400
        elif valve.last_valve_change < valve.config['min_cycle_time']:
            return jsonify({'error': 'last valve change was too recent'}), 400
        else:
            valve.position = 0
            valve.delay = delay

    return jsonify({'data': standard_response()}), 201

@pool_bp.route('/temp', methods=['POST'])
def set_temp():
    body = request.get_json()
    valve.config['max_water_temp'] = int(body['setting'])
    data = {**sensors.data(), **valve.data(), "auto_running":MAINTAINER.is_alive()}
    return jsonify({'data': data}), 201

@pool_bp.route('/start-auto', methods=['POST'])
def start_timer():
    """This allows the user to request auto valve control"""
    MAINTAINER = Maintainer(sensors, valve)
    body = request.get_json()
    try:
        MAINTAINER.upload_flag = body['upload']
    except KeyError:
        pass

    MAINTAINER.start()
    DISCORD.post(content="Maintainer running")
    return jsonify({'data': standard_response()}), 201

@pool_bp.route('/stop-auto', methods=['POST'])
def stop_timer():
    MAINTAINER.stop_sign = True
    return jsonify({'data': standard_response()}), 201