from ..logging import logging

class TestValve:
    """Controller for the Solar Valve"""
    def __init__(self, min_cycle_time):

        # self.position = 0 # This is the requested position, not necessarily the ACTUAL position
        self.delay = 0 # User requested delay in programming
        self.last_valve_change = min_cycle_time # init @ min cycle time
        self.position = 0
    def current_state(self):
        """Returns 0 or 1 for valve position"""
        return self.position

    def open_valve(self):
        """Opens the valve if closed"""
        if self.current_state() == 0:
            # Open the valve
            self.position = 1
            
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
            self.position = 0
            
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
        return {"valve": self.position, 'delay': self.delay, "last_change": self.last_valve_change}