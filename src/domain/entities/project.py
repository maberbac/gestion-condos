"""
Entité Project - Représente un projet de condominium complet.

Cette entité encapsule les informations d'un projet de condominium incluant
la création automatique d'unités selon les spécifications du projet.

[Architecture Hexagonale]
Cette entité fait partie du domaine métier (core) et ne dépend d'aucun adapter
ou port. Elle gère la logique métier de création automatique d'unités.
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import random
from enum import Enum

from .unit import Unit, UnitType, UnitStatus

class ProjectStatus(Enum):
    """Énumération des statuts de projet."""
    PLANNING = "PLANNING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass
class Project:
    """
    Entité représentant un projet de condominium complet.
    
    Cette classe gère un projet de condominium avec ses métadonnées
    et la création automatique d'unités de condo selon les spécifications.
    """
    
    # Attributs de base du projet
    name: str
    address: str
    total_area: float
    construction_year: int
    unit_count: int
    constructor: str
    
    # Attributs optionnels avec valeurs par défaut
    project_id: str = field(default="")
    status: ProjectStatus = field(default=ProjectStatus.PLANNING)
    creation_date: datetime = field(default_factory=datetime.now)
    units: List[Unit] = field(default_factory=list)
    
    def __post_init__(self):
        """Validation des données après création de l'instance."""
        if not self.name or not self.name.strip():
            raise ValueError("Le nom du projet ne peut pas être vide")
        
        # Générer automatiquement un project_id si vide
        if not self.project_id or not self.project_id.strip():
            import uuid
            self.project_id = str(uuid.uuid4())[:8]  # ID court de 8 caractères
        
        if not self.address or not self.address.strip():
            raise ValueError("L'adresse du projet ne peut pas être vide")
        
        if self.total_area <= 0:
            raise ValueError("La superficie totale doit être positive")
        
        if self.construction_year < 1900 or self.construction_year > datetime.now().year + 10:
            raise ValueError("L'année de construction doit être réaliste")
        
        if self.unit_count <= 0:
            raise ValueError("Le nombre d'unités doit être positif")
        
        if not self.constructor or not self.constructor.strip():
            raise ValueError("Le constructeur ne peut pas être vide")
        
        logger.debug(f"Projet validé: {self.name} avec {self.unit_count} unités")
    
    def __str__(self) -> str:
        """Représentation lisible du projet."""
        return f"Projet '{self.name}' - {self.unit_count} unités - {self.constructor}"
    
    def __repr__(self) -> str:
        """Représentation technique du projet."""
        return (f"Project(name='{self.name}', address='{self.address}', "
                f"unit_count={self.unit_count}, constructor='{self.constructor}')")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit le projet en dictionnaire pour sérialisation.
        
        Returns:
            Dict: Représentation en dictionnaire du projet
        """
        return {
            'project_id': self.project_id,
            'name': self.name,
            'address': self.address,
            'total_area': self.total_area,
            'construction_year': self.construction_year,
            'unit_count': self.unit_count,
            'constructor': self.constructor,
            'creation_date': self.creation_date.isoformat(),
            'units': [unit.to_dict() for unit in self.units] if self.units else []
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """
        Crée un projet à partir d'un dictionnaire.
        
        Args:
            data: Dictionnaire contenant les données du projet
            
        Returns:
            Project: Instance du projet
        """
        # Adapter les noms d'attributs des données existantes
        name = data.get('name', '')
        address = data.get('address', '')
        
        # total_area peut venir de building_area ou land_area selon les données
        total_area = data.get('total_area', data.get('building_area', data.get('land_area', 1000.0)))
        
        construction_year = data.get('construction_year', 2020)
        
        # unit_count peut être total_units dans les données
        unit_count = data.get('unit_count', data.get('total_units', 1))
        
        # constructor peut être builder_name dans les données
        constructor = data.get('constructor', data.get('builder_name', 'Constructeur Inconnu'))
        
        # project_id depuis les données ou généré
        project_id = data.get('project_id', '')
        
        project = cls(
            name=name,
            address=address,
            total_area=total_area,
            construction_year=construction_year,
            unit_count=unit_count,
            constructor=constructor,
            project_id=project_id,
            creation_date=datetime.fromisoformat(data['creation_date']) if data.get('creation_date') else datetime.now()
        )
        
        # Restaurer les unités si présentes
        if 'units' in data and data['units']:
            from .unit import Unit
            try:
                project.units = [Unit.from_dict(unit_data) for unit_data in data['units']]
            except Exception as e:
                logger.warning(f"Impossible de charger les unités pour {name}: {e}")
                project.units = []
        
        return project

    def get_project_statistics(self) -> Dict[str, Any]:
        """
        Calcule et retourne les statistiques du projet.
        
        Returns:
            Dict: Statistiques détaillées du projet
        """
        total_units = len(self.units)
        if total_units == 0:
            return {
                'total_units': 0,
                'sold_units': 0,
                'available_units': 0,
                'reserved_units': 0,
                'completion_percentage': 0.0,
                'total_value': 0.0,
                'average_price': 0.0,
                'units_by_type': {},
                'revenue': 0.0
            }
        
        # Compter par statut
        sold_count = sum(1 for unit in self.units if unit.status == UnitStatus.SOLD)
        available_count = sum(1 for unit in self.units if unit.status == UnitStatus.AVAILABLE)
        reserved_count = sum(1 for unit in self.units if unit.status == UnitStatus.RESERVED)
        
        # Calculs financiers
        total_value = sum(unit.estimated_price for unit in self.units if unit.estimated_price)
        revenue = sum(unit.estimated_price for unit in self.units if unit.status == UnitStatus.SOLD and unit.estimated_price)
        average_price = total_value / total_units if total_units > 0 else 0.0
        
        # Répartition par type
        units_by_type = {}
        for unit in self.units:
            unit_type = unit.unit_type.value if hasattr(unit.unit_type, 'value') else str(unit.unit_type)
            units_by_type[unit_type] = units_by_type.get(unit_type, 0) + 1
        
        # Pourcentage de completion (unités vendues)
        completion_percentage = (sold_count / total_units * 100) if total_units > 0 else 0.0
        
        return {
            'total_units': total_units,
            'sold_units': sold_count,
            'available_units': available_count,
            'reserved_units': reserved_count,
            'completion_percentage': completion_percentage,
            'occupancy_rate': completion_percentage,  # Alias pour occupancy_rate
            'total_value': total_value,
            'average_price': average_price,
            'units_by_type': units_by_type,
            'revenue': revenue
        }

    def generate_units(self, unit_count: int = None, blank_units: bool = False) -> List[Unit]:
        """
        Génère automatiquement les unités pour le projet.
        
        Args:
            unit_count: Nombre d'unités à générer (optionnel, utilise self.unit_count par défaut)
            blank_units: Si True, crée des unités vierges sans numéros ni attributions automatiques
            
        Returns:
            List[Condo]: Liste des unités générées
        """
        if unit_count is None:
            unit_count = self.unit_count
            
        units = []
        
        if blank_units:
            # Créer des unités vierges sans attribution automatique
            for i in range(unit_count):
                unit = Unit(
                    unit_number="",  # Pas de numéro automatique
                    project_id=self.project_id,
                    area=0,  # Superficie à définir par le gestionnaire
                    unit_type=UnitType.RESIDENTIAL,  # Type par défaut
                    status=UnitStatus.AVAILABLE,  # Statut disponible
                    estimated_price=0,  # Prix à définir
                    monthly_fees_base=0,  # Frais à définir
                    owner_name="Disponible"  # Pas d'attribution automatique
                )
                units.append(unit)
                
            # Ajouter les unités vierges à la liste du projet
            self.units.extend(units)
            logger.info(f"Généré {len(units)} unités vierges pour le projet {self.name}")
            return units
        
        # Code existant pour la génération automatique complète
        # Types de condos et leurs probabilités
        condo_types = [
            (UnitType.RESIDENTIAL, 0.8),
            (UnitType.COMMERCIAL, 0.15),
            (UnitType.PARKING, 0.05)
        ]
        
        # Répartition typique des superficies par type
        type_areas = {
            UnitType.RESIDENTIAL: (400, 1600),
            UnitType.COMMERCIAL: (800, 2000),
            UnitType.PARKING: (300, 400),      # Minimum 300 pour respect des contraintes métier
            UnitType.STORAGE: (300, 400)       # Minimum 300 pour respect des contraintes métier
        }
        
        # Prix au pied carré basé sur l'année de construction et la localisation
        base_price_per_sqft = 350
        if self.construction_year > 2015:
            base_price_per_sqft += 50
        if self.construction_year > 2020:
            base_price_per_sqft += 30
            
        logger.debug(f"Génération de {unit_count} unités pour {self.name}")
        
        for i in range(unit_count):
            # Numérotation des unités (A-101, B-205, etc.)
            floor = (i // 4) + 1
            unit_on_floor = (i % 4) + 1
            building_section = chr(65 + (i // 100))  # A, B, C, etc. par tranche de 100
            unit_number = f"{building_section}-{floor:01d}{unit_on_floor:02d}"
            
            # Sélection du type selon les probabilités
            rand = random.random()
            cumulative = 0
            selected_type = UnitType.RESIDENTIAL  # défaut
            for condo_type, probability in condo_types:
                cumulative += probability
                if rand <= cumulative:
                    selected_type = condo_type
                    break
            
            # Superficie basée sur la répartition du total
            # Calculer la superficie moyenne cible
            target_avg_area = self.total_area / unit_count
            
            # Ajuster selon le type d'unité avec des variations plus modérées
            type_multipliers = {
                UnitType.RESIDENTIAL: 1.0,    # Taille standard
                UnitType.COMMERCIAL: 1.2,     # Légèrement plus grand
                UnitType.PARKING: 0.8,        # Plus petit
                UnitType.STORAGE: 0.7         # Plus petit
            }
            
            base_area = target_avg_area * type_multipliers[selected_type]
            # Variation aléatoire de ±15% pour rester dans les limites du test
            variation = random.uniform(0.85, 1.15)
            square_feet = int(base_area * variation)
            
            # S'assurer du minimum de 300 pour les contraintes métier
            square_feet = max(square_feet, 300)
            
            # Prix avec variation aléatoire ±15%
            base_price = square_feet * base_price_per_sqft
            price_variation = random.uniform(0.85, 1.15)
            price = round(base_price * price_variation, 2)
            
            # Statut initial (toutes disponibles par défaut)
            status = UnitStatus.AVAILABLE
            
            # Créer l'unité
            unit = Unit(
                unit_number=unit_number,
                project_id=self.project_id,
                area=square_feet,
                unit_type=selected_type,
                status=status,
                estimated_price=price,
                monthly_fees_base=square_feet * 0.45  # Frais de base
            )
            
            units.append(unit)
        
        # Ajouter les unités générées à la liste du projet
        self.units.extend(units)
        
        logger.info(f"Généré {len(units)} unités pour le projet {self.name}")
        return units

    def add_units(self, count: int) -> List[Unit]:
        """
        Ajoute des unités supplémentaires au projet.
        
        Args:
            count: Nombre d'unités à ajouter
            
        Returns:
            List[Condo]: Liste des nouvelles unités ajoutées
        """
        if count <= 0:
            raise ValueError("Le nombre d'unités à ajouter doit être positif")
        
        # Mettre à jour le nombre total d'unités
        self.unit_count += count
        
        # Générer seulement les nouvelles unités (pas toutes les unités)
        current_unit_count = len(self.units)
        added_units = []
        
        # Générer 'count' nouvelles unités en partant du numéro suivant
        next_unit_number = current_unit_count + 1
        for i in range(count):
            unit_index = next_unit_number + i - 1  # Index 0-based pour la génération
            
            # Utiliser la même logique que generate_units mais pour une seule unité
            floor = (unit_index // 4) + 1
            unit_on_floor = (unit_index % 4) + 1
            unit_number = f"A-{floor}{unit_on_floor:02d}"
            
            # Types d'appartements avec distribution réaliste
            apartment_types = [
                (UnitType.RESIDENTIAL, 400, 1600, 180000, 850000),
                (UnitType.COMMERCIAL, 800, 2000, 280000, 950000),
                (UnitType.PARKING, 200, 400, 50000, 80000),
                (UnitType.STORAGE, 100, 300, 30000, 60000)
            ]
            
            # Sélection du type (distribution pondérée réaliste)
            type_weights = [0.75, 0.15, 0.08, 0.02]  # 75% résidentiel, 15% commercial, 8% parking, 2% entreposage
            selected_type_info = random.choices(apartment_types, weights=type_weights, k=1)[0]
            selected_type, min_sqft, max_sqft, min_price, max_price = selected_type_info
            
            # Génération des caractéristiques
            square_feet = random.randint(min_sqft, max_sqft)
            price = random.randint(min_price, max_price)
            status = UnitStatus.AVAILABLE
            
            unit = Unit(
                unit_number=unit_number,
                project_id=self.project_id,
                area=square_feet,
                unit_type=selected_type,
                status=status,
                estimated_price=price,
                monthly_fees_base=square_feet * 0.45
            )
            
            added_units.append(unit)
        
        # Ajouter les nouvelles unités à la liste existante
        self.units.extend(added_units)
        
        logger.info(f"Ajouté {count} unités au projet {self.name}. Total: {len(self.units)} unités")
        return added_units

    def get_average_unit_area(self) -> float:
        """
        Calcule la superficie moyenne par unité.
        
        Returns:
            float: Superficie moyenne en pieds carrés
        """
        if not self.units:
            return 0.0
        
        total_area = sum(unit.area for unit in self.units)
        return total_area / len(self.units)

