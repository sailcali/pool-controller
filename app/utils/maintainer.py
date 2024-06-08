# import threading
# import time
# import requests
# from. logging import logging

# class Maintainer(threading.Thread):
#     def __init__(self, sensors, valve):
#         super(Maintainer, self).__init__()
#         self.sensors = sensors
#         self.valve = valve
#         self.stop_sign = False
#         self.upload_flag = True

#     def standard_response(self):
#         return {"water_temp": self.sensors['water'].temp(), "roof_temp": self.sensors['roof'].temp(),
#             "valve": self.valve.current_state(), 'delay': self.valve.delay,
#             "last_change": self.valve.last_valve_change, "set_temp": self.valve.config.max_water_temp,
#             "temp_range": self.valve.temp_range, "max_hit_delay":self.valve.max_temp_hit_delay}

#     def run(self):
#         upload_seconds = 0
#         errors = 0
#         upload_errors = 0
#         while not self.stop_sign:
                
#                 if self.upload_flag:
#                     upload_seconds += 1
#                 # Wait time between cycles is about 1 second (accounts for run time)
                
#                 # Tracking the last valve change value
#                 self.valve.last_valve_change += 1
#                 # If manually changed, this is the counter to continue the programming
#                 if self.valve.delay > 0:
#                     self.valve.delay -= 1
#                 if errors > 0:
#                     errors -= 1
#                 if upload_errors > 0:
#                     upload_errors -= 1
#             except Exception as e:
#                 errors += 1
#                 logging(f"Pool valve error: {e}\n")
#                 if errors > 20:
#                     break
#         logging(f"Auto stopped!\n(stop_sign={self.stop_sign})")
