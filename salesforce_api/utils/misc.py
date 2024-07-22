import hashlib
from typing import Union

import requests

from ..const import API_VERSION


def parse_bool(input_value: str) -> bool:
    return bool(input_value)


def get_session(session: Union[requests.Session, None] = None):
    if session is None:
        return requests.Session()
    return session


def hash_list(input_list):
    if not isinstance(input_list, list) or input_list is None:
        return None
    return hashlib.md5(str(input_list).encode())\
                  .hexdigest()


def decide_version(version: Union[str, None] = None) -> str:
    if version is None:
        return API_VERSION
    return version


def join_path(*args):
    return '/'.join(x.strip('/') for x in args if x)
