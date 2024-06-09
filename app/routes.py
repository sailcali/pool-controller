from flask import Blueprint, jsonify, request
from discordwebhook import Discord
import os
from datetime import datetime

from . import SENSORS, SOLAR_VALVE, CONFIG
from .utils.logging import logging

pool_bp = Blueprint('pool_bp', __name__, url_prefix='/')

DISCORD_POOL_URL = os.environ.get("DISCORD_POOL_URL")
DISCORD = Discord(url=DISCORD_POOL_URL)

def standard_response():
    if SOLAR_VALVE.current_state() == 0:
        temp_range = CONFIG.temp_range_for_open
    else:
        temp_range = CONFIG.temp_range_for_close
    return {"max_hit_delay": 0, "temp_range": temp_range, "roof_temp": SENSORS['roof'].temp(), 
            "water_temp": SENSORS['water'].temp(), **SOLAR_VALVE.data(), **CONFIG.data()}

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
        elif SOLAR_VALVE.last_valve_change < CONFIG.min_cycle_time:
            return jsonify({'error': 'last valve change was too recent'}), 400
        else:
            SOLAR_VALVE.open_valve()
            SOLAR_VALVE.delay = delay

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

@pool_bp.route('/refresh-valve', methods=['PUT'])
def routine_solar_valve_control():
    """This should be run every second to update the valve setting"""
    
    SOLAR_VALVE.last_valve_change += 1
    if SOLAR_VALVE.delay > 0:
        SOLAR_VALVE.delay -= 1

    # First update the temperatures
    for sensor in SENSORS.values():
                    sensor.refresh_temp()

    # Check our current temp range we are looking for to make a change
    if SOLAR_VALVE.current_state() == 0:
        temp_range = CONFIG.temp_range_for_open
    else:
        temp_range = CONFIG.temp_range_for_close
    # near_open = False # This will trigger once within a specified temp of opening and send a discord notification
    # near_open_temp_diff = 1 # This will be the temp difference when discord notification gets sent

    # First guard clause is for if we are within the cycle limit set by config
    if SOLAR_VALVE.last_valve_change < CONFIG.min_cycle_time:
        return jsonify({'data': standard_response()}), 201
    
    # Second guard clause will stop any further valve action this day once max temp is hit (this also operates the counter)
    if CONFIG.max_temp_hit_date == datetime.today().date():
        return jsonify({'data': standard_response()}), 201
    
    # Third guard clause checks for if we are at max water temp and if so - ensures valve is closed
    if SENSORS['water'].temp() >= CONFIG.max_water_temp:
        SOLAR_VALVE.close_valve()
        logging(f"Max temp ({CONFIG.max_water_temp} deg) reached!")
        # If we hit the max temp, we are going to bypass any further valve actions for 12 hrs
        CONFIG.change_setting(max_temp_hit=True)
        return jsonify({'data': standard_response()}), 201
    
    # # Fourth we will check to see if we are close to opening and send a discord notification
    if not SOLAR_VALVE.near_open and SOLAR_VALVE.current_state() == 0 and SENSORS['roof'].temp() > SENSORS['water'].temp() + CONFIG.temp_range_for_open - CONFIG.near_open_temp_diff:
        logging("Work with Pono! Valve is about to open")
        SOLAR_VALVE.near_open = True

    # If the user selects a delay we will not run the automation. NOTE: This comes AFTER another manual change.
    if SOLAR_VALVE.delay > 0:
        return jsonify({'data': standard_response()}), 201

    # If the roof temp is above the current registered warm value, make sure it get opened, otherwise closed
    if SENSORS['roof'].temp() > SENSORS['water'].temp() + temp_range:
        SOLAR_VALVE.open_valve()
    else:
        SOLAR_VALVE.close_valve()

    return jsonify({'data': standard_response()}), 201