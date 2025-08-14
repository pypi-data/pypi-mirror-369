from bson import ObjectId

from elemental_tools.api.models import UserRequestModel
from elemental_tools.api.models.templates import TemplateRequestModel

from elemental_tools.api.controllers.user import UserController
from elemental_tools.api.controllers.template import TemplateController


class Templates:
    _template_controller = TemplateController()
    _user_controller = UserController()
    this_template = None
    user_templates = None
    _user = None
    _sub = None

    def __init__(self, sub: ObjectId, template_id: ObjectId = None):

        self._sub = sub

        _this_user = self._user_controller.query({"_id": ObjectId(sub)})
        
        if _this_user is not None:
            self._user = UserRequestModel(**_this_user)
            self.user_templates = self._template_controller.query_all({"sub": sub})
            
            if template_id is not None:
                
                self.this_template = self._template_controller.query({"_id": ObjectId(template_id)})
                self.this_template = TemplateRequestModel(**self.this_template)
                
    def reload_all_templates(self):

        _this_user = self._user_controller.query({"_id": ObjectId(self._sub)})

        if _this_user is not None:
            self._user = UserRequestModel(**_this_user)
            self.user_templates = self._template_controller.query_all({"sub": self._sub})

    def load_variables(self, template_id: ObjectId):

        _this_template = self._template_controller.query({"sub": str(self._user.get_id()), "_id": template_id})
        if _this_template is not None:
            _model = TemplateRequestModel(**_this_template)
            self.variables = _model.variables
            return _model.variables
        return False

    def check(self, modifiers: list, variables: dict):

        if self.this_template is not None:
            if all([mod in self.this_template.modifiers.keys() for mod in modifiers]):
                return self.this_template

        invalid_modifiers = [mod not in self.this_template.modifiers.keys() for mod in modifiers]
        raise Exception(f"Invalid modifier's: {invalid_modifiers}")

    def load(self, modifiers: list, variables: dict):

        _this_template = self.check(modifiers, variables)
        _content = ""

        if _this_template.content is not None:
            _content += _this_template.content

        for modifier in modifiers:
            if modifier in _this_template.modifiers.keys():
                _content += _this_template.modifiers[modifier]

        for variable in variables.keys():
            
            _replace_ = "$" + "{" + variable + "}"
            _content = _content.replace(_replace_, variables[variable])

        return str(_content)



