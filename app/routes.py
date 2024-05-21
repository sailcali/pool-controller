from flask import Blueprint, jsonify
from . import sensors, valve
pool_bp = Blueprint('pool_bp', __name__, url_prefix='/')

@pool_bp.route('/', methods=['GET'])
def get_status():
    """Returns the current pool status"""
    print(f"Checking {sensors}")
    return jsonify({'Sensor Status':f"{sensors.data()}", 'Valve Status':f"{valve.data()}"}, 200)