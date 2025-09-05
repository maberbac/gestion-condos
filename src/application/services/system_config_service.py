"""
SystemConfigService - Service pour la gestion de la configuration système.

Service de domaine pour gérer les paramètres de configuration système,
incluant la vérification du setup administrateur initial.
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

from typing import Dict, Any, Optional
from src.adapters.system_config_repository_sqlite import SystemConfigRepositorySQLite

class SystemConfigService:
    """
    Service pour la gestion de la configuration système.
    
    Ce service gère les paramètres critiques du système comme :
    - Le statut du setup administrateur initial
    - Les paramètres de sécurité
    - Les configurations d'application
    """

    def __init__(self, system_config_repository: SystemConfigRepositorySQLite = None):
        """
        Initialise le service avec le repository de configuration.

        Args:
            system_config_repository: Repository pour l'accès aux configurations système
        """
        self.system_config_repository = system_config_repository or SystemConfigRepositorySQLite()
        logger.debug("SystemConfigService initialisé")

    def is_admin_password_changed(self) -> bool:
        """
        Vérifie si l'administrateur a changé son mot de passe par défaut.

        Returns:
            True si le mot de passe admin a été changé, False sinon
        """
        try:
            return self.system_config_repository.get_boolean_config('admin_password_changed', False)
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du statut admin password: {e}")
            return False

    def mark_admin_password_changed(self) -> bool:
        """
        Marque que l'administrateur a changé son mot de passe.

        Returns:
            True si la mise à jour réussit, False sinon
        """
        try:
            success = self.system_config_repository.set_boolean_config(
                'admin_password_changed', 
                True, 
                'Indique si l\'administrateur a changé son mot de passe par défaut'
            )
            if success:
                logger.info("Statut admin password marqué comme changé")
            return success
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du statut admin password: {e}")
            return False

    def reset_admin_password_status(self) -> bool:
        """
        Remet à zéro le statut de changement de mot de passe admin.
        Utilisé principalement pour les tests ou la réinitialisation.

        Returns:
            True si la remise à zéro réussit, False sinon
        """
        try:
            success = self.system_config_repository.set_boolean_config(
                'admin_password_changed', 
                False, 
                'Indique si l\'administrateur a changé son mot de passe par défaut'
            )
            if success:
                logger.info("Statut admin password remis à zéro")
            return success
        except Exception as e:
            logger.error(f"Erreur lors de la remise à zéro du statut admin password: {e}")
            return False

    def is_system_setup_completed(self) -> bool:
        """
        Vérifie si le setup initial du système est terminé.
        Actuellement, cela vérifie uniquement le changement de mot de passe admin.

        Returns:
            True si le setup est terminé, False sinon
        """
        return self.is_admin_password_changed()

    def get_system_setup_status(self) -> Dict[str, Any]:
        """
        Récupère un résumé du statut de setup du système.

        Returns:
            Dictionnaire avec les statuts de setup
        """
        return {
            'admin_password_changed': self.is_admin_password_changed(),
            'setup_completed': self.is_system_setup_completed()
        }

    def get_config_value(self, config_key: str) -> Optional[str]:
        """
        Récupère une valeur de configuration.

        Args:
            config_key: Clé de configuration

        Returns:
            Valeur de configuration ou None
        """
        try:
            return self.system_config_repository.get_config_value(config_key)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la configuration {config_key}: {e}")
            return None

    def set_config_value(self, config_key: str, config_value: str, config_type: str = 'string', description: str = None) -> bool:
        """
        Définit une valeur de configuration.

        Args:
            config_key: Clé de configuration
            config_value: Valeur de configuration
            config_type: Type de configuration
            description: Description optionnelle

        Returns:
            True si la mise à jour réussit
        """
        try:
            return self.system_config_repository.set_config_value(config_key, config_value, config_type, description)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la configuration {config_key}: {e}")
            return False

    def get_boolean_config(self, config_key: str, default_value: bool = False) -> bool:
        """
        Récupère une configuration booléenne.

        Args:
            config_key: Clé de configuration
            default_value: Valeur par défaut

        Returns:
            Valeur booléenne
        """
        try:
            return self.system_config_repository.get_boolean_config(config_key, default_value)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la configuration booléenne {config_key}: {e}")
            return default_value

    def set_boolean_config(self, config_key: str, config_value: bool, description: str = None) -> bool:
        """
        Définit une configuration booléenne.

        Args:
            config_key: Clé de configuration
            config_value: Valeur booléenne
            description: Description optionnelle

        Returns:
            True si la mise à jour réussit
        """
        try:
            return self.system_config_repository.set_boolean_config(config_key, config_value, description)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la configuration booléenne {config_key}: {e}")
            return False

    def delete_config(self, config_key: str) -> bool:
        """
        Supprime une configuration.

        Args:
            config_key: Clé de configuration à supprimer

        Returns:
            True si la suppression réussit
        """
        try:
            return self.system_config_repository.delete_config(config_key)
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la configuration {config_key}: {e}")
            return False

    def get_all_system_configs(self) -> Dict[str, Any]:
        """
        Récupère toutes les configurations système.

        Returns:
            Dictionnaire avec toutes les configurations
        """
        try:
            configs = self.system_config_repository.get_all_configs()
            return {config['config_key']: config for config in configs}
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des configurations système: {e}")
            return {}

    def validate_system_security(self) -> Dict[str, Any]:
        """
        Valide les paramètres de sécurité du système.

        Returns:
            Rapport de validation de sécurité
        """
        validation_report = {
            'admin_password_changed': self.is_admin_password_changed(),
            'security_level': 'HIGH' if self.is_admin_password_changed() else 'LOW',
            'recommendations': []
        }

        if not self.is_admin_password_changed():
            validation_report['recommendations'].append(
                'Changer le mot de passe administrateur par défaut immédiatement'
            )

        return validation_report
