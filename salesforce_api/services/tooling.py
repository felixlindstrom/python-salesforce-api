from pathlib import Path

from . import base
from .. import core
from ..models.tooling import ApexExecutionResult


# https://developer.salesforce.com/docs/atlas.en-us.api_tooling.meta/api_tooling/intro_rest_resources.htm
class Tooling(base.RestService):
    def __init__(self, connection: core.Connection):
        super().__init__(connection, 'tooling')

    def completions(self, sf_type: str):
        return self._get('completions', params={'type': sf_type})

    def execute_apex(self, body: str):
        return ApexExecutionResult.create(
            self._get('executeAnonymous', params={'anonymousBody': body})
        )

    def execute_apex_from_file(self, file_path: str):
        return self.execute_apex(Path(file_path).read_text())

    def query(self, query: str):
        return self._get('query', params={'q': query})

    def run_tests_asynchronous(self):
        raise NotImplementedError

    def run_tests_synchronous(self):
        raise NotImplementedError

    def search(self, query: str):
        raise NotImplementedError

    def sobjects(self):
        return self._get('sobjects')

    def __getattr__(self, name: str):
        return ToolingObject(name, self.connection)


class ToolingObject(base.RestService):
    def __init__(self, object_name: str, connection: core.Connection):
        super().__init__(connection, f'tooling/sobjects/{object_name}')

    def describe(self):
        return self._get('describe')

    def create(self, json: dict = None):
        return self._post(json=json)

    def get(self, record_id: str):
        return self._get(record_id)

    def update(self, record_id: str, json: dict = None):
        return self._patch(record_id, json=json)

    def delete(self, record_id: str):
        return self._delete(record_id)
