"""Custom exception classes for the Banking API.

This module defines domain-specific exceptions that are caught
by exception handlers and converted to appropriate HTTP responses.
"""


class BankingAPIError(Exception):
    """Base exception for Banking API errors.

    Attributes
    ----------
    message : str
        Human-readable error message.
    """

    def __init__(self, message: str) -> None:
        """Initialize the exception.

        Parameters
        ----------
        message : str
            Error message.
        """
        self.message = message
        super().__init__(self.message)


class TransactionNotFoundError(BankingAPIError):
    """Raised when a transaction is not found.

    Attributes
    ----------
    transaction_id : str
        The ID of the transaction that was not found.
    """

    def __init__(self, transaction_id: str) -> None:
        """Initialize the exception.

        Parameters
        ----------
        transaction_id : str
            The transaction ID that was not found.
        """
        self.transaction_id = transaction_id
        super().__init__(f"Transaction '{transaction_id}' not found")


class CustomerNotFoundError(BankingAPIError):
    """Raised when a customer is not found.

    Attributes
    ----------
    customer_id : str
        The ID of the customer that was not found.
    """

    def __init__(self, customer_id: str) -> None:
        """Initialize the exception.

        Parameters
        ----------
        customer_id : str
            The customer ID that was not found.
        """
        self.customer_id = customer_id
        super().__init__(f"Customer '{customer_id}' not found")


class InvalidSearchCriteriaError(BankingAPIError):
    """Raised when search criteria are invalid.

    Attributes
    ----------
    details : str
        Details about what makes the criteria invalid.
    """

    def __init__(self, details: str) -> None:
        """Initialize the exception.

        Parameters
        ----------
        details : str
            Description of the validation error.
        """
        self.details = details
        super().__init__(f"Invalid search criteria: {details}")


class DeleteNotAllowedError(BankingAPIError):
    """Raised when deletion is attempted outside test mode.

    This exception is raised when a DELETE operation is attempted
    while the application is running in production mode.
    """

    def __init__(self) -> None:
        """Initialize the exception."""
        super().__init__(
            "DELETE operations are only allowed in test mode. "
            "Set TEST_MODE=1 to enable."
        )


class DataNotLoadedError(BankingAPIError):
    """Raised when data operations are attempted before data is loaded.

    This exception indicates that the application tried to access
    transaction data before it was successfully loaded at startup.
    """

    def __init__(self) -> None:
        """Initialize the exception."""
        super().__init__(
            "Transaction data is not loaded. "
            "Please check startup logs for errors."
        )
