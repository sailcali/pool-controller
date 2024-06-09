import configparser
from datetime import datetime, date
import os

DEBUG = os.environ.get("FLASK_DEBUG")

if DEBUG == "True":
    FILENAME = "config/config.ini"
else:
    FILENAME = "/var/www/pool-controller/config/config.ini"


class Config:
    def __init__(self):
        """Start with default values, then look for config file"""
        self.config = configparser.ConfigParser()
        
        self.min_cycle_time = 90 # Default to 90
        self.max_water_temp = 82 # Default to 82
        self.temp_range_for_open= 20 # Default to 20
        self.temp_range_for_close = 0 # Default to 0
        self.seconds_cal = 1 # default to 1
        self.max_temp_hit_date = date.today().replace(day=date.today().day - 1) # Default to yesterday
        # self.max_temp_hit_date = datetime.now(tz=pytz.timezone('US/Pacific')).date() - timedelta(days=1) # default to yesterday
        self._get_config()

    def _get_config(self):
        """Get the current config file"""
        self.config.read(FILENAME)
        try:
            vars = self.config['var']
        except KeyError:
            self._new_config_file()
            vars = self.config['var']
            
        self.min_cycle_time = int(vars['min_cycle_time'])
        self.max_water_temp = int(vars['max_water_temp'])
        self.temp_range_for_open = int(vars['temp_range_for_open'])
        self.temp_range_for_close = int(vars['temp_range_for_close'])
        self.seconds_cal = int(vars['seconds_cal'])
        self.max_temp_hit_date = datetime.strptime(vars['max_temp_hit_date'], "%Y-%m-%d").date()
    
    def _new_config_file(self):
        self.config = configparser.ConfigParser()
        self.config.add_section('var')
        self.config.set('var', 'min_cycle_time', str(self.min_cycle_time))
        self.config.set('var', 'max_water_temp', str(self.max_water_temp))
        self.config.set('var', 'temp_range_for_open', str(self.temp_range_for_open))
        self.config.set('var', 'temp_range_for_close', str(self.temp_range_for_close))
        self.config.set('var', 'seconds_cal', str(self.seconds_cal))
        self.config.set('var', 'max_temp_hit_date', datetime.strftime(self.max_temp_hit_date,"%Y-%m-%d"))

        with open(FILENAME, 'w') as configfile:
            self.config.write(configfile)

    def _set_config(self):
        with open(FILENAME, 'w') as configfile:
            self.config.write(configfile)

    def change_setting(self, setting=None, num=None, max_temp_hit=None):
        """Change one of the variables in the config file. Requires setting string and new setting number"""
        if max_temp_hit is not None:
            vars['max_temp_hit_date'] = datetime.strftime(date.today(),"%Y-%m-%d")
        else:
            vars = self.config['var']
            vars[setting] = str(num)
        self._set_config()
        self._get_config()
    
    def data(self):
        return {"set_temp": self.max_water_temp, "min_cycle_time": self.min_cycle_time, "temp_range_for_open": self.temp_range_for_open,
                "temp_range_for_close": self.temp_range_for_close, "seconds_cal": self.seconds_cal, "max_temp_hit_date": self.max_temp_hit_date}
