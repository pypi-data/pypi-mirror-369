from datetime import datetime
from typing import Optional, Union, List

from bson import ObjectId
from fastapi import UploadFile, HTTPException
from pydantic import BaseModel, Field, PrivateAttr, field_validator

from elemental_tools.types import PyObjectId
from elemental_tools.api.models import UserRequestModel


class TemplateResourceModifiers(BaseModel, arbitrary_types_allowed=True):
    modifier_id: PyObjectId = Field(description='Modifier Id', default_factory=ObjectId)
    title: str = Field(description='Modifier Title')
    content: str = Field(description='Modifier Text or HTML Content')

    @classmethod
    @field_validator("title")
    def validate_title(cls, title):
        if len(str(title)) >= 1:
            return title
        else:
            raise HTTPException(detail='Invalid Resource Title', status_code=403)

    @classmethod
    @field_validator("content")
    def validate_content(cls, content):
        if content is None:
            return None
        elif len(str(content)) >= 1:
            return content
        else:
            raise HTTPException(detail='Resource Content Too Short', status_code=403)

    @classmethod
    @field_validator('modifier_id')
    def validate_modifier_id(cls, modifier_id):
        if modifier_id is None:
            return PyObjectId

    def get_id(self):
        if self.modifier_id is not None:
            return ObjectId(self.modifier_id)

    def set_id(self, _id):
        self.modifier_id = ObjectId(_id)
        return self.modifier_id


class TemplateResourceRequestModel(BaseModel, arbitrary_types_allowed=True):
    _id = PrivateAttr(default=None)
    creation_date: str = Field(default_factory=datetime.now().isoformat)
    sub: Union[PyObjectId, None] = Field(description='Resource Owner Id', default=None)
    status: Union[bool, None] = Field(description='Resource Status', default=True)
    title: str = Field(description='Resource Title')
    personal: Optional[bool] = Field(description="Indicates whenever the resource is shared with the siblings users", default=True)
    content: Union[str, None] = Field(description='Resource Text or HTML Content', default=None)
    icon: Union[UploadFile, None] = Field(description="Icon file or url to upload and store as resource icon", default=None)
    editable: Optional[bool] = Field(description="Indicates whenever the resource is editable by users", default=True)
    modifiers: Union[List[TemplateResourceModifiers], None] = Field(description="Store the modifiers for the current resource", default_factory=list, examples=[[{"title": "This Modifier", "content": ""}]])

    def get_id(self):
        if self._id is not None:
            return ObjectId(self._id)

    def set_id(self, _id):
        if _id is not None:
            self._id = ObjectId(_id)
            return self._id

    @classmethod
    @field_validator('modifiers')
    def valid_modifiers(cls, mods: list):
        result = []

        for mod in mods:

            if not isinstance(mod, TemplateResourceModifiers):
                mod = TemplateResourceModifiers(**mod)

            if mod.modifier_id not in [md.modifier_id for md in result]:
                result.append(mod)

        return result


class TemplateRequestModel(BaseModel, arbitrary_types_allowed=True):
    _id = PrivateAttr(default=None)
    creation_date: str = Field(default_factory=datetime.now().isoformat)
    sub: Union[PyObjectId, None] = Field(description='Template User Owner', default=None)
    status: Union[bool, None] = Field(description='Template Status', default=False)
    content: Union[str, None] = Field(description='Template Text or HTML Content', default=None)
    subject: Union[str, None] = Field(description='Template Subject', default=None)
    title: Union[str, None] = Field(description='Template Title', default=None)
    type: str = Field(description='Template Type', default='personal')
    variables: Union[dict, None] = Field(description='Template available variables.', default={key: None for key in UserRequestModel.model_fields.keys()})
    resources: list = Field(description='Template resources.', default=[])

    def get_id(self):
        if self._id is not None:
            return ObjectId(self._id)

    def set_id(self, _id):
        if _id is not None:
            self._id = ObjectId(_id)
            return self._id

