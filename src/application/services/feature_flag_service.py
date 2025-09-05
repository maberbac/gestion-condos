"""
FeatureFlagService - Service métier pour la vérification des feature flags.

Service léger pour vérifier l'état des fonctionnalités optionnelles.
Les feature flags sont contrôlés uniquement via la base de données.
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

from src.ports.feature_flag_repository import FeatureFlagRepositoryPort

class FeatureFlagService:
    """
    Service simple pour vérifier l'état des feature flags.

    Fournit des méthodes de lecture uniquement pour contrôler l'accès aux
    fonctionnalités OPTIONNELLES de l'application.

    NOTE:
    - Les modules de base (dashboard, projets, unités, utilisateurs) sont toujours actifs
    - Seules les fonctionnalités optionnelles sont contrôlées par feature flags
    - La configuration se fait directement en base de données, pas via l'interface web
    """

    def __init__(self, feature_flag_repository: FeatureFlagRepositoryPort):
        """
        Initialise le service avec le repository des feature flags.

        Args:
            feature_flag_repository: Repository pour l'accès aux feature flags
        """
        self.feature_flag_repository = feature_flag_repository
        logger.debug("FeatureFlagService initialisé (lecture seule)")

    def is_finance_module_enabled(self) -> bool:
        """
        Vérifie si le module finance est activé.

        Returns:
            bool: True si le module finance est activé, False sinon
        """
        try:
            return self.feature_flag_repository.is_enabled('finance_module')
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du module finance: {e}")
            return False

    def is_feature_enabled(self, feature_name: str) -> bool:
        """
        Vérifie si une fonctionnalité spécifique est activée.

        Args:
            feature_name: Nom du feature flag à vérifier

        Returns:
            bool: True si la fonctionnalité est activée, False sinon
        """
        try:
            return self.feature_flag_repository.is_enabled(feature_name)
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du feature flag {feature_name}: {e}")
            return False
