from typing import List, Annotated

from bson import ObjectId
from fastapi import HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from pymongo.errors import DuplicateKeyError

from elemental_tools.logger import Logger
from elemental_tools.json import json_parser
from elemental_tools.api.controllers.institution import InstitutionController
from elemental_tools.api.controllers.smtp import SMTPController
from elemental_tools.api.controllers.user import UserController
from elemental_tools.api.depends import auth, pagination
from elemental_tools.exceptions import GetDuplicatedKey
from elemental_tools.api.models import UserRequestModel, SonRequestModel
from elemental_tools.api.models.pagination import PaginationRequestModel
from elemental_tools.config import log_path

router = APIRouter()

user_controller = UserController()
institution_controller = InstitutionController()
smtp_controller = SMTPController()

tags = ['Sons']
logger = Logger(app_name='api-endpoint', owner='sons', destination=log_path).log



@router.get("/sons", tags=tags)
async def get_sons(_user: Annotated[UserRequestModel, None] = Depends(auth), pagination: Annotated[PaginationRequestModel, None] = Depends(pagination)):

    try:
        result = []
        _status_code = 200
        
        _sons = user_controller.query_all({"sub": _user.get_id()})
        
        if _sons is not None:
            result = pagination.get_page(_sons)

        if not result:
            _status_code = 404

        return JSONResponse(content=json_parser(result), headers={**pagination.headers()},
                            status_code=_status_code)
    except:
        raise HTTPException(detail='Cannot query sons', status_code=500)


@router.patch("/sons/add", tags=tags)
async def add_sons(body: List[SonRequestModel], _user: Annotated[UserRequestModel, None] = Depends(auth)):
    try:

        _result = []
        for user in body:
            if user.get_id() is None:
                _this_user = user.model_dump()

                try:
                    del _this_user["_id"]
                except:
                    pass

                _insert_result = user_controller.add({**_this_user, 'sub': ObjectId(_user.get_id())})
                _result.append(str(_insert_result["_id"]))

            else:
                _this_user = user.model_dump()
                del _this_user['_id']
                _result.append(str(user_controller.update({"_id": ObjectId(user.get_id())}, _this_user).upserted_id))

    except DuplicateKeyError as error:
        logger('error', f'Failed to store user because of exception: {str(error)}')
        raise HTTPException(detail=f'An user with this Whatsapp Contact already exists {GetDuplicatedKey(error)}', status_code=403)

    return JSONResponse(content=json_parser({'result': json_parser(_result)}), status_code=200)


@router.delete("/sons/remove", tags=tags)
async def user_remove_sons(body: List[str], _user: Annotated[UserRequestModel, None] = Depends(auth)):
    _result = None
    _id_list = []

    if _user.admin:

        for _id in body:
            try:
                _id_list.append(ObjectId(_id))
            except:
                pass

        _result = user_controller.collection.delete_many({"_id": {"$in": _id_list}, "sub": _user.get_id()}).deleted_count

        if not _result:
            raise HTTPException(detail="Not found", status_code=404)

        return JSONResponse(content=json_parser({'result': str(_result)}), status_code=200)

    raise HTTPException(detail="Unauthorized", status_code=401)

