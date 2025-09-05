"""
Service de création d'utilisateur.
Gère la logique métier pour la création de nouveaux utilisateurs.
"""

from typing import Optional
from src.infrastructure.logger_manager import get_logger
from src.domain.entities.user import User, UserRole, UserValidationError
from src.ports.user_repository import UserRepositoryPort
from src.domain.exceptions.business_exceptions import UserCreationError

logger = get_logger(__name__)

class UserCreationService:
    """
    Service pour la création de nouveaux utilisateurs.

    Ce service encapsule toute la logique métier pour créer des utilisateurs,
    incluant les validations, vérifications de doublons, et persistance.
    """

    def __init__(self, user_repository: UserRepositoryPort):
        """
        Initialise le service avec le repository d'utilisateurs.

        Args:
            user_repository: Port pour la persistance des utilisateurs
        """
        self.user_repository = user_repository
        logger.debug("Service de création d'utilisateur initialisé")

    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str,
        role: UserRole,
        condo_unit: Optional[str] = None,
        phone: Optional[str] = None
    ) -> User:
        """
        Crée un nouveau utilisateur avec validation complète.

        Args:
            username: Nom d'utilisateur unique
            email: Adresse email unique
            password: Mot de passe en clair (sera hashé)
            full_name: Nom complet de l'utilisateur
            role: Rôle de l'utilisateur
            condo_unit: Numéro d'unité (requis pour les résidents)
            phone: Numéro de téléphone optionnel

        Returns:
            User: L'utilisateur créé

        Raises:
            UserCreationError: En cas d'erreur de création
        """
        try:
            logger.info(f"Début de création d'utilisateur: {username}")

            # Validation des données d'entrée
            self._validate_input_data(username, email, password, full_name, role, condo_unit)

            # Vérification des doublons
            await self._check_duplicates(username, email)

            # Création de l'entité User
            user = self._create_user_entity(username, email, password, full_name, role, condo_unit, phone)

            # Sauvegarde
            success = await self.user_repository.save_user(user)

            if not success:
                logger.error(f"Échec de la sauvegarde pour {username}")
                raise UserCreationError("Échec de la sauvegarde de l'utilisateur")

            logger.info(f"Utilisateur créé avec succès: {username}")
            return user

        except UserValidationError as e:
            logger.warning(f"Erreur de validation pour {username}: {e}")
            raise UserCreationError(f"Données utilisateur invalides: {e}")
        except UserCreationError:
            # Re-raise les erreurs de création
            raise
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la création de {username}: {e}")
            raise UserCreationError(f"Erreur lors de la création: {e}")

    def _validate_input_data(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str,
        role: UserRole,
        condo_unit: Optional[str]
    ) -> None:
        """
        Valide les données d'entrée avant création.

        Args:
            username: Nom d'utilisateur à valider
            email: Email à valider
            password: Mot de passe à valider
            full_name: Nom complet à valider
            role: Rôle à valider
            condo_unit: Unité de condo à valider

        Raises:
            UserCreationError: Si les données sont invalides
        """
        if not username or not username.strip():
            raise UserCreationError("Nom d'utilisateur requis")

        if len(username) < 3:
            raise UserCreationError("Nom d'utilisateur doit contenir au moins 3 caractères")

        if not email or "@" not in email:
            raise UserCreationError("Email invalide")

        if not password:
            raise UserCreationError("Mot de passe requis")

        if len(password) < 6:
            raise UserCreationError("Mot de passe trop court (minimum 6 caractères)")

        if not full_name or len(full_name.strip()) < 2:
            raise UserCreationError("Nom complet requis (minimum 2 caractères)")

    async def _check_duplicates(self, username: str, email: str) -> None:
        """
        Vérifie qu'il n'y a pas de doublons pour username et email.

        Args:
            username: Nom d'utilisateur à vérifier
            email: Email à vérifier

        Raises:
            UserCreationError: Si un doublon est trouvé
        """
        # Vérifier username
        existing_user_by_username = await self.user_repository.get_user_by_username(username)
        if existing_user_by_username:
            logger.warning(f"Tentative de création avec username existant: {username}")
            raise UserCreationError("Nom d'utilisateur déjà utilisé")

        # Vérifier email
        existing_user_by_email = await self.user_repository.get_user_by_email(email)
        if existing_user_by_email:
            logger.warning(f"Tentative de création avec email existant: {email}")
            raise UserCreationError("Adresse email déjà utilisée")

    def _create_user_entity(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str,
        role: UserRole,
        condo_unit: Optional[str],
        phone: Optional[str]
    ) -> User:
        """
        Crée l'entité User avec les données validées.

        Args:
            username: Nom d'utilisateur
            email: Email
            password: Mot de passe en clair
            full_name: Nom complet
            role: Rôle
            condo_unit: Unité de condo
            phone: Téléphone

        Returns:
            User: Entité utilisateur créée
        """
        # Hasher le mot de passe
        password_hash = User.hash_password(password)

        # Créer l'entité (la validation se fait dans __post_init__)
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            full_name=full_name,
            condo_unit=condo_unit.strip() if condo_unit else None,
            phone=phone.strip() if phone else None,
            is_active=True
        )

        return user
