from typing import Union

from bson import ObjectId
from icecream import ic
from pydantic import BaseModel
from datetime import datetime, timedelta
from fastapi.exceptions import HTTPException

from elemental_tools.db.mongo import database, Index
from elemental_tools.logger import Logger
from elemental_tools.json import json_to_bson
from elemental_tools.config import db_url, database_name, log_path

collection_name = f'tasks'

_indexes = [
	Index(['sub', 'description'], unique=True, sparse=True),
]

collection = database.collection(collection_name)

database.set_indexes(collection_name, _indexes)
logger = Logger(app_name='api', owner=collection_name, destination=log_path).log


class TaskController:

	@staticmethod
	def add(doc: BaseModel):
		try:
			inserted_doc = collection.insert_one(json_to_bson(doc.model_dump()))

			if inserted_doc.inserted_id is None:
				raise HTTPException(detail='Cannot save task.', status_code=400)

			return inserted_doc.inserted_id

		except Exception as e:
			logger('error', f'Failed to store user because of exception: {str(e)}')

		return False

	@staticmethod
	def set_loop_count(_id: str, loops: int):
		logger('info', f'Setting loop count: {loops} for task _id: {str(_id)} ')

		selector = {'_id': _id}
		content = {"$set": {'loops': loops}}

		try:
			_update_result = collection.update_one(json_to_bson(selector), json_to_bson(content))
			if _update_result is None:
				raise HTTPException(detail='Cannot set task loop count.', status_code=400)

		except Exception as e:
			logger('error', f'Cannot set loop count for task because of exception: {str(e)}')
		return False

	@staticmethod
	def set_last_execution(_id):
		logger('info', f'Setting last execution for task _id: {str(_id)}')

		try:
			_current_date = datetime.now().isoformat()
			_update_result = database.collection(collection_name).update_one({'_id': ObjectId(_id)}, {"$set": {'last_execution': _current_date}})

			if not _update_result:
				raise Exception('Cannot set task last execution date.')

		except Exception as e:
			logger('error', f'Cannot set last execution for task because of exception: {str(e)}')

		return False

	@staticmethod
	def query_not_processed_tasks():

		_current_date = datetime.now().isoformat()
		_too_old = datetime.now() - timedelta(days=100)
		_pipeline_functions_counter = [
			{
				'$addFields': {
					'functionType': 'counter',
					'currentTime': {'$toLong': {"$toDate": str(_current_date)}},
					'tooOld': str(_too_old),
					'lastExecutionInMS': {'$toLong': {"$toDate": '$last_execution'}}
				}
			},
			{
				"$match": {
					"$and": [
						{'status': True},
						{"$or": [{'state': None}, {'state': {"$exists": False}}]},
						{'schedule_date': None},
						{'timer': {'$ne': None}},
						{'loops': {'$gt': 0}},
						{'$expr': {'$gte': [{'$subtract': ['$currentTime', '$lastExecutionInMS']}, '$timer']}}
					]
				}
			}
		]
		_pipeline_functions_infinite = [
			{
				'$addFields': {
					'functionType': 'infinite',
					'currentTime': {'$toLong': {"$toDate": str(_current_date)}},
					'tooOld': str(_too_old),
					'lastExecutionInMS': {'$toLong': {"$toDate": '$last_execution'}}
				}
			},
			{
				"$match": {
					"$and": [
						{'status': True},
						{"$or": [{'state': None}, {'state': {"$exists": False}}]},
						{"$or": [{'schedule_date': None}, {'schedule_date': {"$exists": False}}]},
						{'timer': {'$ne': None}},
						{"$or": [{'loops': None}, {'loops': {"$exists": False}}]},
						{'$expr': {'$gte': [{'$subtract': ['$currentTime', '$lastExecutionInMS']}, '$timer']}}
					]
				}
			}
		]
		_pipeline_functions_scheduled = [
			{
				'$addFields': {
					'functionType': 'scheduled',
					'currentTime': {'$toLong': {"$toDate": str(_current_date)}},
					'tooOld': str(_too_old),
					'lastExecutionInMS': {'$toLong': {"$toDate": '$last_execution'}}
				}
			},
			{
				"$match": {
					"$and": [
						{'status': True},
						{"$or": [{'state': None}, {'state': {"$exists": False}}]},
						{'schedule_date': {'$ne': None}},
						{'$expr': {'$gte': [{'$subtract': ['$currentTime', '$lastExecutionInMS']}, '$timer']}}
					]
				}
			}
		]

		# _all_loops = list(collection.aggregate(_pipeline_functions_infinite))
		_result = list(collection.aggregate(_pipeline_functions_infinite))

		_new_tasks = {"$and": [
			{'status': True},
			{"$or": [{'state': None}, {'state': {"$exists": False}}]},
			{"last_execution": {"$exists": False}}
		]}

		_result += list(collection.find(_new_tasks))

		ic(_result)
		return _result

	@staticmethod
	def set_status(_id: str, status: bool):
		logger('info', f'Setting status task _id: {str(_id)}')

		selector = {'_id': _id}
		content = {"$set": {'status': status}}

		try:
			update_result = collection.update_one(json_to_bson(selector), json_to_bson(content))
			if update_result is None:
				raise HTTPException(detail='Cannot set task status.', status_code=400)

		except Exception as e:
			logger('error', f'Cannot set task status because of exception: {str(e)}')

		return False

	@staticmethod
	def set_state(_id: str, state: Union[str, None] = None):
		logger('info', f'Setting state task _id: {str(_id)}')

		selector = {'_id': _id}
		content = {"$set": {'state': state}}

		try:
			update_result = collection.update_one(json_to_bson(selector), json_to_bson(content))
			if update_result is None:
				raise HTTPException(detail='Cannot set task state.', status_code=400)

		except Exception as e:
			logger('error', f'Cannot set task state because of exception: {str(e)}')

		return False

