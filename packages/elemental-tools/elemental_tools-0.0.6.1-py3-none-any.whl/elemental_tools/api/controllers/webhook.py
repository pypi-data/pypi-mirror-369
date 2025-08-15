from elemental_tools.Jarvis.config import webhook_db_url, webhook_database_name
from elemental_tools.json import json_to_bson

if webhook_db_url is not None:
    from pymongo.errors import ConfigurationError

    from elemental_tools.logger import Logger
    from elemental_tools.db.mongo import database, Index
    from fastapi import HTTPException
    from icecream import ic
    from elemental_tools.config import db_url, log_path, database_name

    collection_name = f'webhook'

    _webhook_indexes = []

    try:
        database = Connect(webhook_db_url, webhook_database_name)

        collection = database.collection(collection_name)
        database.set_indexes(collection_name, _webhook_indexes)

    except ConfigurationError:
        raise Exception(
            'Could not connect to webhook database. Please provide a valid WEBHOOK_DB_URL on your env file.')


    class WebhookController:
        logger = Logger(app_name='controllers', owner=collection_name, destination=log_path).log

        pipeline_all_wpp_ids = [
            {
                '$match': {
                    "body.object": "whatsapp_business_account"
                }
            },
            {
                '$group': {
                    '_id': None,
                    'uniqueIds': {
                        '$addToSet': '$body.entry.id'
                    }
                }
            }, {
                '$unwind': '$uniqueIds'
            }
        ]

        pipeline_unprocessed_wpp_messages = [
            {
                '$match': {
                    '$and': [
                        {
                            'body.object': 'whatsapp_business_account'
                        },
                        {
                            "body.entry.changes.value.messages.type": "text"
                        }
                    ]
                }
            }, {
                '$project': {
                    'messages': {
                        '$ifNull': [
                            '$body.entry.changes.value.messages', ''
                        ]
                    },
                    'user_ids': {
                        '$ifNull': [
                            '$body.entry.id', ''
                        ]
                    }
                }
            }
        ]

        #		[
        #    {
        #        '$project': {
        #            'user_ids': {
        #                '$ifNull': [
        #                    '$body.entry.id', '$body'
        #                ]
        #            },
        #            'messages': {
        #                '$ifNull': [
        #                    '$body.entry.changes.value.messages', '$body.entry.changes'
        #                ]
        #            }
        #        }
        #    }
        # ]
        #
        def __init__(self, timeout: int = None):

            self.timeout = 5
            if timeout is not None:
                self.timeout = timeout

            self.database = database

        def add(self, doc):
            insert = collection.insert_one(json_to_bson(dict(doc)))

            _inserted_item = collection.find_one({"_id": insert.inserted_id})

            return _inserted_item

        def query(self, selector):
            result = None
            query_result = collection.find(json_to_bson(selector))
            if query_result:
                return query_result
            return result

        def select(self, selector: dict):
            return collection.find_one(json_to_bson(selector))

        def update(self, selector, content):
            self.logger('info', f'Updating User Information for Selector: {selector} with: {str(content)} ')
            _update_result = None
            _content = {"$set": json_to_bson(content)}

            try:
                _update_result = collection.update_one(json_to_bson(selector), json_to_bson(_content))

                if _update_result is None:
                    raise HTTPException(detail='Cannot update user information.', status_code=400)

            except Exception as e:
                self.logger('error', f'Cannot update user information: {str(e)}')

            return _update_result

        def query_all(self, selector):
            """
			:return Result Generator
			"""

            result = None
            query_result = collection.find(json_to_bson(selector))

            if query_result:
                return query_result

            return result

        def pipeline(self, pipeline):
            """
			:return Result Generator
			"""

            return collection.aggregate(pipeline)

        def get_all_wpp_ids(self):

            return self.pipeline(self.pipeline_all_wpp_ids)

        def get_unprocessed_wpp_messages(self, wpp_user_id: str = None):
            """

			:param wpp_user_id: Optional wpp_user_id to retrieve only a subset of messages
			:return:
			"""

            _pipeline = self.pipeline_unprocessed_wpp_messages

            if wpp_user_id is not None:
                self.pipeline_unprocessed_wpp_messages[0]['$match']['$and'].append(dict(wpp_user_id=wpp_user_id))

            def messages_generator():
                _result = []
                try:
                    for message in list(self.pipeline(_pipeline)):
                        if len(message['messages'][0]):
                            message['messages'] = message['messages'][0][0]
                            # _eval_mes = eval(str(message).replace('[[[', '[').replace(']]]', ']'))
                            # 
                            _result.append(message)
                except:
                    pass

                yield _result

            return messages_generator()

        def remove(self, _id):

            _result = collection.delete_many({'_id': _id})
            if _result.deleted_count:
                return True

            return False
