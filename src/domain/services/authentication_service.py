"""
Authentication Service - Service d'authentification.
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from src.domain.entities.user import User, UserRole, UserAuthenticationError, UserValidationError
from src.ports.user_repository import UserRepositoryPort

class SessionExpiredError(Exception):
    """Exception pour session expirée."""
    pass

class AuthenticationService:
    """

    Service d'authentification .

    Utilise l'injection de dépendances pour respecter l'inversion de contrôle
    et ne dépend d'aucun détail d'infrastructure.
    """

    def __init__(self, user_repository: UserRepositoryPort):
        """
        Initialise le service d'authentification avec injection de dépendances.

        Args:
            user_repository: Port pour la persistance des utilisateurs
        """
        self.user_repository = user_repository

        # Cache de sessions en mémoire (MVP)
        self._sessions: Dict[str, Dict[str, Any]] = {}

    async def initialize(self) -> None:
        """
        Initialise le service avec les utilisateurs par défaut si nécessaire.


        """
        try:
            await self.user_repository.initialize_default_users()
            logger.info("Service d'authentification initialisé")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du service: {e}")
            raise UserAuthenticationError(f"Impossible d'initialiser le service: {e}")

    async def authenticate(self, username: str, password: str) -> Optional[User]:
        """

        Authentifie un utilisateur avec nom d'utilisateur et mot de passe.

        Args:
            username: Nom d'utilisateur
            password: Mot de passe en clair

        Returns:
            User si authentification réussie, None sinon

        Raises:
            UserAuthenticationError: En cas d'erreur du système
        """
        try:
            if not username or not password:
                logger.warning("Tentative d'authentification avec identifiants vides")
                return None

            user = await self.user_repository.get_user_by_username(username)

            if not user:
                logger.warning(f"Utilisateur inexistant: {username}")
                return None

            if not user.is_active:
                logger.warning(f"Compte désactivé: {username}")
                return None

            #
            # Fonction pure pour validation
            if self._verify_password(password, user.password_hash):
                # Mise à jour de la dernière connexion
                updated_user = User(
                    username=user.username,
                    email=user.email,
                    password_hash=user.password_hash,
                    role=user.role,
                    full_name=user.full_name,
                    condo_unit=user.condo_unit,
                    phone=user.phone,
                    is_active=user.is_active,
                    created_at=user.created_at,
                    last_login=datetime.now()
                )

                await self.user_repository.save_user(updated_user)
                logger.info(f"Authentification réussie pour {username}")
                return updated_user
            else:
                logger.warning(f"Mot de passe incorrect pour {username}")
                return None

        except Exception as e:
            logger.error(f"Erreur lors de l'authentification de {username}: {e}")
            raise UserAuthenticationError(f"Erreur d'authentification: {e}")

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """

        Fonction pure pour vérifier un mot de passe.

        Args:
            password: Mot de passe en clair
            password_hash: Hash stocké

        Returns:
            bool: True si le mot de passe correspond
        """
        return User.verify_password(password, password_hash)

    def create_session(self, user: User) -> str:
        """

        Crée une session simple pour l'utilisateur.

        Args:
            user: Utilisateur pour lequel créer la session

        Returns:
            str: Token de session
        """
        session_token = str(uuid.uuid4())

        # Données de session pures (sans effet de bord)
        session_data = self._create_session_data(user)
        self._sessions[session_token] = session_data

        logger.info(f"Session créée pour {user.username}")
        return session_token

    def _create_session_data(self, user: User) -> Dict[str, Any]:
        """

        Fonction pure pour créer les données de session.

        Args:
            user: Utilisateur pour la session

        Returns:
            Dict[str, Any]: Données de session
        """
        return {
            'user_id': user.username,
            'role': user.role.value,
            'full_name': user.full_name,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=8)  # Session 8h
        }

    def get_user_from_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """

        Récupère les informations utilisateur depuis le token de session.

        Args:
            session_token: Token de session

        Returns:
            Optional[Dict[str, Any]]: Données de session ou None

        Raises:
            SessionExpiredError: Si la session a expiré
        """
        try:
            session = self._sessions.get(session_token)
            if not session:
                return None

            # Vérifier expiration
            if datetime.now() > session['expires_at']:
                del self._sessions[session_token]
                raise SessionExpiredError("Session expirée")

            return session

        except SessionExpiredError:
            raise
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de session: {e}")
            return None

    def clear_session(self, session_token: str) -> None:
        """
        Supprime une session (logout).

        Args:
            session_token: Token de session à supprimer
        """
        if session_token in self._sessions:
            user_id = self._sessions[session_token].get('user_id', 'unknown')
            del self._sessions[session_token]
            logger.info(f"Session supprimée pour {user_id}")

