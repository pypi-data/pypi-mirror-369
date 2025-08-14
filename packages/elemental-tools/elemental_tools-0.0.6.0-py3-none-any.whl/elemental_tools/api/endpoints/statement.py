from typing import Annotated

from fastapi.responses import JSONResponse

from elemental_tools.json import json_parser
from elemental_tools.api.controllers.statement import StatementController
from fastapi import HTTPException
from fastapi.routing import APIRouter
from elemental_tools.api.models import StatementRequestModel, UserRequestModel

router = APIRouter()


@router.get("/statement", tags=['Statement'])
async def statement_get(_user: Annotated[UserRequestModel, None], date: str, institution=None):
	try:
		statement_db = StatementController(sub=_user.get_id(), institution_id=institution)

		result = statement_db.retrieve_statement()

		if result is None:
			return JSONResponse(content=json_parser({'message': 'Cannot find user', 'model': StatementRequestModel().__dict__}), status_code=404)
	except:
		raise HTTPException(detail='Cannot query user', status_code=500)

	return JSONResponse(content=json_parser(result), status_code=200)

