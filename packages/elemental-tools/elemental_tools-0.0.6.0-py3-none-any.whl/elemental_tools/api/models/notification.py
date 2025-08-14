from datetime import datetime
from typing import Union

from bson import ObjectId
from pydantic import BaseModel, Field, PrivateAttr, field_validator

from elemental_tools.types import PyObjectId
from elemental_tools.api.controllers.template import TemplateController


class NotificationRequestModel(BaseModel, extra='allow', arbitrary_types_allowed=True):
	_id: PyObjectId = PrivateAttr()
	creation_date: str = Field(default_factory=datetime.now().isoformat, description='Self generated date time')
	role: Union[list, None] = Field(description='List of roles to notify. Check your admin to obtain more information about that.', default=None)
	status: Union[bool, None] = Field(description='Notification Status', default=False)
	status_email: Union[bool, None] = Field(description='Email Notification Status', default=False)
	smtp_id: Union[PyObjectId, None] = Field(description='The SMTP Configuration that notification must use to be sent.', default=None)
	status_wpp: Union[bool, None] = Field(description='Whatsapp Notification Status', default=False)
	content: Union[str, None] = Field(description='Notification Text or HTML Content', default=None)
	template_id: Union[PyObjectId, None] = Field(description='Template Id', default=None)
	sub: Union[PyObjectId, None] = Field(description='User who creates the Notification', default=None)
	customer_id: Union[PyObjectId, None] = Field(description='User or Users who the Notification is send', default=None)
	modifiers: Union[list, None] = Field(
		description='Template Modifiers to be used in conjunction with the content (Will be placed content > modifiers)',
		default=None)
	variables: Union[dict, None] = Field(
		description="Here you can pass the variables that must be parsed to the template. To use a variable on a template you must enclouser the variable with ${}\nExample: 'This is a sample template for ${name}'.\n\nIn order to place a name inside this template you might use the example on this doc.",
		default=None, examples=[{"name": "John Doe"}])
	last_response_execution: Union[str, None] = None

	def get_id(self):
		return ObjectId(self._id)

	def set_id(self, _id):
		self._id = ObjectId(_id)
		return ObjectId(self._id)

	@field_validator('template_id')
	def valid_template(cls, template_id):
		_this_template = TemplateController().query({"_id": ObjectId(template_id)})
		if _this_template is not None:
			return template_id
