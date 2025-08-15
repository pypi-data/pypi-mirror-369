from datetime import datetime
from datetime import datetime, timedelta

import pytz as pytz

from elemental_tools.db.mongo import Connect as ConnectMongo, Index

database = ConnectMongo("mongodb://192.168.1.10:27017/", "test_database")

collection = database.collection('test_collection')

_test_indexes = [
	Index(['sub', 'title', 'status', 'schedule_date', 'task_name'], unique=True, sparse=True),
]
collection_name = 'test_collection'
#print(database.set_indexes('test_collection', _test_indexes))

print(database.collection('test_collection').find_one({'name': 'value'}))

# print(database.collection('test_collection').insert_many([{
# 	"timer": 10000,
# 	"schedule_date": None,
# 	"loops": None,
# 	"task_name": "test_task",
# 	"parameters": {
# 		"institution": "tcb",
# 		"email": "smartbservice@gmail.com",
# 		"password": "25168775"
# 	},
# 	"sub": "c9c3f0d7b4c78ed5259331ee9b36d1f5",
# 	"last_execution": datetime.now().isoformat(),
# 	"status": False
# },
# 	{
# 		"timer": 10000,
# 		"schedule_date": None,
# 		"loops": None,
# 		"task_name": "gsheet_export_statement",
# 		"parameters": {
# 			"institution": "tcb"
# 		},
# 		"sub": "c9c3f0d7b4c78ed5259331ee9b36d1f5",
# 		"last_execution": datetime.now().isoformat(),
# 		"status": False
# 	}
# ]))
#
desired_timezone = pytz.timezone("America/New_York")
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
				{'schedule_date': None},
				{'timer': {'$ne': None}},
				{'loops': None},
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
				{'schedule_date': {'$ne': None}},
				{'$expr': {'$gte': [{'$subtract': ['$currentTime', '$lastExecutionInMS']}, '$timer']}}
			]
		}
	}
]


print(list(collection.aggregate(_pipeline_functions_loop_count)))

