import os
import re
import json
import inspect
import subprocess
import importlib.util
from copy import deepcopy
from enum import Enum
from typing import Type, Annotated, Union, Tuple, Any

from pydantic import BaseModel, create_model, AfterValidator, PlainSerializer
from pydantic.fields import FieldInfo

from elemental_tools import environ
from elemental_tools.logger import Logger
from elemental_tools.tools import get_package_name
from elemental_tools.exceptions import ScriptModuleMissing
from elemental_tools.pydantic.config import ignored_arguments

__logger__ = Logger(os.getenv(environ.app_name), get_package_name(__file__)).log

from elemental_tools.tools import get_package_name


# Function to generate Pydantic models for script functions
def generate_pydantic_model_from_function(function):
    class Model(BaseModel):
        _: str = None
        class Config:
            arbitrary_types_allowed = True

    arg_spec = inspect.signature(function)
    for param_name, param in arg_spec.parameters.items():
        if param_name in ignored_arguments:
            continue
        param_type = param.annotation if param.annotation != param.empty else None
        Model.__annotations__[param_name] = (param_type, param.default)

    return Model


def generate_pydantic_model_from_path(path: str):
    result = None
    __logger__('info', f"Generating models from path {path}")
    scripts_root_path = path
    script_functions = {}

    # Load scripts from the scripts directory
    try:

        for current_script_dir in os.listdir(scripts_root_path):

            abs_path = os.path.join(scripts_root_path, current_script_dir)
            if os.path.isdir(abs_path):
                for script_file in os.listdir(abs_path):
                    if script_file.endswith('main.py'):
                        script_name = os.path.splitext(script_file)[0]
                        try:
                            script_path = os.path.join(abs_path, script_file)

                            spec = importlib.util.spec_from_file_location(script_name, script_path)
                            module = importlib.util.module_from_spec(spec)
                            try:
                                spec.loader.exec_module(module)
                            except:
                                pass

                            __logger__('info',
                                   f"Testing: {current_script_dir}")
                            try:

                                script_functions[current_script_dir] = module.start
                            except Exception as e:
                                __logger__('critical',
                                       f"Cannot load: {current_script_dir} due to exception '{str(e)}' on testing")

                        except ModuleNotFoundError as e:
                            # Extract the package name from the exception message (if available)
                            package_name_match = re.search(r"'(.*?)'", str(e))
                            if package_name_match:
                                package_name = package_name_match.group(1)
                                try:
                                    # Attempt to install the missing package
                                    subprocess.run(["pip", "install", package_name])
                                except Exception as install_error:
                                    print(f"Error installing {package_name}: {install_error}")
                                else:
                                    # Retry importing the script after successful installation
                                    try:

                                        module = importlib.util.module_from_spec(spec)

                                        spec.loader.exec_module(module)
                                        script_functions[current_script_dir] = module.start
                                    except ModuleNotFoundError:
                                        ScriptModuleMissing(f"{current_script_dir}\nModuleNotFoundError: {str(e)}")
                            else:
                                # ScriptModuleMissing(f"{current_script_dir}\nModuleNotFoundError: {str(e)}")
                                pass

        result = {}
        for script_name, func in script_functions.items():
            try:
                result[script_name] = {'pydantic_model': generate_pydantic_model_from_function(func), 'function': func}
            except Exception as e:
                __logger__('critical', f"Pydantic models cannot be load for script: {script_name} because of exception: {str(e)}")

        __logger__('success', f"Pydantic models loaded successfully: {result.items()}")

    except Exception as e:
        __logger__('alert', f"No script addons found! Because of the exception {e} the script functions were left this way: {script_functions.items()}")

    return result


def generate_script_information_from_pydantic_models(script_pydantic_models=None):

    if script_pydantic_models is None:
        return None

    __logger__('info', f"Generating script information from pydantic models: {str(script_pydantic_models)}")
    scripts_information = {}

    for script_name, parameters_specs in script_pydantic_models.items():

        __logger__('info', f"Processing: {script_name} script")

        pydantic_model = parameters_specs['pydantic_model']
        scripts_information[script_name] = {}
        scripts_information[script_name]['required'] = []
        scripts_information[script_name]['parameters'] = {}

        for parameter_name, parameter_spec in pydantic_model.__annotations__.items():

            if isinstance(parameter_spec, tuple):
                __logger__('info', f"Parameter: {parameter_name} was found in {script_name}")
                try:
                    __logger__('info', f"Parameter: Attempting to retrieve parameter type...")
                    scripts_information[script_name]['parameters'][parameter_name] = {'type': parameter_spec[0].__name__}
                    __logger__('success', f"Parameter: Type found for {parameter_name} is {parameter_spec[0].__name__}")

                except Exception as e:
                    __logger__('alert', f"Parameter: type was not found in {script_name} start method")

                try:
                    if parameter_spec[1] is not None:
                        if parameter_spec[1].__name__ == '_empty':
                            scripts_information[script_name]['required'].append(parameter_name)

                except:
                    scripts_information[script_name]['parameters'][parameter_name]['default_value'] = parameter_spec[1]

                continue

            scripts_information[script_name]['parameters'][parameter_name] = {'type': parameter_spec.__name__}

    __logger__('success', f"Scripts information: \n{json.dumps(scripts_information, indent=2)}")

    return scripts_information


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)


class UserRoles(str, Enum):
    all = "*"
    newby = "newby"

    admin = "admin"
    owner = "owner"
    manager = "manager"
    editor = "editor"
    viewer = "viewer"

    customer = "customer"
    employee = "employee"


def partial_model(model: Type[BaseModel]):
    def make_field_optional(field: FieldInfo, default: Any = None) -> Tuple[Any, FieldInfo]:
        new = deepcopy(field)
        new.default = default
        new.annotation = Optional[field.annotation]  # type: ignore
        return new.annotation, new
    return create_model(
        f'Partial{model.__name__}',
        __base__=model,
        __module__=model.__module__,
        **{
            field_name: make_field_optional(field_info)
            for field_name, field_info in model.model_fields.items()
        }
    )


