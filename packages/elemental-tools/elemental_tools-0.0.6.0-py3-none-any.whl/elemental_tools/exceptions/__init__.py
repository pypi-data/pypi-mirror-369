from elemental_tools.logger import Logger
import sys
from typing import Union

from fastapi.exceptions import HTTPException
from psycopg2.errors import UndefinedTable

from elemental_tools.design import UnicodeColors
from elemental_tools.logger import Logger

__logger__ = Logger(app_name="elemental", owner="Exception").log
__http_origin__ = "http-exception"
__task_origin__ = "task-exception"

def GetDuplicatedKey(exception):
    try:
        return str(exception.details['keyValue'])
    except:
        return None


class DependenciesNotFound(Exception):

    def __init__(self, *args):
        super().__init__()
        Exception(args)


class ScriptModuleMissing:

    def __init__(self, title):
        print(f'Script module missing when validating: {title}')


class ParameterMissing(Exception):

    def __init__(self, title):
        Exception.__init__(self, f"The argument {title} is missing.")


class SettingMissing(Exception):

    def __init__(self, title):
        Exception.__init__(self, f"The Setting: {title} cannot be found on the database\n"
                                 f"If you want to create a custom Setting, you must add to your code:\n\t"
                                 f"""from elemental_tools.api.settings import SettingsController, Setting

                                    _new_setting = Setting(
                                        sub= # user id,
                                        name= # setting name,
                                        value= # setting value
                                    )
                                    _settings = SettingsController()
                                    _settings.create(
                                        _new_setting
                                    )
                                """
                                 
                                 f"\n\n\tIf it was not your intent, try to run: python3 -m elemental_tools.Jarvis.install")


class ThreadTimeout(Exception):
    pass


class ThreadLimitExceeded(Exception):
    pass


class SkipExecution:

    def __init__(self, msg: str = "", app: str = None):
        __logger__('skip-execution', msg, app_name='scripts')


class InvalidCSV(Exception):

    def __init__(self, link):
        super().__init__(f"Cannot find csv on the provided link: {link}")





def __server_response__(det, status_code, headers):
    return f"Server Response: {det}\n\tServer Status:{status_code}\n\tServer Headers:{headers}"


def get_duplicated_key(exception):
    try:
        return str(exception.details['keyValue'])
    except:
        return None


class InvalidORMModel(Exception):

    def __init__(self, origin):
        super().__init__()
        Exception(f"Invalid ORM Model on Controller: {origin}")


class MaximumRetryTimesExceeded(Exception):

    def __init__(self, origin):
        super().__init__()
        __logger__("error", f"[{str(origin)}] - Maximum Retry Times Exceeded!")
        Exception(f"[{str(origin)}] - Maximum Retry Times Exceeded!")


class SettingNotSet(Exception):

    def __init__(self, title):
        Exception.__init__(self, f"Setting not Configured: {title} \n")


class MissingFile(Exception):

    def __init__(self, filename: str = None, exit: bool = False):
        message = f"Invalid File Path"
        if filename is not None:
            message = f"Invalid File Path: {filename}"

        super().__init__(message)
        __logger__("error", message)

        if exit:
            sys.exit(1)


class OverwriteFile(Exception):

    def __init__(self, filename: str):
        message = f"{UnicodeColors.red}File Path Already Exists: {filename}\n{UnicodeColors.bright_cyan}Type yes and hit enter to continue or ctrl+c to cancel.{UnicodeColors.reset}"
        user_input = None
        while user_input != "yes":
            print(message)
            user_input = input()
            __logger__("error", message, clean=True)


class InvalidExtension(Exception):

    def __init__(self, filename: str, ext: Union[str, list] = None):

        message = f"Invalid Extension on File: {filename}"
        if ext is not None and isinstance(ext, str):
            message = f"Invalid Extension: {ext} on {filename}"
        elif ext is not None and isinstance(ext, list):
            extensions = ',\n'.join(ext)
            message = f"Invalid Extension on {filename}\nAvailable Extensions:{extensions}"

        super().__init__(message)
        __logger__("error", message)


class InternalException(Exception):

    def __init__(self, message: str):
        super().__init__(message)
        __logger__("error", message)


class NotFound(HTTPException):
    detail = "Not Found"
    status_code = 404
    headers = None

    def __init__(self, what, message=None, status_code: int = status_code):
        if message is not None:
            self.headers = {"message": message}
        __logger__("error", __server_response__(self.detail, status_code, self.headers), origin=__http_origin__)
        super().__init__(detail=f"{what} {self.detail}", status_code=status_code, headers=self.headers)


class Invalid(HTTPException):
    headers = None
    status_code: int = 500

    def __init__(self, item: str, message=None, status_code: int = status_code):
        if message is not None:
            self.headers = {"message": message}

        self.detail = f"Invalid {item}"

        __logger__("error", __server_response__(self.detail, status_code, self.headers),
                   origin=__http_origin__)
        super().__init__(detail=self.detail, status_code=status_code, headers=self.headers)


class Unauthorized(HTTPException):
    detail: str = "Unauthorized"
    status_code: int = 401
    headers = None

    def __init__(self, item=None, message=None, retry_times: int = None, detail: str = None,
                 status_code: int = status_code):

        if item is not None:
            self.detail = f"Unauthorized {item}"

        if retry_times is not None:
            if retry_times == 0:
                self.detail += ". No Chances Left."
            else:
                self.detail += f". Chances Left: {str(retry_times)}"

        if message is not None:
            self.headers = {"message": message}
        if detail is not None:
            self.detail = detail

        __logger__("error", __server_response__(self.detail, status_code, self.headers), origin=__http_origin__)
        super().__init__(detail=self.detail, status_code=status_code, headers=self.headers)


class SaveException(HTTPException):
    headers = None
    status_code: int = 409

    def __init__(self, item_name: str, exception: str = None, status_code: int = status_code):
        det = f"Cannot Save {item_name}"
        if exception is not None:
            det += f". Because of Exception: {exception}"

        __logger__("error", __server_response__(det, status_code, self.headers), origin=__http_origin__)
        super().__init__(detail=det, status_code=status_code)


class QueryException(HTTPException):
    headers = None
    status_code: int = 409

    def __init__(self, item_name: str, exception: str = None, status_code: int = status_code):
        det = f"Cannot Query {item_name}"
        if exception is not None:
            det += f". Because of Exception: {exception}"

        __logger__("error", __server_response__(det, status_code, self.headers), origin=__http_origin__)
        super().__init__(detail=det, status_code=status_code)


class NotFoundDevice(NotFound):
    headers = None

    def __init__(self):
        super().__init__(f"Device")


class UnauthorizedDevice(HTTPException):
    headers = None
    message = "Unauthorized Device. Please check your e-mail box."
    status_code: int = 401

    def __init__(self):
        super().__init__(detail="Unauthorized Device. Please check your e-mail box.", headers={"message": self.message},
                         status_code=self.status_code)


class Forbidden(HTTPException):
    detail = "Forbidden"
    headers = None
    status_code: int = 403

    def __init__(self, detail, message=None, status_code: int = status_code):
        if message is not None:
            self.headers = {"message": message}

        detail += f" {detail}"
        super().__init__(detail=detail, status_code=status_code, headers=self.headers)


class AlreadyExists(HTTPException):
    headers = None
    status_code: int = 409

    def __init__(self, origin, *duplicates):
        dup_str = None
        last_index = len(duplicates)

        self.detail = f"A {origin} already exists..."
        for idx, dup in enumerate(duplicates):

            if dup_str is None:
                dup_str = str(dup)

            if idx == last_index:
                dup_str += f"and {str(dup)}"

            elif last_index > idx > 0:
                dup_str += f", {dup}"

        if dup_str is not None:
            self.detail = f"A {origin} with {dup_str} already exists..."

        super().__init__(detail=self.detail, status_code=self.status_code)


class TestNotFound(Exception):
    detail = "Test Not Found: "

    def __init__(self, test_title):
        self.test_title = test_title
        super().__init__(f"{self.detail} {test_title}")

    def __call__(self, *args, **kwargs):
        super().__init__(f"{self.detail} {self.test_title}")


class Subscribe(Unauthorized):

    def __init__(self):
        super().__init__(detail="Please, subscribe.", message="Please, subscribe.")


class AskYourManager(Unauthorized):
    detail = "You're unable to perform this action. Please ask for administrator permissions."

    def __init__(self):
        super().__init__(detail=self.detail, message=self.detail)
