import uuid
from typing import Union

from bson import ObjectId
from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import field_validator, Field, PrivateAttr

from elemental_tools.types import PyObjectId
from elemental_tools.json import json_to_bson
from elemental_tools.api.controllers.device import DeviceController
from elemental_tools.api.controllers.user import UserController
from elemental_tools.api.models import UserRequestModel

user_controller = UserController()
device_controller = DeviceController()


class DeviceRequestModel(BaseModel, arbitrary_types_allowed=True):
    _id = PrivateAttr()
    sub: PyObjectId = Field(description='User id')
    fingerprint: str = Field(description='User device fingerprint')
    location: Union[str, None] = Field(description='Device location', default=None)
    status: bool = Field(description='User device allowance status', default=False)
    _retry_times: int = PrivateAttr(default=3)
    _access_token: str = PrivateAttr(default=uuid.uuid4().hex)
    _refresh_token: str = PrivateAttr(default=uuid.uuid4().hex)

    @field_validator('sub')
    def validate_sub(cls, sub):
        try:
            _this_user = user_controller.query({"_id": ObjectId(sub)})
            if _this_user is not None:
                return ObjectId(sub)
        except:
            raise HTTPException(detail='Invalid sub.', status_code=404)

    def get_access_token(self):
        return self._access_token

    def get_refresh_token(self):
        return self._refresh_token

    def get_id(self):
        if self._id is not None:
            return ObjectId(self._id)

    def set_id(self, _id):
        if _id is not None:
            self._id = ObjectId(_id)
            return self._id

    def set_retry_times(self, times):
        self._retry_times = times
        return times

    def get_retry_times(self):
        return self._retry_times

    def set_refresh_token(self, _refresh_token):
        self._refresh_token = _refresh_token
        return _refresh_token


class LoginRequestModel(BaseModel):
    email: str = Field(description='User email for authentication', default=None)
    password: str = Field(description='User password', default=None)
    _this_user = PrivateAttr()

    @field_validator('email')
    def validate_email(cls, email):
        _this_user = user_controller.query({"email": email})

        if _this_user is not None:
            return email
        else:
            raise HTTPException(detail='Invalid e-mail, please register.',
                                status_code=404)

    @field_validator('password')
    def validate_password(cls, password):
        if len(password) >= 6:
            return password
        else:
            raise HTTPException(detail='Invalid password, please make sure you are entering at least 6 chars.', status_code=401)

    def validate_password_and_device(self, fingerprint):
        _authorized_user = user_controller.query({"email": self.email, "password": self.password})

        if _authorized_user is not None:
            _this_user = UserRequestModel(**_authorized_user)
            _this_user.set_id(_authorized_user["_id"])
            _this_user_device = device_controller.query({"fingerprint": fingerprint, "sub": _this_user.get_id()})
            if _this_user_device is not None:
                _device = DeviceRequestModel(**_this_user_device)
                _device.set_id(_this_user_device["_id"])

                if _device.status:
                    _device._access_token = _device.get_access_token()
                    _device.set_retry_times(3)
                    _update_result = device_controller.update({"_id": _device.get_id()}, _device.model_dump(include=["_access_token", "_retry_times"]))

                    return _device.get_id(), _device.get_access_token()

                else:
                    raise HTTPException(
                        detail="Unauthorized Device. Please check your e-mail for a authorization request.",
                        status_code=403
                    )

            _device = DeviceRequestModel(**{"fingerprint": fingerprint, "sub": ObjectId(_this_user.get_id())})
            _device = json_to_bson(_device.model_dump())
            device_controller.add(_device)

            raise HTTPException(detail="Unauthorized Device. Please check your e-mail for a authorization request.", status_code=403)

        else:
            _this_user = user_controller.query({"email": self.email})

            if _this_user is not None:

                _this_user_device = device_controller.query(
                    {"fingerprint": fingerprint, "sub": ObjectId(_this_user['_id'])})

                if _this_user_device is not None:
                    _device = DeviceRequestModel(**_this_user_device)
                    _device.set_id(_this_user_device["_id"])

                    if _device.status:

                        if _device.get_retry_times() > 1:
                            device_controller.update({"_id": ObjectId(_device.get_id())}, {"status": False})
                            raise HTTPException(detail=f'Invalid password, no chances left. Device has been blocked. Please check your email to allow this device again.', status_code=401)

                        device_controller.update({"_id": ObjectId(_device.get_id())}, {"retry_times": _device.get_retry_times() -1})
                        raise HTTPException(detail=f'Invalid password, {_device.get_retry_times()} chances left.',
                                            status_code=401)

            raise HTTPException(detail=f'Invalid email, please check.',
                                status_code=404)

