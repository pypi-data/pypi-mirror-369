from typing import List, Annotated, Union

from bson import ObjectId
from fastapi.responses import JSONResponse

from elemental_tools.json import json_parser
from elemental_tools.api.controllers.smtp import SMTPController

from elemental_tools.api.depends import auth, pagination
from elemental_tools.api.controllers.user import UserController
from elemental_tools.api.controllers.institution import InstitutionController

from elemental_tools.smtp import SendEmail
from fastapi import HTTPException, Depends, Header
from fastapi.routing import APIRouter

from elemental_tools.api.models import UserRequestModel, SMTPRequestModel
from elemental_tools.api.models.pagination import PaginationRequestModel

router = APIRouter()

user_controller = UserController()
institution_controller = InstitutionController()
smtp_controller = SMTPController()

tags = ["SMTP"]


def retrieve_all_smtp_config_list(_user, sub, supress_sensitive_data: bool = True):

    _user_companies = user_controller.query_all({"_id": {"$in": [ObjectId(company.company_id) for company in _user.companies if company.role in ['editor', 'owner']]}})

    all_owners_to_search = [_user.get_id()]

    if _user_companies is not None:
        for company in _user_companies:
            _this_company = UserRequestModel(**company)
            all_owners_to_search.append(_this_company.get_id())

    if sub is None:
        all_user_smtp = smtp_controller.query_all({"sub": {"$in": all_owners_to_search}})
    else:
        all_user_smtp = smtp_controller.query_all({"sub": ObjectId(sub)})

    _result = []
    for smtp in all_user_smtp:
        _current_smtp = SMTPRequestModel(**smtp)

        _smtp_dumped = _current_smtp.model_dump()
        _smtp_dumped['_id'] = _current_smtp.get_id()

        if not supress_sensitive_data:
            _result.append(_smtp_dumped)
        else:
            _result.append({"sub": _current_smtp.sub, "email": _current_smtp.email, "_id": _current_smtp.get_id()})

    return _result


@router.get("/smtp", tags=tags, description="Query SMTP List. With basic info such as smtp ID and it's email.")
async def get_smtp(_user: Annotated[UserRequestModel, Depends(auth)], pagination: Annotated[PaginationRequestModel, None] = Depends(pagination), sub: Union[str, None] = Header(description="User ID", default=None)):

    _result = retrieve_all_smtp_config_list(_user, sub)

    result = []
    if len(_result):
        result = pagination.get_page(_result)

    return JSONResponse(content=json_parser(result), status_code=200)


@router.get("/smtp/config", tags=tags, description="Query SMTP Server Config")
async def get_smtp_config(_user: Annotated[UserRequestModel, Depends(auth)], pagination: Annotated[PaginationRequestModel, None] = Depends(pagination), sub: Union[str, None] = Header(description="User ID", default=None)):

    _result = retrieve_all_smtp_config_list(_user, sub, supress_sensitive_data=False)

    result = []
    if len(_result):
        result = pagination.get_page(_result)

    return JSONResponse(content=json_parser(result), status_code=200)


@router.patch("/smtp/add", tags=tags, description="Add or Edit SMTP Server Config")
async def add_smtp(body: List[SMTPRequestModel], _user: Annotated[UserRequestModel, Depends(auth)]):
    try:
        _result = {}
        _success_count = 0
        _failed_count = 0

        every_sub_user_can_edit = [company.company_id for company in _user.companies if company.role in ['owner', 'editor']]
        every_sub_user_can_edit.append(_user.get_id())

        for smtp_to_add in body:

            if smtp_to_add.sub is None:
                smtp_to_add.sub = _user.get_id()
            
            if smtp_to_add.sub in every_sub_user_can_edit:

                _test_send_email = SendEmail(smtp_to_add.email, smtp_to_add.password, smtp_to_add.server, smtp_to_add.port)
                
                # update or insert smtp to user model if smtp config is valid
                _smtp_is_valid = _test_send_email.check_config()
                
                if _smtp_is_valid:
                    smtp_to_add.status = True

                    _success_count += 1
                else:

                    _failed_count += 1

        result = {"items_failed": []}
        try:
            result += {"insert_items": len(smtp_controller.add([smtp_to_add.model_dump() for smtp_to_add in body if smtp_to_add.status and smtp_to_add.get_id() is None]).inserted_ids)}
        except:
            pass

        try:
            update_result = smtp_controller.bulk_update(selectors=[{"_id": smtp_to_add.get_id()} for smtp_to_add in body if smtp_to_add.status and smtp_to_add.get_id() is not None], contents=[smtp_to_add.model_dump() for smtp_to_add in body if smtp_to_add.status and smtp_to_add.get_id() is not None], upsert=True)
            result += {"modified": update_result.modified_count, "matched": update_result.matched_count, "upserted": update_result.upserted_count}
            
        except:
            pass

        for smtp_conf in body:
            
            if not smtp_conf.status:
                
                _this_smtp = smtp_conf.model_dump()
                del _this_smtp["password"]
                result["items_failed"].append(_this_smtp)

    except Exception as e:
        raise HTTPException(detail=f"Cannot Save SMTP Configuration. Because: No valid configuration was found.", status_code=500)

    return JSONResponse(content=json_parser(json_parser({"count": _success_count, "result": result, "failed": _failed_count})), status_code=200)



