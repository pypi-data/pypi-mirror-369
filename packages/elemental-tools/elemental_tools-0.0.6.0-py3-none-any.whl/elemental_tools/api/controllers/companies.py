from typing import List
from bson import ObjectId
from icecream import ic
from elemental_tools.logger import Logger
from elemental_tools.db.mongo import database, Index, UpdateOne
from fastapi import HTTPException
from elemental_tools.json import json_to_bson
from elemental_tools.config import db_url, log_path, database_name

collection_name = f'companies'

_indexes = [
    Index(["sub", "email"], unique=True),
]


class CompaniesController:
    logger = Logger(app_name='controllers', owner=collection_name, destination=log_path).log

    collection = database.collection(collection_name)
    database.set_indexes(collection_name, _indexes)

    def __init__(self, timeout: int = None):
        self.timeout = 5
        if timeout is not None:
            self.timeout = timeout

        
    def add(self, doc: list):
        insert = self.collection.insert_many(json_to_bson(doc))
        return insert

    def query(self, selector):
        result = None
        query_result = self.collection.find_one(json_to_bson(selector))
        if query_result:
            return query_result
        return result

    def select(self, selector: dict):
        return self.collection.find_one(json_to_bson(selector))

    def update(self, selector, content):
        self.logger('info', f'Updating User Information for Selector: {selector} with: {str(content)} ')
        _update_result = None
        _content = {"$set": content}

        try:
            _update_result = self.collection.update_one(json_to_bson(selector), json_to_bson(_content))

            if _update_result is None:
                raise HTTPException(detail='Cannot update user information.', status_code=400)

        except Exception as e:
            self.logger('error', f'Cannot update user information: {str(e)}')

        return _update_result

    def update_many(self, selector, content: dict, *args):
        _result = self.collection.update_many(selector, {"$set": content}, args)
        return _result.modified_count

    def bulk_update(self, selectors: List[dict], contents: List[dict], *args, **kwargs):
        ops = []
        
        for selector, content in zip(selectors, contents):
            ops.append(UpdateOne(selector, {"$set": json_to_bson(content)}, *args, **kwargs))
        
        _result = self.collection.bulk_write(ops)
        return _result

    def get_status(self, sub):
        _result = None
        print(f'get_status selector "_id":{ObjectId(sub)}')
        query_result = self.collection.find_one({"_id": ObjectId(sub)})
        if 'status' in query_result.keys():
            _result = query_result['status']
        if _result is not None:
            return _result
        return False

    def query_all(self, selector):
        result = None
        query_result = self.collection.find(json_to_bson(selector))
        if query_result:
            return query_result
        return result
