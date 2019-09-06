import pytest
import datetime
from salesforce_api import exceptions, models
from . import helpers


_BASE_URL = '/services/data/v{version}/jobs/ingest'
_JOB_ID = '123'


class TestServiceBulk(helpers.BaseTest):
    def setup_instance(self, requests_mock):
        self.register_uri(requests_mock, 'POST', _BASE_URL, text=helpers.get_data('bulk/create.txt'))

        self.register_uri(requests_mock, 'GET', _BASE_URL + '/' + _JOB_ID, text=helpers.get_data('bulk/info.txt'))
        self.register_uri(requests_mock, 'PATCH', _BASE_URL + '/' + _JOB_ID, text=helpers.get_data('bulk/upload_complete.txt'))
        self.register_uri(requests_mock, 'PUT', _BASE_URL + '/' + _JOB_ID + '/batches', text='')

        self.register_uri(requests_mock, 'GET', _BASE_URL + '/' + _JOB_ID + '/successfulResults', text=helpers.get_data('bulk/successful_results.txt'))
        self.register_uri(requests_mock, 'GET', _BASE_URL + '/' + _JOB_ID + '/failedResults', text=helpers.get_data('bulk/failed_results.txt'))


    def create_contact(self, first_name, last_name):
        return {
            'FirstName': first_name,
            'LastName': last_name
        }


    def test_insert_successful(self, requests_mock):
        self.setup_instance(requests_mock)
        result = self.get_service('bulk').insert('Contact', [
            self.create_contact('FirstName', 'LastName'),
            self.create_contact('FirstName2', 'LastName2'),
            self.create_contact('FirstName3', ''),
        ])
        assert 2 == len([x for x in result if isinstance(x, models.bulk.SuccessResultRecord)])
        assert 1 == len([x for x in result if isinstance(x, models.bulk.FailResultRecord)])


    def test_insert_different_types_successful(self, requests_mock):
        self.setup_instance(requests_mock)
        result = self.get_service('bulk').insert('Contact', [
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


    def test_insert_multiple_structures_failure(self, requests_mock):
        self.setup_instance(requests_mock)
        with pytest.raises(exceptions.MultipleDifferentHeadersError):
            self.get_service('bulk').insert('Contact', [{
                'a': '123'
            }, {
                'b': '456'
            }])


    def test_insert_empty_rows_failure(self, requests_mock):
        self.setup_instance(requests_mock)
        with pytest.raises(exceptions.BulkEmptyRowsError):
            self.get_service('bulk').insert('Contact', [
                self.create_contact('FirstName', 'LastName'),
                self.create_contact('', '')
            ])

    def test_delete_successful(self, requests_mock):
        self.setup_instance(requests_mock)
        result = self.get_service('bulk').delete('Contact', ['123', '456'])
        assert 2 == len([x for x in result if isinstance(x, models.bulk.SuccessResultRecord)])