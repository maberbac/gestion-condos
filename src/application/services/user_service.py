"""
Service de gestion des utilisateurs - Couche application

[ARCHITECTURE HEXAGONALE]
Ce service fait partie de la couche application et orchestre
les opérations métier liées aux utilisateurs. Il utilise les ports
du domaine sans connaître les implémentations concrètes.

[MÉTHODOLOGIE TDD]
Service créé pour satisfaire les tests existants (phase GREEN).
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

from typing import List, Dict, Any, Optional
from src.domain.entities.user import User, UserRole
from src.adapters.user_repository_sqlite import UserRepositorySQLite


class UserService:
    """
    Service de gestion des utilisateurs pour la couche application.
    
    Ce service orchestre les opérations utilisateur et prépare
    les données pour l'affichage web en utilisant l'architecture hexagonale.
    """
    
    def __init__(self, user_repository: Optional[UserRepositorySQLite] = None):
        """
        Initialise le service utilisateur avec son repository.
        
        Args:
            user_repository: Repository pour accéder aux données utilisateur
        """
        self.user_repository = user_repository or UserRepositorySQLite()
        logger.debug("Service utilisateur initialisé")
    
    def _run_async_operation(self, async_func, *args, **kwargs):
        """
        Utilitaire pour exécuter des opérations asynchrones de manière synchrone.
        
        Args:
            async_func: Fonction asynchrone à exécuter
            *args: Arguments positionnels
            **kwargs: Arguments nommés
            
        Returns:
            Résultat de la fonction asynchrone
        """
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(async_func(*args, **kwargs))
    
    def get_all_users(self) -> List[User]:
        """
        Récupère tous les utilisateurs depuis la base de données.
        
        Returns:
            Liste des utilisateurs
        """
        try:
            users = self._run_async_operation(self.user_repository.get_all_users)
            logger.info(f"Récupération de {len(users)} utilisateurs depuis la base")
            return users
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des utilisateurs: {e}")
            return []
    
    def get_user_statistics(self) -> Dict[str, int]:
        """
        Calcule les statistiques des utilisateurs par rôle.
        
        Returns:
            Dictionnaire avec les compteurs par rôle
        """
        try:
            users = self.get_all_users()
            
            stats = {
                'admin_count': 0,
                'resident_count': 0,
                'total_count': len(users)
            }
            
            for user in users:
                if user.role == UserRole.ADMIN:
                    stats['admin_count'] += 1
                elif user.role == UserRole.RESIDENT:
                    stats['resident_count'] += 1
            
            logger.debug(f"Statistiques calculées: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques: {e}")
            return {'admin_count': 0, 'resident_count': 0, 'total_count': 0}
    
    def get_users_for_web_display(self) -> List[Dict[str, Any]]:
        """
        Formate les utilisateurs pour l'affichage web (template compatibility).
        
        Returns:
            Liste des utilisateurs formatés pour les templates Jinja2
        """
        try:
            users = self.get_all_users()
            formatted_users = []
            
            for user in users:
                formatted_user = {
                    'username': user.username,
                    'full_name': user.full_name,
                    'email': user.email,
                    'role': {'value': user.role.value},  # Format compatible template
                    'created_at': user.created_at,
                    'status': 'Actif'  # Par défaut, peut être étendu plus tard
                }
                formatted_users.append(formatted_user)
            
            logger.debug(f"Formatage de {len(formatted_users)} utilisateurs pour affichage web")
            return formatted_users
            
        except Exception as e:
            logger.error(f"Erreur lors du formatage des utilisateurs: {e}")
            return []
    
    def get_users_by_role(self, role: UserRole) -> List[User]:
        """
        Filtre les utilisateurs par rôle.
        
        Args:
            role: Rôle à filtrer
            
        Returns:
            Liste des utilisateurs ayant le rôle spécifié
        """
        try:
            filtered_users = self._run_async_operation(
                self.user_repository.get_users_by_role, role
            )
            
            logger.debug(f"Filtrage: {len(filtered_users)} utilisateurs avec rôle {role.value}")
            return filtered_users
            
        except Exception as e:
            logger.error(f"Erreur lors du filtrage par rôle {role.value}: {e}")
            return []
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Récupère un utilisateur par son nom d'utilisateur.
        
        Args:
            username: Nom d'utilisateur à rechercher
            
        Returns:
            Utilisateur trouvé ou None
        """
        try:
            user = self._run_async_operation(
                self.user_repository.get_user_by_username, username
            )
            if user:
                logger.debug(f"Utilisateur '{username}' trouvé")
            else:
                logger.debug(f"Utilisateur '{username}' non trouvé")
            return user
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de l'utilisateur '{username}': {e}")
            return None
    
    def get_user_details_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les détails complets d'un utilisateur par son nom d'utilisateur.
        
        Args:
            username: Nom d'utilisateur à rechercher
            
        Returns:
            Dictionnaire avec les détails formatés ou None si non trouvé
        """
        try:
            user = self._run_async_operation(
                self.user_repository.get_user_by_username, username
            )
            
            if not user:
                logger.debug(f"Utilisateur '{username}' non trouvé pour détails")
                return None
            
            # Formatage des détails pour l'affichage
            details = {
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'role': user.role.value,
                'role_display': self._get_role_display_name(user.role),
                'condo_unit': user.condo_unit or 'Non assigné',
                'last_login': getattr(user, 'last_login', None) or 'Jamais connecté',
                'created_at': getattr(user, 'created_at', None) or 'Non disponible',
                'status': 'Actif',  # Par défaut
                'has_condo_unit': bool(user.condo_unit)
            }
            
            logger.debug(f"Détails récupérés pour l'utilisateur '{username}'")
            return details
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des détails pour '{username}': {e}")
            return None
    
    def get_user_details_for_api(self, username: str) -> Dict[str, Any]:
        """
        Récupère les détails d'un utilisateur formatés pour l'API JSON.
        
        Args:
            username: Nom d'utilisateur à rechercher
            
        Returns:
            Dictionnaire formaté pour JSON ou dictionnaire d'erreur
        """
        try:
            user = self._run_async_operation(
                self.user_repository.get_user_by_username, username
            )
            
            if not user:
                logger.debug(f"Utilisateur '{username}' non trouvé pour API")
                return {
                    'error': 'Utilisateur non trouvé',
                    'username': username,
                    'found': False
                }
            
            # Formatage pour JSON API
            api_data = {
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'role': user.role.value,
                'condo_unit': user.condo_unit,
                'last_login': getattr(user, 'last_login', None),
                'created_at': getattr(user, 'created_at', None),
                'found': True,
                'details': {
                    'role_display': self._get_role_display_name(user.role),
                    'has_condo_unit': bool(user.condo_unit),
                    'status': 'Actif'
                }
            }
            
            logger.debug(f"Données API préparées pour l'utilisateur '{username}'")
            return api_data
            
        except Exception as e:
            logger.error(f"Erreur API pour l'utilisateur '{username}': {e}")
            return {
                'error': 'Erreur système lors de la récupération des données',
                'username': username,
                'found': False
            }
    
    def _get_role_display_name(self, role: UserRole) -> str:
        """
        Retourne le nom d'affichage du rôle avec icône.
        
        Args:
            role: Rôle utilisateur
            
        Returns:
            Chaîne formatée pour l'affichage
        """
        role_names = {
            UserRole.ADMIN: "Administrateur",
            UserRole.RESIDENT: "Résident", 
            UserRole.GUEST: "Invité"
        }
        return role_names.get(role, "Inconnu")
