from datetime import datetime

from bson import ObjectId
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel
from pydantic import Field

from elemental_tools.api.settings import SettingsController
from elemental_tools.config import log_path, root_user
from elemental_tools.db.mongo import database, Index
from elemental_tools.json import json_to_bson
from elemental_tools.logger import Logger
from elemental_tools.types import PyObjectId

collection_name = f'transaction'


_indexes = [
	Index(['sub', 'status', 'amount_from', 'amount_to', 'price', 'currency_from', 'currency_to', 'creation_date'],
		  unique=True, sparse=True),
]


def get_cooldown():
	settings = SettingsController()
	return str(settings.get(sub=root_user, name='transaction_cooldown', default=5))


class TransactionRequestModel(BaseModel, arbitrary_types_allowed=True):
	creation_date: str = Field(default_factory=datetime.now().isoformat)
	sub: PyObjectId
	currency_from: str = "BRL"
	currency_to: str = "USDT"
	price: float = None
	amount_from: float = None
	amount_to: float = None


class TransactionController:
	logger = Logger(app_name='controllers', owner=collection_name, destination=log_path).log

	collection = database.collection(collection_name)
	database.set_indexes(collection_name, _indexes)

	def add(self, transaction: TransactionRequestModel):
		try:
			self._remove_old_transactions(transaction)
			self.collection.insert_one(json_to_bson(transaction.model_dump()))
			return transaction
		except Exception as e:
			self.logger('error', f'Cannot add transaction: {str(vars(transaction))} because of exception: {str(e)}')

	def _remove_old_transactions(self, transaction: TransactionRequestModel):

		_selector_user_old_transactions = {
			"$and": [
				{"sub": transaction.sub},
				{"status": {"$exists": False}},
				{"processed": {"$exists": False}},
				{"exported": {"$exists": False}}
			]
		}

		_user_old_transactions = self.collection.find(_selector_user_old_transactions)
		_user_old_transactions = list(_user_old_transactions)

		if len(_user_old_transactions):
			for old_transaction in _user_old_transactions:
				self.collection.delete_many({"_id": old_transaction["_id"]})

		else:
			self.logger('alert', f'Remove old transaction skipping, since no old transactions were found.')

	def query(self, selector):
		result = None
		result = self.collection.find(json_to_bson(selector))
		if result:
			return result

	def close_transaction(self, transaction: TransactionRequestModel):

		_cooldown_date = datetime.now() - relativedelta(minutes=int(get_cooldown()))

		_pipeline_transactions = [
			{
				'$addFields': {
					'transactionType': 'open',
					"five_min_ms": {"$toLong": {"$toDate": str(_cooldown_date)}},
					'creation_date_isoformat': {"$toLong": {"$toDate": '$creation_date'}}
				}
			},
			{
				"$match": {
					"$and": [
						{"status": {"$exists": False}},
						{"sub": transaction.sub},
						{'$expr': {'$lte': ["$five_min_ms", "$creation_date_isoformat"]}}
					]
				}
			},
			{
				'$sort': {
					'creation_date': 1
				}
			}
		]

		try:
			
			_current_transaction_list = self.collection.aggregate(_pipeline_transactions)
			_current_transaction_list = list(_current_transaction_list)
			self.logger("info", f"user transaction: {_current_transaction_list}")
			if len(_current_transaction_list):
				_now = datetime.now().isoformat()

				_result = self.collection.update_one({"_id": ObjectId(_current_transaction_list[0]['_id'])},
													 {"$set": {"status": True, "date": str(_now)}})
				if _result.modified_count:
					self.logger('success', f"Transaction closed: {_current_transaction_list[0]}")
					return _current_transaction_list[0]

		except Exception as e:
			self.logger('alert', f'Cannot get transaction because of exception: {e}')

		return False

	def get_to_export_transactions(self, sub):
		try:
			_pipeline_to_export_transactions = [
				{
					'$match': {
						"$and": [
							{"sub": sub},
							{"exported": {"$exists": False}},
							{"status": True}
						]}
				},
				{
					'$sort': {
						'creation_date': 1
					}
				}
			]

			_current_transaction_list = self.collection.aggregate(_pipeline_to_export_transactions)
			_current_transaction_list = list(_current_transaction_list)
			self.logger("info", f"user transactions list: {_current_transaction_list}")
			if len(_current_transaction_list):
				return _current_transaction_list

		except Exception as e:
			self.logger('alert', f'Cannot get transaction because of exception: {e}')

		return False

	def set_exportation_status(self, transaction_ids: list):
		selector = {"_id": {"$in": transaction_ids}}
		_current_transaction_list = self.collection.find(json_to_bson(selector))
		_closed_date = datetime.now().isoformat()
		_result = self.collection.update_one(selector, {"$set": {"exported": True, "date": _closed_date}})

		if _result.modified_count:
			self.logger('success', f"Transaction exported example: {_current_transaction_list[0]}")
			return _current_transaction_list[0]
