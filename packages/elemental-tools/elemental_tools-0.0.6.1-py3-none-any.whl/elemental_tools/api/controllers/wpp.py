from elemental_tools.logger import Logger
from elemental_tools.db.mongo import database, Index
from fastapi import HTTPException

from elemental_tools.json import json_to_bson
from elemental_tools.config import db_url, log_path, database_name


_indexes = [
			Index(['cellphone', 'msg_id'], unique=True, sparse=True),
			Index(['wpp_user_id', 'msg_id'], unique=True, sparse=True),
		]


class WppController:
	collection_name = f'wpp'
	logger = Logger(app_name='controllers', owner=collection_name, destination=log_path).log
	collection = database.collection(collection_name)
	database.set_indexes(collection_name, _indexes)

	def __init__(self, timeout: int = None):
		self.timeout = 5
		if timeout is not None:
			self.timeout = timeout

	def add(self, doc):
		insert = self.collection.insert_one(json_to_bson(dict(doc)))

		_inserted_item = self.collection.find_one({"_id": insert.inserted_id})

		return _inserted_item

	def query(self, selector):
		result = None
		query_result = self.collection.find(json_to_bson(selector))
		if query_result:
			return query_result
		return result

	def select(self, selector: dict):
		return self.collection.find_one(json_to_bson(selector))

	def update(self, selector, content):
		self.logger('info', f'Updating User Information for Selector: {selector} with: {str(content)} ')
		_update_result = None
		_content = {"$set": json_to_bson(content)}

		try:
			_update_result = self.collection.update_one(json_to_bson(selector), json_to_bson(_content))

			if _update_result is None:
				raise HTTPException(detail='Cannot update user information.', status_code=400)

		except Exception as e:
			self.logger('error', f'Cannot update user information: {str(e)}')

		return _update_result
