from typing import Any, Dict, Iterator, List

from . import base, bulk
from .. import core


class SObjects(base.RestService):
    def __init__(self, connection: core.Connection):
        super().__init__(connection, 'sobjects')

    def describe(self):
        return self._get()

    def _query(self, query_string: str, include_deleted: bool = False):
        return self._get('../queryAll' if include_deleted else '../query', params={'q': query_string})

    def _query_more(self, next_url: str):
        return self._get(url=f'{self.connection.instance_url}{next_url}')

    def query_iter(self, query_string: str, include_deleted: bool = False) -> Iterator[Dict[str, Any]]:
        result = self._query(query_string, include_deleted)
        yield from result['records']
        while not result['done']:
            result = self._query_more(result['nextRecordsUrl'])
            yield from result['records']

    def query(self, query_string: str, include_deleted: bool = False) -> List[Dict[str, Any]]:
        return list(self.query_iter(query_string, include_deleted))

    def __getattr__(self, name: str):
        return SObject(self.connection, name)


class SObject(base.RestService):
    def __init__(self, connection: core.Connection, object_name: str):
        super().__init__(connection, f'sobjects/{object_name}')
        self.bulk = bulk.BulkObject(object_name, connection)

    def metadata(self):
        return self._get()

    def describe(self):
        return self._get('describe')

    def get(self, record_id: str):
        return self._get(record_id)

    def insert(self, data: dict):
        return self._post(json=data)

    def upsert(self, external_id_field: str, external_id_value: str, data: dict):
        self._patch(f'{external_id_field}/{external_id_value}', json=data)
        return True

    def update(self, record_id: str, data: dict):
        self._patch(record_id, json=data)
        return True

    def delete(self, record_id: str):
        self._delete(record_id)
        return True

    def updated(self, start: str, end: str):
        raise NotImplementedError

    def deleted(self, start: str, end: str):
        raise NotImplementedError
