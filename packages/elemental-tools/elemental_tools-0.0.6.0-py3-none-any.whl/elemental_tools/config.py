import os
import sys

from dotenv import load_dotenv
from elemental_tools.logger import Logger

# initialize log
log_path = os.environ.get("LOG_PATH", default=None)
logger = Logger(app_name='api', owner='config', destination=log_path).log

# load dot env
logger('info', 'Loading .env file...')
load_dotenv()
logger('success', '.env file loaded successfully!')


logger('info', 'Setting up configuration variables...')


# api config
root_user = 'root'
host = os.environ.get('HOST', '127.0.0.1')
port = int(os.environ.get('PORT', 10200))

app_name = os.environ.get('APP_NAME', 'elemental_api')
envi = os.environ.get('ENVIRONMENT', None)
webdriver_url = os.environ.get('WEBDRIVER_URL', 'http://localhost:4444/')
db_url = os.environ.get('DB_URL', None)

csv_path = os.environ.get("CSV_PATH", "./csv")

thread_limit = 10
enable_grid = os.environ.get('ENABLE_GRID', False)
database_name = os.environ.get('DB_NAME', str(app_name + f"_{envi}"))

download_path = os.environ.get('DOWNLOAD_PATH', '/tmp/downloads')
enable_local_adb = os.environ.get('ENABLE_LOCAL_ADB', False)

logger('success', 'The configuration variables were successfully set.')



logger('info', 'Loading secrets and keys, shhh...')
binance_key = os.environ.get('BINANCE_KEY', None)
binance_secret = os.environ.get('BINANCE_SECRET', None)

b4u_url = os.environ.get('B4U_API_URL', None)
b4u_key = os.environ.get('B4U_API_KEY', None)
b4u_secret = os.environ.get('B4U_API_SECRET', None)
logger('success', 'The configuration variables were successfully set.')











if not os.path.isdir(download_path):
    os.makedirs(download_path, exist_ok=True)


logger('info', 'Setting Environment (debug, production) based on platform')
if envi is None:
    if sys.platform == "darwin" or sys.platform == "win32":
        envi = 'debug'
    else:
        envi = 'production'
logger('success', 'The current environment is set to ' + envi)
