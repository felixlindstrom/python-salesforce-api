import requests
from url_normalize import url_normalize
from . import const
from .const.service import VERB
from .utils import misc as misc_utils


class Connection:
    def __init__(self, version: str = const.API_VERSION, access_token: str = None, instance_url: str = None, session: requests.Session = None):
        self.version = version
        self.access_token = access_token
        self.instance_url = instance_url
        self.session = misc_utils.get_session(session)

    def request(self, verb: VERB, **kwargs) -> requests.Response:
        kwargs['url'] = url_normalize(kwargs['url'])
        return self.session.request(verb.value, **kwargs)
