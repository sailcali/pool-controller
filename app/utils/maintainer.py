import threading
import time
import requests
from. logging import logging

class Maintainer(threading.Thread):
    def __init__(self, sensors, valve):
        super(Maintainer, self).__init__()
        self.sensors = sensors
        self.valve = valve

    def standard_response(self):
        return {"water_temp": self.sensors.water_temp, "roof_temp": self.sensors.roof_temp,
            "valve": self.valve.current_state(), 'delay': self.valve.delay,
            "last_change": self.valve.last_valve_change, "set_temp": self.valve.config['max_water_temp'],
            "temp_range": self.valve.temp_range, "max_hit_delay":self.valve.max_temp_hit_delay}

    def run(self):
        upload_seconds = 0
        errors = 0
        while True:
            try:
                if errors > 0:
                    errors -= 1
                # Refresh the current temperatures
                self.sensors.refresh_temps()
                # Go through algorithm to check for valve change
                self.valve.set_valve(self.sensors)
                # Send data to the server every 60 seconds while running
                if upload_seconds >= 60:
                    try:
                        response = requests.post("http://192.168.86.205/pool/status", json={"data":self.standard_response()})
                        response.close()
                        upload_seconds = -1
                    except OSError:
                        logging("Pool could not connect to RASPI server!\n")
                upload_seconds += 1
                # Wait time between cycles is about 1 second (accounts for run time)
                time.sleep(self.valve.config['seconds_cal'])
                # Tracking the last valve change value
                self.valve.last_valve_change += 1
                # If manually changed, this is the counter to continue the programming
                if self.valve.delay > 0:
                    self.valve.delay -= 1
                
            except Exception as e:
                errors += 1
                logging(f"Pool valve error: {e}\n")
                if errors > 20:
                    break