import json
import requests
from .. import exceptions, config, core
from ..const.service import VERB
from ..utils import soap


class _Service:
    def __init__(self, connection: core.Connection, base_uri: str = None):
        self.connection = connection
        self.base_uri = base_uri
        self._setup()

    def _setup(self):
        pass

    def _format_url(self, uri: str = None) -> str:
        parts = [self.connection.instance_url, self.base_uri]
        if uri is not None:
            parts.append(uri)
        return str('/'.join([
            x.strip('/')
            for x in parts
            if x is not None and x != ''
        ])).format(
            version=self.connection.version
        )

    def request(self, verb: VERB, **kwargs) -> requests.Response:
        if 'uri' in kwargs:
            kwargs['url'] = self._format_url(kwargs['uri'] or '')
            del kwargs['uri']
        return self.connection.request(verb, **kwargs)


class RestService(_Service):
    def __init__(self, connection: core.Connection, base_uri: str = None):
        super().__init__(connection, 'services/data/v{version}/' + (base_uri or ''))

    def _setup(self):
        self._setup_session()

    def _setup_session(self) -> None:
        self.connection.session.headers['Authorization'] = 'Bearer ' + self.connection.access_token

    def _request(self, verb: VERB, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = {
                'Accept': 'application/json',
                'Content-type': 'application/json'
            }
        return self._parse_response(self.request(verb, **kwargs))

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
        except:
            return response.text

    def _get_url(self, url: str, params: dict = None):
        return self._request(VERB.GET, url=url, params=params)

    def _get(self, uri: str = None, params: dict = None):
        return self._request(VERB.GET, uri=uri, params=params)

    def _post(self, uri: str = None, json: dict = None):
        return self._request(VERB.POST, uri=uri, json=json)

    def _put(self, uri: str = None, json: dict = None, data: str = None, **kwargs):
        return self._request(VERB.PUT, uri=uri, json=json, data=data, **kwargs)

    def _patch(self, uri: str = None, json: dict = None, data: str = None):
        return self._request(VERB.PATCH, uri=uri, json=json, data=data)

    def _delete(self, uri: str = None):
        return self._request(VERB.DELETE, uri=uri)


class AsyncService(_Service):
    def __init__(self, connection: core.Connection, base_uri: str = None):
        super().__init__(connection, 'services/async/{version}/' + (base_uri or ''))

    def _setup(self):
        self._setup_session()

    def _setup_session(self) -> None:
        self.connection.session.headers['X-SFDC-Session'] = self.connection.access_token

    def _request(self, verb: VERB, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = {
                'Accept': 'application/json',
                'Content-type': 'application/json'
            }
        return self._parse_response(self.request(verb, **kwargs))

    def _parse_response(self, response: requests.Response):
        try:
            return response.json()
        except:
            return response.text

    def _get(self, uri: str = None, params: dict = None):
        return self._request(VERB.GET, uri=uri, params=params)

    def _post(self, uri: str = None, data = None):
        if not isinstance(data, str):
            data = json.dumps(data, default=str)
        return self._request(VERB.POST, uri=uri, data=data)


class SoapService(_Service):
    def __init__(self, connection: core.Connection):
        super().__init__(connection, 'services/Soap/m/{version}/')

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
        result = self.request(VERB.POST, url=self._format_url(''), data=data, headers={
            'Content-type': 'text/xml',
            'SOAPAction': action
        })
        return soap.Result(result.text)
