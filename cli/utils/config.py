import configparser
from datetime import datetime, date

class Config:
    def __init__(self, debug):
        """Start with default values, then look for config file"""
        self.config = configparser.ConfigParser()
        if debug:
            self.filename = "config/config.ini"
        else:
            self.filename = "/var/www/pool-controller/config/config.ini"
        
        self.min_cycle_time = 90 # Default to 90
        self.max_water_temp = 82 # Default to 82
        self.temp_range_for_open= 20 # Default to 20
        self.temp_range_for_close = 0 # Default to 0
        self.max_temp_hit_date = date.today().replace(day=date.today().day - 1) # Default to yesterday
        self.user_request = {"settled": True, "valve": False, "delay": 0} # Default is "settled, off, no delay"

        # LOCAL CONFIG ONLY, NOT REMOTELY EDITABLE
        self.near_open_temp_diff = 1

        # DEPRECATED
        self.seconds_cal = 1 # default to 1

        self.get_config()

    def get_config(self):
        """Get the current config file (on startup or change)"""
        self.config.read(self.filename)
        try:
            vars = self.config['var']
            request = self.config['request']
        except KeyError:
            self._new_config_file()
            vars = self.config['var']
            request = self.config['request']
            
        self.min_cycle_time = int(vars['min_cycle_time'])
        self.max_water_temp = int(vars['max_water_temp'])
        self.temp_range_for_open = int(vars['temp_range_for_open'])
        self.temp_range_for_close = int(vars['temp_range_for_close'])
        self.seconds_cal = int(vars['seconds_cal'])
        self.max_temp_hit_date = datetime.strptime(vars['max_temp_hit_date'], "%Y-%m-%d").date()
        
        if request['settled'] == "True":
            self.user_request = {"settled": True, "valve": False, "delay": 0}
        else:
            self.user_request['settled'] = False
            self.user_request['valve'] = True if request['valve'] == "True" else False
            self.user_request['delay'] = int(request['delay'])
    
    def _new_config_file(self):
        self.config = configparser.ConfigParser()
        self.config.add_section('var')
        self.config.set('var', 'min_cycle_time', str(self.min_cycle_time))
        self.config.set('var', 'max_water_temp', str(self.max_water_temp))
        self.config.set('var', 'temp_range_for_open', str(self.temp_range_for_open))
        self.config.set('var', 'temp_range_for_close', str(self.temp_range_for_close))
        self.config.set('var', 'seconds_cal', str(self.seconds_cal))
        self.config.set('var', 'max_temp_hit_date', datetime.strftime(self.max_temp_hit_date,"%Y-%m-%d"))

        self.config.add_section('request')
        self.config.set('request', 'settled', "True")
        self.config.set('request', 'valve', "False")
        self.config.set('request', 'delay', "0")

        with open(self.filename, 'w') as configfile:
            self.config.write(configfile)

    def _set_config(self):
        with open(self.filename, 'w') as configfile:
            self.config.write(configfile)

    def change_setting(self, setting=None, num=None, max_temp_hit=None):
        """Change one of the variables in the config file. Requires setting string and new setting number"""
        vars = self.config['var']
        if max_temp_hit is not None:
            vars['max_temp_hit_date'] = datetime.strftime(date.today(),"%Y-%m-%d")
        else:
            vars[setting] = str(num)
        self._set_config()
        self.get_config()
    
    def settle_user_change(self):
        """After user initiated valve change, adjust the config to settled"""
        request = self.config['request']
        request['settled'] = "True"
        self._set_config()
        self.get_config()

    def max_temp_today(self):
        """Returns True if max temp was hit today"""
        if self.max_temp_hit_date == date.today():
            return True
        else:
            return False

    def data(self):
        return {"set_temp": self.max_water_temp, "min_cycle_time": self.min_cycle_time, "temp_range_for_open": self.temp_range_for_open,
                "temp_range_for_close": self.temp_range_for_close, "seconds_cal": self.seconds_cal, "max_temp_hit_date": self.max_temp_hit_date}
