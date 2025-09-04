"""
Entité Unit - Entité métier représentant une unité dans un projet.

Cette entité représente une unité individuelle dans un projet de condominium.
Elle encapsule les propriétés et comportements essentiels d'une unité,
indépendamment de toute infrastructure ou technologie externe.

[Architecture Hexagonale]
Cette entité fait partie du domaine métier (core) et ne dépend d'aucun adapter
ou port. Elle peut être testée de manière isolée et réutilisée dans différents
contextes.
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum


class UnitStatus(Enum):
    """Statut d'une unité."""
    AVAILABLE = "available"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"
    NONE = "none" # Utilisé principalement pour indiqué que c'est occupé par le propriétaire


class UnitType(Enum):
    """Type d'unité selon la fonction."""
    RESIDENTIAL = "RESIDENTIAL"
    COMMERCIAL = "COMMERCIAL"
    PARKING = "PARKING"
    STORAGE = "STORAGE"


@dataclass
class Unit:
    """
    Entité représentant une unité dans un projet de condominium.
    
    Cette entité encapsule toute la logique métier liée à une unité,
    incluant les calculs de frais, validations, et règles
    de gestion spécifiques.
    
    Attributs:
        id: ID de base de données SQLite (auto-incrémenté)
        unit_number: Numéro unique de l'unité (ex: 'A-101', 'P-001')
        project_id: ID du projet auquel appartient cette unité
        area: Superficie en pieds carrés
        unit_type: Type d'unité (résidentiel, commercial, parking, etc.)
        status: Statut actuel (disponible, vendu, réservé, maintenance)
        estimated_price: Prix estimé de l'unité
        owner_name: Nom du propriétaire (None si disponible)
        calculated_monthly_fees: Frais mensuels calculés (peut être JSON)
        created_at: Date de création
        updated_at: Date de dernière modification
    """
    
    # Attributs obligatoires
    unit_number: str
    project_id: str
    area: float
    unit_type: UnitType
    status: UnitStatus
    
    # Attributs optionnels
    id: Optional[int] = None  # ID de base de données SQLite
    estimated_price: Optional[float] = None
    owner_name: Optional[str] = None
    calculated_monthly_fees: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """Validation et initialisation après création."""
        # Permettre les numéros d'unité vides pour les unités vierges en configuration
        # Dans ce cas, le gestionnaire assignera le numéro plus tard
        if self.unit_number is None:
            raise ValueError("Le numéro d'unité ne peut pas être None")
            
        # Chaîne vide autorisée pour les unités vierges
        if self.unit_number == "":
            pass  # OK pour unités vierges
        elif not self.unit_number.strip():
            raise ValueError("Le numéro d'unité ne peut pas être composé uniquement d'espaces")
        
        if not self.project_id or not self.project_id.strip():
            raise ValueError("L'ID du projet ne peut pas être vide")
            
        # Permettre superficie 0 pour les unités vierges en configuration
        if self.area == 0:
            pass  # OK pour unités vierges
        elif self.area < 0:
            raise ValueError("La superficie ne peut pas être négative")
            
        # Initialiser les dates si nécessaire
        now = datetime.now()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
    
    def calculate_monthly_fees(self) -> float:
        """
        Calcule les frais mensuels pour cette unité.
        
        Returns:
            float: Frais mensuels calculés
        """
        # Calcul par défaut basé sur le type et la superficie
        rate_per_sqft = {
            UnitType.RESIDENTIAL: 0.45,
            UnitType.COMMERCIAL: 0.60,
            UnitType.PARKING: 0.375,
            UnitType.STORAGE: 0.30
        }
        
        base_rate = rate_per_sqft.get(self.unit_type, 0.45)
        return float(self.area * base_rate)
    
    @property
    def monthly_fees(self) -> float:
        """
        Propriété pour accéder aux frais mensuels.
        Utilise la valeur stockée (calculated_monthly_fees) si disponible,
        sinon utilise le calcul automatique.
        
        Returns:
            float: Frais mensuels pour cette unité
        """
        # Priorité à la valeur stockée
        if self.calculated_monthly_fees is not None:
            try:
                return float(self.calculated_monthly_fees)
            except (ValueError, TypeError):
                # Si conversion échoue, utiliser le calcul comme fallback
                pass
        
        # Fallback sur le calcul automatique
        return self.calculate_monthly_fees()
    
    @property
    def square_feet(self) -> float:
        """
        Propriété pour accéder à la superficie (alias pour area).
        
        Returns:
            float: Superficie en pieds carrés
        """
        return self.area
    
    @property
    def type_icon(self) -> str:
        """
        Icône correspondant au type d'unité.
        
        Returns:
            str: Emoji représentant le type d'unité
        """
        icons = {
            UnitType.RESIDENTIAL: "🏠",
            UnitType.COMMERCIAL: "🏢",
            UnitType.PARKING: "🚗",
            UnitType.STORAGE: "📦"
        }
        return icons.get(self.unit_type, "🏠")
    
    @property
    def status_icon(self) -> str:
        """
        Icône correspondant au statut de l'unité.
        
        Returns:
            str: Emoji représentant le statut
        """
        icons = {
            UnitStatus.AVAILABLE: "✅",
            UnitStatus.RESERVED: "⏳",
            UnitStatus.MAINTENANCE: "🔧",
            UnitStatus.INACTIVE: "❌",           # AJOUT: Icône pour statut inactif
            UnitStatus.NONE: "🏠"
        }
        return icons.get(self.status, "❓")
    
    def is_available(self) -> bool:
        """Vérifie si l'unité est disponible."""
        return self.status == UnitStatus.AVAILABLE

        
        logger.info(f"Unité {self.unit_number} vendue à {self.owner_name}")
    
    def transfer_ownership(self, owner_name: str, purchase_date: datetime = None) -> None:
        """
        Transfère la propriété de l'unité.
        
        Args:
            owner_name: Nom du nouveau propriétaire
            purchase_date: Date d'achat (par défaut maintenant)
        """
        if purchase_date is None:
            purchase_date = datetime.now()
            
        self.owner_name = owner_name
        self.purchase_date = purchase_date
        self.status = UnitStatus.AVAILABLE  # Status reste available
        self.updated_at = datetime.now()
        
        logger.debug(f"Unité {self.unit_number} transférée à {owner_name}")
    
    def make_available(self) -> None:
        """Rend l'unité disponible."""
        self.owner_name = None
        self.status = UnitStatus.AVAILABLE
        self.purchase_date = None
        self.updated_at = datetime.now()
        
        logger.info(f"Unité {self.unit_number} rendue disponible")
    
    def reserve(self) -> None:
        """Réserve l'unité."""
        if self.status != UnitStatus.AVAILABLE:
            raise ValueError("Seules les unités disponibles peuvent être réservées")
        
        self.status = UnitStatus.RESERVED
        self.updated_at = datetime.now()
        
        logger.info(f"Unité {self.unit_number} réservée")
    
    def set_maintenance(self) -> None:
        """Met l'unité en maintenance."""
        self.status = UnitStatus.MAINTENANCE
        self.updated_at = datetime.now()
        
        logger.info(f"Unité {self.unit_number} mise en maintenance")
    
    def update_area(self, new_area: float) -> None:
        """
        Met à jour la superficie de l'unité.
        
        Args:
            new_area: Nouvelle superficie
        """
        if new_area <= 0:
            raise ValueError("La superficie doit être positive")
        
        old_area = self.area
        self.area = new_area
        self.updated_at = datetime.now()
        
        logger.info(f"Superficie unité {self.unit_number} mise à jour: {old_area} -> {new_area} pi²")
    
    def get_display_info(self) -> dict:
        """
        Retourne les informations d'affichage pour l'interface utilisateur.
        
        Returns:
            dict: Informations formatées pour l'affichage
        """
        return {
            'unit_number': self.unit_number,
            'type': self.unit_type.value.title(),
            'area': f"{self.area:.0f} pi²",
            'status': self.status.value.title(),
            'owner': self.owner_name or "Disponible",
            'monthly_fees': f"${self.calculate_monthly_fees():.2f}",
            'is_available': self.is_available()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Unit':
        """
        Crée une instance Unit à partir d'un dictionnaire.
        
        Args:
            data: Dictionnaire contenant les données de l'unité
            
        Returns:
            Unit: Instance créée
        """
        # Conversion des types enum
        unit_type = data.get('unit_type')
        if isinstance(unit_type, str):
            unit_type = UnitType(unit_type.upper())
        
        status = data.get('status')
        if isinstance(status, str):
            status = UnitStatus(status.lower())
        
        # Conversion des dates
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        
        updated_at = data.get('updated_at')
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        
        return cls(
            id=data.get('id'),
            unit_number=data['unit_number'],
            project_id=data['project_id'],
            area=float(data['area']),
            unit_type=unit_type,
            status=status,
            estimated_price=data.get('estimated_price'),
            owner_name=data.get('owner_name'),
            calculated_monthly_fees=data.get('calculated_monthly_fees'),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def to_dict(self) -> dict:
        """
        Convertit l'unité en dictionnaire.
        
        Returns:
            dict: Représentation en dictionnaire
        """
        return {
            'id': self.id,
            'unit_number': self.unit_number,
            'project_id': self.project_id,
            'area': self.area,
            'unit_type': self.unit_type.value,
            'status': self.status.value,
            'estimated_price': self.estimated_price,
            'owner_name': self.owner_name,
            'calculated_monthly_fees': self.calculated_monthly_fees,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
