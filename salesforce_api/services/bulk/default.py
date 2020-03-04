from typing import List

from . import v1, v2
from ...models import bulk as models
from ... import config


def get_default_client():
    return v1.Client if config.BULK_VERSION == 1 else v2.Client


class Client(get_default_client()):
    pass


class BulkObject:
    def __init__(self, object_name, connection):
        self.object_name = object_name
        self.bulk_service = get_default_client()(connection)

    def insert(self, entries: List[dict]) -> List[models.ResultRecord]:
        return self.bulk_service.insert(self.object_name, entries)

    def delete(self, ids: List[str]) -> List[models.ResultRecord]:
        return self.bulk_service.delete(self.object_name, ids)

    def update(self, entries: List[dict]) -> List[models.ResultRecord]:
        return self.bulk_service.update(self.object_name, entries)

    def upsert(self, entries: List[dict], external_id_field_name='Id') -> List[models.ResultRecord]:
        return self.bulk_service.upsert(self.object_name, entries, external_id_field_name)