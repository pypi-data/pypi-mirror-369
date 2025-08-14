class PortalError(RuntimeError):
    """Base exception class for Portal-related errors.

    This is the base exception class that all Portal-specific errors inherit from.
    It extends RuntimeError and provides a standard structure for Portal errors.
    """

    def __init__(self, type: str, message: str) -> None:
        """Initialize a PortalError.

        Args:
            type: The type/category of the error.
            message: A descriptive error message.
        """
        super(PortalError, self).__init__(message)
        self.type = type
        self.message = message


class PortalClientError(PortalError):
    """Exception raised for client-side Portal errors.

    This exception is raised when there are client-side issues such as
    configuration problems, invalid requests, or client connectivity issues.
    """

    def __init__(self, type: str, message: str, details: str | None = None) -> None:
        super(PortalClientError, self).__init__(type, message)
        self.details = details


class PortalApiError(PortalError):
    """Exception raised for server-side Portal API errors.

    This exception is raised when the Portal API returns an error response,
    such as authentication failures, server errors, or invalid API requests.
    """

    def __init__(
        self,
        type: str,
        message: str,
        status_code: int,
        details: str | None = None,
    ) -> None:
        self.type = type
        self.message = message
        self.status_code = status_code
        self.details = details
        super(PortalApiError, self).__init__(type, message)


class ClientError(PortalClientError):
    """Simplified client error exception for backward compatibility.

    This is a convenience exception that provides a simpler interface
    for client-side errors without requiring an explicit error type.
    """

    def __init__(self, message: str, details: str | None = None) -> None:
        super(ClientError, self).__init__("ClientError", message, details)
