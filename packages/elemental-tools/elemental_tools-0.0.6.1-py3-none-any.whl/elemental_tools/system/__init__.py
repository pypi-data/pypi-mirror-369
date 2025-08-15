import json
import os
from json import JSONDecodeError
from typing import Union

from dotenv import load_dotenv
from elemental_tools.logger import Logger
import multiprocessing
import os
import shutil
import struct

import psutil

from typing import Union, List, TextIO
from uuid import uuid4
from icecream import ic
from tqdm import tqdm
from time import sleep

from elemental_tools.constants import ref_length

from datetime import datetime, timedelta

from dotenv import load_dotenv

from elemental_tools.logger import Logger
from elemental_tools.tools import get_package_name

cache_file = None  # './_cache/.dump'
os.environ['TERM'] = "xterm"
float_precision = "d"


class Cache:

    def __init__(self, file: str = cache_file):
        self.cache_file = file

        if not os.path.isdir(os.path.dirname(os.path.abspath(cache_file))):
            os.makedirs(os.path.dirname(os.path.abspath(cache_file)), exist_ok=True)

        self.cache_file_content = open(cache_file, 'a+')
        if self.cache_file_content.readlines():
            self.cache_file_content = self.load()
            try:
                data = eval(self.cache_file_content.read())
                for cache_item in data:
                    for title, value in cache_item.items():
                        setattr(self, title, value)

            except SyntaxError:
                raise Exception("Failed to parse the cache file!")

    def save(self) -> Union[TextIO, str]:
        self.cache_file_content.write(
            str([{title: value for title, value in self.__dict__.items() if not title.startswith('__')}]))
        self.cache_file_content.close()
        if cache_file is not None:
            return open(cache_file, 'a+')
        return str()

    def load(self):
        return open(self.cache_file, 'a+')

    def get(self, prop):
        return getattr(self, prop, None)


class Config:
    """
    A class for managing configuration settings and persisting them to a file.

    Attributes:
        target (args):
        _debug (bool): Flag indicating whether debug mode is enabled.
        _path (str): Path to the configuration file.

    Methods:
        __init__(): Initializes the Config object by loading configuration from file.
        _dump(): Serializes the non-private attributes to JSON and writes to the config file.
        _load(): Loads configuration from the config file, or creates a new one if not found.
        update_config(**kwargs): Updates configuration settings with new values and writes them to file.
    """
    _debug: bool = True
    _path: str = os.path.join(os.path.abspath('./'), '.config')
    _log: Logger.log = Logger(app_name="Elemental-Tools", owner='config').log
    _loaded: bool = False

    def __init__(self, *target):
        """
        Initializes the Config object by loading configuration from file.

        Parameters:
            target (Union[object, callable]): Methods or Classes to bound the config.\
             So whenever the config changes, the assigned items gets propagated to its bound Methods and Classes;

        """
        self._target = target
        self._load()

    def _dump(self):
        """
        Serializes the non-private attributes to JSON and writes to the config file.
        """
        content = self._attributes()

        with open(self._path, 'w') as config_file:
            json.dump(content, config_file, indent=4)

    def __setattr__(self, key, value):

        object.__setattr__(self, key, value)
        if self._loaded:
            self._dump()

    def _load(self):
        """
        Loads configuration from the config file, or creates a new one if not found.
        """

        _path = object.__getattribute__(self, '_path')
        _dump = object.__getattribute__(self, '_dump')
        _targets = [*object.__getattribute__(self, '_target')]
        _attributes = object.__getattribute__(self, '_attributes')().items
        _log = object.__getattribute__(self, '_log')

        try:
            with open(_path, 'r') as config_file:
                try:
                    content = json.load(config_file)
                    # Assign loaded values to class attributes
                    for name, value in content.items():
                        object.__setattr__(self, name, value)

                except JSONDecodeError as json_e:
                    _dump()

        # If the file doesn't exist, dump default configuration
        except FileNotFoundError as file_e:
            _dump()

        for target in _targets:
            for attr, value in _attributes():
                try:
                    _log('info', f'Assigning Config: {attr} to {value}', origin=target)
                    object.__setattr__(target, attr, value)
                    _log('success', f'Config Assigned', origin=target)
                except AttributeError as e:
                    _log('alert', f'Failed Assigning {attr}: {str(e)}', origin=target)

        for attr, value in _attributes():
            try:
                _log('info', f'Assigning Config: {attr} to {value}')
                object.__setattr__(self, attr, value)
                _log('success', f'Config Assigned')
            except AttributeError as e:
                _log('alert', f'Failed Assigning {attr}: {str(e)}')

        object.__setattr__(self, '_loaded', True)

    def _attributes(self):
        content = {name: value for name, value in object.__getattribute__(self, '__dict__').items() if
                   not name.startswith('_') and not name == 'update_config'}
        return content

    def __getattr__(self, attr):
        self._load()
        return None

    def __getattribute__(self, item):
        object.__getattribute__(self, '_load')()
        return object.__getattribute__(self, item)


def run_cmd(command, debug: bool = False, supress: bool = True, expected_status: int = 0):
    """
    Execute batch without struggling;

    Args:
        command: The batch command you want to execute
        debug: The log must show additional info (True) or should it run on a stealth mode (False)?
        supress: The stdout must be suppressed (True), indicating no logging at command the prompt result will be placed on the console.
        expected_status: An int that may vary on different OS`s;

    Returns:
        bool: Containing the result of the validation if the command returns the expected_status;
    """

    _log = Logger(app_name="Elemental-Tools", owner='cmd').log

    if supress:
        # Redirect stdout and stderr to /dev/null
        command = f"{command} > /dev/null 2>&1"

    if debug:
        _log('info', f'Running command: {command}')
    _exec = os.system(command)

    if os.WEXITSTATUS(_exec) == expected_status:
        if debug:
            _log('success', os.WEXITSTATUS(_exec))
    else:
        if debug:
            _log('error', os.WEXITSTATUS(_exec))

    return os.WEXITSTATUS(_exec) == expected_status


class LoadEnvironmentFile:
    if os.path.isfile(os.path.join(os.getcwd(), '.env')):
        load_dotenv(os.path.join(os.getcwd(), '.env'))

    def __init__(self, env_path: str):
        load_dotenv(env_path)

    @staticmethod
    def validate():
        return True


def float_to_bytes(value):
    return struct.pack(float_precision, value)


def bytes_to_float(value):
    return struct.unpack(float_precision, value)[0]


def ms_to_datetime(ms):
    seconds = ms / 1000.0
    dt = datetime.fromtimestamp(seconds)
    return dt


def current_timestamp() -> str:
    return datetime.now().isoformat()


def generate_reference(object_id: Union[str, None] = None) -> str:
    res = str(uuid4())[:ref_length]

    if object_id is not None:

        if len(object_id) == ref_length and isinstance(object_id, str):
            res = object_id

        elif len(object_id) > ref_length:
            raise ValueError(
                f"Failed to Convert Reference due to length restrictions. {str(len(object_id) - ref_length)} chars exceeded.")

    return res


class PerformanceMeter:
    cooldown: float = 0.2
    ram: float = 0.0
    cpu: float = 0.0

    def _tqdm(self):
        with tqdm(total=100, desc='cpu%', position=1) as cpubar, tqdm(total=100, desc='ram%', position=0) as rambar:
            while True:
                self.ram = psutil.virtual_memory().percent
                self.cpu = psutil.cpu_percent()
                rambar.n = self.ram
                cpubar.n = self.cpu
                rambar.refresh()
                cpubar.refresh()
                sleep(self.cooldown)

    def meter(self):

        while True:
            self.ram = psutil.virtual_memory().percent
            self.cpu = psutil.cpu_percent()
            ic(self.ram, self.cpu)
            sleep(self.cooldown)

    def __init__(self):
        multiprocessing.Process(target=self.meter).start()


class NumeralMenu:
    title: str = None
    description: str = None
    prefix: str = " - "
    suffix: str = ""
    sep: str = "\n"

    __string__: str = ""
    __menu_items__: dict = {}
    __exception__ = lambda: Exception("Invalid Option.")

    def __init__(self, _list: list, prefix: str = " - ", suffix: str = "", sep: str = "\n", title: str = None,
                 description: str = None):

        self.title = title
        self.description = description
        self.suffix = suffix
        self.prefix = prefix
        self.sep = sep

        self.__string__ = ""
        self.__logger__ = Logger(app_name=f"{self.title}", owner="MENU").log

        for idx, e in enumerate(_list):
            self.__string__ += f"\t{idx}{self.prefix}{e}{self.suffix}{self.sep}"
            self.__menu_items__[str(idx)] = e

    def __repr__(self):
        return self.__string__

    def get(self, name_or_num, default=None):

        try:
            return self.__menu_items__[name_or_num]
        except KeyError:
            for val in self.__menu_items__.values():
                if name_or_num == val:
                    return self.__menu_items__

        if default is not None:
            return default
        try:
            raise self.__exception__()
        except TypeError:
            self.__exception__()

    def show(self):

        content = ""
        if self.title is not None:
            content += f"\n[{self.title} - Menu]\n\n"
        content += str(self)
        if self.description is not None:
            content += f"\n{self.description}"

        self.__logger__("WAITING", content)
        os.environ["elemental-supress-log"] = "TRUE"
        user_input = input()
        del os.environ["elemental-supress-log"]

        return user_input


def multireplace(value: str, from_: Union[List[str], str], to: Union[List[str], str]) -> str:
    if isinstance(from_, list):
        for i in range(len(from_)):
            value = value.replace(from_[i], to[i] if isinstance(to, list) else to)
    else:
        if isinstance(to, list):
            for i in to:
                value = value.replace(from_, str(i))
        else:
            value = value.replace(from_, str(to))

    return value


