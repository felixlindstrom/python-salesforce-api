from typing import Union

import requests
from url_normalize import url_normalize

from .const import API_VERSION
from .const.service import VERB
from .utils.misc import get_session, join_path


class Connection:
    def __init__(self, version: str = API_VERSION, access_token: str = None, instance_url: str = None, session: requests.Session = None):
        self.version = version
        self.access_token = access_token
        self.instance_url = instance_url
        self.session = get_session(session)

    def request(self, verb: VERB, uri: Union[str, None], **kwargs) -> requests.Response:
        if 'url' not in kwargs:
            kwargs['url'] = join_path(self.instance_url, uri).format(version=self.version)
        kwargs['url'] = url_normalize(kwargs['url'])
        return self.session.request(verb.value, **kwargs)
