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
        delay = body['delay']
    except KeyError:
        delay = 90
    if body['valve'] == True:
        if valve.position == 0:
            valve.open_valve(delay=delay)
        else:
            return jsonify({'error': 'valve already open'}), 400
    elif body['valve'] == False:
        if valve.position == 1:
            valve.close_valve(delay=delay)
        else:
            return jsonify({'error': 'valve already closed'}), 400
    data = {**sensors.data(), **valve.data()}
    return jsonify({'data': data}), 201

@pool_bp.route('/temp', methods=['POST'])
def set_temp():
    body = request.get_json()
    valve.config['max_water_temp'] = body['setting']
    data = {**sensors.data(), **valve.data()}
    return jsonify({'data': data}), 201