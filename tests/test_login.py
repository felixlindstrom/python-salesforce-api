import pytest
from . import helpers
from salesforce_api import login, core, exceptions, const


class TestOAuth:
    def create_login(self):
        return login.OAuth(
            client_id=helpers.TEST_CLIENT_KEY,
            client_secret=helpers.TEST_CLIENT_SECRET,
            username=helpers.TEST_USER_EMAIL,
            password=helpers.TEST_PASSWORD,
            instance_url=helpers.TEST_INSTANCE_URL
        )

    def test_authenticate_success(self, requests_mock):
        requests_mock.register_uri('POST', '/services/oauth2/token', text=helpers.get_data('login/oauth/success.txt'), status_code=200)
        connection = self.create_login().authenticate()
        assert isinstance(connection, core.Connection)
        assert connection.access_token == helpers.TEST_ACCESS_TOKEN

    def test_authenticate_client_id_failure(self, requests_mock):
        requests_mock.register_uri('POST', '/services/oauth2/token', text=helpers.get_data('login/oauth/invalid_client_id.txt'), status_code=400)
        with pytest.raises(exceptions.AuthenticationInvalidClientIdError):
            self.create_login().authenticate()

    def test_authenticate_client_secret_failure(self, requests_mock):
        requests_mock.register_uri('POST', '/services/oauth2/token', text=helpers.get_data('login/oauth/invalid_client_secret.txt'), status_code=400)
        with pytest.raises(exceptions.AuthenticationInvalidClientSecretError):
            self.create_login().authenticate()

    def test_authenticate_invalid_grant_failure(self, requests_mock):
        requests_mock.register_uri('POST', '/services/oauth2/token', text=helpers.get_data('login/oauth/invalid_grant.txt'), status_code=400)
        with pytest.raises(exceptions.AuthenticationError):
            self.create_login().authenticate()


class TestSoap:
    def create_login(self):
        return login.Soap(
            instance_url=helpers.TEST_INSTANCE_URL,
            username=helpers.TEST_USER_EMAIL,
            password=helpers.TEST_PASSWORD,
            security_token=helpers.TEST_SECURITY_TOKEN
        )

    def test_authenticate_success(self, requests_mock):
        requests_mock.register_uri('POST', '/services/Soap/c/' + const.API_VERSION, text=helpers.get_data('login/soap/success.txt'))
        connection = self.create_login().authenticate()

        assert isinstance(connection, core.Connection)
        assert connection.access_token == helpers.TEST_ACCESS_TOKEN

    def test_authenticate_missing_token_failure(self, requests_mock):
        requests_mock.register_uri('POST', '/services/Soap/c/' + const.API_VERSION, text=helpers.get_data('login/soap/missing_token.txt'))
        with pytest.raises(exceptions.AuthenticationMissingTokenError):
            self.create_login().authenticate()

    def test_invalid_login_failure(self, requests_mock):
        requests_mock.register_uri('POST', '/services/Soap/c/' + const.API_VERSION, text=helpers.get_data('login/soap/invalid_login.txt'))
        with pytest.raises(exceptions.AuthenticationError):
            self.create_login().authenticate()
