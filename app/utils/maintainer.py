import threading
import time
import requests
from. logging import logging

class Maintainer(threading.Thread):
    def __init__(self, sensors, valve):
        super(Maintainer, self).__init__()
        self.sensors = sensors
        self.valve = valve

    def run(self):
        while True:
            
            # upload_seconds = 0
            try:
                
                # Refresh the current temperatures
                self.sensors.refresh_temps()
                # Go through algorithm to check for valve change
                self.valve.set_valve(self.sensors)
                print(self.sensors.data())
                print(self.valve.data())
                # If the user instituted a delay, reduce that here by a second
                # if valve.delay > 0:
                #     valve.delay -= 1
                # Send data to the server every 60 seconds while running
                # if upload_seconds >= 60:
                    # try:
                        # response = requests.post("http://192.168.86.205/pool/status", json={"data":standard_response()})
                        # response.close()
                        # upload_seconds = 0
                    # except OSError:
                        # logging("Pool could not connect to RASPI server!\n")
                # else:
                    # upload_seconds += 1
                # Wait time between cycles is about 1 second (accounts for run time)
                time.sleep(self.valve.config['seconds_cal'])
                # Tracking the last valve change value
                self.valve.last_valve_change += 1
                
            except Exception as e:
                logging(f"Pool valve error: {e}\n")