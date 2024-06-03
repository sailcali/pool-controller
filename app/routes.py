from flask import Blueprint, jsonify, request
from . import sensors, valve
pool_bp = Blueprint('pool_bp', __name__, url_prefix='/')

@pool_bp.route('/', methods=['GET'])
def get_status():
    """Returns the current pool status"""
    data = {**sensors.data(), **valve.data()}
    return jsonify({'data': data}), 200

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

    data = {**sensors.data(), **valve.data()}
    return jsonify({'data': data}), 201

@pool_bp.route('/temp', methods=['POST'])
def set_temp():
    body = request.get_json()
    valve.config['max_water_temp'] = int(body['setting'])
    data = {**sensors.data(), **valve.data()}
    return jsonify({'data': data}), 201