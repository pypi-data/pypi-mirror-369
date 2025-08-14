import os
import pathlib

from elemental_tools.api.settings import SettingsController
from elemental_tools.config import root_user
from elemental_tools.json import json_to_temp_file
from elemental_tools.logger import Logger
from google.oauth2.service_account import Credentials
from elemental_tools.path import Relative


relative = Relative(__file__).relative

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

__logger__ = Logger(app_name='scripts', owner='google-sync').log
settings = SettingsController()

try:

    google_credentials = Credentials.from_service_account_info(
        settings.get(sub=root_user, name='google_api_credentials_json'),
        scopes=scopes
    )

    __logger__('info-error', "Google credentials has been loaded.")
except Exception as e:

    google_credentials = Credentials.from_service_account_info(
        settings.get(sub=root_user, name='google_api_credentials_json'),
        scopes=scopes
    )
    __logger__('critical-error', str(e))
