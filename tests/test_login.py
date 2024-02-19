import pytest

from salesforce_api import core, exceptions, login
from salesforce_api.const import API_VERSION
from salesforce_api.const.service import VERB
from . import helpers


class TestOAuth:
    def create_connection(self, api_version: str = None):
        return login.oauth2(
            client_id=helpers.TEST_CLIENT_KEY,
            client_secret=helpers.TEST_CLIENT_SECRET,
            username=helpers.TEST_USER_EMAIL,
            password=helpers.TEST_PASSWORD,
            instance_url=helpers.TEST_INSTANCE_URL,
            api_version=api_version
        )

    def test_authenticate_success(self, requests_mock):
        requests_mock.register_uri('POST', '/services/oauth2/token', text=helpers.get_data('login/oauth/success.txt'), status_code=200)
        connection = self.create_connection()
        assert isinstance(connection, core.Connection)
        assert connection.access_token == helpers.TEST_ACCESS_TOKEN

    def test_authenticate_success_client_credentials(self, requests_mock):
        requests_mock.register_uri('POST', '/services/oauth2/token', text=helpers.get_data('login/oauth/success.txt'), status_code=200)
        connection = login.oauth2(
            instance_url=helpers.TEST_INSTANCE_URL,
            client_id=helpers.TEST_CLIENT_KEY,
            client_secret=helpers.TEST_CLIENT_SECRET,
        )
        assert isinstance(connection, core.Connection)
        assert connection.access_token == helpers.TEST_ACCESS_TOKEN

    def test_authenticate_client_id_failure(self, requests_mock):
        requests_mock.register_uri('POST', '/services/oauth2/token', text=helpers.get_data('login/oauth/invalid_client_id.txt'), status_code=400)
        with pytest.raises(exceptions.AuthenticationInvalidClientIdError):
            self.create_connection()

    def test_authenticate_client_secret_failure(self, requests_mock):
        requests_mock.register_uri('POST', '/services/oauth2/token', text=helpers.get_data('login/oauth/invalid_client_secret.txt'), status_code=400)
        with pytest.raises(exceptions.AuthenticationInvalidClientSecretError):
            self.create_connection()

    def test_authenticate_invalid_grant_failure(self, requests_mock):
        requests_mock.register_uri('POST', '/services/oauth2/token', text=helpers.get_data('login/oauth/invalid_grant.txt'), status_code=400)
        with pytest.raises(exceptions.AuthenticationError):
            self.create_connection()

    def test_automatic_api_version(self, requests_mock):
        requests_mock.register_uri('POST', '/services/oauth2/token', text=helpers.get_data('login/oauth/success.txt'), status_code=200)
        connection = self.create_connection()
        assert connection.version == API_VERSION

    def test_manual_api_version(self, requests_mock):
        expected_api_version = '123.4'
        requests_mock.register_uri('POST', '/services/oauth2/token', text=helpers.get_data('login/oauth/success.txt'), status_code=200)
        connection = self.create_connection(expected_api_version)
        assert connection.version == expected_api_version


class TestSoap(helpers.BaseTest):
    def create_connection(self, api_version: str = None):
        return login.soap(
            instance_url=helpers.TEST_INSTANCE_URL,
            username=helpers.TEST_USER_EMAIL,
            password=helpers.TEST_PASSWORD,
            security_token=helpers.TEST_SECURITY_TOKEN,
            api_version=api_version
        )

    def test_authenticate_success(self, requests_mock):
        self.register_uri(requests_mock, VERB.POST, '/services/Soap/c/{version}', text=helpers.get_data('login/soap/success.txt'))
        connection = self.create_connection()

        assert isinstance(connection, core.Connection)
        assert connection.access_token == helpers.TEST_ACCESS_TOKEN

    def test_authenticate_alt_password_success(self, requests_mock):
        self.register_uri(requests_mock, VERB.POST, '/services/Soap/c/{version}', text=helpers.get_data('login/soap/success.txt'))
        connection = login.soap(
            instance_url=helpers.TEST_INSTANCE_URL,
            username=helpers.TEST_USER_EMAIL,
            password_and_security_token=helpers.TEST_PASSWORD
        )
        assert isinstance(connection, core.Connection)
        assert connection.access_token == helpers.TEST_ACCESS_TOKEN

    def test_authenticate_missing_token_failure(self, requests_mock):
        self.register_uri(requests_mock, VERB.POST, '/services/Soap/c/{version}', text=helpers.get_data('login/soap/missing_token.txt'))
        with pytest.raises(exceptions.AuthenticationMissingTokenError):
            self.create_connection()

    def test_automatic_api_version(self, requests_mock):
        self.register_uri(requests_mock, VERB.POST, '/services/Soap/c/{version}', text=helpers.get_data('login/soap/success.txt'))
        assert self.create_connection().version == API_VERSION

    def test_manual_api_version(self, requests_mock):
        expected_api_version = '123.4'
        self.register_uri(requests_mock, VERB.POST, f'/services/Soap/c/{expected_api_version}', text=helpers.get_data('login/soap/success.txt', {'version': expected_api_version}))
        assert self.create_connection(expected_api_version).version == expected_api_version
