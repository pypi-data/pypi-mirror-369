from bson import ObjectId

from elemental_tools.logger import Logger
from fastapi import HTTPException, Header

from elemental_tools.api import UserController
from elemental_tools.api.controllers.device import DeviceController
from elemental_tools.api.models import UserRequestModel
from elemental_tools.api.models.pagination import PaginationRequestModel
from elemental_tools.config import log_path

_device_controller = DeviceController()
logger = Logger(app_name='api', owner='dependencies', destination=log_path).log


def auth(fingerprint: str = Header(json_schema_extra={"default": "{{fingerprint}}"}), refresh_token: str = Header(json_schema_extra={"default": "{{refresh_token}}"}), access_token: str = Header(json_schema_extra={"default": "{{access_token}}"})):
    logger('info', f'User Signing With:\n\tFingerprint: {fingerprint}\n\tRefresh Token: {refresh_token}\n\tAccess Token: {access_token}', owner='authentication')
    if len(fingerprint) == 24:
        try:
            _auth = _device_controller.query(
                {"fingerprint": fingerprint, "_refresh_token": refresh_token, "_access_token": access_token,
                 "status": True})
            _user = UserController().query({"_id": ObjectId(_auth['sub'])})

            if _auth is not None and _user is not None:
                _this_user = UserRequestModel(**_user)
                _this_user.set_id(_user['_id'])

                # renew the token for the next authentication
                #   _device_controller.update({"_id": _auth['_id']}, {"_refresh_token": None})

                logger('success',
                       f'Authorized!', owner='authentication')

                return _this_user
            else:
                logger('error',
                       f'Unauthorized!', owner='authentication')

                raise HTTPException(detail="Unauthorized.", status_code=401)
        except Exception as e:
            logger('error',
                   f'Unauthorized!', owner='authentication')
            raise HTTPException(detail=f"Unauthorized.", status_code=401)

    else:
        logger('critical-error',
               f'Invalid Fingerprint!', owner='authentication')
        raise HTTPException(detail='The provided fingerprint, do not match the required (24 chars)', status_code=500)


def pagination(page_num: int = Header(default=1), page_size: int = Header(default=50)):
    logger('info',
           f'Querying for Page\n\tNum: {page_num}\n\tPage Size: {page_size}', owner='pagination')
    result = PaginationRequestModel(page_size=page_size, page_num=page_num)
    logger('success',
           f'Result was found!', owner='pagination')
    return result

