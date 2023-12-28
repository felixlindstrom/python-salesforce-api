from . import base


class Basic(base.RestService):
    def __init__(self, connection):
        super().__init__(connection)

    def versions(self) -> dict:
        return self._get('..')

    def resources(self) -> dict:
        return self._get()

    def limits(self) -> dict:
        return self._get('limits')
