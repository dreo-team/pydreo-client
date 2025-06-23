"""
HSCloud exception classes.

This module defines custom exception classes for different types of HSCloud API errors.
"""


class HsCloudException(Exception):
    """Base exception class for HSCloud API errors."""

    def __init__(self, message):
        """
        Initialize HSCloud exception.
        
        Args:
            message: Error message describing the exception.
        """
        self.message = message
        super().__init__(self.message)


class HsCloudBusinessException(Exception):
    """Exception for HSCloud business logic errors."""

    def __init__(self, message):
        """
        Initialize HSCloud business exception.
        
        Args:
            message: Error message describing the business logic error.
        """
        self.message = message
        super().__init__(self.message)


class HsCloudAccessDeniedException(Exception):
    """Exception for HSCloud access denied errors."""

    def __init__(self, message):
        """
        Initialize HSCloud access denied exception.
        
        Args:
            message: Error message describing the access denial.
        """
        self.message = message
        super().__init__(self.message)


class HsCloudFlowControlException(Exception):
    """Exception for HSCloud flow control errors (rate limiting)."""

    def __init__(self, message):
        """
        Initialize HSCloud flow control exception.
        
        Args:
            message: Error message describing the flow control issue.
        """
        self.message = message
        super().__init__(self.message)
