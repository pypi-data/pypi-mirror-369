import os.path
from typing import Any, Union

from bson import ObjectId
from pydantic import BaseModel, Field

from elemental_tools.config import root_user
from elemental_tools.db.mongo import database, Index
from elemental_tools.json import json_to_bson
from elemental_tools.logger import Logger

if "install" in __name__:
	logger = Logger(app_name=f'{os.path.basename(__name__)}', owner='installation').log
else:
	logger = Logger(app_name=f'{os.path.basename(__name__)}', owner='settings').log

from elemental_tools.exceptions import SettingMissing

collection_name = f'settings'
collection = database.collection(collection_name)

_setting_indexes = [Index(['name', 'sub'], unique=True, sparse=True)]

database.set_indexes(collection_name, _setting_indexes)


class Setting(BaseModel):
	name: str = Field(description="Setting Name")
	value: Any = Field(description="Setting Value", default=None)

	"""
	Default setting class
	:param name: The name of the setting
	:param value: The value of the setting
	"""


class SettingsController:
	"""
	Manipulates settings class
	"""

	def __init__(self, _collection=collection):
		self._collection = _collection

	def set(self, sub, _setting: Setting):
		try:
			# parse the document

			_update_selector = {
				"$and": [
					{"name": _setting.name},
					{"sub": sub}
				]
			}

			_update_content = {
				"$set": _setting.model_dump()
			}

			insert = self._collection.update_one(json_to_bson(_update_selector), json_to_bson(_update_content), upsert=True)

			return insert

		except Exception as e:
			logger('error', f'Failed to store Setting because of exception: {str(e)}')

		return False

	def get(self, sub, name, ignore_default=None, **kwargs):
		result = None
		try:
			selector = {"$and": [{"name": name}, {"sub": sub}]}
			result = self._collection.find_one(json_to_bson(selector))['value']
			return result
		except:
			if not kwargs.items() and ignore_default is not None:
				raise SettingMissing(name)
			else:
				if result is None:
					try:
						result = kwargs['default']
					except KeyError:
						raise SettingMissing(name)

		return result


# INSTALL
class SettingsInstaller:

	def __init__(self, _settings=SettingsController()):
		self._settings = _settings

		self.google_sheet_users_root_folder_id = Setting(name="google_sheet_users_root_folder_id", value="")
		self.google_sheet_default_permissions = Setting(name="google_sheet_default_permissions", value=[])
		self.transaction_cooldown = Setting(name='transaction_cooldown', value=5)
		self.google_api_credentials_json = Setting(name="google_api_credentials_json", value={})

	def check(self):

		for _name, _value in vars(self).items():
			if _name.startswith("_"):
				continue

			try:
				self._settings.get(root_user, _name, ignore_default=True)

			except:
				logger('alert', f"Default configuration: {_name} was not found at settings database.")

				try:
					logger('installing', f"Installing {_name}...")
					self._settings.set(root_user, getattr(self, _name))
				except:
					raise Exception(f'Default configuration {_name} was not set, please reinstall or update.')


def default_tax(parent_id: Union[str, ObjectId] = root_user):
	settings = SettingsController()

	logger('info', 'Retrieving Tax Information...')
	tax = settings.get(sub=parent_id, name='crypto_default_taxes', default=0.0065)
	logger('success', f'The defined tax is: {tax}')

	return tax