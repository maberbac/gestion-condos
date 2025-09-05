"""
Entité FeatureFlag - Gestion des fonctionnalités activables/désactivables.

Cette entité représente un feature flag qui permet de contrôler
l'activation/désactivation de fonctionnalités de l'application.
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class FeatureFlag:
    """
    Entité métier représentant un feature flag.

    Attributs:
        flag_name: Nom unique du feature flag
        is_enabled: État d'activation (True/False)
        description: Description de la fonctionnalité
        created_at: Date de création
        updated_at: Date de dernière modification
        id: Identifiant unique (optionnel pour création)
    """
    flag_name: str
    is_enabled: bool
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None

    def __post_init__(self):
        """Initialisation après création de l'objet."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def enable(self) -> None:
        """Active le feature flag."""
        logger.debug(f"Activation du feature flag: {self.flag_name}")
        self.is_enabled = True
        self.updated_at = datetime.now()

    def disable(self) -> None:
        """Désactive le feature flag."""
        logger.debug(f"Désactivation du feature flag: {self.flag_name}")
        self.is_enabled = False
        self.updated_at = datetime.now()

    def toggle(self) -> None:
        """Inverse l'état du feature flag."""
        logger.debug(f"Inversion du feature flag: {self.flag_name} ({self.is_enabled} -> {not self.is_enabled})")
        self.is_enabled = not self.is_enabled
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Convertit l'entité en dictionnaire pour sérialisation."""
        return {
            'id': self.id,
            'flag_name': self.flag_name,
            'is_enabled': self.is_enabled,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'FeatureFlag':
        """Crée une instance FeatureFlag à partir d'un dictionnaire."""
        return cls(
            id=data.get('id'),
            flag_name=data['flag_name'],
            is_enabled=data['is_enabled'],
            description=data.get('description'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )

    def __str__(self) -> str:
        """Représentation textuelle du feature flag."""
        status = "ACTIVÉ" if self.is_enabled else "DÉSACTIVÉ"
        return f"FeatureFlag({self.flag_name}: {status})"

    def __repr__(self) -> str:
        """Représentation détaillée pour debug."""
        return (f"FeatureFlag(id={self.id}, flag_name='{self.flag_name}', "
                f"is_enabled={self.is_enabled}, description='{self.description}')")
