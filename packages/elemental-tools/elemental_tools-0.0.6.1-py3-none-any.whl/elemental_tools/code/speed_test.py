import os
import time
from datetime import datetime, timedelta

from icecream import ic

from elemental_tools import environ


class StorageVariable:
    stored_value: float = 0

    def __get__(self, instance, owner):
        return self.stored_value

    def set(self, value):
        self.stored_value = value

    def __repr__(self):
        return str(self.stored_value)

    def __float__(self):
        return float(self.stored_value)

    def __init__(self):
        self.stored_value = float(0)

    def __str__(self):
        return str(self.stored_value)


    def as_float(self):
        return float(self.stored_value)


def speed_test(store_variable=None):
    def speed_test_func(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            if store_variable is not None:
                value = end_time - start_time
                if "e-" in str(value):
                    value = float(0)

                store_variable.set(value)
            else:
                print(f"Function '{func.__name__}' took {end_time - start_time} seconds to execute.")
            return result
        return wrapper

    return speed_test_func


class Timer:
    __start__: float

    def __init__(self):
        self.__start__ = time.time()

    def per_sec(self):
        end = time.time()
        return int((1 / (end - self.__start__)) * float(os.environ.get(environ.cpu_count, 1)))

    def per_min(self):
        end = time.time()
        return int((60 / (end - self.__start__)) * float(os.environ.get(environ.cpu_count, 1)))

    def per_hour(self):
        end = time.time()
        return int((3600 / (end - self.__start__)) * float(os.environ.get(environ.cpu_count, 1)))


