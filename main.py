# from datetime import datetime, timedelta, date
# import configparser
# import pytz

# config = configparser.ConfigParser()
# today = date.today()
# today = today.replace(day=today.day - 1)

# print(today)
# config.add_section('var')
# config.set('var', 'min_cycle_time', '90')
# config.set('var', 'max_water_temp', '82')
# config.set('var', 'temp_range_for_open', '20')
# config.set('var', 'temp_range_for_close', '0')
# config.set('var', 'seconds_cal', '1')
# config.set('var', 'max_temp_hit_date', str(today))

# with open('configtest.ini', 'w') as configfile:
#     config.write(configfile)

# config.read('configtest.ini')

# vars = config['var']
# last_max = datetime.strptime(vars['max_temp_hit_date'],'%Y-%m-%d').date()
# print(datetime.strftime(last_max, "%Y-%m-%d"))

