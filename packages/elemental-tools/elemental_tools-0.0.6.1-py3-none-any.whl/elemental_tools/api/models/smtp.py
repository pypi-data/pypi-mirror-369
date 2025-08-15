from typing import Union

from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr, PrivateAttr

from elemental_tools.types import PyObjectId
from elemental_tools.api.controllers.smtp import SMTPController


_smtp_controller = SMTPController()


class SMTPRequestModel(BaseModel, arbitrary_types_allowed=True):
    _id: PyObjectId = PrivateAttr()
    sub: Union[PyObjectId, None] = Field(description="User Who Own the SMTP Configuration", default=None)
    status: bool = Field(description="Status of the SMTP Configuration. True when it's working otherwise False.", default=False)

    server: str = Field(description='SMTP Server')
    port: int = Field(description='SMTP Server Port')
    email: EmailStr = Field(description='User email for google drive sharing and other stuff')
    password: Union[str, None] = Field(description='Password', default=None)

    def get_id(self):
        """
        :return: The hidden element "_id" as ObjectId
        :type: ObjectId
        """
        try:
            this_smtp_query_result = _smtp_controller.query({"sub": self.sub, "email": self.email})
            if this_smtp_query_result is not None:
                self._id = this_smtp_query_result['_id']
            return ObjectId(self._id)
        except:
            return None
