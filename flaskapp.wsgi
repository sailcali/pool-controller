import sys 
import os
sys.path.insert(0, '/var/www/pool-controller')
from app import create_app
application = create_app()

