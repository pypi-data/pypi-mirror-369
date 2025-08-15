from datetime import datetime
from enum import Enum
from typing import Optional, Union, List, Dict

from bson import ObjectId

from pydantic import field_validator, Field, PrivateAttr, EmailStr
from pydantic import BaseModel

from fastapi import HTTPException

from elemental_tools.types import PyObjectId
from elemental_tools.api.models.smtp import SMTPRequestModel


class GooglePermission(BaseModel, arbitrary_types_allowed=True):

    sub: Union[PyObjectId, None] = Field(description='Id`s of the user that is gaining access to this doc', default=None)
    email: str = Field(description='The current email assigned to the permission of this sub. For later updates.', default=None)
    date: str = Field(description='A timestamp for the changes made to the doc', default=datetime.now().isoformat())


class GoogleDriveFolder(BaseModel):

    folder_caption: str = Field(description='A string containing the Google Drive folder caption identifier', default=None)
    external_id: Union[str, None] = Field(description='Save the id for the current sheet', default=None)
    permissions: Union[list, None] = Field(description='A list containing the ids and emails of the users that already have access to this sheet', default=[])


class GoogleSheet(BaseModel):

    name: Union[str, None] = Field(description='A name for the sheet to ease identification', default=None)
    external_id: Union[str, None] = Field(description='Id for the current sheet', default=None)
    date: str = Field(description='A timestamp for the changes made to the doc', default=datetime.now().isoformat())
    authorized_emails: list = Field(description='A list with the emails of the persons who can see this sheet.', default=[])


class GoogleInformation(BaseModel):

    sheets: Dict[str, GoogleSheet] = Field(description='Store the Year and the Id for each Google Sheet Already Created.', default={})
    sheets_permissions: list = Field(description='Save email list with the permissions to the sheets', default=[])
    drive: Dict[str, GoogleDriveFolder] = Field(description='Keeps ids for the folders where the user information is stored.', default={})


class UserInstitutionSetting(BaseModel, arbitrary_types_allowed=True):

    status: Union[bool, None] = Field(examples=[True, False], description='A boolean indicating whether the institution integration will be enabled', default=True)

    institution_id: Union[PyObjectId, str] = Field(description='A string id obtained using the institution endpoint')

    email: str = Field(description='Email for the user account on the current institution website')

    password: str = Field(description='Password for the user account on the current institution website')

    last_sync: str = Field(description='Timestamp for the last synchronization to this institution', default=datetime.now().isoformat())

    @field_validator('institution_id')
    def validate_institution_id(cls, institution_id):
        try:
            return str(institution_id)
        except:
            raise HTTPException(detail='Invalid Institution Id.', status_code=500)


class UserCompanyRoles(str, Enum):
    owner = 'owner'
    editor = 'editor'
    viewer = 'viewer'
    

class UserCompany(BaseModel, arbitrary_types_allowed=True):
    role: UserCompanyRoles = Field(description='User Role')
    company_id: PyObjectId = Field(description='Company Id')


class SonRequestModel(BaseModel, arbitrary_types_allowed=True):
    _id: PyObjectId = PrivateAttr()
    sub: Union[PyObjectId, None] = Field(description='Parent ID',  default=None)
    name: str = Field(description='Username')
    email: EmailStr = Field(description='User Email')
    phone: Union[str, None] = Field(description='User Phone', default=None)
    cellphone: Union[str, None] = Field(description='User Cellphone, for whatsapp and sms', default=None)
    wpp_user_id: Union[str, None] = Field(description='Whatsapp User ID', default=None)
    status: bool = Field(description='User Status', default=False)
    parent_assigned_status: Union[str, None] = Field(description="String for user set a status to customer", default=None)
    obs: Union[str, None] = Field(description="String for user set a obs to customer", default=None)
    admin: bool = Field(description='Set if a user has admin privileges', default=False)
    tax: float = Field(description='Set tax for user transactions', default=0.0065)
    language: str = Field(description='Language for message translation', default='pt')
    is_human_attendance: Optional[bool] = Field(description='Indicate whenever the user is under attendance by a human being.', default=False)
    last_subject: Optional[str] = Field(description='Indicates the latest subject threaded with the chat', default="")
    _last_update: str = PrivateAttr(default='')
    companies: Union[List[UserCompany], list, None] = Field(description='User Companies', default=[])
    google_sync: bool = Field(description='Activate the google statement synchronization for the current user', default=False)
    institutions: Union[List[UserInstitutionSetting], list, None] = Field(examples=[[UserInstitutionSetting(**{"status": True, "institution_id": ObjectId(str("65dbfb92b01fc2f7ebe66620")), "email": "a@b.com", "password": "123456"})]], description='Store the user information for the institutions to be integrated', default=[])
    google: Optional[GoogleInformation] = Field(default=GoogleInformation())

    def set_id(self, value):
        self._id = value

    @classmethod
    @field_validator('cellphone')
    def validate_cellphone(cls, cellphone):
        if cellphone is not None:
            cls._last_update = datetime.now().isoformat()
            return cellphone
        else:
            raise HTTPException(detail='Invalid cellphone.', status_code=500)

    @classmethod
    @field_validator('password')
    def validate_password(cls, password):
        if password is not None:
            if len(password) >= 6:
                return password
            else:
                raise HTTPException(detail='Invalid password, please make sure you are entering at least 6 chars.', status_code=403)

    @classmethod
    @field_validator('companies')
    def valid_companies(cls, companies: list):
        result = []

        for company in companies:
            if not isinstance(company, UserCompany):
                result.append(UserCompany(**company))
            else:
                result.append(company)

        return result

    @classmethod
    @field_validator('institutions')
    def valid_institutions(cls, institutions: list):
        result = []

        for institution in institutions:
            if not isinstance(institution, UserInstitutionSetting):
                result.append(UserInstitutionSetting(**institution))
            else:
                result.append(institution)

        return result

    def get_id(self):
        """

        :return: The hidden element _id as ObjectId
        :type: ObjectId
        """
        try:
            return ObjectId(self._id)
        except:
            return None

    def get_google(self):
        return self.google


class UserRequestModel(BaseModel, arbitrary_types_allowed=True):
    _id: PyObjectId = PrivateAttr()
    sub: Union[PyObjectId, None] = Field(description='Parent ID',  default=None)
    name: str = Field(description='Username')
    email: EmailStr = Field(description='User Email')
    password: str = Field(description='Password')
    phone: Union[str, None] = Field(description='User Phone', default=None)
    cellphone: Union[str, None] = Field(description='User Cellphone, for whatsapp and sms', default=None)
    wpp_user_id: Union[str, None] = Field(description='Whatsapp User ID', default=None)
    status: bool = Field(description='User Status', default=False)
    parent_assigned_status: Union[str, None] = Field(description="String for user set a status to customer", default=None)
    obs: Union[str, None] = Field(description="String for user set a obs to customer", default=None)
    admin: bool = Field(description='Set if a user has admin privileges', default=False)
    tax: float = Field(description='Set tax for user transactions', default=0.0065)
    language: str = Field(description='Language for message translation', default='pt')
    is_human_attendance: Optional[bool] = Field(description='Indicate whenever the user is under attendance by a human being.', default=False)
    last_subject: Optional[str] = Field(description='Indicates the latest subject threaded with the chat', default="")
    _last_update: str = PrivateAttr(default='')
    companies: Union[List[UserCompany], list, None] = Field(description='User Companies', default=[])
    google_sync: bool = Field(description='Activate the google statement synchronization for the current user', default=False)
    institutions: Union[List[UserInstitutionSetting], list, None] = Field(examples=[[UserInstitutionSetting(**{"status": True, "institution_id": ObjectId(str("65dbfb92b01fc2f7ebe66620")), "email": "a@b.com", "password": "123456"})]], description='Store the user information for the institutions to be integrated', default=[])
    google: Optional[GoogleInformation] = Field(default=GoogleInformation())

    def set_id(self, value):
        self._id = value

    @classmethod
    @field_validator('cellphone')
    def validate_cellphone(cls, cellphone):
        if cellphone is not None:
            cls._last_update = datetime.now().isoformat()
            return cellphone
        else:
            raise HTTPException(detail='Invalid cellphone.', status_code=500)

    @classmethod
    @field_validator('password')
    def validate_password(cls, password):
        if password is not None:
            if len(password) >= 6:
                return password
            else:
                raise HTTPException(detail='Invalid password, please make sure you are entering at least 6 chars.', status_code=403)

    @classmethod
    @field_validator('companies')
    def valid_companies(cls, companies: list):
        result = []

        for company in companies:
            if not isinstance(company, UserCompany):
                result.append(UserCompany(**company))
            else:
                result.append(company)

        return result

    @classmethod
    @field_validator('institutions')
    def valid_institutions(cls, institutions: list):
        result = []

        for institution in institutions:
            if not isinstance(institution, UserInstitutionSetting):
                result.append(UserInstitutionSetting(**institution))
            else:
                result.append(institution)

        return result

    def get_id(self):
        """

        :return: The hidden element _id as ObjectId
        :type: ObjectId
        """
        try:
            return ObjectId(self._id)
        except:
            return None

    def get_google(self):
        return self.google


class StatementRequestModel(BaseModel, arbitrary_types_allowed=True):
    sub: Union[PyObjectId, None] = Field(description='User id for the current statement registration', default=None)
    status: bool = Field(description='User status', default=False)
    admin: bool = Field(description='Set if a user has admin privileges', default=False)
    tax: float = Field(description='Set tax for user transactions', default=0.0065)
    language: str = Field(description='Language for message translation', default='pt')
    last_update: str = Field(
        description='A date time that will be defined automatically whenever the document changes',
        default=datetime.now())


class SheetStyle(BaseModel):
    background: str
    color: str


class InstitutionRequestModel(BaseModel):
    tax_number: str = Field(description='Institution tax number known as CNPJ in Brazil')
    name: str = Field(description='Institution name', default=None)
    alias: str = Field(description='The name that will be used in user sheets')
    status: bool = Field(description='Institution status', default=False)
    website: str = Field(description='Website of the current institution', default=None)

    style: SheetStyle = Field(description='Save the style of the current institution', examples=[{'background': "#000000", 'color': "#ffffff"}])

    last_update: str = Field(
        examples=[datetime.now().isoformat()],
        description='A date time that will be defined automatically whenever the document changes',
        default=datetime.now().isoformat()
    )

    def get_id(self):
        if self._id is not None:
            return ObjectId(self._id)


class CompanyRequestModel(BaseModel, arbitrary_types_allowed=True):
    _id: PyObjectId = PrivateAttr()
    sub: Union[PyObjectId, None] = Field(description='Parent ID',  default=None)
    name: str = Field(description='Company Name')
    email: EmailStr = Field(description='Company Email')
    phone: Union[str, None] = Field(description='Company Phone', default=None)
    cellphone: Union[str, None] = Field(description='Company Cellphone, for Whatsapp and SMS', default=None)
    status: bool = Field(description='Company Status', default=False)
    tax: float = Field(description='Set Tax for Company Transactions', default=0.0065)

    def set_id(self, value):
        self._id = value

    @field_validator('cellphone')
    def validate_cellphone(cls, cellphone):
        if cellphone is not None:
            cls._last_update = datetime.now().isoformat()
            return cellphone
        else:
            raise HTTPException(detail='Invalid cellphone.', status_code=500)

    def get_id(self):
        """

        :return: The hidden element _id as ObjectId
        :type: ObjectId
        """
        try:
            return ObjectId(self._id)
        except:
            return None
