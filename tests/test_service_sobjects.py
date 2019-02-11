import pytest
from salesforce_api import exceptions
from . import helpers


_TEST_OBJECT = 'Contact'


class TestServiceSObjects(helpers.BaseTest):
    def test_describe(self, requests_mock):
        self.register_uri(requests_mock, 'GET', '/services/data/v{version}/sobjects', text='{}')
        result = self.get_service('sobjects').describe()
        assert {} == result

    def test_query(self, requests_mock):
        self.register_uri(requests_mock, 'GET', '/services/data/v{version}/query', json={'done': True, 'records': []})
        result = self.get_service('sobjects').query('test')
        assert [] == result


class TestServiceSObject(helpers.BaseTest):
    def _get_service(self):
        return self.get_service('sobjects').__getattr__(_TEST_OBJECT)

    def _get_url(self, additional=None):
        return '/services/data/v{version}/sobjects/' + _TEST_OBJECT + ('/' + additional if additional else '')

    def test_metadata(self, requests_mock):
        self.register_uri(requests_mock, 'GET', self._get_url(), text='{}')
        result = self._get_service().metadata()
        assert {} == result

    def test_describe(self, requests_mock):
        self.register_uri(requests_mock, 'GET', self._get_url('describe'), text='{}')
        result = self._get_service().describe()
        assert {} == result

    def test_get_successful(self, requests_mock):
        self.register_uri(requests_mock, 'GET', self._get_url('123'), text='{}')
        result = self._get_service().get('123')
        assert {} == result

    def test_get_failure(self, requests_mock):
        self.register_uri(requests_mock, 'GET', self._get_url('123'), text='{}', status_code=404)
        with pytest.raises(exceptions.RestResourceNotFoundError):
            self._get_service().get('123')

    def test_insert_successful(self, requests_mock):
        pass

    def test_insert_failure(self, requests_mock):
        pass

    def test_upsert_successful(self, requests_mock):
        pass

    def test_upsert_failure(self, requests_mock):
        pass

    def test_update_successful(self, requests_mock):
        pass

    def test_update_failure(self, requests_mock):
        pass

    def test_delete_successful(self, requests_mock):
        pass

    def test_delete_failure(self, requests_mock):
        pass

    def test_deleted(self, requests_mock):
        pass

    def test_updated(self, requests_mock):
        pass
