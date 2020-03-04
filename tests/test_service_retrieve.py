import pytest
from salesforce_api import models, exceptions
from salesforce_api.const.service import VERB
from . import helpers


class TestServiceRetrieve(helpers.BaseTest):
    def setup_instance(self, requests_mock, texts):
        self.register_uri(requests_mock, VERB.POST, '/services/Soap/m/{version}', response_list=[
            {'text': x, 'status_code': 200} if isinstance(x, str) else x
            for x in texts
        ])

    def test_create_successful(self, requests_mock):
        self.setup_instance(requests_mock, [
            helpers.get_data('retrieve/create_success.txt')
        ])
        retrievement = self.create_client().retrieve.retrieve([
            models.shared.Type('ApexClass')
        ])
        assert '123' == retrievement.async_process_id

    def test_create_failure(self, requests_mock):
        self.setup_instance(requests_mock, [
            helpers.get_data('retrieve/create_failure.txt')
        ])
        with pytest.raises(exceptions.RetrieveCreateError):
            self.create_client().retrieve.retrieve([
                models.shared.Type('ApexClass')
            ])

    def test_full_retrieve_successful(self, requests_mock):
        self.setup_instance(requests_mock, [
            helpers.get_data('retrieve/create_success.txt'),
            helpers.get_data('retrieve/status_success.txt'),
            helpers.get_data('retrieve/status_with_zip.txt')
        ])
        retrievement = self.create_client().retrieve.retrieve([
            models.shared.Type('ApexClass')
        ])
        assert retrievement.is_done()

        zip_file = retrievement.get_zip_file()
        assert b'zip-file-content' == zip_file.read()