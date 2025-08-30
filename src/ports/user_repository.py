"""
Port pour Repository d'Utilisateurs - Interface du pattern hexagonal.

Ce port définit le contrat que le domaine métier attend pour la persistance
et récupération des données utilisateur. Les adapters concrets implémentent
cette interface selon la technologie choisie (fichiers, base de données, API).

[Architecture Hexagonale]
Ce port fait partie de la couche ports et définit les interfaces que
le domaine métier utilise sans connaître les implémentations concrètes.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from src.domain.entities.user import User, UserRole


class UserRepositoryPort(ABC):
    """
    Interface abstraite pour la persistance des données utilisateur.
    
    Cette interface définit tous les contrats que le domaine métier
    attend pour manipuler les données utilisateur. Les adapters concrets
    (FileAdapter, DatabaseAdapter, etc.) implémenteront cette interface.
    
    Avantages de cette approche :
    - Le domaine métier ne dépend d'aucune technologie spécifique
    - Facilite les tests avec des mocks
    - Permet de changer d'implémentation sans affecter la logique métier
    - Extensibilité pour futures technologies (API, cloud, etc.)
    """
    
    @abstractmethod
    async def get_all_users(self) -> List[User]:
        """
        Récupère tous les utilisateurs.
        
        Returns:
            Liste de tous les utilisateurs
            
        Raises:
            Exception: En cas d'erreur de lecture
        """
        pass
    
    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Récupère un utilisateur par son nom d'utilisateur.
        
        Args:
            username: Nom d'utilisateur à rechercher
            
        Returns:
            Utilisateur trouvé ou None si introuvable
            
        Raises:
            Exception: En cas d'erreur de lecture
        """
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Récupère un utilisateur par son email.
        
        Args:
            email: Email à rechercher
            
        Returns:
            Utilisateur trouvé ou None si introuvable
            
        Raises:
            Exception: En cas d'erreur de lecture
        """
        pass
    
    @abstractmethod
    async def save_user(self, user: User) -> User:
        """
        Sauvegarde un utilisateur (création ou mise à jour).
        
        Args:
            user: Utilisateur à sauvegarder
            
        Returns:
            Utilisateur sauvegardé
            
        Raises:
            Exception: En cas d'erreur de sauvegarde
        """
        pass
    
    @abstractmethod
    async def save_users(self, users: List[User]) -> List[User]:
        """
        Sauvegarde une liste d'utilisateurs.
        
        Args:
            users: Liste des utilisateurs à sauvegarder
            
        Returns:
            Liste des utilisateurs sauvegardés
            
        Raises:
            Exception: En cas d'erreur de sauvegarde
        """
        pass
    
    @abstractmethod
    async def delete_user(self, username: str) -> bool:
        """
        Supprime un utilisateur.
        
        Args:
            username: Nom d'utilisateur à supprimer
            
        Returns:
            True si supprimé, False si introuvable
            
        Raises:
            Exception: En cas d'erreur de suppression
        """
        pass
    
    @abstractmethod
    async def user_exists(self, username: str) -> bool:
        """
        Vérifie si un utilisateur existe.
        
        Args:
            username: Nom d'utilisateur à vérifier
            
        Returns:
            True si l'utilisateur existe, False sinon
            
        Raises:
            Exception: En cas d'erreur de vérification
        """
        pass
    
    @abstractmethod
    async def get_users_by_role(self, role: UserRole) -> List[User]:
        """
        Récupère tous les utilisateurs d'un rôle donné.
        
        Args:
            role: Rôle à filtrer
            
        Returns:
            Liste des utilisateurs ayant ce rôle
            
        Raises:
            Exception: En cas d'erreur de lecture
        """
        pass
    
    @abstractmethod
    async def update_user_password(self, username: str, new_password_hash: str) -> bool:
        """
        Met à jour le mot de passe d'un utilisateur.
        
        Args:
            username: Nom d'utilisateur
            new_password_hash: Nouveau hash du mot de passe
            
        Returns:
            True si mis à jour, False si utilisateur introuvable
            
        Raises:
            Exception: En cas d'erreur de mise à jour
        """
        pass
    
    @abstractmethod
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authentifie un utilisateur avec son nom d'utilisateur et mot de passe.
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe en clair
            
        Returns:
            Utilisateur authentifié ou None si échec
            
        Raises:
            Exception: En cas d'erreur d'authentification
        """
        pass
    
    @abstractmethod
    async def initialize_default_users(self) -> None:
        """
        Initialise les utilisateurs par défaut si aucun n'existe.
        
        Raises:
            Exception: En cas d'erreur d'initialisation
        """
        pass
