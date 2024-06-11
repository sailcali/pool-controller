import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

VALVE_PIN = 17

class Valve:
    """Controller for the Solar Valve"""
    def __init__(self):
        GPIO.setup(VALVE_PIN, GPIO.OUT)
        GPIO.output(VALVE_PIN, False)

    def current_state(self):
        """Returns 0 or 1 for valve position"""
        return GPIO.input(VALVE_PIN)