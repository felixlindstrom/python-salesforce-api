from . import base


class ResultRecord(base.Model):
    def __init__(self, record_id: str, success: bool):
        self.record_id = record_id
        self.success = success


class SuccessResultRecord(ResultRecord):
    def __init__(self, record_id):
        super().__init__(record_id, True)


class FailResultRecord(ResultRecord):
    def __init__(self, record_id, error):
        super().__init__(record_id, False)
        self.error = error
