from collections import OrderedDict
import xmltodict
from .. import exceptions, config


def get_message(path: str) -> str:
    return open(config.DATA_DIRECTORY + 'soap_messages/' + path).read()

def parse_path(path: str) -> list:
    return path.split('/')


class Result:
    def __init__(self, data):
        if isinstance(data, str):
            self._dict = dict(xmltodict.parse(data))
        elif isinstance(data, dict):
            self._dict = data

    def has(self, path: str) -> bool:
        try:
            self._get(self._dict, parse_path(path))
        except exceptions.NodeNotFoundError:
            return False
        return True

    def get(self, path, default_value=None):
        try:
            result = self._get(self._dict, parse_path(path))
        except exceptions.NodeNotFoundError:
            return default_value
        if isinstance(result, (dict, OrderedDict)):
            return Result(result)
        return result

    def get_list(self, path):
        try:
            result = self._get(self._dict, parse_path(path))
        except exceptions.NodeNotFoundError:
            return []
        if isinstance(result, list):
            return result
        if isinstance(result, (dict, OrderedDict)):
            return [result]
        return

    def get_value(self, path, default_value=False):
        result = self.get(path, default_value)
        if isinstance(result, Result):
            raise exceptions.NotTextFound
        return result

    def _get(self, data, keys):
        try:
            return self._get(data[keys[0]], keys[1:]) if keys else data
        except KeyError:
            raise exceptions.NodeNotFoundError
