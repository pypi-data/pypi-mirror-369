import os.path
import tempfile
import uuid
from typing import Union
from fastapi.encoders import jsonable_encoder


def json_parser(obj: Union[dict, list]):
    import bson

    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                obj[key] = json_parser(value)
            elif isinstance(value, bson.ObjectId):
                obj[key] = str(value)
    elif isinstance(obj, list):
        for i in range(len(obj)):
            if isinstance(obj[i], (dict, list)):
                obj[i] = json_parser(obj[i])
            elif isinstance(obj[i], bson.ObjectId):
                obj[i] = str(obj[i])
    elif isinstance(obj, bson.ObjectId):
        obj = str(obj)

    return jsonable_encoder(obj)


def json_to_bson(obj: Union[dict, list]):
    import bson

    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                obj[key] = json_to_bson(value)
            elif isinstance(value, str) and 'id' in key.lower() or 'sub' == key.lower():
                try:
                    obj[key] = bson.ObjectId(value)
                except:
                    obj[key] = value
    elif isinstance(obj, list):
        for i in range(len(obj)):
            if isinstance(obj[i], (dict, list)):
                obj[i] = json_to_bson(obj[i])
            elif isinstance(obj[i], str) and len(obj[i]) == 24:
                try:
                    obj[i] = bson.ObjectId(obj[i])
                except:
                    obj[i] = obj[i]

    return obj


def json_to_temp_file(obj: Union[dict, list]):
    _file_root_path = tempfile.mkdtemp(prefix='e-json')
    _file_name = str(uuid.uuid4())

    _file_path = os.path.join(_file_root_path, _file_name)

    with open(_file_path, 'w') as json_out:
        json_out.write(str(obj))

    return _file_path
