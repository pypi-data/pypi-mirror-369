from datetime import datetime
from typing import Union

import uvicorn
from bson import ObjectId
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from pydantic import field_validator, BaseModel, Field
from starlette.middleware.cors import CORSMiddleware

from elemental_tools.api.models.task import TaskModel
from elemental_tools.logger import Logger

from elemental_tools.scripts.install import run as install_scripts

from elemental_tools.exceptions import ParameterMissing
from elemental_tools.pydantic import generate_script_information_from_pydantic_models

from elemental_tools.config import log_path, root_user
from elemental_tools.api.settings import SettingsController

from elemental_tools.api.controllers import TaskController
from elemental_tools.api.controllers.user import UserController

from elemental_tools.api.endpoints.auth import router as auth_endpoints
from elemental_tools.api.endpoints.companies import router as companies_endpoints
from elemental_tools.api.endpoints.institution import router as institution_endpoints
from elemental_tools.api.endpoints.notifications import router as notification_endpoints
from elemental_tools.api.endpoints.smtp import router as smtp_endpoints
from elemental_tools.api.endpoints.sons import router as sons_endpoints
from elemental_tools.api.endpoints.templates import router as template_endpoints
from elemental_tools.api.endpoints.user import router as user_endpoints


router = APIRouter()

logger = Logger(app_name='api', owner='kernel', destination=log_path).log


class Api(FastAPI):
    script_pydantic_models = None
    settings_db = SettingsController()

    def __init__(self, title: str = "", endpoints=None, log_path: str = None, script_pydantic_models: Union[dict, None] = None):
        super().__init__()
        self.logger = logger
        self.openapi_tags = [
            {"name": f"""{self.settings_db.get(root_user, "company_name")} - Backoffice API""", "description": "This API is designed to allow integration scripts schedules, and the models in it are also part of our Jarvis arsenal. See the documentation for more information."},
        ]

        self.include_router(auth_endpoints)
        self.include_router(user_endpoints)
        self.include_router(institution_endpoints)
        self.include_router(notification_endpoints)
        self.include_router(template_endpoints)
        self.include_router(companies_endpoints)
        self.include_router(smtp_endpoints)
        self.include_router(sons_endpoints)

        origins = ["*"]
        self.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS", "PATCH", "PUT", "DELETE"],
            allow_headers=["*"],
        )

        if endpoints is not None:
            self.include_router(**user_endpoints)

        if script_pydantic_models is not None:

            _user_controller = UserController()
            _task_controller = TaskController()

            install_scripts()

            script_router = APIRouter()
            scripts_information = generate_script_information_from_pydantic_models(script_pydantic_models)


            # Endpoint to schedule tasks
            class TaskRequestModel(TaskModel):

                @field_validator("task_name")
                def task_name_validator(cls, name):
                    cls._entrypoint = script_pydantic_models[name]
                    cls.parameters = script_pydantic_models[name]
                    return name

            def instant_run(func, args):

                def execute_function(func, args: dict = None):
                    if args is None:
                        return func()

                    try:
                        result = func(**args)
                    except TypeError:
                        try:
                            result = func(*args.values())
                        except TypeError as e:
                            raise ParameterMissing(str(e))

                    return result

                try:
                    result = execute_function(func, args)
                    return result
                except ParameterMissing as e:
                    raise HTTPException(detail=str(e), status_code=500)

            @script_router.post("/tasks/add", tags=['Scripts/Tasks'])
            def schedule_task(body: TaskRequestModel, run_test: bool = False):
                response = {"message": "Task processed successfully!"}

                logger('info', f"Searching for tasks by name: {body.task_name} in {script_pydantic_models}")

                # Store task data
                if body.task_name in script_pydantic_models.keys():
                    logger('info', f"Task {body.task_name} found in dict: {str(script_pydantic_models.keys())}")
                    if body.timer is None or run_test:
                        response['execution_result'] = instant_run(script_pydantic_models[body.task_name]['function'],
                                                                   body.parameters)
                        if not run_test:
                            return JSONResponse(content=str(response), status_code=200)

                    try:
                        _sub = ObjectId(body.sub)
                    except:
                        raise HTTPException(detail="sub is invalid", status_code=500)

                    _user = _user_controller.query({"_id": _sub})

                    if _user:

                        _insert_result = _task_controller.add(body)

                        if _insert_result:
                            return JSONResponse(content={"id": str(_insert_result)}, status_code=200)
                        else:
                            raise HTTPException(detail='Cannot save task schedule', status_code=500)

                    raise HTTPException(detail='sub not found', status_code=400)

                else:
                    raise HTTPException(detail='Task Not Found', status_code=404)

            # Endpoint to list available tasks
            @script_router.get("/tasks/list", tags=['Scripts/Tasks'])
            def list_tasks():
                return scripts_information

            self.include_router(script_router)


run = uvicorn.run
