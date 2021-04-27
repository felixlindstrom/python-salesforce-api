import time
from enum import Enum
from typing import List

from . import base as bulk_base
from .. import base
from ... import config, exceptions
from ...models import bulk as models


class OPERATION(Enum):
    DELETE = 'delete'
    INSERT = 'insert'
    QUERY = 'query'
    QUERY_ALL = 'queryall'
    UPSERT = 'upsert'
    UPDATE = 'update'
    HARD_DELETE = 'hardDelete'


class JOB_STATE(Enum):
    OPEN = 'Open'
    CLOSED = 'Closed'
    ABORTED = 'Aborted'
    FAILED = 'Failed'


class BATCH_STATE(Enum):
    QUEUED = 'Queued'
    IN_PROGRESS = 'InProgress'
    COMPLETED = 'Completed'
    FAILED = 'Failed'
    NOT_PROCESSED = 'Not Processed'


BATCH_STATE_DONE = [BATCH_STATE.COMPLETED, BATCH_STATE.FAILED]


class Client(bulk_base.Client, base.AsyncService):
    def insert(self, object_name: str, entries: List[dict]) -> List[models.ResultRecord]:
        return self._execute_operation(OPERATION.INSERT, object_name, entries)

    def update(self, object_name: str, entries: List[dict]) -> List[models.ResultRecord]:
        return self._execute_operation(OPERATION.UPDATE, object_name, entries)

    def upsert(self, object_name: str, entries: List[dict], external_id_field_name: str = 'Id') -> List[models.ResultRecord]:
        return self._execute_operation(OPERATION.UPSERT, object_name, entries, external_id_field_name)

    def select(self, **kwargs):
        raise NotImplementedError

    def delete(self, object_name: str, ids: List[str]) -> List[models.ResultRecord]:
        return self._execute_operation(OPERATION.DELETE, object_name, [{'Id': id} for id in ids])

    def _execute_operation(self, operation: OPERATION, object_name: str, entries: List[dict], external_id_field_name: str = None) -> List[models.ResultRecord]:
        job = Job.create(self.connection, operation, object_name, external_id_field_name)
        job.upload(entries)
        return job.wait()


class Job(base.AsyncService):
    def __init__(self, connection, job_id):
        super().__init__(connection, 'job/' + job_id)
        self.job_id = job_id
        self.batches = []

    def _set_state(self, new_state: JOB_STATE):
        result = self._post(data={
            'state': new_state.value
        })

    def upload(self, entries: List[dict]):
        self.add_batch(entries)
        self.close()

    def add_batch(self, entries: List[dict]):
        return self.batches.append(
            Batch.create(self.connection, self.job_id, entries)
        )

    def close(self):
        return self._set_state(JOB_STATE.CLOSED)

    def get_result(self) -> List[models.ResultRecord]:
        results = [batch.get_result() for batch in self.batches]
        return [item for sublist in results for item in sublist]

    def get_errors(self):
        return [
            batch.get_state_message()
            for batch in self.batches
            if batch.is_failed()
        ]

    def wait(self) -> List[models.ResultRecord]:
        batch_states = [batch.get_state() for batch in self.batches]

        for state in batch_states:
            if state not in BATCH_STATE_DONE:
                time.sleep(config.BULK_SLEEP_SECONDS)
                return self.wait()

        if BATCH_STATE.FAILED in batch_states:
            raise exceptions.BulkJobFailedError('One or more batches failed')

        return self.get_result()

    @classmethod
    def create(cls, connection, operation: OPERATION, object_name: str, external_id_field_name: str = None):
        result = base.AsyncService(connection, 'job')._post(uri='', data={
            'operation': operation.value,
            'object': object_name,
            'contentType': 'JSON',
            'externalIdFieldName': external_id_field_name
        })
        return cls(connection, result['id'])


class Batch(base.AsyncService):
    def __init__(self, connection, job_id, batch_id):
        super().__init__(connection, f'job/{job_id}/batch/{batch_id}')

    def get_info(self):
        return self._get()

    def get_state(self) -> BATCH_STATE:
        return BATCH_STATE(self.get_info().get('state'))

    def get_state_message(self) -> BATCH_STATE:
        return self.get_info().get('stateMessage')

    def is_done(self):
        return self.get_state() in BATCH_STATE_DONE

    def is_failed(self):
        return self.get_state() == BATCH_STATE.FAILED

    def get_result(self) -> List[models.ResultRecord]:
        reader = self._get('result')
        return [
            self._convert_result(x)
            for x in reader
        ]

    def _convert_result(self, row):
        if row['success']:
            return models.SuccessResultRecord(row['id'], row)
        error = ', '.join([
            x['message']
            for x in row['errors']
            if x['message'] != None
        ])
        return models.FailResultRecord(row['id'], error, row)

    def wait(self) -> List[models.ResultRecord]:
        while not self.is_done():
            time.sleep(config.BULK_SLEEP_SECONDS)
        if self.get_state() == BATCH_STATE.FAILED:
            raise exceptions.BulkJobFailedError(self.get_state_message())
        return self.get_result()

    @classmethod
    def create(cls, connection, job_id, entries):
        result = base.AsyncService(connection, f'job/{job_id}/batch')._post(data=entries)
        return cls(connection, job_id, result['id'])
