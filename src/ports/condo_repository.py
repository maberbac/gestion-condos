"""
Port pour Repository de Condos - Interface du pattern hexagonal.

Ce port définit le contrat que le domaine métier attend pour la persistance
et récupération des données de condos. Les adapters concrets implémentent
cette interface selon la technologie choisie (fichiers, base de données, API).

[Architecture Hexagonale]
Ce port fait partie de la couche ports et définit les interfaces que
le domaine métier utilise sans connaître les implémentations concrètes.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from src.domain.entities.condo import Condo, CondoStatus, CondoType


class CondoRepositoryPort(ABC):
    """
    Interface abstraite pour la persistance des données de condos.
    
    Cette interface définit tous les contrats que le domaine métier
    attend pour manipuler les données de condos. Les adapters concrets
    (FileAdapter, DatabaseAdapter, etc.) implémenteront cette interface.
    
    Avantages de cette approche :
    - Le domaine métier ne dépend d'aucune technologie spécifique
    - Facilite les tests avec des mocks
    - Permet de changer d'implémentation sans affecter la logique métier
    - Extensibilité pour futures technologies (API, cloud, etc.)
    """
    
    @abstractmethod
    async def save_condo(self, condo: Condo) -> bool:
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
    async def get_condo_by_unit_number(self, unit_number: str) -> Optional[Condo]:
        """
        Récupère un condo par son numéro d'unité.
        
        Args:
            unit_number: Numéro d'unité à rechercher
            
        Returns:
            Optional[Condo]: Instance du condo trouvé, ou None si inexistant
        """
        pass
    
    @abstractmethod
    async def get_all_condos(self) -> List[Condo]:
        """
        Récupère tous les condos du système.
        
        Returns:
            List[Condo]: Liste de tous les condos
        """
        pass
    
    @abstractmethod
    async def get_condos_by_owner(self, owner_name: str) -> List[Condo]:
        """
        Récupère tous les condos appartenant à un propriétaire.
        
        Args:
            owner_name: Nom du propriétaire
            
        Returns:
            List[Condo]: Liste des condos du propriétaire
        """
        pass
    
    @abstractmethod
    async def get_condos_by_status(self, status: CondoStatus) -> List[Condo]:
        """
        Récupère tous les condos ayant un statut spécifique.
        
        Args:
            status: Statut recherché
            
        Returns:
            List[Condo]: Liste des condos avec ce statut
        """
        pass
    
    @abstractmethod
    async def get_condos_by_type(self, condo_type: CondoType) -> List[Condo]:
        """
        Récupère tous les condos d'un type spécifique.
        
        Args:
            condo_type: Type de condo recherché
            
        Returns:
            List[Condo]: Liste des condos de ce type
        """
        pass
    
    @abstractmethod
    async def delete_condo(self, unit_number: str) -> bool:
        """
        Supprime un condo du système.
        
        Args:
            unit_number: Numéro d'unité à supprimer
            
        Returns:
            bool: True si suppression réussie, False si condo inexistant
            
        Raises:
            CondoRepositoryError: Si erreur pendant la suppression
        """
        pass
    
    @abstractmethod
    async def get_condos_with_filters(self, filters: Dict[str, Any]) -> List[Condo]:
        """
        Récupère des condos selon des critères de filtrage flexibles.
        
        Args:
            filters: Dictionnaire de critères de filtrage
                   Exemples: {'min_square_feet': 500, 'max_monthly_fees': 400}
                   
        Returns:
            List[Condo]: Liste des condos correspondant aux critères
        """
        pass
    
    @abstractmethod
    async def count_condos(self) -> int:
        """
        Compte le nombre total de condos dans le système.
        
        Returns:
            int: Nombre total de condos
        """
        pass
    
    @abstractmethod
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Récupère des statistiques sur les condos.
        
        Returns:
            Dict[str, Any]: Statistiques (totaux par type, statut, etc.)
        """
        pass


class FileHandlerPort(ABC):
    """
    Interface pour la manipulation de fichiers.
    
    [CONCEPT: Lecture de fichiers]
    Ce port sera implémenté par FileAdapter pour démontrer
    le concept technique de lecture de fichiers.
    """
    
    @abstractmethod
    async def read_json_file(self, filepath: str) -> Dict[str, Any]:
        """
        Lit un fichier JSON et retourne son contenu.
        
        Args:
            filepath: Chemin du fichier JSON
            
        Returns:
            Dict[str, Any]: Contenu du fichier JSON
            
        Raises:
            FileReadError: Si erreur de lecture
        """
        pass
    
    @abstractmethod
    async def write_json_file(self, filepath: str, data: Dict[str, Any]) -> bool:
        """
        Écrit des données dans un fichier JSON.
        
        Args:
            filepath: Chemin du fichier de destination
            data: Données à écrire
            
        Returns:
            bool: True si écriture réussie
        """
        pass
    
    @abstractmethod
    async def read_csv_file(self, filepath: str) -> List[Dict[str, str]]:
        """
        Lit un fichier CSV et retourne ses données.
        
        Args:
            filepath: Chemin du fichier CSV
            
        Returns:
            List[Dict[str, str]]: Données du CSV sous forme de liste de dictionnaires
        """
        pass
    
    @abstractmethod
    async def write_csv_file(self, filepath: str, data: List[Dict[str, str]], 
                           fieldnames: List[str]) -> bool:
        """
        Écrit des données dans un fichier CSV.
        
        Args:
            filepath: Chemin du fichier de destination
            data: Données à écrire
            fieldnames: Noms des colonnes
            
        Returns:
            bool: True si écriture réussie
        """
        pass


class NotificationPort(ABC):
    """
    Interface pour le système de notifications.
    
    Ce port sera utile pour les extensions futures (location, juridique)
    où il faudra notifier les propriétaires, locataires, ou services externes.
    """
    
    @abstractmethod
    async def send_notification(self, recipient: str, message: str, 
                              notification_type: str = "info") -> bool:
        """
        Envoie une notification.
        
        Args:
            recipient: Destinataire de la notification
            message: Contenu du message
            notification_type: Type de notification (info, warning, error)
            
        Returns:
            bool: True si envoi réussi
        """
        pass
    
    @abstractmethod
    async def send_bulk_notifications(self, recipients: List[str], 
                                    message: str) -> Dict[str, bool]:
        """
        Envoie des notifications en lot.
        
        Args:
            recipients: Liste des destinataires
            message: Message à envoyer
            
        Returns:
            Dict[str, bool]: Statut d'envoi par destinataire
        """
        pass


# Exceptions spécifiques aux ports
class CondoRepositoryError(Exception):
    """Erreur de base pour les opérations de repository."""
    pass


class FileReadError(Exception):
    """Erreur lors de la lecture de fichiers."""
    pass


class NotificationError(Exception):
    """Erreur lors de l'envoi de notifications."""
    pass
