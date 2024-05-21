from flask import Blueprint, jsonify, request
from . import sensors, valve
pool_bp = Blueprint('pool_bp', __name__, url_prefix='/')

@pool_bp.route('/', methods=['GET'])
def get_status():
    """Returns the current pool status"""
    return jsonify(sensors.data().update(valve.data()), 200)

@pool_bp.route('/valve', methods=['POST'])
def change_valve():
    """Manually opens or closes the solar valve"""
    body = request.get_json()
    if body['valve'] == True:
        valve.open_valve(delay=90)
    elif body['valve'] == False:
        valve.close_valve(delay=90)
    return jsonify(sensors.data().update(valve.data()), 201)

@pool_bp.route('/temp', methods=['POST'])
def set_temp():
    body = request.get_json()
    valve.config['max_water_temp'] = body['setting']
    return jsonify(sensors.data().update(valve.data()), 201)