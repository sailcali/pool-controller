
import configparser
config = configparser.ConfigParser()
config.read('confi.ini')

print(config['var'])



