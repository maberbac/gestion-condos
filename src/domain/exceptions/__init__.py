"""
Module exceptions du domaine.
"""

from .business_exceptions import (
    BusinessException,
    UserCreationError,
    UserNotFoundError,
    DuplicateUserError,
    InvalidUserDataError
)

__all__ = [
    'BusinessException',
    'UserCreationError',
    'UserNotFoundError',
    'DuplicateUserError',
    'InvalidUserDataError'
]
