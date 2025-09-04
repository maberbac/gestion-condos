"""
User Entity - Entité utilisateur pour authentification MVP.

[CONCEPT TECHNIQUE: Gestion des erreurs par exceptions]
Cette entité démontre la validation robuste avec exceptions personnalisées.
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

import hashlib
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
import hashlib
import json


class UserRole(Enum):
    """
    Rôles utilisateur simplifiés pour MVP.
    
    [ARCHITECTURE: Extension future prévue]
    Cette énumération peut facilement être étendue sans impact sur le core.
    """
    RESIDENT = "resident"           # Copropriétaire - lecture seule
    ADMIN = "admin"                # Conseil d'administration - accès complet
    GUEST = "guest"                # Invité - accès très limité


class UserAuthenticationError(Exception):
    """Exception spécialisée pour l'authentification."""
    pass


class UserValidationError(Exception):
    """Exception spécialisée pour la validation des données utilisateur."""
    pass


@dataclass
class User:
    """
    Entité utilisateur avec authentification basique.
    
    [CONCEPT: Gestion des erreurs par exceptions]
    Validation robuste avec exceptions spécialisées.
    
    [CONCEPT: Lecture de fichiers] 
    Persistance via JSON avec gestion d'erreurs.
    """
    username: str
    email: str
    password_hash: str
    role: UserRole
    full_name: str
    condo_unit: Optional[str] = None  # Numéro d'unité si resident
    phone: Optional[str] = None       # Numéro de téléphone
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    def __post_init__(self):
        """Validation automatique à la création."""
        if self.created_at is None:
            self.created_at = datetime.now()
        self._validate()
    
    def _validate(self) -> None:
        """
        [CONCEPT: Gestion des erreurs par exceptions]
        Validation robuste avec exceptions spécialisées.
        """
        if not self.username or len(self.username) < 3:
            raise UserValidationError("Username doit contenir au moins 3 caractères")
        
        if not self.email or "@" not in self.email:
            raise UserValidationError("Email invalide")
        
        if not self.password_hash:
            raise UserValidationError("Mot de passe requis")
        
        if not self.full_name or len(self.full_name.strip()) < 2:
            raise UserValidationError("Nom complet requis")
        
        # Note: L'unité de condo est optionnelle pour tous les rôles
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hashage sécurisé du mot de passe.
        
        [CONCEPT: Programmation fonctionnelle]
        Fonction pure sans effet de bord.
        """
        if not password or len(password) < 6:
            raise UserValidationError("Mot de passe doit contenir au moins 6 caractères")
        
        # Utiliser un salt unique pour chaque mot de passe
        import secrets
        salt = secrets.token_hex(16)
        # Hashage avec salt pour MVP (en production: bcrypt)
        hash_with_salt = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{hash_with_salt}:{salt}"
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Vérification du mot de passe.
        
        [CONCEPT: Programmation fonctionnelle]
        Fonction pure qui retourne un booléen.
        """
        try:
            if ':' not in password_hash:
                # Format ancien sans salt (rétrocompatibilité)
                return password_hash == hashlib.sha256(password.encode()).hexdigest()
            
            # Nouveau format avec salt
            hash_part, salt = password_hash.split(':', 1)
            expected_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return hash_part == expected_hash
        except (UserValidationError, Exception):
            return False
    
    def has_permission(self, permission: str) -> bool:
        """
        [CONCEPT: Programmation fonctionnelle]
        Fonction pure pour vérification des permissions.
        
        Args:
            permission: Type de permission ('read_condos', 'modify_finances', etc.)
            
        Returns:
            bool: True si l'utilisateur a la permission
        """
        if not self.is_active:
            return False
        
        # Permissions par rôle (extensible facilement)
        permissions_map = {
            UserRole.ADMIN: [
                'read_condos', 'create_condos', 'update_condos', 'delete_condos',
                'read_finances', 'modify_finances', 'generate_reports',
                'manage_users', 'system_admin'
            ],
            UserRole.RESIDENT: [
                'read_condos', 'read_own_finances', 'view_reports'
            ],
            UserRole.GUEST: [
                'read_basic_info'
            ]
        }
        
        return permission in permissions_map.get(self.role, [])
    
    def update_last_login(self) -> None:
        """Met à jour la dernière connexion."""
        self.last_login = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        [CONCEPT: Lecture de fichiers]
        Sérialisation pour persistance JSON.
        """
        return {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role.value,
            'full_name': self.full_name,
            'condo_unit': self.condo_unit,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        [CONCEPT: Lecture de fichiers + Gestion d'erreurs]
        Désérialisation depuis JSON avec validation.
        """
        try:
            # Conversion des dates
            created_at = None
            if data.get('created_at'):
                created_at = datetime.fromisoformat(data['created_at'])
            
            last_login = None
            if data.get('last_login'):
                last_login = datetime.fromisoformat(data['last_login'])
            
            # Conversion du rôle
            role = UserRole(data['role'])
            
            return cls(
                username=data['username'],
                email=data['email'],
                password_hash=data['password_hash'],
                role=role,
                full_name=data['full_name'],
                condo_unit=data.get('condo_unit'),
                phone=data.get('phone'),
                is_active=data.get('is_active', True),
                created_at=created_at,
                last_login=last_login
            )
            
        except KeyError as e:
            raise UserValidationError(f"Champ manquant dans les données utilisateur: {e}")
        except ValueError as e:
            raise UserValidationError(f"Données utilisateur invalides: {e}")
    
    def has_permission(self, permission: str) -> bool:
        """
        [CONCEPT: Programmation fonctionnelle]
        Fonction pure pour vérification des permissions.
        
        Args:
            permission: Le nom de la permission à vérifier
            
        Returns:
            bool: True si l'utilisateur a la permission
        """
        # Permissions par rôle
        permissions = {
            UserRole.ADMIN: {'read', 'write', 'delete', 'modify_finances', 'manage_users'},
            UserRole.RESIDENT: {'read', 'write', 'write_own'},
            UserRole.GUEST: {'read'}
        }
        
        user_permissions = permissions.get(self.role, set())
        return permission in user_permissions
    
    def deactivate(self) -> None:
        """Désactive l'utilisateur."""
        self.is_active = False
    
    def reactivate(self) -> None:
        """Réactive l'utilisateur."""
        self.is_active = True
    
    def activate(self) -> None:
        """Alias pour reactivate().""" 
        self.reactivate()
    
    def update_last_login(self) -> None:
        """Met à jour la date de dernière connexion."""
        self.last_login = datetime.now()
    
    def __str__(self) -> str:
        """Représentation string de l'utilisateur."""
        unit_info = f" (Unité: {self.condo_unit})" if self.condo_unit else ""
        return f"{self.username} - {self.full_name} ({self.role.value}){unit_info}"
    
    def __eq__(self, other) -> bool:
        """Égalité entre utilisateurs basée sur username et email."""
        if not isinstance(other, User):
            return False
        return self.username == other.username and self.email == other.email
