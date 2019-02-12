import re
import requests
from . import core, exceptions, const
from .utils import soap


class LoginMethod:
    def authenticate(self) -> core.Connection:
        raise NotImplementedError


class AccessToken(LoginMethod):
    def __init__(self, instance_url: str, access_token: str, session: requests.Session):
        self.instance_url = instance_url
        self.access_token = access_token
        self.session = session

    def authenticate(self) -> core.Connection:
        return core.Connection(
            version=const.API_VERSION,
            access_token=self.access_token,
            instance_url=self.instance_url,
            session=self.session
        )


class OAuth(LoginMethod):
    def __init__(self, instance_url: str, client_id: str, client_secret: str, username: str, password: str, session: requests.Session = requests.Session()):
        self.instance_url = instance_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.session = session

    def authenticate(self) -> core.Connection:
        response = self.session.post(self.instance_url + '/services/oauth2/token', data=dict(
            grant_type='password',
            client_id=self.client_id,
            client_secret=self.client_secret,
            username=self.username,
            password=self.password
        ))
        response_json = response.json()
        if response.status_code == 200:
            return self._handle_success(response_json)
        return self._handle_error(response_json)

    def _handle_success(self, response):
        return core.Connection(
            version=const.API_VERSION,
            access_token=response['access_token'],
            instance_url=response['instance_url']
        )

    def _handle_error(self, response):
        if response.get('error') == 'invalid_client_id':
            raise exceptions.AuthenticationInvalidClientIdError
        elif response.get('error') == 'invalid_client':
            raise exceptions.AuthenticationInvalidClientSecretError
        else:
            raise exceptions.AuthenticationError


class Soap(LoginMethod):
    def __init__(self, instance_url: str, username: str, password: str, security_token: str, session: requests.Session = requests.Session()):
        self.instance_url = instance_url + '/services/Soap/c/' + const.API_VERSION
        self.username = username
        self.password = password
        self.security_token = security_token
        self.session = session

    def _get_body(self) -> str:
        return soap.get_message('login/login.msg').format(
            username=self.username,
            password=self.password + self.security_token
        )

    def authenticate(self) -> core.Connection:
        response = self.session.post(self.instance_url, headers={
            'Content-Type': 'text/xml',
            'SOAPAction': 'login'
        }, data=self._get_body())
        result = soap.Result(response.text)

        if result.has('soapenv:Envelope/soapenv:Body/loginResponse/result/sessionId'):
            return self._handle_success(result)

        return self._handle_error(result)

    def _handle_success(self, result: soap.Result):
        session_id = result.get_value('soapenv:Envelope/soapenv:Body/loginResponse/result/sessionId')
        server_url = result.get_value('soapenv:Envelope/soapenv:Body/loginResponse/result/serverUrl')
        instance = re.match(r'(https://(.*).salesforce\.com/)', server_url).group(1)
        return core.Connection(
            version=const.API_VERSION,
            access_token=session_id,
            instance_url=instance
        )

    def _handle_error(self, result: soap.Result):
        if not result.has('soapenv:Envelope/soapenv:Body/soapenv:Fault/faultcode'):
            raise exceptions.AuthenticationError
        code = result.get_value('soapenv:Envelope/soapenv:Body/soapenv:Fault/faultcode')
        if code.find('LOGIN_MUST_USE_SECURITY_TOKEN'):
            raise exceptions.AuthenticationMissingTokenError
        raise exceptions.AuthenticationError
