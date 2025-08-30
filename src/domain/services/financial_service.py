"""
Service Financier - Logique métier pour calculs financiers.

[CONCEPT TECHNIQUE: Programmation fonctionnelle]
Ce service démontre l'utilisation des paradigmes fonctionnels en Python :
- Fonctions pures sans effets de bord
- Utilisation de map(), filter(), reduce()
- Composition de fonctions
- Immutabilité des données
- Transformation de données par pipelines fonctionnels

Architecture Hexagonale:
Ce service fait partie du domaine métier et ne dépend d'aucun adapter
ou infrastructure externe. Il peut être testé de manière isolée.
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)


from functools import reduce
from typing import List, Dict, Callable, Tuple, Optional
from decimal import Decimal
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum

from src.domain.entities.condo import Condo, CondoType, CondoStatus


class FeeCalculationMethod(Enum):
    """Méthodes de calcul des frais de copropriété."""
    STANDARD = "standard"           # Calcul standard par superficie
    PROGRESSIVE = "progressive"     # Tarif progressif selon la taille
    FLAT_RATE = "flat_rate"        # Tarif fixe par unité
    CUSTOM = "custom"              # Calcul personnalisé


@dataclass(frozen=True)  # Immutable pour approche fonctionnelle
class FinancialRecord:
    """
    Enregistrement financier immutable.
    
    [CONCEPT: Programmation fonctionnelle]
    Cette classe utilise frozen=True pour garantir l'immutabilité,
    un principe clé de la programmation fonctionnelle.
    """
    unit_number: str
    owner_name: str
    amount: Decimal
    calculation_date: datetime
    calculation_method: FeeCalculationMethod
    details: Dict[str, Decimal]
    
    def to_dict(self) -> Dict[str, str]:
        """Convertit l'enregistrement en dictionnaire pour sérialisation."""
        return {
            'unit_number': self.unit_number,
            'owner_name': self.owner_name,
            'amount': str(self.amount),
            'calculation_date': self.calculation_date.isoformat(),
            'calculation_method': self.calculation_method.value,
            'details': {k: str(v) for k, v in self.details.items()}
        }


@dataclass(frozen=True)
class FinancialSummary:
    """Résumé financier immutable pour un ensemble d'unités."""
    total_monthly_fees: Decimal
    total_annual_fees: Decimal
    average_fees_per_unit: Decimal
    fees_by_type: Dict[str, Decimal]
    fees_by_status: Dict[str, Decimal]
    calculation_date: datetime
    units_count: int


class FinancialService:
    """
    Service métier pour les calculs financiers.
    
    [CONCEPT: Programmation fonctionnelle]
    Ce service utilise exclusivement des fonctions pures qui :
    - Ne modifient jamais les données d'entrée
    - Retournent toujours le même résultat pour les mêmes entrées
    - N'ont pas d'effets de bord
    - Utilisent les paradigmes fonctionnels de Python
    """
    
    @staticmethod
    def calculate_monthly_fees_functional(condos: List[Condo], 
                                        method: FeeCalculationMethod = FeeCalculationMethod.STANDARD) -> List[FinancialRecord]:
        """
        [CONCEPT: Programmation fonctionnelle] Calcul des frais mensuels.
        
        Démonstration des paradigmes fonctionnels :
        - Pipeline de transformation avec map() et filter()
        - Fonctions pures sans modification des données d'entrée
        - Composition de fonctions
        - Immutabilité des résultats
        
        Args:
            condos: Liste des condos (non modifiée)
            method: Méthode de calcul des frais
            
        Returns:
            List[FinancialRecord]: Enregistrements financiers immutables
        """
        
        # 1. FILTER: Conserver seulement les condos actifs
        active_condos = list(filter(
            lambda condo: condo.status == CondoStatus.ACTIVE,
            condos
        ))
        
        # 2. MAP: Transformer chaque condo en enregistrement financier
        calculation_function = FinancialService._get_calculation_function(method)
        
        financial_records = list(map(
            lambda condo: FinancialService._create_financial_record(condo, calculation_function),
            active_condos
        ))
        
        # 3. SORT: Trier par numéro d'unité (functional style)
        sorted_records = sorted(
            financial_records,
            key=lambda record: record.unit_number
        )
        
        return sorted_records
    
    @staticmethod
    def _get_calculation_function(method: FeeCalculationMethod) -> Callable[[Condo], Tuple[Decimal, Dict[str, Decimal]]]:
        """
        [CONCEPT: Programmation fonctionnelle] Retourne une fonction de calcul.
        
        Higher-order function qui retourne une fonction spécialisée
        selon la méthode de calcul demandée.
        """
        calculation_functions = {
            FeeCalculationMethod.STANDARD: FinancialService._calculate_standard_fees,
            FeeCalculationMethod.PROGRESSIVE: FinancialService._calculate_progressive_fees,
            FeeCalculationMethod.FLAT_RATE: FinancialService._calculate_flat_rate_fees,
            FeeCalculationMethod.CUSTOM: FinancialService._calculate_custom_fees
        }
        
        return calculation_functions.get(method, FinancialService._calculate_standard_fees)
    
    @staticmethod
    def _create_financial_record(condo: Condo, 
                               calculation_func: Callable[[Condo], Tuple[Decimal, Dict[str, Decimal]]]) -> FinancialRecord:
        """
        [CONCEPT: Programmation fonctionnelle] Crée un enregistrement financier.
        
        Fonction pure qui transforme un Condo en FinancialRecord
        sans modifier les données d'entrée.
        """
        amount, details = calculation_func(condo)
        
        return FinancialRecord(
            unit_number=condo.unit_number,
            owner_name=condo.owner_name,
            amount=amount,
            calculation_date=datetime.now(),
            calculation_method=FeeCalculationMethod.STANDARD,  # TODO: passer la méthode
            details=details
        )
    
    @staticmethod
    def _calculate_standard_fees(condo: Condo) -> Tuple[Decimal, Dict[str, Decimal]]:
        """Fonction pure pour calcul standard des frais."""
        base_fee = condo.calculate_monthly_fees()
        
        details = {
            'base_fee': base_fee,
            'square_feet': Decimal(str(condo.square_feet)),
            'rate_per_sqft': base_fee / Decimal(str(condo.square_feet))
        }
        
        return base_fee, details
    
    @staticmethod
    def _calculate_progressive_fees(condo: Condo) -> Tuple[Decimal, Dict[str, Decimal]]:
        """
        [CONCEPT: Programmation fonctionnelle] Calcul progressif des frais.
        
        Tarif progressif selon la superficie:
        - 0-500 sq ft: taux normal
        - 500-1000 sq ft: taux normal + 10%
        - 1000+ sq ft: taux normal + 20%
        """
        base_fee = condo.calculate_monthly_fees()
        
        # Calcul du multiplicateur progressif (fonction pure)
        def get_progressive_multiplier(square_feet: float) -> Decimal:
            if square_feet <= 500:
                return Decimal('1.0')
            elif square_feet <= 1000:
                return Decimal('1.1')  # +10%
            else:
                return Decimal('1.2')  # +20%
        
        multiplier = get_progressive_multiplier(condo.square_feet)
        progressive_fee = base_fee * multiplier
        
        details = {
            'base_fee': base_fee,
            'progressive_multiplier': multiplier,
            'progressive_fee': progressive_fee,
            'square_feet': Decimal(str(condo.square_feet))
        }
        
        return progressive_fee, details
    
    @staticmethod
    def _calculate_flat_rate_fees(condo: Condo) -> Tuple[Decimal, Dict[str, Decimal]]:
        """Fonction pure pour calcul à tarif fixe."""
        # Tarifs fixes par type d'unité
        flat_rates = {
            CondoType.RESIDENTIAL: Decimal('250.00'),
            CondoType.COMMERCIAL: Decimal('500.00'),
            CondoType.PARKING: Decimal('50.00'),
            CondoType.STORAGE: Decimal('75.00')
        }
        
        flat_fee = flat_rates.get(condo.condo_type, Decimal('250.00'))
        
        details = {
            'flat_rate': flat_fee,
            'condo_type': Decimal(str(condo.condo_type.value)),
            'square_feet': Decimal(str(condo.square_feet))
        }
        
        return flat_fee, details
    
    @staticmethod
    def _calculate_custom_fees(condo: Condo) -> Tuple[Decimal, Dict[str, Decimal]]:
        """Fonction pure pour calcul personnalisé."""
        # Si des frais de base sont définis, les utiliser
        if condo.monthly_fees_base is not None:
            custom_fee = condo.monthly_fees_base
        else:
            custom_fee = condo.calculate_monthly_fees()
        
        details = {
            'custom_fee': custom_fee,
            'is_custom_base': Decimal('1' if condo.monthly_fees_base is not None else '0')
        }
        
        return custom_fee, details
    
    @staticmethod
    def calculate_total_revenue_functional(financial_records: List[FinancialRecord]) -> Decimal:
        """
        [CONCEPT: Programmation fonctionnelle] Calcul du revenu total avec reduce().
        
        Utilise reduce() pour agréger les montants de manière fonctionnelle.
        """
        return reduce(
            lambda total, record: total + record.amount,
            financial_records,
            Decimal('0.00')
        )
    
    @staticmethod
    def group_by_type_functional(condos: List[Condo]) -> Dict[CondoType, List[Condo]]:
        """
        [CONCEPT: Programmation fonctionnelle] Groupement par type.
        
        Utilise reduce() pour grouper les condos par type de manière fonctionnelle.
        """
        return reduce(
            lambda groups, condo: {
                **groups,  # Spread operator pour immutabilité
                condo.condo_type: groups.get(condo.condo_type, []) + [condo]
            },
            condos,
            {}
        )
    
    @staticmethod
    def filter_by_fee_range_functional(financial_records: List[FinancialRecord],
                                     min_fee: Decimal,
                                     max_fee: Decimal) -> List[FinancialRecord]:
        """
        [CONCEPT: Programmation fonctionnelle] Filtrage par plage de frais.
        
        Chaîne de fonctions filter() pour critères multiples.
        """
        # Pipeline de filtres fonctionnels
        above_minimum = filter(lambda record: record.amount >= min_fee, financial_records)
        within_range = filter(lambda record: record.amount <= max_fee, above_minimum)
        
        return list(within_range)
    
    @staticmethod
    def calculate_statistics_functional(financial_records: List[FinancialRecord]) -> Dict[str, Decimal]:
        """
        [CONCEPT: Programmation fonctionnelle] Calcul de statistiques.
        
        Combinaison de map(), reduce() et fonctions pures pour statistiques.
        """
        if not financial_records:
            return {
                'total': Decimal('0.00'),
                'average': Decimal('0.00'),
                'minimum': Decimal('0.00'),
                'maximum': Decimal('0.00'),
                'count': Decimal('0')
            }
        
        # Extraction des montants avec map()
        amounts = list(map(lambda record: record.amount, financial_records))
        
        # Calculs avec reduce() et fonctions pures
        total = reduce(lambda acc, amount: acc + amount, amounts, Decimal('0.00'))
        count = Decimal(str(len(amounts)))
        average = total / count if count > 0 else Decimal('0.00')
        minimum = reduce(lambda acc, amount: min(acc, amount), amounts, amounts[0])
        maximum = reduce(lambda acc, amount: max(acc, amount), amounts, amounts[0])
        
        return {
            'total': total,
            'average': average.quantize(Decimal('0.01')),
            'minimum': minimum,
            'maximum': maximum,
            'count': count
        }
    
    @staticmethod
    def generate_financial_summary_functional(condos: List[Condo],
                                            method: FeeCalculationMethod = FeeCalculationMethod.STANDARD) -> FinancialSummary:
        """
        [CONCEPT: Programmation fonctionnelle] Génération de résumé financier.
        
        Pipeline fonctionnel complet pour créer un résumé financier immutable.
        """
        # 1. Calcul des enregistrements financiers
        financial_records = FinancialService.calculate_monthly_fees_functional(condos, method)
        
        # 2. Calculs avec paradigmes fonctionnels
        total_monthly = FinancialService.calculate_total_revenue_functional(financial_records)
        total_annual = total_monthly * 12
        
        units_count = len(financial_records)
        average_fees = total_monthly / Decimal(str(units_count)) if units_count > 0 else Decimal('0.00')
        
        # 3. Groupement par type avec programmation fonctionnelle
        grouped_condos = FinancialService.group_by_type_functional(
            [condo for condo in condos if condo.status == CondoStatus.ACTIVE]
        )
        
        # 4. Calcul des frais par type
        fees_by_type = {}
        for condo_type, type_condos in grouped_condos.items():
            type_records = FinancialService.calculate_monthly_fees_functional(type_condos, method)
            type_total = FinancialService.calculate_total_revenue_functional(type_records)
            fees_by_type[condo_type.value] = type_total
        
        # 5. Groupement par statut
        fees_by_status = {}
        for status in CondoStatus:
            status_condos = list(filter(lambda c: c.status == status, condos))
            if status_condos:
                status_records = FinancialService.calculate_monthly_fees_functional(status_condos, method)
                status_total = FinancialService.calculate_total_revenue_functional(status_records)
                fees_by_status[status.value] = status_total
        
        # 6. Création du résumé immutable
        return FinancialSummary(
            total_monthly_fees=total_monthly,
            total_annual_fees=total_annual,
            average_fees_per_unit=average_fees.quantize(Decimal('0.01')),
            fees_by_type=fees_by_type,
            fees_by_status=fees_by_status,
            calculation_date=datetime.now(),
            units_count=units_count
        )
    
    # Méthodes pour compatibilité avec les tests
    @staticmethod
    def calculate_monthly_fees(condo: Condo) -> Decimal:
        """Calcul frais mensuels pour un condo."""
        return condo.calculate_monthly_fees()
    
    @staticmethod  
    def calculate_monthly_fees_with_taxes(condo: Condo, tax_rate: float = 0.15) -> float:
        """Calcul frais mensuels avec taxes."""
        if tax_rate < 0:
            raise ValueError("Le taux de taxe ne peut pas être négatif")
        base_fees = condo.calculate_monthly_fees()
        result = base_fees * (1 + tax_rate)
        return round(result, 2)
    
    @staticmethod
    def calculate_annual_fees(condo: Condo) -> Decimal:
        """Calcul frais annuels pour un condo."""
        return condo.calculate_annual_fees()
    
    @staticmethod
    def calculate_total_building_fees(condos: List[Condo]) -> Decimal:
        """Calcul total des frais pour un immeuble."""
        return sum((Decimal(str(condo.calculate_monthly_fees())) for condo in condos), Decimal('0'))
    
    @staticmethod
    def calculate_fees_by_square_footage(condo: Condo, rate_per_sqft) -> Decimal:
        """Calcul frais basé sur superficie."""
        return Decimal(str(condo.square_feet)) * Decimal(str(rate_per_sqft))
    
    @staticmethod
    def calculate_special_assessment(condo: Condo, total_assessment: float, 
                                   total_building_sqft: float) -> float:
        """Calcul évaluation spéciale."""
        return (condo.square_feet / total_building_sqft) * total_assessment
    
    @staticmethod
    def calculate_management_fees(base_fees, management_rate: float = 0.05) -> Decimal:
        """Calcul frais de gestion."""
        return Decimal(str(base_fees)) * Decimal(str(management_rate))
    
    @staticmethod
    def calculate_reserve_fund_contribution(condo: Condo, contribution_rate: float = 0.10) -> Decimal:
        """Calcul contribution fonds de réserve."""
        base_fees = Decimal(str(condo.calculate_monthly_fees()))
        return base_fees * Decimal(str(contribution_rate))
    
    @staticmethod
    def calculate_comprehensive_monthly_bill(condo: Condo, rates: Dict[str, float]) -> Dict[str, float]:
        """Calcul facture mensuelle complète."""
        base_fees = condo.calculate_monthly_fees()
        taxes = base_fees * rates.get('tax_rate', 0.15)
        management = base_fees * rates.get('management_fee_rate', 0.05)
        reserve = base_fees * rates.get('reserve_fund_rate', 0.10)
        total = base_fees + taxes + management + reserve
        
        return {
            'base_fees': base_fees,
            'taxes': taxes,
            'management_fees': management,
            'reserve_fund': reserve,
            'total': total
        }
    
    @staticmethod
    def calculate_fees_by_type(condo: Condo) -> Decimal:
        """Calcul frais par type de condo."""
        base_fees = Decimal(str(condo.calculate_monthly_fees()))
        if condo.condo_type == CondoType.COMMERCIAL:
            return base_fees * Decimal('1.25')  # 25% de plus pour commercial
        return base_fees
    
    @staticmethod
    def calculate_proration(monthly_amount: float, days_occupied: int, 
                          days_in_month: int) -> float:
        """Calcul prorata pour mois partiel."""
        if days_in_month <= 0:
            raise ValueError("Jours dans le mois doit être positif")
        daily_rate = monthly_amount / days_in_month
        return daily_rate * days_occupied
    
    @staticmethod
    def calculate_late_payment_penalty(amount, days_late: int,
                                     penalty_rate: float = 0.05) -> Decimal:
        """Calcul pénalité retard de paiement."""
        amount = Decimal(str(amount))
        if days_late <= 0:
            return Decimal('0')
        return amount * Decimal(str(penalty_rate)) * Decimal(str(days_late)) / Decimal('30')
    
    @staticmethod
    def calculate_budget_variance(budgeted: float, actual: float) -> Dict[str, float]:
        """Calcul écart budgétaire."""
        variance_amount = actual - budgeted
        variance_percent = (variance_amount / budgeted * 100) if budgeted != 0 else 0
        
        if variance_amount > 0:
            status = 'over_budget'
        elif variance_amount < 0:
            status = 'under_budget'
        else:
            status = 'on_budget'
        
        return {
            'amount': variance_amount,
            'percentage': variance_percent,
            'status': status
        }
    
    @staticmethod
    def validate_payment_amount(payment_amount: float, expected_amount: float, 
                              tolerance: float = 0.01) -> bool:
        """Validation montant paiement avec tolérance."""
        difference = abs(payment_amount - expected_amount)
        return difference <= tolerance
    
    @staticmethod
    def generate_building_financial_summary(condos: List[Condo], rates: Dict[str, float]) -> Dict[str, any]:
        """Génération résumé financier immeuble."""
        total_monthly_fees = sum(condo.calculate_monthly_fees() for condo in condos)
        total_annual_fees = total_monthly_fees * 12
        active_units = sum(1 for condo in condos if condo.status == CondoStatus.ACTIVE)
        
        # Répartition par type
        breakdown_by_type = {}
        for condo in condos:
            condo_type = condo.condo_type.value
            if condo_type not in breakdown_by_type:
                breakdown_by_type[condo_type] = {'count': 0, 'total_fees': 0}
            breakdown_by_type[condo_type]['count'] += 1
            breakdown_by_type[condo_type]['total_fees'] += condo.calculate_monthly_fees()
        
        reserve_fund_rate = rates.get('reserve_fund_rate', 0.12)
        reserve_fund_total = total_monthly_fees * reserve_fund_rate
        
        return {
            'total_units': len(condos),
            'total_monthly_revenue': total_monthly_fees,
            'total_annual_revenue': total_annual_fees,
            'breakdown_by_type': breakdown_by_type,
            'reserve_fund_total': reserve_fund_total,
            'calculation_date': datetime.now().isoformat()
        }
    
    @staticmethod
    def calculate_debt_to_income_ratio(debt_amount, income_amount) -> float:
        """Calcul ratio dette/revenu en pourcentage."""
        if income_amount == 0:
            raise ValueError("Revenu ne peut pas être zéro")
        return (debt_amount / income_amount) * 100


# Fonctions utilitaires fonctionnelles
def compose_functions(*functions: Callable) -> Callable:
    """
    [CONCEPT: Programmation fonctionnelle] Composition de fonctions.
    
    Permet de composer plusieurs fonctions en une seule.
    Exemple: compose(f, g, h)(x) équivaut à f(g(h(x)))
    """
    return reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)


def curry_fee_calculation(method: FeeCalculationMethod) -> Callable[[List[Condo]], List[FinancialRecord]]:
    """
    [CONCEPT: Programmation fonctionnelle] Currying d'une fonction.
    
    Transforme une fonction à plusieurs paramètres en fonction
    partiellement appliquée.
    """
    return lambda condos: FinancialService.calculate_monthly_fees_functional(condos, method)


# Exemple d'utilisation des paradigmes fonctionnels
if __name__ == "__main__":
    # Import pour l'exemple
    from src.domain.entities.condo import Condo, CondoType, CondoStatus
    
    # Créer des condos de test
    test_condos = [
        Condo("A-101", "Jean Dupont", 850.0, CondoType.RESIDENTIAL),
        Condo("A-102", "Marie Tremblay", 1200.0, CondoType.RESIDENTIAL),
        Condo("B-001", "Entreprise ABC", 300.0, CondoType.COMMERCIAL),
        Condo("P-001", "Pierre Martin", 150.0, CondoType.PARKING)
    ]
    
    # Démonstration programmation fonctionnelle
    service = FinancialService()
    
    # 1. Calcul des frais avec différentes méthodes
    standard_records = service.calculate_monthly_fees_functional(test_condos, FeeCalculationMethod.STANDARD)
    progressive_records = service.calculate_monthly_fees_functional(test_condos, FeeCalculationMethod.PROGRESSIVE)
    
    logger.info("=== Calculs Standards ===")
    for record in standard_records:
        logger.info(f"{record.unit_number}: {record.amount}$ - {record.details}")
    
    logger.info("\n=== Calculs Progressifs ===")
    for record in progressive_records:
        logger.info(f"{record.unit_number}: {record.amount}$ - {record.details}")
    
    # 2. Statistiques fonctionnelles
    stats = service.calculate_statistics_functional(standard_records)
    logger.info(f"\n=== Statistiques ===")
    logger.info(f"Total: {stats['total']}$")
    logger.info(f"Moyenne: {stats['average']}$")
    logger.info(f"Min: {stats['minimum']}$ | Max: {stats['maximum']}$")
    
    # 3. Résumé financier complet
    summary = service.generate_financial_summary_functional(test_condos)
    logger.info(f"\n=== Résumé Financier ===")
    logger.info(f"Frais mensuels totaux: {summary.total_monthly_fees}$")
    logger.info(f"Frais annuels totaux: {summary.total_annual_fees}$")
    logger.info(f"Frais par type: {summary.fees_by_type}")
    
    # 4. Démonstration currying
    standard_calculator = curry_fee_calculation(FeeCalculationMethod.STANDARD)
    progressive_calculator = curry_fee_calculation(FeeCalculationMethod.PROGRESSIVE)
    
    standard_result = standard_calculator(test_condos)
    progressive_result = progressive_calculator(test_condos)
    
    logger.info(f"\n=== Currying ===")
    logger.info(f"Standard via currying: {len(standard_result)} enregistrements")
    logger.info(f"Progressif via currying: {len(progressive_result)} enregistrements")
