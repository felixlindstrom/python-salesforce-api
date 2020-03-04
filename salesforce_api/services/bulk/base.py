import abc
from typing import List

from ...models import bulk as models


class Client(abc.ABC):
    @abc.abstractmethod
    def insert(self, object_name: str, entries: List[dict]) -> List[models.ResultRecord]:
        pass

    def update(self, object_name: str, entries: List[dict]) -> List[models.ResultRecord]:
        pass

    def upsert(self, object_name: str, entries: List[dict], external_id_field_name: str = 'Id') -> List[models.ResultRecord]:
        pass

    def select(self, **kwargs):
        pass

    def delete(self, object_name: str, ids: List[str]) -> List[models.ResultRecord]:
        pass
