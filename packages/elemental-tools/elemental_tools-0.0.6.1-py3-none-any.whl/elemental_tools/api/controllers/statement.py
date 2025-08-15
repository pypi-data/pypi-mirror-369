from datetime import datetime
from typing import Union

from bson import ObjectId
from pymongo.errors import BulkWriteError

from elemental_tools.db.mongo import database, Index
from elemental_tools.logger import Logger
from elemental_tools.json import json_to_bson
from elemental_tools.config import db_url, log_path, database_name

_index_cache = []


class StatementController:
	collection_name_processed_files = f'processed_files'
	collection_name_statement = f'statement'
	logger = Logger(app_name='controllers', owner=collection_name_statement, destination=log_path).log

	def __init__(self, sub: ObjectId, institution_id: Union[ObjectId, None] = None):

		self.database = database
		self.sub, self.institution_id = sub, institution_id

		self.processed_files = self.database.collection(self.collection_name_processed_files)
		self.statement = self.database.collection(self.collection_name_statement)

		_processed_files_index = Index(['date', 'filename', 'sub', 'institution_id'], unique=True)
		if _processed_files_index not in _index_cache:
			try:
				self.database.set_index(collection_name=self.collection_name_processed_files,
										_index_specs=_processed_files_index)
				_index_cache.append(_processed_files_index)
			except:
				pass

		_statement_index = Index(['date', 'sub', 'institution_id', 'value', 'type'], unique=True)
		if _statement_index not in _index_cache:
			try:
				_statement_index = Index(['date', 'sub', 'institution_id', 'value', 'type'], unique=True)
				self.database.set_index(collection_name=self.collection_name_statement, _index_specs=_statement_index)
			except:
				pass

			_index_cache.append(_statement_index)

	def save_processed_csv(self, filename):

		_doc = {
			'date': datetime.now().isoformat(),
			'filename': filename,
			'sub': self.sub,
			'institution_id': self.institution_id
		}

		try:
			insert_result = self.processed_files.insert_one(json_to_bson(_doc))

			if insert_result.inserted_id:
				return insert_result.inserted_id

		except:
			self.logger('critical', "Cannot save processed csv")

		return False

	def retrieve_processed_csv(self, filename):

		try:
			self.logger('info', f"Looking for processed file: {filename} ")

			_selector = {
				"$and": [
					{"filename": filename},
					{"sub": self.sub},
					{"institution_id": self.institution_id}
				]
			}

			_result = self.processed_files.find_many(_selector)

			return _result

		except:
			self.logger('alert', "File already processed!")

	def save_statement_from_df(self, df):
		_df = df
		self.logger('info', f"Saving statement from dataframe: {_df.head()}")
		_df.rename(columns={'Data': 'date', 'Descrição': 'name', 'Valor': 'value'}, inplace=True)

		_df = df.dropna()
		_df = _df.drop_duplicates()

		_df['institution_id'] = self.institution_id
		_df['sub'] = self.sub
		_df['type'] = df['value'].apply(lambda x: 'income' if x > 0 else 'outcome' if x < 0 else 'neutral')

		print(f"saving {_df}")

		_update_result = False

		_df_dict = _df.to_dict(orient='records')

		try:
			_update_result = self.statement.insert_many(_df_dict, ordered=False)

		except BulkWriteError as e:
			_df_len = len(_df_dict)
			_n_errors = e.details['nInserted'] - _df_len

			if not e.details['nInserted']:
				self.logger('critical', f'No records were inserted!')

			self.logger('alert', f'Duplicate Found: {abs(_n_errors)}, Inserted: {e.details["nInserted"]}')

		if _update_result:
			self.logger('success', "Statements were saved successfully.")

	def retrieve_statement(self, _type='income', today=None, status=None, time_interval=None):
		self.logger('info', "Retrieving Statement...")

		selector = {"$and": [
			{"sub": self.sub},
			{"type": _type},
		]}

		if status is not None:
			_status_condition = dict(status=status)
		else:
			_status_condition = {"status": {'$exists': False}}

		selector['$and'].append(_status_condition)

		if self.institution_id is not None:
			selector['$and'].append(dict(institution_id=self.institution_id))

		if today is not None:
			if today:
				# Get today's date
				today_date = datetime.today().date()
				# Calculate the start and end of the day
				start_of_day = f"{today_date}T00:00:00Z"
				end_of_day = f"{today_date}T23:59:59Z"
				selector["date"] = {"$gte": start_of_day, "$lte": end_of_day}
			elif time_interval is not None and len(time_interval) == 2:
				start_date, end_date = time_interval
				selector["date"] = {"$gte": start_date, "$lte": end_date}

		try:
			self.logger('alert', f'Querying selector: {selector}')
			result = self.statement.find(json_to_bson(selector))

			if result is None:
				self.logger('error', f'Could not find statement information for selector: {selector}')

			self.logger('success', "Statements were successfully retrieved.")
			return result

		except Exception as e:
			print(e)
			self.logger('critical', "Cannot retrieve statement!")

	def update(self, selector, content):
		self.logger('info', f'Updating Statement Information with: {str(content)} ')
		_update_result = None
		_content = {"$set": json_to_bson(content)}

		try:
			_update_result = self.statement.update_many(selector, _content)

			return _update_result.upserted_id

		except Exception as e:
			self.logger('error', f'Cannot update statement information: {str(e)}')

		return _update_result

	def retrieve_institution_ids(self):

		_pipeline_institution_ids = [
			{
				'$match': {
					"sub": self.sub
				}
			},
			{
				'$group': {
					'_id': '$institution_id'
				}
			}, {
				'$project': {
					'institution_id': '$_id',
					'_id': 0
				}
			}
		]

		_result = self.statement.aggregate(_pipeline_institution_ids)

		return list(_result)



