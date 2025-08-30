"""
Service de modification de mot de passe
Gère la logique métier pour le changement de mots de passe des utilisateurs
"""

from src.infrastructure.logger_manager import get_logger
from src.ports.user_repository import UserRepositoryPort
from src.domain.services.authentication_service import AuthenticationService

logger = get_logger(__name__)


class PasswordChangeError(Exception):
    """Exception levée lors d'erreurs de changement de mot de passe."""
    pass


class PasswordChangeService:
    """Service pour gérer les changements de mots de passe des utilisateurs."""
    
    def __init__(self, user_repository: UserRepositoryPort, authentication_service: AuthenticationService):
        """
        Initialise le service de changement de mot de passe.
        
        Args:
            user_repository: Repository pour accéder aux données utilisateur
            authentication_service: Service d'authentification pour valider les mots de passe
        """
        self.user_repository = user_repository
        self.authentication_service = authentication_service
        logger.debug("Service de changement de mot de passe initialisé")
    
    async def change_password(self, username: str, current_password: str, new_password: str) -> bool:
        """
        Change le mot de passe d'un utilisateur.
        
        Args:
            username: Nom d'utilisateur
            current_password: Mot de passe actuel
            new_password: Nouveau mot de passe
            
        Returns:
            True si le changement a réussi
            
        Raises:
            PasswordChangeError: Si le changement échoue
        """
        logger.info(f"Tentative de changement de mot de passe pour l'utilisateur: {username}")
        
        # Validation des paramètres
        if not username:
            logger.warning("Tentative de changement avec nom d'utilisateur vide")
            raise PasswordChangeError("Le nom d'utilisateur ne peut pas être vide")
        
        if not current_password:
            logger.warning(f"Tentative de changement avec mot de passe actuel vide pour {username}")
            raise PasswordChangeError("Le mot de passe actuel ne peut pas être vide")
        
        if not new_password:
            logger.warning(f"Tentative de changement avec nouveau mot de passe vide pour {username}")
            raise PasswordChangeError("Le nouveau mot de passe ne peut pas être vide")
        
        # Validation de la force du nouveau mot de passe
        self._validate_password_strength(new_password)
        
        # Vérification que l'utilisateur existe et que le mot de passe actuel est correct
        authenticated_user = await self.authentication_service.authenticate(username, current_password)
        if not authenticated_user:
            logger.warning(f"Échec d'authentification pour {username} lors du changement de mot de passe")
            raise PasswordChangeError("Nom d'utilisateur ou mot de passe actuel incorrect")
        
        # Vérification que le nouveau mot de passe est différent de l'actuel
        if current_password == new_password:
            logger.info(f"Tentative de changement avec le même mot de passe pour {username}")
            raise PasswordChangeError("Le nouveau mot de passe doit être différent du mot de passe actuel")
        
        # Mise à jour du mot de passe
        try:
            # Hasher le nouveau mot de passe avant de l'envoyer au repository
            from src.domain.entities.user import User
            new_password_hash = User.hash_password(new_password)
            
            success = await self.user_repository.update_user_password(username, new_password_hash)
            if success:
                logger.info(f"Mot de passe changé avec succès pour l'utilisateur: {username}")
                return True
            else:
                logger.error(f"Échec de mise à jour du mot de passe pour {username}")
                raise PasswordChangeError("Échec de la mise à jour du mot de passe")
                
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du mot de passe pour {username}: {str(e)}")
            raise PasswordChangeError(f"Erreur lors de la mise à jour: {str(e)}")
    
    def _validate_password_strength(self, password: str) -> None:
        """
        Valide la force du nouveau mot de passe.
        
        Args:
            password: Mot de passe à valider
            
        Raises:
            PasswordChangeError: Si le mot de passe ne respecte pas les critères
        """
        if not password or not password.strip():
            logger.warning("Tentative de changement avec mot de passe vide ou composé d'espaces")
            raise PasswordChangeError("Le nouveau mot de passe ne peut pas être vide")
        
        if len(password) < 6:
            logger.warning("Tentative de changement avec mot de passe trop court")
            raise PasswordChangeError("Le mot de passe doit contenir au moins 6 caractères")
        
        # Vérifications supplémentaires optionnelles
        if password.lower() in ['password', '123456', 'azerty', 'qwerty']:
            logger.warning("Tentative de changement avec mot de passe commun")
            raise PasswordChangeError("Le mot de passe choisi est trop commun")
        
        logger.debug("Validation de la force du mot de passe réussie")
