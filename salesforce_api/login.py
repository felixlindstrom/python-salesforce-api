import re
from typing import Union

import requests
from . import core, exceptions
from .utils import misc as misc_utils
from .utils import soap as soap_utils


def magic(domain: str = None, username: str = None, password: str = None, security_token: str = None,
          password_and_security_token: str = None, client_id: str = None, client_secret: str = None,
          access_token: str = None, session: requests.Session = None, is_sandbox=False, api_version: str = None) -> core.Connection:
    session = misc_utils.get_session(session)
    # Determine instance url
    if domain is None:
        domain = 'test.salesforce.com' if is_sandbox else 'login.salesforce.com'
    instance_url = f'https://{domain}'

    # Figure out how to authenticate
    if username:
        return soap(
            instance_url=instance_url,
            username=username,
            password=password,
            security_token=security_token,
            password_and_security_token=password_and_security_token,
            session=session,
            api_version=api_version
        )
    elif client_id and client_secret:
        return oauth2(
            instance_url=instance_url,
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            session=session,
            api_version=api_version
        )
    elif access_token:
        return plain_access_token(
            instance_url=instance_url,
            access_token=access_token,
            session=session,
            api_version=api_version
        )

    # Could not decide
    raise exceptions.AuthenticationError('Not enough information to select authentication-method')


def plain_access_token(instance_url: str, access_token: str, session: requests.Session, api_version: str = None) -> core.Connection:
    return core.Connection(
        version=misc_utils.decide_version(api_version),
        access_token=access_token,
        instance_url=instance_url,
        session=misc_utils.get_session(session)
    )


def oauth2(instance_url: str, client_id: str, client_secret: str, username: Union[str, None] = None, password: Union[str, None] = None,
           session: Union[requests.Session, None] = None, api_version: Union[str, None] = None) -> core.Connection:
    session = misc_utils.get_session(session)
    url = f'{instance_url}/services/oauth2/token'
    if username and password:
        response = session.post(url, data=dict(
            grant_type='password',
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
        ))
    else:
        response = session.post(
            url,
            data=dict(grant_type='client_credentials'),
            auth=(client_id, client_secret),
        )
    response_json = response.json()

    if response_json.get('error') == 'invalid_client_id':
        raise exceptions.AuthenticationInvalidClientIdError
    elif response_json.get('error') == 'invalid_client':
        raise exceptions.AuthenticationInvalidClientSecretError
    elif response.status_code != 200:
        raise exceptions.AuthenticationError(f'Status-code {response.status_code} returned while trying to authenticate')

    return plain_access_token(response_json['instance_url'], access_token=response_json['access_token'], session=session, api_version=api_version)


def soap(instance_url: str, username: str, password: str = None, security_token: str = None,
         password_and_security_token: str = None, session: requests.Session = None,
         api_version: str = None) -> core.Connection:
    if not ((password and security_token) or password_and_security_token):
        raise exceptions.AuthenticationError('password and security_token or password_and_security_token required')
    session = misc_utils.get_session(session)
    instance_url = f'{instance_url}/services/Soap/c/{misc_utils.decide_version(api_version)}'

    body = soap_utils.get_message('login/login.msg').format(
        username=username,
        password=password_and_security_token or password + security_token
    )

    response = soap_utils.Result(session.post(instance_url, headers={
        'Content-Type': 'text/xml',
        'SOAPAction': 'login'
    }, data=body).text)

    if response.has('soapenv:Envelope/soapenv:Body/loginResponse/result/sessionId'):
        session_id = response.get_value('soapenv:Envelope/soapenv:Body/loginResponse/result/sessionId')
        server_url = response.get_value('soapenv:Envelope/soapenv:Body/loginResponse/result/serverUrl')
        instance = re.match(r'(https://(.*).salesforce\.com/)', server_url).group(1)
        return plain_access_token(access_token=session_id, instance_url=instance, session=session, api_version=api_version)

    if not response.has('soapenv:Envelope/soapenv:Body/soapenv:Fault/faultcode'):
        raise exceptions.AuthenticationError
    code = response.get_value('soapenv:Envelope/soapenv:Body/soapenv:Fault/faultcode')
    if code.find('LOGIN_MUST_USE_SECURITY_TOKEN'):
        raise exceptions.AuthenticationMissingTokenError('Missing or invalid security-token provided.')
    raise exceptions.AuthenticationError
