class SalesforceBaseError(Exception):
    pass


class AuthenticationError(SalesforceBaseError):
    pass


class ServiceConnectionError(SalesforceBaseError):
    pass


class ServiceConnectionResourceNotFoundError(SalesforceBaseError):
    pass


class AuthenticationInvalidClientIdError(AuthenticationError):
    pass


class AuthenticationInvalidClientSecretError(AuthenticationError):
    pass


class AuthenticationMissingTokenError(AuthenticationError):
    pass


class NodeNotFoundError(SalesforceBaseError):
    pass


class NotTextFound(SalesforceBaseError):
    pass


class RequestFailedError(SalesforceBaseError):
    pass


class ZipNotAvailableError(SalesforceBaseError):
    pass


class NoEntriesError(SalesforceBaseError):
    pass


class MultipleDifferentHeadersError(SalesforceBaseError):
    pass


class BulkEmptyRowsError(SalesforceBaseError):
    pass


class BulkCouldNotCreateJobError(SalesforceBaseError):
    pass


class BulkJobFailedError(SalesforceBaseError):
    pass


class DeployCreateError(SalesforceBaseError):
    pass


class RetrieveCreateError(SalesforceBaseError):
    pass


class RetrieveNotDone(SalesforceBaseError):
    pass


class RestRequestCouldNotBeUnderstoodError(SalesforceBaseError):
    pass


class RestSessionHasExpiredError(SalesforceBaseError):
    pass


class RestRequestRefusedError(SalesforceBaseError):
    pass


class RestResourceNotFoundError(SalesforceBaseError):
    pass


class RestMethodNotAllowedForResourceError(SalesforceBaseError):
    pass


class RestNotWellFormattedEntityInRequestError(SalesforceBaseError):
    pass


class RestSalesforceInternalServerError(SalesforceBaseError):
    pass
