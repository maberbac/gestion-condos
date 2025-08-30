"""
Authentication Service - Service d'authentification respectant l'architecture hexagonale.

[ARCHITECTURE HEXAGONALE]
Ce service fait partie du domaine métier et utilise les ports pour la persistance.
Il ne dépend d'aucun détail d'infrastructure grâce à l'injection de dépendances.

[CONCEPTS TECHNIQUES INTÉGRÉS]
- Lecture de fichiers : Via port UserRepositoryPort (abstraction)
- Programmation fonctionnelle : Fonctions pures pour validation et filtrage
- Gestion des erreurs : Exceptions spécialisées
- Programmation asynchrone : Opérations non-bloquantes
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
    [ARCHITECTURE HEXAGONALE + 4 CONCEPTS TECHNIQUES]
    Service d'authentification respectant l'architecture hexagonale.
    
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
        
        [CONCEPT: Programmation asynchrone]
        """
        try:
            await self.user_repository.initialize_default_users()
            logger.info("Service d'authentification initialisé")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du service: {e}")
            raise UserAuthenticationError(f"Impossible d'initialiser le service: {e}")
    
    async def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        [CONCEPT: Programmation asynchrone + Gestion d'erreurs]
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
            
            # Récupération via le port (respect architecture hexagonale)
            user = await self.user_repository.get_user_by_username(username)
            
            if not user:
                logger.warning(f"Utilisateur inexistant: {username}")
                return None
            
            if not user.is_active:
                logger.warning(f"Compte désactivé: {username}")
                return None
            
            # [CONCEPT: Programmation fonctionnelle]
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
        [CONCEPT: Programmation fonctionnelle]
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
        [CONCEPT: Programmation fonctionnelle]
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
        [CONCEPT: Programmation fonctionnelle]
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
        [CONCEPT: Gestion d'erreurs]
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


# Exemple d'utilisation pour démonstration MVP
async def demo_authentication_service():
    """
    [DÉMONSTRATION DES 4 CONCEPTS + ARCHITECTURE HEXAGONALE]
    Exemple d'utilisation du service d'authentification avec injection de dépendances.
    """
    logger.info("=== Démonstration Service d'Authentification (Architecture Hexagonale) ===")
    
    # Import de l'adaptateur concret
    from src.adapters.user_file_adapter import UserFileAdapter
    
    try:
        # [ARCHITECTURE HEXAGONALE] : Injection de dépendances
        user_repository = UserFileAdapter("tmp/demo_users.json")
        auth_service = AuthenticationService(user_repository)
        
        # Initialisation
        await auth_service.initialize()
        
        # [CONCEPT: Programmation asynchrone]
        logger.info("\n1. Test d'authentification...")
        
        auth_user = await auth_service.authenticate("admin", "admin124")
        if auth_user:
            logger.info(f"Authentification réussie: {auth_user.username}")
            
            # Création de session
            session_token = auth_service.create_session(auth_user)
            logger.info(f"Session créée: {session_token[:8]}...")
        
        logger.info("\n=== Démonstration terminée avec succès ===")
        
    except (UserAuthenticationError, UserValidationError) as e:
        logger.error(f"Erreur d'authentification: {e}")
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")


if __name__ == "__main__":
    # Exécuter la démonstration
    asyncio.run(demo_authentication_service())
