"""
DreoCloud exception classes.

This module defines custom exception classes for different types of DreoCloud API errors.
"""


class DreoException(Exception):
    """Base exception class for DreoCloud API errors."""

    def __init__(self, message):
        """
        Initialize DreoCloud exception.

        Args:
            message: Error message describing the exception.
        """
        self.message = message
        super().__init__(self.message)


class DreoBusinessException(Exception):
    """Exception for DreoCloud business logic errors."""

    def __init__(self, message):
        """
        Initialize DreoCloud business exception.

        Args:
            message: Error message describing the business logic error.
        """
        self.message = message
        super().__init__(self.message)


class DreoAccessDeniedException(Exception):
    """Exception for DreoCloud access denied errors."""

    def __init__(self, message):
        """
        Initialize DreoCloud access denied exception.

        Args:
            message: Error message describing the access denial.
        """
        self.message = message
        super().__init__(self.message)


class DreoFlowControlException(Exception):
    """Exception for DreoCloud flow control errors (rate limiting)."""

    def __init__(self, message):
        """
        Initialize DreoCloud flow control exception.

        Args:
            message: Error message describing the flow control issue.
        """
        self.message = message
        super().__init__(self.message)
