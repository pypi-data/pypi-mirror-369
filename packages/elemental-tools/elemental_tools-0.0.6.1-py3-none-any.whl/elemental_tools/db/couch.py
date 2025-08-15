from cloudant.client import CouchDB
from cloudant.result import Result, ResultByKey
from time import sleep

from elemental_tools.db.exceptions import InsertException, Mismatch


class CollectionAbstraction:
	timeout = 10

	def __init__(self, connection):
		self.connection = connection

	def find_one(self, selector):
		# Find the first document matching the selector
		result = self.connection.get_query_result(selector)
		try:
			return next((e for e in result))
		except StopIteration:
			return None

	def find_many(self, selector):
		# Find all documents matching the selector
		return list(self.connection.get_query_result(selector))

	def insert(self, doc, upsert=False, upsert_selector: dict = None, constraints: list = None):

		if constraints:
			for constraint in constraints:
				if len(self.connection.get_query_result(constraint).all()):
					raise ValueError("Duplicate constraint for %s" % constraint)

		if upsert and upsert_selector is None:
			raise Exception('You must specify a upsert_selector')

		# Check if the document already exists
		existing_doc = None
		if upsert_selector:
			existing_doc = self.find_one({"_id": doc["_id"]})

		if existing_doc is not None:
			if upsert and upsert_selector:
				# Update the existing document
				existing_doc.update(doc)
				self.connection.save(existing_doc)
				return existing_doc
			else:
				return None
		else:
			# Insert the new document
			_doc = self.connection.create_document(doc)
			if '_rev' in _doc.keys():
				_doc.save()
				return _doc
			else:
				return None

	def insert_many(self, docs, constraints: list = None):

		if constraints is not None:
			for constraint in constraints:
				if len(self.connection.get_query_result(constraint).all()):
					raise ValueError("Duplicate constraint for %s" % constraint)

		return (doc for doc in self.connection.bulk_docs(docs))

	def update(self, selector, update_fields, upsert=False, chunk_size=2000):
		# Check if the document already exists
		existing_docs = self.connection.get_query_result(selector)

		_exists = False
		_change = False
		_chunk_pos = 0
		_chunk_end = chunk_size

		_deleted_ids = []
		update_result = []
		existing_docs_list = list(existing_docs)

		while len(existing_docs_list) >= _chunk_pos:

			_update_result = []
			_exists = True

			_current_chunk = existing_docs_list[_chunk_pos:_chunk_end]

			# delete all existing documents for these chunk
			_to_be_deleted_list = [{**doc, "_deleted": True} for doc in list(_current_chunk) if doc["_id"] not in _deleted_ids]
			_deleted_docs = self.connection.bulk_docs(_to_be_deleted_list)
			_deleted_ids += [update_doc["id"] for update_doc in _deleted_docs if "ok" in update_doc.keys()]

			_update_chunk = []
			# starts the update process...
			for _doc in list(_current_chunk):
				_doc = {_field: _value for _field, _value in _doc.items() if "rev" not in _field}
				for _New_field, _New_value in update_fields.items():
					_doc[_New_field] = _New_value

				_update_chunk.append(_doc)

			if _update_chunk:
				_update_result = self.connection.bulk_docs(_update_chunk)
				_update_chunk = []

				_oks = [update_doc for update_doc in _update_result if "ok" in update_doc.keys()]
				if len(_oks):
					_change = True
					update_result += _oks
					_oks = []

				# existing_docs = self.connection.get_query_result(selector)
				_chunk_pos += chunk_size
				_chunk_end += chunk_size

		# Calculate the result for the update request
		if len(update_result):
			return [update_doc for update_doc in update_result if "ok" in update_doc.keys()]

		elif upsert and not _exists:
			# Insert a new document
			_doc = self.connection.create_document(update_fields)
			if '_rev' in _doc.keys():
				_doc.save()
				return _doc
			else:
				raise InsertException(_doc)
		else:
			return None

	def delete(self, selector, chunk_size=10000):
		# Check if the document already exists
		existing_docs = self.connection.get_query_result(selector)

		_chunk_pos = 0
		_chunk_end = chunk_size

		_deleted_ids = []
		existing_docs_list = list(existing_docs)

		while len(existing_docs_list) >= _chunk_pos:
			# delete all existing documents for these chunk
			_to_be_deleted_list = [{"_id": doc["_id"], "_deleted": True} for doc in existing_docs_list[_chunk_pos:_chunk_end] if doc["_id"] not in _deleted_ids]
			_deleted_docs = self.connection.bulk_docs(_to_be_deleted_list)

			_chunk_pos += _chunk_end
			_chunk_end += _chunk_pos

			_deleted_ids += [_deleted_doc["_id"] for _deleted_doc in _deleted_docs if "ok" in _deleted_doc.keys()]

		if _deleted_ids:
			return _deleted_ids
		else:
			return False


class Connect:

	def __init__(self, url, db_user, db_pass, connect=True, auto_renew=True, *args, **kwargs):
		self.server = CouchDB(db_user, db_pass, url=url, connect=True, auto_renew=True, *args, **kwargs)

	def collection(self, name):

		try:
			self.server[name]
		except KeyError:
			self.server.create_database(name)

		return CollectionAbstraction(self.server[name])


# usage:
if __name__ == '__main__':
	url = "http://localhost:5984"
	database = Connect(url=url, db_user='admin', db_pass='admin', connect=True, auto_renew=True)
	collection = database.collection('test')

	# insert many:
	# insert_load = [{"name": 'test', "value": e} for e in range(10000)]
	# print(f"""inserting: {list(collection.insert_many(docs=insert_load))}, expected result: document""")
	# input("waiting for input...")

	# find_one:
	#print(f"""find_one: {collection.find_one(selector={'name': {"$eq": "test"}})}, expected result: document""")
	#input("waiting for input...")
#
	## find_many:
	#print(f"""find_many: {collection.find_many(selector={'name': {"$eq": "test"}})}, expected result: document""")
	#input("waiting for input...")
#
	# update:
	print(f"""update: {collection.update(selector={'name': {"$eq": "test1"}}, update_fields={'name': "test"})}, expected result: document""")
	input("waiting for input...")
#
	## delete:
	#print(f"""delete: {collection.delete(selector={"name": {"$eq": "test1"}})}, expected result: {True}""")
	#input("waiting for input...")
#
	## delete:
	#print(f"""delete: {collection.delete(selector={"name": {"$eq": "test1"}})}, expected result: {False}""")
	#input("waiting for input...")
#
#