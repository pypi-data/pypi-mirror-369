from typing import Annotated, Union

import pandas as pd
from bson import ObjectId
from fastapi import HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from pymongo.errors import DuplicateKeyError

from elemental_tools.logger import Logger
from elemental_tools.json import json_parser
from elemental_tools.config import log_path
from elemental_tools.api.controllers.template import TemplateController, TemplateResourcesController
from elemental_tools.api.controllers.user import UserController
from elemental_tools.api.depends import auth
from elemental_tools.api.models import UserRequestModel
from elemental_tools.api.models.templates import TemplateRequestModel, TemplateResourceRequestModel

router = APIRouter()

template_controller = TemplateController()
user_controller = UserController()
template_resources_controller = TemplateResourcesController()

logger = Logger(app_name='api-endpoint', owner='template', destination=log_path).log


@router.patch("/template/add", tags=['Template'])
async def template_save(body: TemplateRequestModel, _user: Annotated[UserRequestModel, None] = Depends(auth), template_id = Header(default=None)):
    try:
        body.set_id(template_id)

        body.sub = _user.get_id()

        body.resources = [ObjectId(res) for res in body.resources]

        if body.get_id() is not None:
            try:
                _result = template_controller.update({"_id": ObjectId(body.get_id())}, body)

                if _result:
                    _result = {"_id": body.get_id()}
                else:
                    _result = {"_id": None}

            except DuplicateKeyError as e:
                raise HTTPException(detail=f'Another Template with this title already exists.', status_code=403)

        else:
            _result = template_controller.add(body)

    except Exception as e:
        raise HTTPException(detail=f'Cannot save Template because of: {str(e)}', status_code=500)

    return JSONResponse(content=json_parser(_result), status_code=200)


@router.get("/template", tags=['Template'])
async def template_get(_user: Annotated[UserRequestModel, None] = Depends(auth), template_id = Header(default=None)):
    try:

        # When user not provide an id, return all templates available:
        if template_id is None:
            result = []
            _result = template_controller.query_all({'sub': {"$eq": _user.get_id()}})
            
            for e in _result:
                result.append(e)

        # Otherwise, query for the requested id:
        else:
            result = template_controller.query({"$and": [{'sub': _user.get_id()}, {"_id": ObjectId(template_id)}]})
            
            if result is not None:
                result['_id'] = str(result["_id"])
                if result['resources'] is not None:
                    result['temp'] = []
                    for res in result['resources']:

                        _this_resource = template_resources_controller.query({"$and": [{'sub': _user.get_id()}, {"_id": ObjectId(res)}]})
                        if _this_resource is not None:
                            result['temp'].append(_this_resource)

        if result is None:
            return JSONResponse(
                content=json_parser({'message': 'Cannot find templates', 'model': TemplateRequestModel().__dict__}),
                status_code=404)

    except:
        raise HTTPException(detail='Cannot query templates', status_code=500)

    return JSONResponse(content=json_parser(result), status_code=200)


@router.patch("/template/resources/add", tags=['Template Resource'], description="Create a new template resource")
async def template_resource_save(body: TemplateResourceRequestModel, _user: Annotated[UserRequestModel, None] = Depends(auth), resource_id = Header(default=None)):
    try:
        body.set_id(resource_id)
        body.sub = _user.get_id()
        if body.icon is not None:
            body.icon = await body.icon.read()

        if body.get_id() is not None:
            try:
                body.modifiers = [mod for mod in body.modifiers if mod is not None]

                for mod in body.modifiers:
                    if mod.modifier_id is None:
                        mod.modifier_id = ObjectId()

                _result = template_resources_controller.update({"_id": ObjectId(body.get_id())}, body)
                if _result is not None:
                    _result = {"result": _result.modified_count}

            except DuplicateKeyError as e:
                raise HTTPException(detail=f'Another Resource with this name already exists.', status_code=403)

        else:
            _result = template_resources_controller.add(body)
            _result = _result['_id']

    except Exception as e:
        raise HTTPException(detail=f'Cannot save template resource because of: {str(e)}', status_code=500)

    return JSONResponse(content=json_parser(_result), status_code=200)


@router.get("/template/resources", tags=['Template Resource'], description="Returns the template resources")
async def template_resource(resource_id: Union[str, None] = Header(default=None), _user: Annotated[UserRequestModel, None] = Depends(auth)):
    _result = []
    try:

        if resource_id is None:

            _siblings = user_controller.query_all({'sub': _user.sub})
            if _siblings is not None:
                _siblings = list(_siblings)
            else:
                _siblings = []

            _user_resources = template_resources_controller.query_all(sub=ObjectId(_user.get_id()), parent_sub=_user.sub, siblings=_siblings)
            if _user_resources is not None:
                _result = list(_user_resources)

        else:
            
            _user_selected_resource = template_resources_controller.select({"sub": _user.get_id(), "_id": ObjectId(resource_id)})
            
            if _user_selected_resource is not None:
                _result = [{**_user_selected_resource}]
            
        result = []
        for resource in list(_result):
            resource["_id"] = str(resource["_id"])
            del resource["sub"]
            result.append(resource)

    except Exception as e:
        raise HTTPException(detail=f'Cannot query templates resources because of: {str(e)}', status_code=500)
    
    return JSONResponse(content=json_parser(list(result)), status_code=200)


@router.get("/template/resources/modifiers", tags=['Template Resource'], description="Returns the template resources modifiers")
async def template_resource_modifiers(
        template_id: str = Header(description="When not set, return all templates for the current user."),
        _user: Annotated[UserRequestModel, None] = Depends(auth)
):
    _result = []
    try:

        _siblings = user_controller.query_all({'sub': _user.sub})
        if _siblings is not None:
            _siblings = list(_siblings)
        else:
            _siblings = []

        current_template = template_controller.query(dict(_id=ObjectId(template_id)))

        if current_template is not None:
            current_template = TemplateRequestModel(**current_template)
            _user_resources = list(template_resources_controller.query_all(sub=_user.get_id(), parent_sub=_user.sub, siblings=_siblings))
            _user_resources_df = pd.DataFrame(_user_resources)
            for resource in current_template.resources:
                # Filter the DataFrame based on _id
                current_resource = _user_resources_df[_user_resources_df['_id'] == ObjectId(resource)]
                # Convert the filtered DataFrame to dictionary with 'records' orientation
                for modifiers in current_resource.modifiers:
                    for mod in modifiers:
                        _result.append(mod)

    except Exception as e:
        raise HTTPException(detail=f'Cannot query templates resources modifiers because of: {str(e)}', status_code=500)

    return JSONResponse(content=json_parser(list(_result)), status_code=200)
