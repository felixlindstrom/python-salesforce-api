import requests
from .core import Connection
from . import login
from .services import sobjects, basic, tooling, deploy, retrieve, bulk


class Client:
    def __init__(self, connection: Connection = None,
                 instance_url: str = None, login_domain: str = None, username: str = None, password: str = None,
                 security_token: str = None, client_id: str = None, client_secret: str = None,
                 access_token: str = None, session: requests.Session = None, is_sandbox=False):

        if login_domain is None:
            login_domain = 'test.salesforce.com' if is_sandbox else 'login.salesforce.com'
            instance_url = 'https://' + login_domain

        session = session or requests.Session()

        if connection is not None:
            self.connection = connection
        elif all([instance_url, username, password, security_token]):
            self.connection = login.Soap(
                instance_url=instance_url,
                username=username,
                password=password,
                security_token=security_token,
                session=session
            ).authenticate()
        elif all([instance_url, client_id, client_secret, username, password]):
            self.connection = login.OAuth(
                instance_url=instance_url,
                client_id=client_id,
                client_secret=client_secret,
                username=username,
                password=password,
                session=session
            ).authenticate()
        elif all([instance_url, access_token]):
            self.connection = login.AccessToken(
                instance_url=instance_url,
                access_token=access_token,
                session=session
            ).authenticate()

        self._setup_services()

    def _setup_services(self):
        self.basic = basic.Basic(self.connection)
        self.sobjects = sobjects.SObjects(self.connection)
        self.bulk = bulk.Bulk(self.connection)
        self.tooling = tooling.Tooling(self.connection)
        self.deploy = deploy.Deploy(self.connection)
        self.retrieve = retrieve.Retrieve(self.connection)


def create_client(login_method: login.LoginMethod) -> Client:
    return Client(
        login_method.authenticate()
    )
