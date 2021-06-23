import requests
from .core import Connection
from . import login
from .services import sobjects, basic, tooling, deploy, retrieve, bulk
from .utils import misc as misc_utils


class Client:
    def __init__(self,
                 connection: Connection = None,
                 domain: str = None,
                 username: str = None,
                 password: str = None,
                 security_token: str = None,
                 password_and_security_token: str = None,
                 client_id: str = None,
                 client_secret: str = None,
                 access_token: str = None,
                 session: requests.Session = None,
                 is_sandbox=False,
                 api_version: str = None):
        self.connection = connection if connection else login.magic(
            domain=domain,
            username=username,
            password=password,
            security_token=security_token,
            password_and_security_token=password_and_security_token,
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token,
            session=misc_utils.get_session(session),
            is_sandbox=is_sandbox,
            api_version=api_version
        )
        self._setup_services()

    def _setup_services(self):
        self.basic = basic.Basic(self.connection)
        self.sobjects = sobjects.SObjects(self.connection)
        self.tooling = tooling.Tooling(self.connection)
        self.deploy = deploy.Deploy(self.connection)
        self.retrieve = retrieve.Retrieve(self.connection)

        self.bulk = bulk.Client(self.connection)
        self.bulk_v1 = bulk.v1.Client(self.connection)
        self.bulk_v2 = bulk.v2.Client(self.connection)
