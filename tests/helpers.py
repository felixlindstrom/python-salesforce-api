import time
import os
import json
from string import Template
from salesforce_api import Salesforce, const
from salesforce_api.const.service import VERB

TEST_CLIENT_KEY = 'test-key'
TEST_CLIENT_SECRET = 'test-secret'
TEST_SECURITY_TOKEN = 'test-token'
TEST_ACCESS_TOKEN = 'test-access-token'
TEST_DOMAIN = 'example.cs108.my.salesforce.com'
TEST_INSTANCE_URL = 'https://' + TEST_DOMAIN
TEST_ISSUE_TIME = time.time()
TEST_ID = 'https://test.salesforce.com/id/123/456'
TEST_SIGNATURE = '123456789'
TEST_USER_ID = 'user-123'
TEST_USER_FULL_NAME = 'Test Name'
TEST_USER_EMAIL = 'test@example.com.dev'
TEST_PASSWORD = 'test-password'
TEST_ROLE_ID = '123'
TEST_PROFILE_ID = '123'
TEST_ORG_NAME = 'Test Org'
TEST_ORG_ID = '123'
TEST_SERVER_URL = TEST_INSTANCE_URL + '/services/Soap/c/44.0/123'
TEST_METADATA_URL = TEST_INSTANCE_URL + '/services/Soap/m/44.0/123'
TEST_OBJECT_NAME = 'Contact'
TEST_BULK_OPERATION = 'insert'


def get_data(path):
    return Template(open(os.path.dirname(__file__) + '/data/' + path, 'r').read()).substitute(
        access_token=TEST_ACCESS_TOKEN,
        instance_url=TEST_INSTANCE_URL,
        id=TEST_ID,
        issued_at=TEST_ISSUE_TIME,
        signature=TEST_SIGNATURE,

        user_email=TEST_USER_EMAIL,
        user_id=TEST_USER_ID,
        user_full_name=TEST_USER_FULL_NAME,
        role_id=TEST_ROLE_ID,
        profile_id=TEST_PROFILE_ID,
        org_name=TEST_ORG_NAME,
        org_id=TEST_ORG_ID,
        server_url=TEST_SERVER_URL,
        metadata_url=TEST_METADATA_URL,

        object=TEST_OBJECT_NAME,
        operation=TEST_BULK_OPERATION,

        version=const.API_VERSION
    )


class BaseTest:
    def create_client(self):
        return Salesforce(
            domain=TEST_DOMAIN,
            access_token=TEST_ACCESS_TOKEN
        )

    def get_service(self, service_name):
        return self.create_client().__getattribute__(service_name)

    def register_uri(self, requests_mock, verb: VERB, uri: str, **kwargs):
        if 'json' in kwargs:
            kwargs['text'] = json.dumps(kwargs['json'])
            del kwargs['json']
        requests_mock.register_uri(
            verb.value,
            uri.format_map({'version': const.API_VERSION}),
            **kwargs
        )