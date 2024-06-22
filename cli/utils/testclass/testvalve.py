from ..logging import logging

class TestValve:
    """Controller for the Solar Valve"""
    def __init__(self, min_cycle_time):

        # self.position = 0 # This is the requested position, not necessarily the ACTUAL position
        self.delay = 0 # User requested delay in programming
        self.last_valve_change = min_cycle_time # init @ min cycle time
        self.position = 0
        self.near_open = False

    def current_state(self):
        """Returns 0 or 1 for valve position"""
        return self.position

    def open_valve(self, delay):
        """Opens the valve if closed"""
        if self.current_state() == 0:
            # Open the valve
            self.position = 1
            
            # Set user requested delay
            if delay > 0:
                self.delay = delay

            # Reset the triggers and notify
            self.last_valve_change = 0 # reset the last valve change timer
            self.near_open = False # Reset the near_open FOR DISCORD NOTIFICATION
            logging("Solar valve open!")
            return True
        else:
            return False
            
    def close_valve(self, delay):
        """Closes the valve if open"""
        if self.current_state() == 1:
            # Open the valve
            self.position = 0

            # Set user requested delay
            if delay > 0:
                self.delay = delay
            
            #Reset the triggers and notify
            self.last_valve_change = 0 # Reset the last valve change timer
            logging("Solar valve closed!")
            return True
        else:
            return False
    
    def data(self):
        """Gathers all relavent data into a dictionary"""
        return {"valve": self.position, 'delay': self.delay, "last_change": self.last_valve_change}