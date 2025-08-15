import os.path
from typing import Union

import geocoder
import requests
from icecream import ic
from elemental_tools.logger import Logger
from elemental_tools.exceptions import Invalid


def agg(func, obj: Union[dict, list]):
    """
    Recursively applies a given function to all elements within a nested dictionary or list.

    Args:
        func: The function to be applied to each element.
        obj (Union[dict, list]): The object (either a dictionary or a list) to be processed.

    Returns:
        Union[dict, list]: The object with the function applied to each element.
    """

    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                obj[key] = agg(func, value)
            else:
                obj[key] = func(value)

    elif isinstance(obj, list):
        for i in range(len(obj)):
            if isinstance(obj[i], (dict, list)):
                obj[i] = agg(func, obj[i])
            else:
                obj[i] = func(obj[i])
    else:
        obj = func(obj)

    return obj


def get_package_name(origin, avoid: list = None, max_retry_times: int = 3):
    """
    Extracts the package name from a file path, avoiding specified names and retrying if necessary.

    Args:
        origin (str): The original file path.
        avoid (list, optional): List of names to avoid when extracting package name. Defaults to None.
        max_retry_times (int, optional): Maximum number of times to retry extracting package name. Defaults to 3.

    Returns:
        str: The extracted package name.
    """

    this_retry_time = 0

    ext = '.py'
    _avoid = ['__init__']

    if avoid is not None:
        _avoid += avoid

    _pck_name = os.path.basename(origin)

    while _pck_name.replace(ext, '') in _avoid:
        _pck_name = os.path.basename(os.path.dirname(origin))
        this_retry_time += 1
        if this_retry_time > max_retry_times:
            break

    return _pck_name.replace(ext, "")


__logger__ = Logger(app_name=os.getenv("APP_NAME", "elemental-tools"), owner="tools").log


def get_ip_address_location(ip_address) -> Union[dict, None]:
    try:
        response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
        if response.get("error", False):
            raise Exception("https://ipapi.co/ Failed")

        city = response.get("city")
        region = response.get("region")
        country = response.get("country_name")

    except Exception as e:
        __logger__("critical", f"https://ipapi.co/ Failed!!! EXCEPTION: {str(e)}")
        try:
            ip = geocoder.ip(ip_address)

            city = str(ip.current_result.json["city"])
            region = str(ip.current_result.json["address"])
            country = str(ip.current_result.json["country"])

            response = ip.current_result.json

        except Exception as e:
            __logger__("critical", f"LOCATION NOT SET FOR {ip_address}!!! EXCEPTION: {str(e)}")
            # raise Invalid("Location", message=str(e))
            return {}

    return {
        "ip": ip_address,
        "city": city,
        "region": region,
        "country": country,
        **response
    }


def remove_private(dic: dict):
    return {key: item for key, item in dic.items() if not key.startswith("_")}