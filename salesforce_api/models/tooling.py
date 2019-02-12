from . import base


class ApexExecutionResult(base.Model):
    def __init__(self, input_data):
        self.line = input_data['line']
        self.column = input_data['column']
        self.compiled = input_data['compiled']
        self.success = input_data['success']
        self.compile_problem = input_data['compileProblem']
        self.exception_stack_trace = input_data['exceptionStackTrace']
        self.exception_message = input_data['exceptionMessage']

    @staticmethod
    def create(input_data):
        if 'success' in input_data and input_data['success']:
            return SuccessfulApexExecutionResult(input_data)
        return FailedApexExecutionResult(input_data)


class SuccessfulApexExecutionResult(ApexExecutionResult):
    pass


class FailedApexExecutionResult(ApexExecutionResult):
    pass
