from typing import List
from .. import const
from . import base


#pylint: disable=invalid-name
class Options(base.Model):
    def __init__(self, **kwargs):
        self.allowMissingFiles = False
        self.autoUpdatePackage = False
        self.checkOnly = False
        self.ignoreWarnings = False
        self.performRetrieve = False
        self.purgeOnDelete = False
        self.rollbackOnError = True
        self.runTests = []
        self.singlePackage = True
        self.testLevel = 'RunLocalTests'

        self.set_values(**kwargs)

    def set_values(self, **kwargs):
        acceptable = vars(self)
        specials = ['runTests', 'testLevel']

        for key in kwargs:
            if key not in acceptable:
                raise Exception('Invalid option')
            elif key == 'testLevel' and kwargs[key] not in const.TEST_LEVELS:
                raise Exception('Invalid test-level')
            elif key == 'runTests' and not isinstance(kwargs[key], list):
                raise Exception('Tests must be specified as a list')
            elif key not in specials and not isinstance(kwargs[key], bool):
                raise Exception('Invalid option value for ' + key)

            self.__setattr__(key, kwargs[key])

    def as_xml(self):
        return '\n'.join([
            self._get_data_for_key(key, value)
            for key, value in vars(self).items()
        ])

    def _get_data_for_key(self, key, value):
        if key == 'runTests':
            return ''.join([
                f'<met:runTests>{test}</met:runTests>'
                for test in value
            ])
        return f'<met:{key}>{value}</met:{key}>'


class Status(base.Model):
    def __init__(self, status, details, components: 'DeployDetails', tests: 'DeployDetails'):
        self.status = status
        self.details = details
        self.components = components
        self.tests = tests


class _Failure(base.Model):
    pass


class DeployDetails(base.Model):
    def __init__(self, total_count: int, failed_count: int, completed_count: int, failures: List[_Failure] = None):
        self.total_count = total_count
        self.failed_count = failed_count
        self.completed_count = completed_count
        self.failures = failures or []

    def append_failure(self, failure: _Failure):
        self.failures.append(failure)


class ComponentFailure(_Failure):
    def __init__(self, component_type, file, status, message):
        self.component_type = component_type
        self.file = file
        self.status = status
        self.message = message


class UnitTestFailure(_Failure):
    def __init__(self, class_name, method, message, stack_trace):
        self.class_name = class_name
        self.method = method
        self.message = message
        self.stack_trace = stack_trace
