import certifi

from elemental_tools.config import db_url, database_name
from elemental_tools.logger import Logger
from pymongo import MongoClient, IndexModel, UpdateOne
from pymongo.server_api import ServerApi

# internal modules

# index management:
index_cache = []


class Index:

	fields: list
	unique: bool = False
	order = 'asc'
	sparse: bool = True

	def __init__(self, fields: list, unique: bool = False, order: str = 'asc', sparse: bool = True, **kwargs):

		"""
		Model for Index Dictations.
		:param fields: List of fields included in the index.
		:param unique: Bool indicating presence of unique or not unique constraint. (Default: False).
		:param order: (Default: asc). Available Options (asc, desc). Indicates order for the current field presentation, useful with dates and other information that must be presented first and loaded faster.
		:param sparse: (Default: True). Available Options (True, False). Indicates when null or None values must be ignored by the current index.
		"""

		self.fields = fields
		self.unique = unique
		self.order = order

		self.sparse = True

		self.kwargs = kwargs


class Connect:
	def __init__(self, uri: str, database: str, environment: str = None):

		"""
		Initialize the Database Connection.
		:param uri: The URL or URI to the Mongo Cluster you want to connect.
		:param environment: (Optional) Controls the tlsCAFile certification location. Available Options: 'debug' or 'production'. (default is None).

		"""
		self.logger = Logger(app_name='database', owner='mongo').log
		self.logger(level='info', message=f'Connecting to:\n\tURI: {uri}\n\tDatabase: {database}')
		self.mongo_client = MongoClient(uri, server_api=ServerApi('1'))

		if environment is not None:
			if environment == 'debug':
				self.mongo_client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())

		self.db = self.mongo_client[database]

		try:
			self.mongo_client.admin.command('ping')
			self.logger(level='success', message=f'Connected!')
		except Exception as e:
			self.logger(level='critical-error', message=f'Failed to Connect!')
			raise e

	def collection(self, collection_name):
		"""
		Initialize the Collection.
		:param collection_name: The name for the collection.

		:return success: Returns collection for the given collection name
		:return failure: Returns None
		"""

		try:
			self.logger(level='info', message=f'Accessing Collection: {collection_name}')
			collection_name = f'{collection_name}'
			collection = self.db[collection_name]
			self.logger(level='success', message=f'Collection Loaded!')
		except:
			self.logger(level='critical-error', message=f'Collection Not Found!')
			return None

		return collection

	def set_indexes(self, collection_name, _indexes_specs: list[Index]):
		"""
		Load a list of indexes and apply to the desired collection.
		:param collection_name: The name for the collection.
		:param _indexes_specs: A List of Index, that you can generate with the Class: Index imported from this same module.

		:return success: Returns True
		:return failure: Returns None
		"""

		for _index in _indexes_specs:

			self.set_index(collection_name, _index)


		return True

	def set_index(self, collection_name, _index_specs: Index):

		"""
		Load a list of indexes and apply to the desired collection.
		:param collection_name: The name for the collection.
		:param _index_specs: A single Index, that you can generate with the Class: Index imported from this same module.

		:return success: Returns True
		:return failure: Returns None
		"""

		if _index_specs.order == 'asc':
			_index_specs.order = 1
		else:
			_index_specs.order = -1

		_index = [
			IndexModel([(_i, _index_specs.order) for _i in _index_specs.fields], unique=_index_specs.unique, sparse=_index_specs.sparse, **_index_specs.kwargs),
		]

		self.logger(level='info', message=f'Applying Index:\n\tCollection: {collection_name}\n\tIndex: {_index_specs.__dict__}')
		self.collection(collection_name).create_indexes(_index)
		self.logger(level='success', message=f'Index Applied!')

		return True


database = Connect(db_url, database_name)
