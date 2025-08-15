from typing import List, Annotated

from bson import ObjectId
from fastapi import HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from pymongo.errors import DuplicateKeyError

from elemental_tools.logger import Logger
from elemental_tools.json import json_parser
from elemental_tools.config import log_path
from elemental_tools.api.controllers.institution import InstitutionController
from elemental_tools.api.controllers.smtp import SMTPController
from elemental_tools.api.controllers.user import UserController
from elemental_tools.api.depends import auth, pagination
from elemental_tools.api.models import UserRequestModel, UserInstitutionSetting
from elemental_tools.api.models.pagination import PaginationRequestModel


router = APIRouter()

user_controller = UserController()
institution_controller = InstitutionController()
smtp_controller = SMTPController()

logger = Logger(app_name='api-endpoint', owner='user', destination=log_path).log

@router.get("/user/me", tags=['User'])
async def user_get(_user: Annotated[UserRequestModel, None] = Depends(auth), list_sons: bool = Header(False), pagination: Annotated[PaginationRequestModel, None] = Depends(pagination)):
    try:

        if not list_sons:
            _user_json = _user.model_dump()

            del _user_json['password']

            return JSONResponse(content=json_parser(_user_json), status_code=200)
        else:
            _result = []
            _status_code = 200

            _sons = user_controller.query_all({"sub": _user.get_id()})

            if _sons is not None:
                _result = pagination.get_page(_sons)

                for son in _result:
                    son["_id"] = str(son["_id"])

            if not _result:
                _status_code = 404

            return JSONResponse(content=json_parser(_result), headers={**pagination.headers()},
                                status_code=_status_code)

    except Exception as e:
        raise HTTPException(detail=f'Cannot query user: {str(e)}', status_code=500)


@router.post("/user/register", tags=['User'])
async def user_add(body: UserRequestModel):
    try:
        for inst in body.institutions:
            try:
                _this_inst = institution_controller.query({'_id': ObjectId(inst.institution_id)})

                if _this_inst is None:
                    raise HTTPException(detail='Unavailable institution, please check the available institutions at /institutions endpoint.', status_code=404)
            except:
                raise HTTPException(
                    detail='Unavailable institution, please check the available institutions at /institutions endpoint.',
                    status_code=404)

        result = user_controller.add(body.model_dump())

        _inserted_id = result['_id']
    except DuplicateKeyError as d:
        logger('error', f'Failed to store user because of exception: {str(d)}')
        raise HTTPException(detail='An user with this Whatsapp Contact already exists', status_code=403)

    return JSONResponse(content=json_parser(dict(sub=str(_inserted_id))), status_code=200)


@router.put("/user/edit", tags=['User'])
async def user_edit(body: UserRequestModel, _user: Annotated[UserRequestModel, Depends(auth)]):
    try:
        for inst in body.institutions:
            _this_inst = institution_controller.query({'_id': ObjectId(inst['_id'])})

            if _this_inst is None:
                raise HTTPException(
                    detail='Unavailable institution, please check the available institutions at /institutions endpoint.',
                    status_code=404)

        result = user_controller.update({'_id': ObjectId(_user.get_id())}, body.model_dump()).upserted_id
    except:
        raise HTTPException(detail='Cannot edit user', status_code=500)

    return JSONResponse(content=json_parser(result), status_code=200)


@router.patch("/user/institutions/add", tags=['User'], description="To add institutions to a user")
async def user_add_institutions(body: List[UserInstitutionSetting], _user: Annotated[UserRequestModel, Depends(auth)]):
    try:
        for inst_to_add in body:

            _this_inst = institution_controller.query({'_id': ObjectId(inst_to_add.institution_id)})

            if _this_inst is None:
                raise HTTPException(
                    detail='Unavailable institution, please check the available institutions at /institutions endpoint.',
                    status_code=404)

        _new_user_institutions = [e.model_dump() for e in body]
        _new_user_institutions_ids = [inst['institution_id'] for inst in _new_user_institutions]

        _current_user_institutions = user_controller.query({'_id': ObjectId(_user.get_id())}).get('institutions', [])

        _merge_user_institutions = [c_i for c_i in _current_user_institutions if c_i['institution_id'] not in _new_user_institutions_ids] + _new_user_institutions

        result = user_controller.update({'_id': ObjectId(_user.get_id())}, {"institutions": _merge_user_institutions})

    except Exception as e:
        raise HTTPException(detail=f'Cannot edit user because of {str(e)}', status_code=500)

    return JSONResponse(content=json_parser({'count': result.modified_count}), status_code=200)




