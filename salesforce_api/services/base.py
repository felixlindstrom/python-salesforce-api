from typing import Union

import requests

from .. import config, core, exceptions
from ..const.service import VERB
from ..utils import soap
from ..utils.misc import join_path


class _Service:
    def __init__(self, connection: core.Connection, base_uri: str = None):
        self.connection = connection
        self.base_uri = base_uri
        self._setup()

    def _setup(self):
        pass

    def request(self, verb: VERB, uri: Union[str, None] = None, **kwargs) -> requests.Response:
        return self.connection.request(verb, join_path(self.base_uri, uri), **kwargs)


class RestService(_Service):
    def __init__(self, connection: core.Connection, base_uri: str = None):
        super().__init__(connection, join_path('services/data/v{version}', base_uri))

    def _setup(self):
        self._setup_session()

    def _setup_session(self) -> None:
        self.connection.session.headers['Authorization'] = f'Bearer {self.connection.access_token}'

    def _request(self, verb: VERB, uri: Union[str, None] = None, **kwargs):
        response = self.request(verb, uri, **kwargs)
        return self._parse_response(response)

    def _response_is_json(self, response):
        return 'Content-Type' in response.headers and \
               'application/json' in response.headers['Content-Type']

    def _handle_status_codes(self, response):
        if response.status_code < 400:
            return
        exceptions_by_code = {
            400: exceptions.RestRequestCouldNotBeUnderstoodError,
            401: exceptions.RestSessionHasExpiredError,
            403: exceptions.RestRequestRefusedError,
            404: exceptions.RestResourceNotFoundError,
            405: exceptions.RestMethodNotAllowedForResourceError,
            415: exceptions.RestNotWellFormattedEntityInRequestError,
            500: exceptions.RestSalesforceInternalServerError
        }

        message = ''
        if self._response_is_json(response):
            if isinstance(response.json(), list) and 'errorCode' in response.json()[0]:
                message = response.json()[0]

        if response.status_code in exceptions_by_code:
            raise exceptions_by_code[response.status_code](message)

    def _parse_response(self, response: requests.Response):
        self._handle_status_codes(response)
        try:
            return response.json()
        except requests.JSONDecodeError:
            return response.text

    def _get(self, uri: Union[str, None] = None, **kwargs):
        return self._request(VERB.GET, uri, **kwargs)

    def _post(self, uri: Union[str, None] = None, **kwargs):
        return self._request(VERB.POST, uri, **kwargs)

    def _put(self, uri: Union[str, None] = None, **kwargs):
        return self._request(VERB.PUT, uri, **kwargs)

    def _patch(self, uri: Union[str, None] = None, **kwargs):
        return self._request(VERB.PATCH, uri, **kwargs)

    def _delete(self, uri: Union[str, None] = None, **kwargs):
        return self._request(VERB.DELETE, uri, **kwargs)


class AsyncService(_Service):
    def __init__(self, connection: core.Connection, base_uri: str = None):
        super().__init__(connection, join_path('services/async/{version}', base_uri))

    def _setup(self):
        self._setup_session()

    def _setup_session(self) -> None:
        self.connection.session.headers['X-SFDC-Session'] = self.connection.access_token

    def _request(self, verb: VERB, uri: Union[str, None] = None, **kwargs):
        response = self.request(verb, uri, **kwargs)
        return self._parse_response(response)

    def _parse_response(self, response: requests.Response):
        try:
            return response.json()
        except requests.JSONDecodeError:
            return response.text

    def _get(self, uri: Union[str, None] = None, **kwargs):
        return self._request(VERB.GET, uri, **kwargs)

    def _post(self, uri: Union[str, None] = None, **kwargs):
        return self._request(VERB.POST, uri, **kwargs)


class SoapService(_Service):
    def __init__(self, connection: core.Connection):
        super().__init__(connection, 'services/Soap/m/{version}')

    def _extend_attributes(self, attributes: dict) -> dict:
        return {**attributes, **{
            'client_name': config.CLIENT_NAME,
            'session_id': self.connection.access_token
        }}

    def _prepare_message(self, message_path: str, attributes: dict) -> str:
        return soap.get_message(message_path) \
                   .format_map(self._extend_attributes(attributes))

    def _post(self, action=None, message_path=None, message_attributes=None) -> soap.Result:
        data = self._prepare_message(message_path, message_attributes or {})
        result = self.request(VERB.POST, data=data, headers={
            'Content-type': 'text/xml',
            'SOAPAction': action
        })
        return soap.Result(result.text)
