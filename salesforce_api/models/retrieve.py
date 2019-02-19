from typing import List
from . import base


class Options(base.Model):
    def __init__(self):
        self.single_package = True
        self.unpackaged = []


class StatusMessage(base.Model):
    def __init__(self, file: str, message: str):
        self.file = file
        self.message = message


class Status(base.Model):
    def __init__(self, status: str, error_message: str, messages: List[StatusMessage] = None):
        self.status = status
        self.error_message = error_message
        self.messages = messages or []

    def append_message(self, message: StatusMessage):
        self.messages.append(message)
