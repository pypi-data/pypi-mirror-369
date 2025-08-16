"""
RMNpy custom exceptions

This module defines custom exception types for RMNpy library errors.
"""


class RMNError(Exception):
    """
    Base exception class for all RMNpy errors.

    This exception is raised when operations fail in the underlying
    C libraries (OCTypes, SITypes, RMNLib) or in the Python wrapper code.
    """

    pass


class OCTypesError(RMNError):
    """
    Exception raised for OCTypes library errors.

    This includes memory management errors, type conversion failures,
    and other issues specific to the OCTypes library.
    """

    pass


class SITypesError(RMNError):
    """
    Exception raised for SITypes library errors.

    This includes dimensional analysis errors, unit conversion failures,
    and invalid physical quantity operations.
    """

    pass


class RMNLibError(RMNError):
    """
    Exception raised for RMNLib library errors.

    This includes computation errors, data processing failures,
    and other issues specific to the RMNLib library.
    """

    pass
