import os
import sys
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options
import random
import string

from elemental_tools.logger import Logger

module_name = 'config'

app_name = 'jarvis'

# load cache into class
cache_file = '.cache'

if sys.platform == "darwin" or sys.platform == "win32":
    envi = 'debug'
else:
    envi = 'production'


logger = Logger(
    app_name=app_name,
    owner='initialization',
    # destination=log_path
).log

logger('info', 'Setting Environment (debug, production) based on platform')
if sys.platform == "darwin" or sys.platform == "win32":
    envi = 'debug'
else:
    envi = 'production'
logger('success', 'The current environment is set to ' + envi)


class Cache:

    def __init__(self, file: str = cache_file):
        self.cache_file = file

        if not os.path.isdir(os.path.dirname(os.path.abspath(cache_file))):
            os.makedirs(os.path.dirname(os.path.abspath(cache_file)), exist_ok=True)

        self.cache_file_content = open(cache_file, 'a+')
        if self.cache_file_content.readlines():
            self.cache_file_content = self.load()
            try:
                data = eval(self.cache_file_content.read())
                for cache_item in data:
                    for title, value in cache_item.items():
                        setattr(self, title, value)

            except SyntaxError:
                raise Exception("Failed to parse the cache file!")

    def save(self):
        self.cache_file_content.write(
            str([{title: value for title, value in self.__dict__.items() if not title.startswith('__')}]))
        self.cache_file_content.close()
        return open(cache_file, 'a+')

    def load(self):
        return open(self.cache_file, 'a+')

    def get(self, prop):
        return getattr(self, prop, None)


logger('info', 'Loading .env file...')
load_dotenv()
logger('success', '.env file loaded successfully!')
webdriver_url = os.environ.get('WEBDRIVER_URL', 'http://localhost:4444/')


def default_tax():
    logger('info', 'Retrieving tax information...')
    load_dotenv()
    tax = float(os.environ.get('TAX'))
    logger('success', f'The defined tax is: {tax}')
    return tax


logger('info', 'Setting up configuration variables...')

app_name = os.environ.get('APP_NAME', 'jarvis')

db_url = os.environ.get('DB_URL', None)
database_name = os.environ.get('DB_NAME', str(app_name + f"_{envi}"))
db_user = os.environ.get('DB_USERNAME')
db_pass = os.environ.get('DB_PASSWORD')

webhook_db_url = os.environ.get('WEBHOOK_DB_URL', None)
webhook_database_name = os.environ.get('WEBHOOK_DB_NAME', str("webhook"))

wpp_phone_number_id = os.environ.get('WPP_PHONE_NUMBER_ID', None)
wpp_api_token = os.environ.get('WPP_API_TOKEN', None)

binance_key = os.environ.get('BINANCE_KEY', None)
binance_secret = os.environ.get('BINANCE_KEY', None)

chrome_data_dir = os.environ.get('CHROME_USER_DATA_DIR', '/tmp')


logger('success', 'The configuration variables were successfully set.')

logger('info', 'Initializing Chrome configuration')
chrome_options = Options()
chrome_options.add_argument("start-maximized")
user_data_dir = ''.join(random.choices(string.ascii_letters, k=8))
chrome_options.add_argument("--disable-gpu")  # Disable GPU
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--disable-dev-shm-usage")

logger('success', 'Chrome was configured successfully!')
