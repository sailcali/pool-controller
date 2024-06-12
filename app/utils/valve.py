import RPi.GPIO as GPIO
from app.utils.config import Config as CONFIG

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

VALVE_PIN = 17

class Valve:
    """Controller for the Solar Valve"""
    def __init__(self):
        GPIO.setup(VALVE_PIN, GPIO.OUT)
        GPIO.output(VALVE_PIN, False)

    def open_valve(self, delay):
        CONFIG.request_user_change(True, delay)

    def close_valve(self, delay):
        CONFIG.request_user_change(False, delay)

    def current_state(self):
        """Returns 0 or 1 for valve position"""
        return GPIO.input(VALVE_PIN)