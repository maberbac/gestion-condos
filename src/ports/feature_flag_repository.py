"""
Port FeatureFlagRepository - Interface pour la persistance des feature flags.

[ARCHITECTURE HEXAGONALE - PORTS]
Interface définissant les opérations de persistance pour les feature flags.
Implémentations concrètes dans la couche adapters.
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.feature_flag import FeatureFlag


class FeatureFlagRepositoryPort(ABC):
    """
    Interface du repository pour les feature flags.
    
    Définit les opérations CRUD et métier pour la gestion des feature flags.
    """
    
    @abstractmethod
    def get_all(self) -> List[FeatureFlag]:
        """
        Récupère tous les feature flags.
        
        Returns:
            List[FeatureFlag]: Liste de tous les feature flags
        """
        pass
    
    @abstractmethod
    def get_by_name(self, flag_name: str) -> Optional[FeatureFlag]:
        """
        Récupère un feature flag par son nom.
        
        Args:
            flag_name: Nom du feature flag
            
        Returns:
            Optional[FeatureFlag]: Le feature flag ou None si non trouvé
        """
        pass
    
    @abstractmethod
    def is_enabled(self, flag_name: str) -> bool:
        """
        Vérifie si un feature flag est activé.
        
        Args:
            flag_name: Nom du feature flag
            
        Returns:
            bool: True si activé, False sinon (ou si non trouvé)
        """
        pass
    
    @abstractmethod
    def create(self, feature_flag: FeatureFlag) -> FeatureFlag:
        """
        Crée un nouveau feature flag.
        
        Args:
            feature_flag: Le feature flag à créer
            
        Returns:
            FeatureFlag: Le feature flag créé avec son ID
        """
        pass
    
    @abstractmethod
    def update(self, feature_flag: FeatureFlag) -> FeatureFlag:
        """
        Met à jour un feature flag existant.
        
        Args:
            feature_flag: Le feature flag à mettre à jour
            
        Returns:
            FeatureFlag: Le feature flag mis à jour
        """
        pass
    
    @abstractmethod
    def enable_flag(self, flag_name: str) -> bool:
        """
        Active un feature flag par son nom.
        
        Args:
            flag_name: Nom du feature flag à activer
            
        Returns:
            bool: True si succès, False sinon
        """
        pass
    
    @abstractmethod
    def disable_flag(self, flag_name: str) -> bool:
        """
        Désactive un feature flag par son nom.
        
        Args:
            flag_name: Nom du feature flag à désactiver
            
        Returns:
            bool: True si succès, False sinon
        """
        pass
    
    @abstractmethod
    def toggle_flag(self, flag_name: str) -> bool:
        """
        Inverse l'état d'un feature flag par son nom.
        
        Args:
            flag_name: Nom du feature flag à inverser
            
        Returns:
            bool: True si succès, False sinon
        """
        pass
    
    @abstractmethod
    def delete(self, flag_name: str) -> bool:
        """
        Supprime un feature flag par son nom.
        
        Args:
            flag_name: Nom du feature flag à supprimer
            
        Returns:
            bool: True si succès, False sinon
        """
        pass
