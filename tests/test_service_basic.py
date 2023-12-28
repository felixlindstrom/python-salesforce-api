from salesforce_api.const.service import VERB
from . import helpers


class TestServiceBasic(helpers.BaseTest):
    def test_versions(self, requests_mock):
        self.register_uri(requests_mock, VERB.GET, '/services/data/', json={})
        result = self.get_service('basic').versions()
        assert result == {}

    def test_resources(self, requests_mock):
        self.register_uri(requests_mock, VERB.GET, '/services/data/v{version}', json={})
        result = self.get_service('basic').resources()
        assert result == {}

    def test_limits(self, requests_mock):
        self.register_uri(requests_mock, VERB.GET, '/services/data/v{version}/limits', json={})
        result = self.get_service('basic').limits()
        assert result == {}
