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
    SOLD = "sold"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"


class UnitType(Enum):
    """Type d'unité selon la fonction."""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    PARKING = "parking"
    STORAGE = "storage"


@dataclass
class Unit:
    """
    Entité représentant une unité dans un projet de condominium.
    
    Cette entité encapsule toute la logique métier liée à une unité,
    incluant les calculs de frais, validations, et règles
    de gestion spécifiques.
    
    Attributs:
        unit_number: Numéro unique de l'unité (ex: 'A-101', 'P-001')
        project_id: ID du projet auquel appartient cette unité
        area: Superficie en pieds carrés
        unit_type: Type d'unité (résidentiel, commercial, parking, etc.)
        status: Statut actuel (disponible, vendu, réservé, maintenance)
        estimated_price: Prix estimé de l'unité
        owner_name: Nom du propriétaire (None si disponible)
        purchase_date: Date d'achat (None si pas vendue)
        monthly_fees_base: Frais mensuels de base
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
    estimated_price: Optional[float] = None
    owner_name: Optional[str] = None
    purchase_date: Optional[datetime] = None
    monthly_fees_base: Optional[float] = None
    calculated_monthly_fees: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """Validation et initialisation après création."""
        if not self.unit_number or not self.unit_number.strip():
            raise ValueError("Le numéro d'unité ne peut pas être vide")
        
        if not self.project_id or not self.project_id.strip():
            raise ValueError("L'ID du projet ne peut pas être vide")
            
        if self.area <= 0:
            raise ValueError("La superficie doit être positive")
            
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
        if self.monthly_fees_base:
            return float(self.monthly_fees_base)
        
        # Calcul par défaut basé sur le type et la superficie
        rate_per_sqft = {
            UnitType.RESIDENTIAL: 0.45,
            UnitType.COMMERCIAL: 0.60,
            UnitType.PARKING: 0.375,
            UnitType.STORAGE: 0.30
        }
        
        base_rate = rate_per_sqft.get(self.unit_type, 0.45)
        return float(self.area * base_rate)
    
    def is_available(self) -> bool:
        """Vérifie si l'unité est disponible."""
        return self.status == UnitStatus.AVAILABLE
    
    def is_sold(self) -> bool:
        """Vérifie si l'unité est vendue."""
        return self.status == UnitStatus.SOLD
    
    def sell_to(self, owner_name: str, purchase_date: datetime = None) -> None:
        """
        Vend l'unité à un propriétaire.
        
        Args:
            owner_name: Nom du nouveau propriétaire
            purchase_date: Date d'achat (par défaut maintenant)
        """
        if not owner_name or not owner_name.strip():
            raise ValueError("Le nom du propriétaire ne peut pas être vide")
        
        self.owner_name = owner_name.strip()
        self.status = UnitStatus.SOLD
        self.purchase_date = purchase_date or datetime.now()
        self.updated_at = datetime.now()
        
        logger.info(f"Unité {self.unit_number} vendue à {self.owner_name}")
    
    def transfer_ownership(self, owner_name: str, purchase_date: datetime = None) -> None:
        """
        Transfère la propriété de l'unité (alias pour sell_to).
        
        Args:
            owner_name: Nom du nouveau propriétaire
            purchase_date: Date d'achat (par défaut maintenant)
        """
        self.sell_to(owner_name, purchase_date)
    
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
    
    def update_monthly_fees(self, new_fees: float) -> None:
        """
        Met à jour les frais mensuels de base.
        
        Args:
            new_fees: Nouveaux frais mensuels
        """
        if new_fees < 0:
            raise ValueError("Les frais mensuels ne peuvent pas être négatifs")
        
        old_fees = self.monthly_fees_base
        self.monthly_fees_base = new_fees
        self.updated_at = datetime.now()
        
        logger.info(f"Frais mensuels unité {self.unit_number} mis à jour: {old_fees} -> {new_fees}$")
    
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
            'is_available': self.is_available(),
            'is_sold': self.is_sold()
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
            unit_type = UnitType(unit_type.lower())
        
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
        
        purchase_date = data.get('purchase_date')
        if isinstance(purchase_date, str):
            purchase_date = datetime.fromisoformat(purchase_date.replace('Z', '+00:00'))
        
        return cls(
            unit_number=data['unit_number'],
            project_id=data['project_id'],
            area=float(data['area']),
            unit_type=unit_type,
            status=status,
            estimated_price=data.get('estimated_price'),
            owner_name=data.get('owner_name'),
            purchase_date=purchase_date,
            monthly_fees_base=data.get('monthly_fees_base'),
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
            'unit_number': self.unit_number,
            'project_id': self.project_id,
            'area': self.area,
            'unit_type': self.unit_type.value,
            'status': self.status.value,
            'estimated_price': self.estimated_price,
            'owner_name': self.owner_name,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'monthly_fees_base': self.monthly_fees_base,
            'calculated_monthly_fees': self.calculated_monthly_fees,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
