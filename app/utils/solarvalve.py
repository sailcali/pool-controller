import RPi.GPIO as GPIO
from .logging import logging

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

VALVE_PIN = 17

class SolarValve:
    """Controller for the Solar Valve"""
    def __init__(self):
        self.config = {'min_cycle_time': 90, 
            'max_water_temp': 80, 
            'temp_range_for_open': 20, 
            'temp_range_for_close': 1, 
            'seconds_cal': 1}
        GPIO.setup(VALVE_PIN, GPIO.OUT)
        GPIO.output(VALVE_PIN, False)
        self.position = 0
        self.delay = 0
        self.last_valve_change = self.config['min_cycle_time'] # init @ min cycle time
        self.max_temp_hit_delay = 0 # this will jump to 43200 (12 hrs) if max temp is hit
        self.temp_range = self.config['temp_range_for_open'] # init at the closed setting (high)
    
    def set_valve(self, sensors):
        """This is run every second to update the valve setting"""
        
        # First guard clause is for if a valve change delay was initiated manually or we are within the cycle limit set by config
        if self.delay > 0 or self.last_valve_change < self.config['min_cycle_time']:
            return
        
        # Second guard clause will stop any further valve action for 12 hrs once max temp is hit (this also operates the counter)
        if self.max_temp_hit_delay > 0:
            self.max_temp_hit_delay -= 1
            return
        
        # Third guard clause checks for if we are at max water temp and if so - ensures valve is closed
        if sensors.water_temp >= self.config['max_water_temp']:
            self.close_valve()
            # If we hit the max temp, we are going to bypass any further valve actions for 12 hrs
            self.max_temp_hit_delay = 43200
            return
        
        # If the roof temp is above the current registered warm value, make sure it get opened, otherwise closed
        if sensors.roof_temp > sensors.water_temp + self.temp_range:
            self.open_valve()
        else:
            self.close_valve()
    
    def open_valve(self, delay=0):
        if self.position == 0:
            GPIO.output(VALVE_PIN, True)
            self.position = 1
            logging("Solar valve open!")
            self.last_valve_change = 0
            self.temp_range = self.config["temp_range_for_close"]
            self.delay=delay
            return True
        else:
            return False
            
    def close_valve(self, delay=0):
        if self.position == 1:
            GPIO.output(VALVE_PIN, False)
            self.position = 0
            logging("Solar valve closed!")
            self.last_valve_change = 0
            self.temp_range = self.config["temp_range_for_open"]
            self.delay=delay
            return True
        else:
            return False
    
    def data(self):
        return {"valve": self.position, 'delay': self.delay,
                    "last_change": self.last_valve_change, "set_temp": self.config['max_water_temp'],
                    "temp_range": self.temp_range, "max_hit_delay":self.max_temp_hit_delay}