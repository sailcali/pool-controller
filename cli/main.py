#!/var/www/pool-controller/venv/bin/python3

import requests
import time as timer
from discordwebhook import Discord
import os
from dotenv import load_dotenv
from datetime import datetime, time

from utils.config import Config

load_dotenv()

UPLOAD_SECONDS = 0
UPLOAD_ERRORS = 0
ERRORS = 0
# Roof is ADC ch 0 and water is ADC ch 7
ROOF_CH = 0
WATER_CH = 7
PUMP_START = time(10, 0, 0)
PUMP_STOP = time(16, 0, 0)
DEBUG = os.environ.get("FLASK_DEBUG")
if DEBUG == "True":
    DEBUG = True
else:
    DEBUG = False

CONFIG = Config(DEBUG)
if DEBUG:
    from utils.testclass.testvalve import TestValve
    from utils.testclass.testsensor import TestSensor
    SENSORS = {"roof": TestSensor(ROOF_CH), "water": TestSensor(WATER_CH)}
    SOLAR_VALVE = TestValve(CONFIG.min_cycle_time)
else:
    from utils.valve import Valve
    from utils.sensor import Sensor
    SENSORS = {"roof": Sensor(ROOF_CH), "water": Sensor(WATER_CH)}
    SOLAR_VALVE = Valve(CONFIG.min_cycle_time)

# TODO Remove seconds cal from config?

DISCORD_POOL_URL = os.environ.get("DISCORD_POOL_URL")
DISCORD = Discord(url=DISCORD_POOL_URL)

def logging(string=None):
        """Simple function for logging to discord, just send a string"""
        try:
            DISCORD.post(content=string)
        except ConnectionError:
            pass

def valve_logic():
    """Determine if valve should be open or closed"""
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
        return False
    
    # Second guard clause will stop any further valve action this day once max temp is hit (this also operates the counter)
    if CONFIG.max_temp_today():
        return False
    
    # Third guard clause checks for if we are at max water temp and if so - ensures valve is closed
    if SENSORS['water'].temp() >= CONFIG.max_water_temp:
        SOLAR_VALVE.close_valve()
        logging(f"Max temp ({CONFIG.max_water_temp} deg) reached!")
        # If we hit the max temp, we are going to bypass any further valve actions for 12 hrs
        CONFIG.change_setting(max_temp_hit=True)
        return True
    
    # Fourth we will check to see if we are close to opening and send a discord notification
    if not SOLAR_VALVE.near_open and SOLAR_VALVE.current_state() == 0 and SENSORS['roof'].temp() > SENSORS['water'].temp() + CONFIG.temp_range_for_open - CONFIG.near_open_temp_diff:
        logging("Work with Pono! Valve is about to open")
        SOLAR_VALVE.near_open = True

    # If the user selects a delay we will not run the automation. NOTE: This comes AFTER another manual change.
    if SOLAR_VALVE.delay > 0:
        return False

    # If the roof temp is above the current registered warm value, make sure it get opened, otherwise closed
    if SENSORS['roof'].temp() > SENSORS['water'].temp() + temp_range:
        SOLAR_VALVE.open_valve()
        return True
    else:
        SOLAR_VALVE.close_valve()
        return True

def check_user_option():
    """Check the config file for a user requested valve change"""
    CONFIG.get_config()
    if not CONFIG.user_request['settled']:
        new_valve = CONFIG.user_request['valve']
        delay = CONFIG.user_request['delay']
        if new_valve:
            SOLAR_VALVE.open_valve(delay=delay)
            CONFIG.settle_user_change()
            return True
        else:
            SOLAR_VALVE.close_valve(delay=delay)
            CONFIG.settle_user_change()
            return False

def standard_data():
    """Standard required info for server"""
    if SOLAR_VALVE.current_state() == 0:
        temp_range = CONFIG.temp_range_for_open
    else:
        temp_range = CONFIG.temp_range_for_close
    if CONFIG.max_temp_today():
        max_hit_delay = 1
    else:
        max_hit_delay = 0
    pump_on = datetime.now().time() >= PUMP_START and datetime.now().time() < PUMP_STOP
    return {"valve": SOLAR_VALVE.current_state(), "roof_temp": SENSORS['roof'].temp(), "water_temp": SENSORS['water'].temp(), "temp_range": temp_range, "max_hit_delay": max_hit_delay, "pump_on": pump_on}

def upload_data():
    """Upload pool data to server"""
    
    # Upload the data to server
    try:
        if DEBUG:
            print(standard_data())
        else:
            response = requests.post("http://192.168.86.205/pool/status", json={"data":standard_data()})
            if response.status_code != 201:
                raise OSError
        return True
    except OSError:
        logging("Pool could not connect to RASPI server!\n")
        return False
        
if __name__ == "__main__":
    while True:
        try:
            check_user_option()
            valve_logic()
        except Exception as error:
            ERRORS += 1
            logging(f"Problem with the auto program: {error}")
            if ERRORS > 20:
                break
            else:
                if ERRORS > 0:
                    ERRORS -= 1

        # Only upload if pump is running, and every 60 seconds
        if standard_data()['pump_on']:
            if UPLOAD_SECONDS >= 60:
                # Upload
                uploaded = upload_data()
                UPLOAD_SECONDS = -1
                
                # Error handling for upload
                if uploaded:
                    if UPLOAD_ERRORS > 0:
                        UPLOAD_ERRORS -= 1
                else:
                    UPLOAD_ERRORS += 1
                    if UPLOAD_ERRORS > 20:
                        UPLOAD_FLAG = False
        
        timer.sleep(1) # One second between checks
        
        # Apply second counters
        UPLOAD_SECONDS += 1
        SOLAR_VALVE.delay -= 1
        SOLAR_VALVE.last_valve_change += 1
    
    # If loop broke
    logging(f'Too many errors, auto closing.')

