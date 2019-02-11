from . import base


class ApexExecutionResult(base.Model):
    def __init__(self, input):
        self.line = input['line']
        self.column = input['column']
        self.compiled = input['compiled']
        self.success = input['success']
        self.compile_problem = input['compileProblem']
        self.exception_stack_trace = input['exceptionStackTrace']
        self.exception_message = input['exceptionMessage']

    @staticmethod
    def create(input):
        if 'success' in input and input['success']:
            return SuccessfulApexExecutionResult(input)
        return FailedApexExecutionResult(input)


class SuccessfulApexExecutionResult(ApexExecutionResult):
    pass


class FailedApexExecutionResult(ApexExecutionResult):
    pass

