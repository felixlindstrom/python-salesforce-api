import time
from base64 import b64decode
from io import BytesIO
from typing import List
from .. import exceptions, const, config
from ..utils import soap
from ..models import retrieve as retrieve_models
from ..models import shared as shared_models
from . import base


class Retrieve(base.SoapService):
    def retrieve(self, types: List[shared_models.Type], options: retrieve_models.Options = retrieve_models.Options()) -> 'Retrievement':
        result = self._post(action='retrieve', message_path='retrieve/retrieve.msg', message_attributes={
            'api_version': self.connection.version,
            'single_package': options.single_package,
            'unpackaged': self._prepare_unpackaged_xml(types)
        })
        if result.has('soapenv:Envelope/soapenv:Body/soapenv:Fault'):
            raise exceptions.RetrieveCreateError(result.get_value('soapenv:Envelope/soapenv:Body/soapenv:Fault/faultstring'))
        return Retrievement(self, result.get_value('soapenv:Envelope/soapenv:Body/retrieveResponse/result/id'))

    def _retrieve_status(self, async_process_id: str, include_zip_file: bool = False) -> soap.Result:
        result = self._post(action='checkRetrieveStatus', message_path='retrieve/status.msg', message_attributes={
            'async_process_id': async_process_id,
            'include_zip': include_zip_file
        })
        return result.get('soapenv:Envelope/soapenv:Body/checkRetrieveStatusResponse/result')

    def get_status(self, async_process_id: str) -> retrieve_models.Status:
        result = self._retrieve_status(async_process_id, False)
        status = retrieve_models.Status(result.get_value('status'), result.get_value('errorMessage'))
        messages = result.get('messages', [])
        messages = messages if isinstance(messages, list) else [messages]
        for message in messages:
            status.append_message(retrieve_models.StatusMessage(
                message.get('fileName'),
                message.get('problem')
            ))
        return status

    def get_zip_file(self, async_process_id: str) -> BytesIO:
        result = self._retrieve_status(async_process_id, True)
        status = result.get_value('status')
        if status not in const.STATUSES_DONE:
            raise exceptions.RetrieveNotDone()
        if status != 'Succeeded':
            raise exceptions.ZipNotAvailableError
        return BytesIO(b64decode(result.get_value('zipFile')))

    def _prepare_unpackaged_xml(self, types: List[shared_models.Type]):
        output = []
        for _type in types:
            output.append('<types>')
            for member in _type.members:
                output.append('<members>' + member + '</members>')
            output.append('<name>' + _type.name + '</name>')
            output.append('</types>')
        return '\n'.join(output)


class Retrievement:
    def __init__(self, retrieve_service: Retrieve, async_process_id: str):
        self.async_process_id = async_process_id
        self.retrieve_service = retrieve_service

    def get_status(self) -> retrieve_models.Status:
        return self.retrieve_service.get_status(self.async_process_id)

    def is_done(self):
        return self.get_status().status in const.STATUSES_DONE

    def wait(self, tick: callable = None):
        while True:
            status = self.get_status()
            if status.status in const.STATUSES_DONE:
                break
            if tick is not None and callable(tick):
                tick(status)
            time.sleep(config.RETRIEVE_SLEEP_SECONDS)

    def get_zip_file(self) -> BytesIO:
        return self.retrieve_service.get_zip_file(self.async_process_id)
