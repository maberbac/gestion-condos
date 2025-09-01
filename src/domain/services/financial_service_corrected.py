"""
Service Financier - Logique métier pour calculs financiers.

[CONCEPT TECHNIQUE: Programmation fonctionnelle]
Ce service démontre l'utilisation des paradigmes fonctionnels en Python :
- Fonctions pures sans effets de bord
- Utilisation de map(), filter(), reduce()
- Composition de fonctions
- Immutabilité des données
- Transformation de données par pipelines fonctionnels

[CONCEPT TECHNIQUE: Analyse de données financières]
Implémentation de fonctions d'analyse et de calcul financier :
- Calculs de frais de copropriété multi-méthodes
- Agrégations de données financières
- Statistiques de revenus et dépenses
- Projections et comparaisons financières
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

from decimal import Decimal
from typing import List, Dict, Tuple, Callable, Optional
from functools import reduce
from dataclasses import dataclass
from enum import Enum

from src.domain.entities.unit import Unit, UnitType, UnitStatus


class FeeCalculationMethod(Enum):
    """Méthodes de calcul des frais de copropriété."""
    STANDARD = "standard"           # Calcul standard par superficie
    PROGRESSIVE = "progressive"     # Tarif progressif selon la taille
    FLAT_RATE = "flat_rate"        # Tarif fixe par unité
    CUSTOM = "custom"              # Calcul personnalisé


@dataclass(frozen=True)  # Immutable pour approche fonctionnelle
class FinancialRecord:
    """Enregistrement financier immutable d'une unité."""
    unit_number: str
    monthly_amount: Decimal
    calculation_details: Dict[str, Decimal]
    unit_type: UnitType
    area: Decimal


@dataclass(frozen=True)
class FinancialSummary:
    """Résumé financier global immutable."""
    total_monthly_income: Decimal
    average_fees_per_unit: Decimal
    total_units: int
    active_units: int
    breakdown_by_type: Dict[UnitType, Decimal]
    

class FinancialService:
    """
    Service de calculs financiers avec approche fonctionnelle.
    
    [CONCEPT: Programmation fonctionnelle]
    Toutes les méthodes de cette classe sont des fonctions pures qui :
    - Ne modifient jamais les données d'entrée
    - Retournent toujours le même résultat pour les mêmes entrées
    - N'ont pas d'effets de bord
    - Utilisent les paradigmes fonctionnels de Python
    """
    
    @staticmethod
    def calculate_monthly_fees_functional(units: List[Unit], 
                                        method: FeeCalculationMethod = FeeCalculationMethod.STANDARD) -> List[FinancialRecord]:
        """
        [CONCEPT: Programmation fonctionnelle] Calcul des frais mensuels.
        
        Utilise une approche purement fonctionnelle avec :
        - Filter pour sélectionner les unités actives
        - Map pour transformer en enregistrements financiers
        - Composition de fonctions
        - Immutabilité des résultats
        
        Args:
            units: Liste des unités (non modifiée)
            method: Méthode de calcul des frais
            
        Returns:
            List[FinancialRecord]: Enregistrements financiers immutables
        """
        
        # 1. FILTER: Conserver seulement les unités actives
        active_units = list(filter(
            lambda unit: unit.status == UnitStatus.SOLD,
            units
        ))
        
        # 2. MAP: Transformer chaque unité en enregistrement financier
        calculation_function = FinancialService._get_calculation_function(method)
        
        financial_records = list(map(
            lambda unit: FinancialService._create_financial_record(unit, calculation_function),
            active_units
        ))
        
        # 3. SORT: Trier par numéro d'unité (functional style)
        return sorted(financial_records, key=lambda record: record.unit_number)
    
    @staticmethod
    def _get_calculation_function(method: FeeCalculationMethod) -> Callable[[Unit], Tuple[Decimal, Dict[str, Decimal]]]:
        """
        [CONCEPT: Programmation fonctionnelle] Factory de fonctions de calcul.
        
        Retourne une fonction pure basée sur la méthode choisie.
        Utilise le pattern Strategy avec des fonctions pures.
        """
        calculation_methods = {
            FeeCalculationMethod.STANDARD: FinancialService._calculate_standard_fees,
            FeeCalculationMethod.PROGRESSIVE: FinancialService._calculate_progressive_fees,
            FeeCalculationMethod.FLAT_RATE: FinancialService._calculate_flat_rate_fees,
            FeeCalculationMethod.CUSTOM: FinancialService._calculate_custom_fees
        }
        
        return calculation_methods.get(method, FinancialService._calculate_standard_fees)
    
    @staticmethod
    def _create_financial_record(unit: Unit, 
                               calculation_func: Callable[[Unit], Tuple[Decimal, Dict[str, Decimal]]]) -> FinancialRecord:
        """
        [CONCEPT: Programmation fonctionnelle] Transformation d'entité.
        
        Fonction pure qui transforme une Unit en FinancialRecord
        sans modifier l'objet d'entrée.
        """
        amount, details = calculation_func(unit)
        
        return FinancialRecord(
            unit_number=unit.unit_number,
            monthly_amount=amount,
            calculation_details=details,
            unit_type=unit.unit_type,
            area=Decimal(str(unit.area))
        )
    
    @staticmethod
    def _calculate_standard_fees(unit: Unit) -> Tuple[Decimal, Dict[str, Decimal]]:
        """
        [CONCEPT: Logique métier] Calcul standard des frais.
        
        Fonction pure basée sur la superficie et le type d'unité.
        """
        base_rate = FinancialService._get_base_rate_by_type(unit.unit_type)
        area = Decimal(str(unit.area))
        amount = area * base_rate
        
        details = {
            'base_rate': base_rate,
            'area': area,
            'calculation_method': 'standard'
        }
        
        return amount, details
    
    @staticmethod
    def _calculate_progressive_fees(unit: Unit) -> Tuple[Decimal, Dict[str, Decimal]]:
        """
        [CONCEPT: Logique métier] Calcul progressif des frais.
        
        Utilise des paliers progressifs selon la superficie.
        """
        area = Decimal(str(unit.area))
        
        # Paliers progressifs (fonction pure)
        if area <= 500:
            rate = Decimal('0.20')
        elif area <= 1000:
            rate = Decimal('0.25')
        elif area <= 1500:
            rate = Decimal('0.30')
        else:
            rate = Decimal('0.35')
        
        amount = area * rate
        
        details = {
            'progressive_rate': rate,
            'area': area,
            'calculation_method': 'progressive'
        }
        
        return amount, details
    
    @staticmethod
    def _calculate_flat_rate_fees(unit: Unit) -> Tuple[Decimal, Dict[str, Decimal]]:
        """
        [CONCEPT: Logique métier] Calcul à tarif fixe.
        
        Tarif fixe par type d'unité, indépendant de la superficie.
        """
        flat_rates = {
            UnitType.RESIDENTIAL: Decimal('250.00'),
            UnitType.COMMERCIAL: Decimal('500.00'),
            UnitType.PARKING: Decimal('50.00'),
            UnitType.STORAGE: Decimal('75.00')
        }
        
        amount = flat_rates.get(unit.unit_type, Decimal('200.00'))
        
        details = {
            'flat_rate': amount,
            'unit_type': unit.unit_type.value,
            'calculation_method': 'flat_rate'
        }
        
        return amount, details
    
    @staticmethod
    def _calculate_custom_fees(unit: Unit) -> Tuple[Decimal, Dict[str, Decimal]]:
        """
        [CONCEPT: Logique métier] Calcul personnalisé complexe.
        
        Combine superficie, type et facteurs additionnels.
        """
        base_amount = FinancialService._calculate_standard_fees(unit)[0]
        
        # Facteur de complexité personnalisé
        complexity_factor = Decimal('1.0')
        if unit.unit_type == UnitType.COMMERCIAL:
            complexity_factor = Decimal('1.2')
        elif unit.area > 1500:
            complexity_factor = Decimal('1.1')
        
        amount = base_amount * complexity_factor
        
        details = {
            'base_amount': base_amount,
            'complexity_factor': complexity_factor,
            'final_amount': amount,
            'calculation_method': 'custom'
        }
        
        return amount, details
    
    @staticmethod
    def _get_base_rate_by_type(unit_type: UnitType) -> Decimal:
        """
        [CONCEPT: Logique métier] Tarifs de base par type.
        
        Fonction pure qui retourne le tarif de base selon le type.
        """
        rates = {
            UnitType.RESIDENTIAL: Decimal('0.25'),
            UnitType.COMMERCIAL: Decimal('0.35'),
            UnitType.PARKING: Decimal('0.10'),
            UnitType.STORAGE: Decimal('0.15')
        }
        
        return rates.get(unit_type, Decimal('0.25'))
    
    @staticmethod
    def group_by_type_functional(units: List[Unit]) -> Dict[UnitType, List[Unit]]:
        """
        [CONCEPT: Programmation fonctionnelle] Groupement par type.
        
        Utilise reduce() pour grouper les unités par type de manière fonctionnelle.
        """
        def group_reducer(groups: Dict[UnitType, List[Unit]], unit: Unit) -> Dict[UnitType, List[Unit]]:
            """Fonction reducer pure pour le groupement."""
            # Copie immutable du dictionnaire
            new_groups = groups.copy()
            
            if unit.unit_type not in new_groups:
                new_groups[unit.unit_type] = []
            else:
                new_groups[unit.unit_type] = new_groups[unit.unit_type].copy()
            
            new_groups[unit.unit_type].append(unit)
            return new_groups
        
        return reduce(group_reducer, units, {})
    
    @staticmethod
    def calculate_total_income_functional(financial_records: List[FinancialRecord]) -> Decimal:
        """
        [CONCEPT: Programmation fonctionnelle] Calcul du revenu total.
        
        Utilise reduce() pour sommer tous les montants mensuels.
        """
        return reduce(
            lambda total, record: total + record.monthly_amount,
            financial_records,
            Decimal('0.00')
        )
    
    @staticmethod
    def filter_by_amount_range_functional(financial_records: List[FinancialRecord],
                                        min_amount: Decimal,
                                        max_amount: Decimal) -> List[FinancialRecord]:
        """
        [CONCEPT: Programmation fonctionnelle] Filtrage par montant.
        
        Filtre fonctionnel basé sur une plage de montants.
        """
        return list(filter(
            lambda record: min_amount <= record.monthly_amount <= max_amount,
            financial_records
        ))
    
    @staticmethod
    def generate_financial_summary_functional(units: List[Unit],
                                           method: FeeCalculationMethod = FeeCalculationMethod.STANDARD) -> FinancialSummary:
        """
        [CONCEPT: Programmation fonctionnelle] Génération de résumé financier.
        
        Pipeline fonctionnel complet :
        1. Calcul des frais pour toutes les unités
        2. Filtrage des unités actives
        3. Agrégation des données financières
        4. Construction du résumé immutable
        """
        # Pipeline de transformation fonctionnelle
        financial_records = FinancialService.calculate_monthly_fees_functional(units, method)
        
        # Utilisation de fonctions pures pour les calculs
        total_income = FinancialService.calculate_total_income_functional(financial_records)
        
        active_units_count = len(
            [unit for unit in units if unit.status == UnitStatus.SOLD]
        )
        
        average_fees = total_income / active_units_count if active_units_count > 0 else Decimal('0.00')
        
        # Groupement par type avec reduce()
        groups = FinancialService.group_by_type_functional(units)
        
        # Calcul du breakdown par type (functional style)
        breakdown_by_type = {}
        for unit_type in UnitType:
            type_units = groups.get(unit_type, [])
            if type_units:
                type_records = FinancialService.calculate_monthly_fees_functional(type_units, method)
                breakdown_by_type[unit_type] = FinancialService.calculate_total_income_functional(type_records)
            else:
                breakdown_by_type[unit_type] = Decimal('0.00')
        
        return FinancialSummary(
            total_monthly_income=total_income,
            average_fees_per_unit=average_fees,
            total_units=len(units),
            active_units=active_units_count,
            breakdown_by_type=breakdown_by_type
        )
    
    @staticmethod
    def calculate_monthly_fees(unit: Unit) -> Decimal:
        """
        [CONCEPT: Logique métier] Calcul simple des frais mensuels.
        
        Version simplifiée pour compatibilité avec les tests existants.
        """
        return unit.calculate_monthly_fees()
    
    @staticmethod
    def calculate_annual_income(units: List[Unit]) -> Decimal:
        """
        [CONCEPT: Logique métier] Calcul du revenu annuel total.
        
        Fonction pure qui calcule le revenu annuel de toutes les unités.
        """
        monthly_records = FinancialService.calculate_monthly_fees_functional(units)
        monthly_total = FinancialService.calculate_total_income_functional(monthly_records)
        return monthly_total * 12
    
    @staticmethod
    def calculate_debt_to_income_ratio(debt_amount: Decimal, income_amount: Decimal) -> Decimal:
        """
        [CONCEPT: Logique métier] Calcul du ratio dette/revenu.
        
        Fonction pure pour calculs financiers de base.
        """
        if income_amount == 0:
            return Decimal('0.00')
        
        return (debt_amount / income_amount) * 100
