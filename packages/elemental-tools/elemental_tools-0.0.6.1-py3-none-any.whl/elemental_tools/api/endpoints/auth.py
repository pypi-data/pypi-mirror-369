import uuid

from bson import ObjectId
from fastapi import HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from elemental_tools.logger import Logger
from elemental_tools.json import json_parser

from elemental_tools.api.controllers.device import DeviceController
from elemental_tools.api.models.auth import LoginRequestModel, DeviceRequestModel
from elemental_tools.config import log_path

router = APIRouter()

device_controller = DeviceController()
logger = Logger(app_name='api-endpoint', owner='auth', destination=log_path).log


@router.get("/")
async def root():
    return {"message": "Up and running"}


@router.post("/auth/login", tags=['Auth'])
async def login(body: LoginRequestModel, fingerprint: str = Header(json_schema_extra={"default": "{{fingerprint}}"})):
    if len(fingerprint) == 24:
        device_id, _token = body.validate_password_and_device(fingerprint)
        try:
            _authorized = device_controller.update({"fingerprint": fingerprint, "_id": ObjectId(device_id), "status": True},{"_access_token": _token})

            if _authorized.matched_count:
                _result = dict(access_token=str(_token))
                return JSONResponse(content=json_parser(_result), headers=_result, status_code=200)
            else:
                raise HTTPException(detail='Unauthorized', status_code=401)

        except:
            raise HTTPException(detail='Unauthorized', status_code=401)

    raise HTTPException(detail='Unavailable fingerprint', status_code=500)


@router.post("/auth/logout", tags=['Auth'])
async def logout(access_token: str = Header(json_schema_extra={"default": "{{access_token}}"}), _refresh_token: str = Header(json_schema_extra={"default": "{{refresh_token}}"}), fingerprint: str = Header(json_schema_extra={"default": "{{fingerprint}}"})):

    if len(fingerprint) == 24:
        try:
            _device_in_database = device_controller.query({"fingerprint": fingerprint, "_access_token": access_token, "_refresh_token": _refresh_token})

            if _device_in_database is not None:
                _device = DeviceRequestModel(**_device_in_database)
                _device.set_id(_device_in_database['_id'])
                _device._access_token = _device.get_access_token()
                _device.status = False
                _device.set_refresh_token(None)
                device_controller.update({"_id": ObjectId(_device.get_id())}, {**_device.model_dump()})
                return JSONResponse(content=json_parser(dict(message='Device logged out successfully')), headers=dict(access_token=''), status_code=200)

            raise HTTPException(detail='Unavailable Device.', status_code=404)

        except Exception as e:
            logger('error', f'Failed to run device auth because of exception: {str(e)}')
            raise HTTPException(detail='Failed to store auth.', status_code=403)

    elif len(fingerprint) != 24:
        raise HTTPException(detail='The provided fingerprint, do not match the required (24 chars)', status_code=500)

    raise HTTPException(detail='Unavailable fingerprint', status_code=500)


@router.post("/auth/refresh", tags=['Auth'])
async def post_refresh_token(access_token: str = Header(json_schema_extra={"default": "{{access_token}}"}), fingerprint: str = Header(json_schema_extra={"default": "{{fingerprint}}"})):

    if len(fingerprint) == 24:

        _device_in_database = device_controller.query({"$and": [{"fingerprint": fingerprint}, {"_access_token": access_token}, {"status": True}]})
        
        if _device_in_database is not None:

            _device = DeviceRequestModel(**_device_in_database)
            
            _device._access_token = _device.get_access_token()
            _device._refresh_token = uuid.uuid4().hex
            _device.set_id(_device_in_database['_id'])

            device_controller.update({"_id": _device.get_id()}, {**_device.model_dump(), "_refresh_token": _device.get_refresh_token()})

            _result = dict(refresh_token=_device.get_refresh_token(), access_token=_device.get_access_token())
            
            return JSONResponse(content=json_parser(_result), headers=_result, status_code=200)

        raise HTTPException(detail='Unauthorized.', status_code=401)

    elif len(fingerprint) != 24:
        raise HTTPException(detail='The provided fingerprint, do not match the required (24 chars)',
                            status_code=500)

    raise HTTPException(detail='Unavailable fingerprint', status_code=401)

