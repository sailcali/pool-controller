import RPi.GPIO as GPIO
from .logging import logging

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

VALVE_PIN = 17

class Valve:
    """Controller for the Solar Valve"""
    def __init__(self, min_cycle_time):

        # self.config = config
        GPIO.setup(VALVE_PIN, GPIO.OUT)
        GPIO.output(VALVE_PIN, False)
        # self.position = 0 # This is the requested position, not necessarily the ACTUAL position
        self.delay = 0 # User requested delay in programming
        self.last_valve_change = min_cycle_time # init @ min cycle time
    
    def current_state(self):
        """Returns 0 or 1 for valve position"""
        return GPIO.input(VALVE_PIN)

    def open_valve(self):
        """Opens the valve if closed"""
        if self.current_state() == 0:
            # Open the valve
            GPIO.output(VALVE_PIN, True)
            
            # Reset the triggers and notify
            # self.position = 1 # Local position tracker gets updated
            logging("Solar valve open!")
            self.last_valve_change = 0 # reset the last valve change timer
            # self.temp_range = self.config.temp_range_for_close # Change the temp range trigger to CLOSE
            # self.near_open = False # Reset the near_open FOR DISCORD NOTIFICATION
            return True
        else:
            return False
            
    def close_valve(self):
        """Closes the valve if open"""
        if self.current_state() == 1:
            # Open the valve
            GPIO.output(VALVE_PIN, False)
            
            #Reset the triggers and notify
            # self.position = 0 # Local position tracker gets updated
            logging("Solar valve closed!")
            self.last_valve_change = 0 # Reset the last valve change timer
            # self.temp_range = self.config.temp_range_for_open # Change the temp range trigger to OPEN
            return True
        else:
            return False
    
    def data(self):
        """Gathers all relavent data into a dictionary"""
        return {"valve": GPIO.input(VALVE_PIN), 'delay': self.delay, "last_change": self.last_valve_change}