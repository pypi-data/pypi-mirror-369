import os
from os import path

from icecream import ic

from elemental_tools import environ
from elemental_tools.logger import Logger
from elemental_tools.config import root_user
from elemental_tools.api.controllers import TaskController, collection as task_collection
from elemental_tools.tools import get_package_name


def run():
    __logger__ = Logger(app_name=os.getenv(environ.app_name, "elemental-tools"), owner=get_package_name(__file__))

    task_controller = TaskController()
    current_installed_scripts = task_collection.find({"sub": root_user})
    current_installed_script_names: list = [task["task_name"] for task in current_installed_scripts]

    internal_scripts_fp = path.dirname(path.abspath(__file__))
    internal_scripts_folder_items: list = os.listdir(internal_scripts_fp)
    internal_script_folders: list = [item for item in internal_scripts_folder_items if os.path.isdir(os.path.join(internal_scripts_fp, item)) and not str(item).startswith("_") and "main.py" in os.listdir(os.path.join(internal_scripts_fp, item))]

    if not len(internal_script_folders):
        __logger__("alert", f"Skipping Task Installation")

    for folder in internal_script_folders:
        if folder not in current_installed_script_names:
            __logger__("info", f"Installing Task: {folder}")

