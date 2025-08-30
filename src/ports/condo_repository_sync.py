"""
Port pour Repository de Condos - Version synchrone pour compatibilité initiale.

Ce port définit le contrat que le domaine métier attend pour la persistance
et récupération des données de condos. Version synchrone temporaire pour
faciliter l'intégration avec SQLite standard.

[Architecture Hexagonale]
Ce port fait partie de la couche ports et définit les interfaces que
le domaine métier utilise sans connaître les implémentations concrètes.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from src.domain.entities.condo import Condo, CondoStatus, CondoType


class CondoRepositoryError(Exception):
    """Exception levée pour les erreurs de repository."""
    pass


class CondoRepositoryPort(ABC):
    """
    Interface abstraite pour la persistance des données de condos.
    
    Cette interface définit tous les contrats que le domaine métier
    attend pour manipuler les données de condos. Les adapters concrets
    (FileAdapter, SQLiteAdapter, etc.) implémenteront cette interface.
    
    Avantages de cette approche :
    - Le domaine métier ne dépend d'aucune technologie spécifique
    - Facilite les tests avec des mocks
    - Permet de changer d'implémentation sans affecter la logique métier
    - Extensibilité pour futures technologies (API, cloud, etc.)
    """
    
    @abstractmethod
    def save_condo(self, condo: Condo) -> bool:
        """
        Sauvegarde ou met à jour un condo.
        
        Args:
            condo: Instance de Condo à sauvegarder
            
        Returns:
            bool: True si la sauvegarde réussit, False sinon
            
        Raises:
            CondoRepositoryError: Si erreur de persistance
        """
        pass
    
    @abstractmethod
    def get_condo_by_unit_number(self, unit_number: str) -> Optional[Condo]:
        """
        Récupère un condo par son numéro d'unité.
        
        Args:
            unit_number: Numéro d'unité à rechercher
            
        Returns:
            Optional[Condo]: Instance du condo trouvé, ou None si inexistant
        """
        pass
    
    @abstractmethod
    def get_all_condos(self) -> List[Condo]:
        """
        Récupère tous les condos.
        
        Returns:
            List[Condo]: Liste de tous les condos enregistrés
        """
        pass
    
    @abstractmethod
    def get_condos_by_status(self, status: CondoStatus) -> List[Condo]:
        """
        Récupère tous les condos avec un statut spécifique.
        
        Args:
            status: Statut à filtrer
            
        Returns:
            List[Condo]: Liste des condos avec le statut spécifié
        """
        pass
    
    @abstractmethod
    def get_condos_by_type(self, condo_type: CondoType) -> List[Condo]:
        """
        Récupère tous les condos d'un type spécifique.
        
        Args:
            condo_type: Type de condo à filtrer
            
        Returns:
            List[Condo]: Liste des condos du type spécifié
        """
        pass
    
    @abstractmethod
    def delete_condo(self, unit_number: str) -> bool:
        """
        Supprime un condo.
        
        Args:
            unit_number: Numéro d'unité du condo à supprimer
            
        Returns:
            bool: True si la suppression réussit, False si le condo n'existe pas
            
        Raises:
            CondoRepositoryError: Si erreur durant la suppression
        """
        pass
    
    @abstractmethod
    def count_condos(self) -> int:
        """
        Compte le nombre total de condos.
        
        Returns:
            int: Nombre total de condos enregistrés
        """
        pass
    
    @abstractmethod
    def get_condos_with_filters(self, filters: Dict[str, Any]) -> List[Condo]:
        """
        Récupère des condos selon des critères de filtrage flexibles.
        
        Args:
            filters: Dictionnaire de critères de filtrage
                   Exemples: {'min_square_feet': 500, 'max_monthly_fees': 400,
                            'condo_type': 'residential', 'status': 'occupied'}
                   
        Returns:
            List[Condo]: Liste des condos correspondant aux critères
            
        Notes:
            - Les filtres sont combinés avec AND
            - Les clés supportées peuvent inclure :
              * min_square_feet: superficie minimale
              * max_square_feet: superficie maximale
              * condo_type: type de condo
              * status: statut du condo
              * min_monthly_fees: frais mensuels minimaux
              * max_monthly_fees: frais mensuels maximaux
        """
        pass
    
    # Méthodes optionnelles avec implémentation par défaut
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Récupère des statistiques sur les condos.
        
        Returns:
            Dict[str, Any]: Dictionnaire contenant les statistiques
            
        Note:
            Cette méthode est optionnelle. L'implémentation par défaut
            retourne des statistiques basiques calculées à partir
            des autres méthodes.
        """
        # Implémentation par défaut basée sur les autres méthodes
        all_condos = self.get_all_condos()
        
        if not all_condos:
            return {
                'total_condos': 0,
                'total_square_feet': 0,
                'average_square_feet': 0,
                'by_type': {},
                'by_status': {}
            }
        
        total_square_feet = sum(condo.square_feet for condo in all_condos)
        
        # Statistiques par type
        by_type = {}
        for condo in all_condos:
            type_name = condo.condo_type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1
        
        # Statistiques par statut
        by_status = {}
        for condo in all_condos:
            status_name = condo.status.value
            by_status[status_name] = by_status.get(status_name, 0) + 1
        
        return {
            'total_condos': len(all_condos),
            'total_square_feet': total_square_feet,
            'average_square_feet': round(total_square_feet / len(all_condos), 2),
            'by_type': by_type,
            'by_status': by_status
        }


# Alias pour compatibilité avec l'ancienne version asynchrone
CondoRepositoryPortAsync = CondoRepositoryPort
