from datetime import datetime
from typing import Union

from bson import ObjectId
from pydantic import BaseModel, Field, field_validator, PrivateAttr

from elemental_tools.types import PyObjectId


class TaskModel(BaseModel, arbitrary_types_allowed=True):
    _id: PyObjectId = PrivateAttr(default=None)
    description: str = Field(examples=["ras"],
                             description="Name of the folder where the script you are running is stored")

    timer: int = Field(examples=[10, 30, 1000], default=None, description="A milliseconds timer (ms) for task execution loop, if no timer is specified the task will be executed immediately or by the schedule date if provided.")

    schedule_date: Union[datetime, None] = Field(examples=[str(datetime.now().isoformat())],
                                                 description="A timestamp to schedule task execution if no schedule_date is specified, task will be executed immediately or by the timer if provided",
                                                 default=None)

    loops: Union[int, None] = Field(examples=[0, 1, 10000, None], default=None,
                                    description="A loop counter for the task execution, if no loops were provided the task will be executed immediately infinitely")

    task_name: str = Field(examples=["ras"],
                           description="Name of the folder where the script you are running is stored")

    parameters: Union[dict, None] = Field(examples=[{"current_script_param": "current_execution_argument"}],
                             description="A dictionary to store the execution arguments, such as passwords, usernames, and so on... They must have the correct type on your start method at the main.py of each script folder located at the scripts directory.", default={})

    sub: Union[ObjectId, str, None] = Field(examples=["User id"],
                                            description="A loop counter for the task execution, if no loops were provided the task will be executed immediately infinitely")

    status: bool = Field(description="Indicates when a Task will be Executed or Not.", examples=[True, False], default=False)
    state: Union[str, None] = Field(description="Indicates the Task State.", examples=["Running", "Finished"], default=None)

    _entrypoint: str

    @field_validator("schedule_date")
    def future_date_validator(cls, value):
        if value is not None:
            if value <= datetime.now():
                raise ValueError("schedule_date must be a future date and time")
            return value
        else:
            pass

    def get_entrypoint(self):
        return self._entrypoint
