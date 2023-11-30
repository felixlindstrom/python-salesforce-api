import datetime

import pytest

from salesforce_api import exceptions, models
from salesforce_api.const.service import VERB
from salesforce_api.services.bulk.v1 import BATCH_STATE, JOB_STATE
from . import helpers

_BASE_URL = '/services/async/{version}/job'
_JOB_ID = '123'
_BATCH_ID = '456'


class TestServiceBulk(helpers.BaseTest):
    def setup_instance(self, requests_mock):
        self.register_uri(requests_mock, VERB.POST, _BASE_URL, json={
            'id': _JOB_ID
        })

        self.register_uri(requests_mock, VERB.POST, f'{_BASE_URL}/{_JOB_ID}', json={
            'id': _JOB_ID
        })

        self.register_uri(requests_mock, VERB.GET, f'{_BASE_URL}/{_JOB_ID}', json={
            'id': _JOB_ID,
            'state': JOB_STATE.CLOSED.value
        })

        self.register_uri(requests_mock, VERB.POST, f'{_BASE_URL}/{_JOB_ID}/batch', json={
            'id': _BATCH_ID
        })

        self.register_uri(requests_mock, VERB.GET, f'{_BASE_URL}/{_JOB_ID}/batch/{_BATCH_ID}', json={
            'id': _BATCH_ID,
            'state': BATCH_STATE.COMPLETED.value
        })

        self.register_uri(requests_mock, VERB.GET, f'{_BASE_URL}/{_JOB_ID}/batch/{_BATCH_ID}/result', text=helpers.get_data('bulk/v1/success_result.txt'))

    def create_contact(self, first_name, last_name):
        return {
            'FirstName': first_name,
            'LastName': last_name
        }

    def test_insert_successful(self, requests_mock):
        self.setup_instance(requests_mock)
        result = self.get_service('bulk_v1').insert('Contact', [
            self.create_contact('FirstName', 'LastName'),
            self.create_contact('FirstName2', 'LastName2'),
            self.create_contact('FirstName3', ''),
        ])
        assert 2 == len([x for x in result if isinstance(x, models.bulk.SuccessResultRecord)])
        assert 1 == len([x for x in result if isinstance(x, models.bulk.FailResultRecord)])

    def test_insert_different_types_successful(self, requests_mock):
        self.setup_instance(requests_mock)
        result = self.get_service('bulk_v1').insert('Contact', [
            {
                'a': 1,
                'b': 1.23,
                'c': datetime.datetime.now(),
                'd': False,
                'e': True,
                'f': 'string'
            }
        ])
        assert 2 == len([x for x in result if isinstance(x, models.bulk.SuccessResultRecord)])
        assert 1 == len([x for x in result if isinstance(x, models.bulk.FailResultRecord)])

    def test_delete_successful(self, requests_mock):
        self.setup_instance(requests_mock)
        result = self.get_service('bulk_v1').delete('Contact', ['123', '456'])
        assert 2 == len([x for x in result if isinstance(x, models.bulk.SuccessResultRecord)])
