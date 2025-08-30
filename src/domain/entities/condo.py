"""
Entité Condo - Entité métier fondamentale.

Cette entité représente une unité de condominium dans le système de gestion.
Elle encapsule les propriétés et comportements essentiels d'une unité,
indépendamment de toute infrastructure ou technologie externe.

[Architecture Hexagonale]
Cette entité fait partie du domaine métier (core) et ne dépend d'aucun adapter
ou port. Elle peut être testée de manière isolée et réutilisée dans différents
contextes (MVP actuel, extensions futures).
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)


from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum


class CondoStatus(Enum):
    """Statut d'une unité de condo."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SOLD = "sold"
    MAINTENANCE = "maintenance"


class CondoType(Enum):
    """Type d'unité de condo selon la fonction."""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    PARKING = "parking"
    STORAGE = "storage"


@dataclass
class Condo:
    """
    Entité représentant une unité de condominium.
    
    Cette entité encapsule toute la logique métier liée à une unité
    de condo, incluant les calculs de frais, validations, et règles
    de gestion spécifiques.
    
    Attributs:
        unit_number: Numéro unique de l'unité (ex: "A-101", "B-205")
        owner_name: Nom du propriétaire actuel
        square_feet: Superficie en pieds carrés
        condo_type: Type d'unité (résidentiel, commercial, etc.)
        status: Statut actuel de l'unité
        purchase_date: Date d'achat (optionnel)
        monthly_fees_base: Frais de base mensuels personnalisés (optionnel)
        building_name: Nom du projet/bâtiment (pour compatibilité projets)
        is_sold: Indicateur de vente (pour statistiques projets)
    """
    
    unit_number: str
    square_feet: float
    condo_type: CondoType = CondoType.RESIDENTIAL
    status: CondoStatus = CondoStatus.ACTIVE
    owner_name: str = "Disponible"
    floor: int = 1
    price: float = 0.0
    purchase_date: Optional[datetime] = None
    monthly_fees_base: Optional[Decimal] = None
    building_name: Optional[str] = None
    is_sold: bool = False
    address: Optional[str] = None
    construction_year: Optional[int] = None
    
    # Constantes métier - Peuvent être configurées via infrastructure
    RATE_PER_SQFT_RESIDENTIAL = Decimal('0.45')   # 0.45$ par pied carré pour résidentiel
    RATE_PER_SQFT_COMMERCIAL = Decimal('0.60')    # 0.60$ par pied carré pour commercial
    RATE_PER_SQFT_PARKING = Decimal('0.15')       # 0.15$ par pied carré pour parking  
    RATE_PER_SQFT_STORAGE = Decimal('0.25')       # 0.25$ par pied carré pour entreposage
    
    def __post_init__(self):
        """Validation après initialisation."""
        self._validate_unit_number()
        self._validate_square_feet()
        self._validate_owner_name()
    
    def _validate_unit_number(self) -> None:
        """Valide le format du numéro d'unité."""
        if not self.unit_number or not self.unit_number.strip():
            raise ValueError("Le numéro d'unité ne peut pas être vide")
        
        if len(self.unit_number) > 10:
            raise ValueError("Le numéro d'unité ne peut pas dépasser 10 caractères")
    
    def _validate_square_feet(self) -> None:
        """Valide la superficie."""
        if self.square_feet <= 0:
            raise ValueError("La superficie doit être positive")
        
        if self.square_feet > 10000:  # Limite raisonnable
            raise ValueError("La superficie semble anormalement grande")
    
    def _validate_owner_name(self) -> None:
        """Valide le nom du propriétaire."""
        if not self.owner_name or not self.owner_name.strip():
            raise ValueError("Le nom du propriétaire ne peut pas être vide")
    
    def calculate_monthly_fees(self) -> Decimal:
        """
        Calcule les frais mensuels de copropriété pour cette unité.
        
        Logique métier:
        - Si des frais de base personnalisés sont définis, les utiliser
        - Sinon, calculer selon le type d'unité et la superficie
        - Appliquer les taux standards par type d'unité
        
        Returns:
            Decimal: Montant des frais mensuels en dollars
        """
        if self.monthly_fees_base is not None:
            return self.monthly_fees_base
        
        rate_per_sqft = self._get_rate_by_type()
        base_fees = Decimal(str(self.square_feet)) * rate_per_sqft
        
        # Arrondir à 2 décimales (dollars et cents)
        return base_fees.quantize(Decimal('0.01'))
    
    def _get_rate_by_type(self) -> Decimal:
        """Retourne le taux par pied carré selon le type d'unité."""
        rate_mapping = {
            CondoType.RESIDENTIAL: self.RATE_PER_SQFT_RESIDENTIAL,
            CondoType.COMMERCIAL: self.RATE_PER_SQFT_COMMERCIAL,
            CondoType.PARKING: self.RATE_PER_SQFT_PARKING,
            CondoType.STORAGE: self.RATE_PER_SQFT_STORAGE,
        }
        return rate_mapping.get(self.condo_type, self.RATE_PER_SQFT_RESIDENTIAL)
    
    def calculate_annual_fees(self) -> Decimal:
        """Calcule les frais annuels de copropriété."""
        return self.calculate_monthly_fees() * 12
    
    def is_active(self) -> bool:
        """Vérifie si l'unité est active et génère des frais."""
        return self.status == CondoStatus.ACTIVE
    
    def is_commercial(self) -> bool:
        """Vérifie si l'unité est de type commercial."""
        return self.condo_type == CondoType.COMMERCIAL
    
    def get_ownership_duration_years(self) -> Optional[float]:
        """
        Calcule la durée de possession en années.
        
        Returns:
            Optional[float]: Nombre d'années de possession, ou None si date inconnue
        """
        if self.purchase_date is None:
            return None
        
        duration = datetime.now() - self.purchase_date
        return duration.days / 365.25  # Inclut les années bissextiles
    
    def set_maintenance_mode(self) -> None:
        """Met l'unité en mode maintenance (frais suspendus)."""
        self.status = CondoStatus.MAINTENANCE
    
    def reactivate(self) -> None:
        """Réactive l'unité après maintenance."""
        self.status = CondoStatus.ACTIVE
    
    def transfer_ownership(self, new_owner: str, transfer_date: datetime = None) -> None:
        """
        Transfère la propriété de l'unité.
        
        Args:
            new_owner: Nom du nouveau propriétaire
            transfer_date: Date du transfert (par défaut: maintenant)
        """
        if not new_owner or not new_owner.strip():
            raise ValueError("Le nom du nouveau propriétaire ne peut pas être vide")
        
        old_owner = self.owner_name
        self.owner_name = new_owner.strip()
        self.purchase_date = transfer_date or datetime.now()
        self.status = CondoStatus.SOLD
        self.is_sold = True
        
        logger.info(f"Transfert de propriété - Unité {self.unit_number}: {old_owner} → {new_owner}")
    
    def to_dict(self) -> dict:
        """
        Convertit l'entité en dictionnaire pour sérialisation.
        
        Utile pour les adapters qui doivent sauvegarder ou transmettre
        les données vers des systèmes externes.
        """
        return {
            'unit_number': self.unit_number,
            'owner_name': self.owner_name,
            'square_feet': self.square_feet,
            'condo_type': self.condo_type.value,
            'status': self.status.value,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'monthly_fees_base': str(self.monthly_fees_base) if self.monthly_fees_base else None,
            'calculated_monthly_fees': str(self.calculate_monthly_fees())
        }
    
    def is_owned(self) -> bool:
        """
        Vérifie si l'unité a un propriétaire défini (n'est pas disponible).
        
        Returns:
            bool: True si l'unité a un propriétaire
        """
        return self.owner_name.strip() not in ['', 'Disponible', 'À vendre', 'Vacant']
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Condo':
        """
        Crée une instance Condo à partir d'un dictionnaire.
        
        Utile pour les adapters qui lisent des données depuis
        des sources externes (fichiers JSON, APIs, etc.)
        """
        return cls(
            unit_number=data['unit_number'],
            owner_name=data['owner_name'],
            square_feet=float(data['square_feet']),
            condo_type=CondoType(data.get('condo_type', 'residential')),
            status=CondoStatus(data.get('status', 'active')),
            purchase_date=datetime.fromisoformat(data['purchase_date']) if data.get('purchase_date') else None,
            monthly_fees_base=Decimal(data['monthly_fees_base']) if data.get('monthly_fees_base') else None,
            building_name=data.get('building_name'),
            is_sold=data.get('is_sold', False),
            address=data.get('address'),
            construction_year=data.get('construction_year')
        )
    
    def __str__(self) -> str:
        """Représentation lisible de l'unité."""
        return f"Condo {self.unit_number} - {self.owner_name} ({self.square_feet} sq ft)"
    
    def __repr__(self) -> str:
        """Représentation technique de l'unité."""
        return (f"Condo(unit_number='{self.unit_number}', owner_name='{self.owner_name}', "
                f"square_feet={self.square_feet}, condo_type={self.condo_type}, "
                f"status={self.status})")


# Exemple d'utilisation et validation de l'entité
if __name__ == "__main__":
    # Créer une unité résidentielle standard
    condo = Condo(
        unit_number="A-101",
        owner_name="Jean Dupont",
        square_feet=850.0,
        condo_type=CondoType.RESIDENTIAL
    )
    
    logger.info(f"Unité créée: {condo}")
    logger.info(f"Frais mensuels: {condo.calculate_monthly_fees()}$")
    logger.info(f"Frais annuels: {condo.calculate_annual_fees()}$")
    
    # Démonstration de la validation
    try:
        invalid_condo = Condo("", "Propriétaire", -100)
    except ValueError as e:
        logger.info(f"Validation échouée comme attendu: {e}")
    
    # Démonstration sérialisation
    condo_dict = condo.to_dict()
    logger.info(f"Sérialisé: {condo_dict}")
    
    # Démonstration désérialisation
    restored_condo = Condo.from_dict(condo_dict)
    logger.info(f"Restauré: {restored_condo}")
