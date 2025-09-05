"""
Module exceptions du domaine.
"""

from .business_exceptions import (
    BusinessException,
    UserCreationError,
    UserNotFoundError,
    DuplicateUserError,
    InvalidUserDataError,
    ProjectCreationError,
    ProjectNotFoundError,
    DuplicateProjectError,
    InvalidProjectDataError,
    ProjectStatusError
)

__all__ = [
    'BusinessException',
    'UserCreationError',
    'UserNotFoundError',
    'DuplicateUserError',
    'InvalidUserDataError',
    'ProjectCreationError',
    'ProjectNotFoundError',
    'DuplicateProjectError',
    'InvalidProjectDataError',
    'ProjectStatusError'
]
