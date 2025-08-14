from typing import Union

import pydantic
from bson import ObjectId
from icecream import ic
from pydantic import BaseModel

from elemental_tools.logger import Logger
from elemental_tools.db.mongo import database, Index
from fastapi import HTTPException

from elemental_tools.json import json_to_bson
from elemental_tools.config import db_url, log_path, database_name


class TemplateController:
	collection_name = f'templates'
	logger = Logger(app_name='controllers', owner=collection_name, destination=log_path).log

	_indexes = [
		Index(['title', 'sub'], unique=True),
	]


	collection = database.collection(collection_name)
	database.set_indexes(collection_name, _indexes)

	def __init__(self, timeout: int = None):
		self.timeout = 5
		if timeout is not None:
			self.timeout = timeout

		
	def add(self, doc: BaseModel):
		insert = self.collection.insert_one(json_to_bson(doc.model_dump()))

		_inserted_item = self.collection.find_one({"_id": insert.inserted_id})

		return _inserted_item

	def query(self, selector):
		result = None
		query_result = self.collection.find_one(json_to_bson(selector))
		if query_result:
			return query_result
		return result

	def select(self, selector: dict):
		return self.collection.find_one(json_to_bson(selector))

	def update(self, selector, content: BaseModel):
		self.logger('info', f'Updating Template Information for Selector: {selector} with: {str(content)} ')
		_update_result = None
		content = content.model_dump()
		_content = {"$set": json_to_bson(content)}

		try:
			_update_result = self.collection.update_one(json_to_bson(selector), json_to_bson(_content))

			if _update_result is None:
				raise HTTPException(detail='Cannot update template information.', status_code=400)

		except Exception as e:
			self.logger('error', f'Cannot update template information: {str(e)}')

		return _update_result

	def query_all(self, selector):
		result = None
		query_result = self.collection.find(json_to_bson(selector))
		if query_result:
			return query_result
		return result


class TemplateResourcesController:
	collection_name = f'templates_resources'
	logger = Logger(app_name='controllers', owner=collection_name, destination=log_path).log
	_indexes = [
		Index(['title', 'sub'], unique=True),
	]
	collection = database.collection(collection_name)
	database.set_indexes(collection_name, _indexes)
	insert_many = collection.insert_many

	def __init__(self, timeout: int = None):
		self.timeout = 5
		if timeout is not None:
			self.timeout = timeout

		
	def add(self, doc: pydantic.BaseModel):
		insert = self.collection.insert_one(json_to_bson(doc.model_dump()))

		_inserted_item = self.collection.find_one({"_id": insert.inserted_id})

		return _inserted_item

	def query(self, selector):
		result = None
		query_result = self.collection.find_one(json_to_bson(selector))
		if query_result:
			return query_result
		return result

	def select(self, selector: dict):
		return self.collection.find_one(json_to_bson(selector))

	def update(self, selector, content: BaseModel):
		self.logger('info', f'Updating Template Information for Selector: {selector} with: {str(content)} ')
		_update_result = None
		_content = {"$set": content.model_dump()}

		try:
			_update_result = self.collection.update_one(json_to_bson(selector), json_to_bson(_content))

			if _update_result is None:
				raise HTTPException(detail='Cannot update template information.', status_code=400)

		except Exception as e:
			self.logger('error', f'Cannot update template information: {str(e)}')

		return _update_result

	def query_all(self, sub: ObjectId, parent_sub: Union[ObjectId, None] = None, siblings: Union[list, None] = None):

		_pipeline_resources = [
			{
				"$match": {
					"$or": [
						{"sub": sub},
						{"sub": {"$exists": False}},
						{"sub": parent_sub},
						{"$and": [{"sub": {"$in": [sib for sib in siblings]}}, {"global": True}]},
					]
				}
			},
			{
				"$sort": {"creation_date": -1}
			}
		]

		result = None
		
		query_result = self.collection.aggregate(json_to_bson(_pipeline_resources))
		if query_result:
			return query_result
		return result

	def select_all(self, selector):
		result = None
		query_result = self.collection.find(json_to_bson(selector))
		if query_result:
			return query_result
		return result

