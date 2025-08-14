from pymongo.errors import DuplicateKeyError

from fastapi import HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse

from elemental_tools.logger import Logger
from elemental_tools.json import json_parser
from elemental_tools.api.controllers.institution import InstitutionController
from elemental_tools.api.models import InstitutionRequestModel
from elemental_tools.config import log_path

router = APIRouter()

institution_controller = InstitutionController()
logger = Logger(app_name='api-endpoint', owner='institution', destination=log_path).log


@router.post("/institution/add", tags=['Institution'])
async def institution_add(body: InstitutionRequestModel):

    logger('info', f'API received the doc: {str(body.__dict__)}')
    try:
        result = institution_controller.add(body.__dict__)
    except DuplicateKeyError:
        raise HTTPException(detail='An institution with this tax_number already exists', status_code=403)
    if result is None:
        raise HTTPException(detail='An exception was thrown when trying to add a institution.', status_code=500)

    return JSONResponse(content=json_parser(dict(result)), status_code=200)


@router.put("/institution/edit", tags=['Institution'])
async def institution_edit(body: InstitutionRequestModel):
    try:
        result = institution_controller.update({body.tax_number}, body.__dict__)
    except:
        raise HTTPException(detail='Cannot edit institution', status_code=500)

    return JSONResponse(content=json_parser(result), status_code=200)


@router.get("/institution", tags=['Institution'])
async def institution_get():
    try:
        result = list(institution_controller.query_all({'status': True}))

        for res in result:
            res['_id'] = str(res['_id'])

        if result is None:
             return JSONResponse(content=json_parser({'message': 'Cannot find institutions', 'model': InstitutionRequestModel().__dict__}), status_code=404)
    except:
        raise HTTPException(detail='Cannot query institution, maybe no institution is available', status_code=500)

    return JSONResponse(content=json_parser(result), status_code=200)

