"""
Exceptions métier du domaine.
Définit les exceptions spécifiques aux règles de gestion.
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)


class BusinessException(Exception):
    """Exception de base pour les erreurs métier."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(message)
        self.message = message
        self.details = details
        logger.error(f"Business exception: {message}" + (f" - {details}" if details else ""))


class UserCreationError(BusinessException):
    """Exception levée lors d'erreurs de création d'utilisateur."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(f"Erreur de création d'utilisateur: {message}", details)


class UserNotFoundError(BusinessException):
    """Exception levée quand un utilisateur n'est pas trouvé."""
    
    def __init__(self, identifier: str, details: str = None):
        super().__init__(f"Utilisateur non trouvé: {identifier}", details)


class DuplicateUserError(BusinessException):
    """Exception levée lors de tentative de création d'utilisateur en doublon."""
    
    def __init__(self, field: str, value: str, details: str = None):
        super().__init__(f"Utilisateur en doublon - {field}: {value}", details)


class InvalidUserDataError(BusinessException):
    """Exception levée lors de validation de données utilisateur invalides."""
    
    def __init__(self, field: str, reason: str, details: str = None):
        super().__init__(f"Données utilisateur invalides - {field}: {reason}", details)
