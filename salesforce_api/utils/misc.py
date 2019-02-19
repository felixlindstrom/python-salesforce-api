import distutils.util
import requests


def parse_bool(input_value: str) -> bool:
    return distutils.util.strtobool(input_value)


def get_session(session: requests.Session = None):
    return session if isinstance(session, requests.Session) else requests.Session()
