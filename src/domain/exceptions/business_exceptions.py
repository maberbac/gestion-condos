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

class ProjectCreationError(BusinessException):
    """Exception levée lors d'erreurs de création de projet."""

    def __init__(self, message: str, details: str = None):
        super().__init__(f"Erreur de création de projet: {message}", details)

class ProjectNotFoundError(BusinessException):
    """Exception levée quand un projet n'est pas trouvé."""

    def __init__(self, identifier: str, details: str = None):
        super().__init__(f"Projet non trouvé: {identifier}", details)

class DuplicateProjectError(BusinessException):
    """Exception levée lors de tentative de création de projet en doublon."""

    def __init__(self, field: str, value: str, details: str = None):
        super().__init__(f"Projet en doublon - {field}: {value}", details)

class InvalidProjectDataError(BusinessException):
    """Exception levée lors de validation de données de projet invalides."""

    def __init__(self, field: str, reason: str, details: str = None):
        super().__init__(f"Données de projet invalides - {field}: {reason}", details)

class ProjectStatusError(BusinessException):
    """Exception levée lors d'opérations invalides selon le statut du projet."""

    def __init__(self, project_name: str, current_status: str, attempted_operation: str, details: str = None):
        super().__init__(f"Opération '{attempted_operation}' invalide pour le projet '{project_name}' (statut: {current_status})", details)

class UnitCreationError(BusinessException):
    """Exception levée lors d'erreurs de création d'unité."""

    def __init__(self, message: str, details: str = None):
        super().__init__(f"Erreur de création d'unité: {message}", details)

class UnitNotFoundError(BusinessException):
    """Exception levée quand une unité n'est pas trouvée."""

    def __init__(self, identifier: str, details: str = None):
        super().__init__(f"Unité non trouvée: {identifier}", details)

class DuplicateUnitError(BusinessException):
    """Exception levée lors de tentative de création d'unité en doublon."""

    def __init__(self, field: str, value: str, project_name: str = None, details: str = None):
        project_info = f" dans le projet '{project_name}'" if project_name else ""
        super().__init__(f"Unité en doublon - {field}: {value}{project_info}", details)

class InvalidUnitDataError(BusinessException):
    """Exception levée lors de validation de données d'unité invalides."""

    def __init__(self, field: str, reason: str, details: str = None):
        super().__init__(f"Données d'unité invalides - {field}: {reason}", details)

class UnitStatusError(BusinessException):
    """Exception levée lors d'opérations invalides selon le statut de l'unité."""

    def __init__(self, unit_number: str, current_status: str, attempted_operation: str, details: str = None):
        super().__init__(f"Opération '{attempted_operation}' invalide pour l'unité '{unit_number}' (statut: {current_status})", details)
