from typing import List, Annotated

import pandas as pd
from bson import ObjectId
from fastapi import HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from pymongo.errors import DuplicateKeyError

from elemental_tools.logger import Logger
from elemental_tools.json import json_parser
from elemental_tools.api import UserController
from elemental_tools.api.controllers.notification import NotificationController
from elemental_tools.api.controllers.template import TemplateController, TemplateResourcesController
from elemental_tools.api.depends import auth
from elemental_tools.api.models import UserRequestModel
from elemental_tools.api.models.notification import NotificationRequestModel
from elemental_tools.api.models.templates import TemplateResourceRequestModel
from elemental_tools.config import log_path
from elemental_tools.templates import Templates

router = APIRouter()

notification_controller = NotificationController()
user_controller = UserController()
template_controller = TemplateController()
template_resources_controller = TemplateResourcesController()
logger = Logger(app_name='api-endpoint', owner='notifications', destination=log_path).log


@router.post("/notifications/add", tags=['Notifications'])
async def notification_add(body: List[NotificationRequestModel], _user: Annotated[UserRequestModel, None] = Depends(auth)):
    try:
        result = []
        for notification in body:
            notification.sub = ObjectId(_user.get_id())
            if notification.template_id is not None:
                try:
                    templates = Templates(notification.sub, notification.template_id)
                    if templates.user_templates is None:
                        raise HTTPException(detail='Unavailable templates', status_code=404)

                    if templates.this_template is not None:
                        notification.last_response_execution = None

                except Exception as exc:
                    logger('error', f'Failed to store notification because of a template exception: {str(exc)}')
                    raise HTTPException(detail='Failed to store notification because of a template exception', status_code=403)

            try:
                notification.modifiers = [ObjectId(str(mod)) for mod in notification.modifiers if mod is not None]
            except TypeError:
                raise HTTPException(detail="Invalid Resource Id",
                                    status_code=403)
            try:
                notification.customer_id = ObjectId(notification.customer_id)
            except TypeError:
                raise HTTPException(detail="Invalid Client ID",
                                    status_code=403)

            try:
                notification.template_id = ObjectId(notification.template_id)
            except TypeError:
                raise HTTPException(detail="Invalid Template ID",
                                    status_code=403)

            _result = notification_controller.add(notification)
            result.append(_result['_id'])

        return JSONResponse(content=json_parser(result), status_code=200)

    except DuplicateKeyError as d:
        logger('error', f'Failed to store notification because of exception: {str(d)}')
        raise HTTPException(detail='An notification with this cellphone already exists', status_code=403)


@router.put("/notifications/edit", tags=['Notifications'])
async def notification_edit(sub: str, body: NotificationRequestModel):
    try:
        result = notification_controller.update({'_id': ObjectId(sub)}, body.model_dump())

    except:
        raise HTTPException(detail='Cannot edit notification', status_code=500)

    return JSONResponse(content=json_parser(result), status_code=200)


@router.get("/notifications", tags=['Notifications'])
async def notification_get(_user: Annotated[UserRequestModel, None] = Depends(auth)):
    try:
        result = None
        users_id = [_user.get_id()]

        siblings = user_controller.query_all({"sub": {"$eq": _user.sub}})
        if siblings is not None:
            users_id += [sib['_id'] for sib in siblings]

        notifications = notification_controller.query_all({'sub': {"$in": users_id}})

        if notifications is not None:
            
            result = []

            all_user_resources = template_resources_controller.query_all(sub=_user.get_id(), parent_sub=_user.sub, siblings=users_id)

            if all_user_resources is not None:
                resources_dataframe = pd.DataFrame(all_user_resources)

            else:
                resources_dataframe = pd.DataFrame({**TemplateResourceRequestModel().model_dump()})

            # iterate on every notification found to retrieve add data:
            for notification in notifications:
                
                current_notification = NotificationRequestModel(**notification)

                # query template:
                current_template = template_controller.query({"_id": ObjectId(current_notification.template_id)})

                
                if current_template is not None:
                    current_notification.template_title = current_template['title']
                    current_notification.template_subject = current_template['subject']

                    # query destination:
                    current_destination = user_controller.query({"_id": ObjectId(current_notification.customer_id)})
                    if current_destination is not None:
                        
                        current_notification.destination_name = current_destination['name']
                        current_notification.destination_email = current_destination['email']
                        current_notification.destination_cellphone = current_destination['cellphone']
                        current_notification.modifier_labels = []
                        for notification_modifier in current_notification.modifiers:
                            
                            try:
                                current_resources = resources_dataframe[resources_dataframe['_id'].isin(current_template['resources'])]
                                _this_resource_modifiers = current_resources['modifiers'].iloc[0]

                                for mod in _this_resource_modifiers:
                                    current_notification.modifier_labels.append(mod['title'])

                            except KeyError:
                                pass

                    # convert to jsonable data:
                    _result = json_parser(current_notification.model_dump())
                    result.append(_result)

        if result is None:
            return JSONResponse(content=json_parser({'message': 'Cannot find notifications', 'model': NotificationRequestModel().__dict__}), status_code=404)

    except Exception as e:
        raise HTTPException(detail=f'Cannot query notifications because of exception: {str(e)}', status_code=500)

    return JSONResponse(content=result, status_code=200)

