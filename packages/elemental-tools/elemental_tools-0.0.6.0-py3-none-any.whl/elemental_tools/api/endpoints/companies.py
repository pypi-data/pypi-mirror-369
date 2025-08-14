from typing import List, Annotated, Union

from bson import ObjectId
from fastapi import HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from pymongo.errors import DuplicateKeyError

from elemental_tools.logger import Logger
from elemental_tools.exceptions import GetDuplicatedKey

from elemental_tools.json import json_parser
from elemental_tools.api.controllers.companies import CompaniesController
from elemental_tools.api.depends import auth, pagination

from elemental_tools.api.models import UserRequestModel, CompanyRequestModel, UserCompany, UserCompanyRoles
from elemental_tools.api.models.pagination import PaginationRequestModel

router = APIRouter()

companies_controller = CompaniesController()


tags = ['Companies']
logger = Logger(app_name='api-endpoint', owner='companies').log


@router.get("/companies", tags=tags, response_model=List[CompanyRequestModel])
async def get_companies(_user: Annotated[UserRequestModel, None] = Depends(auth), pagination: Annotated[PaginationRequestModel, None] = Depends(pagination), scope: Union[str, None] = Header(default=None)):
    companies = None
    result = []

    if scope is None:
        companies = list(companies_controller.query_all({"_id": {"$in": [ObjectId(company.company_id) for company in _user.companies]}}))
    else:
        available_scopes = [e for e in UserCompanyRoles.__dict__ if not e.startswith('_')]
        selected_scopes = scope.split(',')
        for scope in selected_scopes:
            if scope not in available_scopes:
                raise HTTPException(detail="Invalid Scope", status_code=403)

        companies = list(companies_controller.query_all(
            {"_id": {"$in": [ObjectId(company.company_id) for company in _user.companies if company.role in selected_scopes]}}))

    if companies is not None:
        result = pagination.get_page(companies)

    return JSONResponse(content=json_parser({'result': json_parser(result)}), status_code=200)


@router.patch("/companies/add", tags=tags)
async def add_companies(body: List[CompanyRequestModel], _user: Annotated[UserRequestModel, None] = Depends(auth)):
    try:
        _result = []
        for company in body:
            if company.get_id() is None:
                _this_user = company.model_dump()
                try:
                    del _this_user["_id"]
                except:
                    pass

                _insert_result = companies_controller.add([{**_this_user, 'sub': ObjectId(_user.get_id())}])
                _result.append(str(_insert_result["_id"]))

                _new_company = UserCompany()
                _new_company.company_id = _insert_result["_id"]
                _new_company.role = 'owner'

                companies_controller.update({"_id": _user.get_id()}, _new_company.model_dump())

            else:
                _this_user = company.model_dump()
                _result.append(str(companies_controller.update({"_id": ObjectId(company.get_id())}, _this_user).upserted_id))

    except DuplicateKeyError as error:
        logger('error', f'Failed to store user because of exception: {str(error)}')
        raise HTTPException(detail=f'An user with this Whatsapp Contact already exists {GetDuplicatedKey(error)}', status_code=403)

    return JSONResponse(content=json_parser({'result': json_parser(_result)}), status_code=200)



