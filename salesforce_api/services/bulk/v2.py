import csv
import io
import json
import time
from enum import Enum
from typing import List

from . import base as bulk_base
from .. import base
from ... import config, exceptions
from ...const.service import VERB
from ...models import bulk as models
from ...utils import bulk as bulk_utils


class OPERATION(Enum):
    INSERT = 'insert'
    UPDATE = 'update'
    UPSERT = 'upsert'
    DELETE = 'delete'
    SELECT = 'select'


class JOB_STATE(Enum):
    OPEN = 'Open'
    UPLOAD_COMPLETE = 'UploadComplete'
    ABORTED = 'Aborted'
    JOB_COMPLETE = 'JobComplete'
    FAILED = 'Failed'
    IN_PROGRESS = 'InProgress'


JOB_STATES_DONE = [JOB_STATE.JOB_COMPLETE, JOB_STATE.ABORTED, JOB_STATE.FAILED]
JOB_STATES_FAIL = [JOB_STATE.ABORTED, JOB_STATE.FAILED]


class Client(bulk_base.Client, base.RestService):
    def __init__(self, connection):
        super().__init__(connection, 'jobs/ingest')

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


class Job(base.RestService):
    def __init__(self, connection, job_id):
        super().__init__(connection, 'jobs/ingest/' + job_id)
        self.job_id = job_id

    def _set_state(self, new_state: JOB_STATE):
        return self._patch(json={'state': new_state.value})

    def _prepare_data(self, entries):
        return bulk_utils.FilePreparer(entries).get_csv_string()

    def upload(self, entries):
        try:
            self._put('batches', data=self._prepare_data(entries), headers={
                'Content-Type': 'text/csv'
            })
        except json.decoder.JSONDecodeError:
            pass
        self._set_state(JOB_STATE.UPLOAD_COMPLETE)
        return True

    def close(self):
        return self._set_state(JOB_STATE.UPLOAD_COMPLETE)

    def abort(self):
        return self._set_state(JOB_STATE.ABORTED)

    def delete(self):
        return self._delete()

    def info(self):
        return self._get()

    def get_state(self) -> JOB_STATE:
        return JOB_STATE(self.info().get('state'))

    def is_done(self) -> bool:
        return self.get_state() in JOB_STATES_DONE

    def _get_results(self, uri, callback):
        result = self.connection.request(VERB.GET, url=self._format_url(uri)).text
        reader = csv.DictReader(io.StringIO(result))
        return [callback(x) for x in reader]

    def get_successful_results(self) -> List[models.ResultRecord]:
        return self._get_results('successfulResults', lambda x: models.SuccessResultRecord(x['sf__Id'], x))

    def get_failed_results(self) -> List[models.ResultRecord]:
        return self._get_results('failedResults', lambda x: models.FailResultRecord(x['sf__Id'], x['sf__Error'], x))

    def get_unprocessed_records(self) -> List[models.ResultRecord]:
        raise NotImplementedError

    def wait(self) -> List[models.ResultRecord]:
        while not self.is_done():
            time.sleep(config.BULK_SLEEP_SECONDS)

        if self.get_state() in JOB_STATES_FAIL:
            raise exceptions.BulkJobFailedError(self.info().get('errorMessage'))

        return self.get_failed_results() + \
               self.get_successful_results()

    @classmethod
    def create(cls, connection, operation: OPERATION, object_name: str, external_id_field_name: str = None) -> 'Job':
        result = base.RestService(connection, 'jobs/ingest')._post(json={
            'columnDelimiter': 'COMMA',
            'contentType': 'CSV',
            'lineEnding': 'LF',
            'object': object_name,
            'operation': operation.value,
            'externalIdFieldName': external_id_field_name
        })
        return Job(connection, result.get('id'))
