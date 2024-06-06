import configparser

class Config:
    def __init__(self):
        """Start with default values, then look for config file"""
        self.config = configparser.ConfigParser()

        self.min_cycle_time = 90
        self.max_water_temp = 82
        self.temp_range_for_open= 20
        self.temp_range_for_close = 0
        self.seconds_cal = 1
        self._get_config()
        
    def _get_config(self):
        """Get the current config file"""
        self.config.read('config.ini')
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
    
    def _new_config_file(self):
        self.config = configparser.ConfigParser()
        self.config.add_section('var')
        self.config.set('var', 'min_cycle_time', '90')
        self.config.set('var', 'max_water_temp', '82')
        self.config.set('var', 'temp_range_for_open', '20')
        self.config.set('var', 'temp_range_for_close', '0')
        self.config.set('var', 'seconds_cal', '1')

        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    def _set_config(self):
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    def change_setting(self, setting, num):
        """Change one of the variables in the config file. Requires setting string and new setting number"""
        vars = self.config['var']
        vars[setting] = str(num)
        self._set_config()
    
    def data(self):
        return {"set_temp": self.max_water_temp, "min_cycle_time": self.min_cycle_time, "temp_range_for_open": self.temp_range_for_open,
                "temp_range_for_close": self.temp_range_for_close, "seconds_cal": self.seconds_cal}
