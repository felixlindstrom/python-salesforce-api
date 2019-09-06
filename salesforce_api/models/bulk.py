from . import base


class ResultRecord(base.Model):
    def __init__(self, record_id: str, success: bool, data: dict):
        self.record_id = record_id
        self.success = success
        self.data = {
            key: value
            for key, value in data.items()
            if not key.startswith('sf__')
        }


class SuccessResultRecord(ResultRecord):
    def __init__(self, record_id, data):
        super().__init__(record_id, True, data)


class FailResultRecord(ResultRecord):
    def __init__(self, record_id, error, data):
        super().__init__(record_id, False, data)
        self.error = error
