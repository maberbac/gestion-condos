"""
Tests unitaires pour FinancialService.

Ces tests valident la logique métier des calculs financiers, incluant :
- Calculs de frais mensuels et annuels
- Calculs avec approche fonctionnelle
- Validation des montants et règles métier
- Gestion des erreurs financières
"""

import unittest
from decimal import Decimal
from datetime import datetime, date
from unittest.mock import Mock, patch

from src.domain.services.financial_service import FinancialService, FeeCalculationMethod
from src.domain.entities.unit import Unit, UnitType, UnitStatus
from src.domain.entities.user import User, UserRole


class TestFinancialService(unittest.TestCase):
    """Tests pour le service financier."""

    def setUp(self):
        """Configuration pour chaque test"""
        self.financial_service = FinancialService()
        
        # Données de test pour unités
        self.test_units = [
            Unit(
                unit_number='101',
                owner_name='Jean Dupont',
                area=850.0,
                unit_type=UnitType.RESIDENTIAL,
                status=UnitStatus.AVAILABLE,
                project_id='project_123'
            ),
            Unit(
                unit_number='102',
                owner_name='Marie Martin',
                area=1200.0,
                unit_type=UnitType.COMMERCIAL,
                status=UnitStatus.AVAILABLE,
                project_id='project_123'
            ),
            Unit(
                unit_number='P1',
                owner_name='Pierre Dubois',
                area=200.0,
                unit_type=UnitType.PARKING,
                status=UnitStatus.AVAILABLE,
                project_id='project_123'
            )
        ]

    def test_calculate_monthly_fees_basic(self):
        """Test calcul frais mensuels de base"""
        # Arrange
        unit = self.test_units[0]  # Unité résidentielle
        
        # Act
        fees = self.financial_service.calculate_monthly_fees(unit)
        
        # Assert
        # Le service peut retourner float ou Decimal selon l'implémentation de Unit
        self.assertIsInstance(fees, (Decimal, float))
        if isinstance(fees, float):
            fees = Decimal(str(fees))
        self.assertGreater(fees, Decimal('0'))

    def test_calculate_annual_fees(self):
        """Test calcul frais annuels"""
        # Arrange
        units = self.test_units
        
        # Act
        annual_income = self.financial_service.calculate_annual_income(units)
        
        # Assert
        self.assertIsInstance(annual_income, Decimal)
        self.assertGreater(annual_income, Decimal('0'))

    def test_calculate_debt_to_income_ratio(self):
        """Test calcul ratio dette/revenu"""
        # Arrange
        debt = Decimal('50000.00')
        income = Decimal('100000.00')
        
        # Act
        ratio = self.financial_service.calculate_debt_to_income_ratio(debt, income)
        
        # Assert
        self.assertEqual(ratio, Decimal('50.00'))

    def test_calculate_debt_to_income_ratio_zero_income(self):
        """Test calcul ratio dette/revenu avec revenu zéro"""
        # Arrange
        debt = Decimal('50000.00')
        income = Decimal('0.00')
        
        # Act
        ratio = self.financial_service.calculate_debt_to_income_ratio(debt, income)
        
        # Assert
        self.assertEqual(ratio, Decimal('0.00'))

    def test_calculate_monthly_fees_functional_standard(self):
        """Test calcul fonctionnel avec méthode standard"""
        # Arrange
        units = self.test_units
        
        # Act
        records = self.financial_service.calculate_monthly_fees_functional(
            units, FeeCalculationMethod.STANDARD
        )
        
        # Assert
        self.assertIsInstance(records, list)
        self.assertEqual(len(records), 3)  # Toutes les unités sont vendues
        for record in records:
            self.assertGreater(record.monthly_amount, Decimal('0'))

    def test_calculate_monthly_fees_functional_progressive(self):
        """Test calcul fonctionnel avec méthode progressive"""
        # Arrange
        units = self.test_units
        
        # Act
        records = self.financial_service.calculate_monthly_fees_functional(
            units, FeeCalculationMethod.PROGRESSIVE
        )
        
        # Assert
        self.assertIsInstance(records, list)
        self.assertEqual(len(records), 3)
        for record in records:
            self.assertGreater(record.monthly_amount, Decimal('0'))

    def test_calculate_monthly_fees_functional_flat_rate(self):
        """Test calcul fonctionnel avec tarif fixe"""
        # Arrange
        units = self.test_units
        
        # Act
        records = self.financial_service.calculate_monthly_fees_functional(
            units, FeeCalculationMethod.FLAT_RATE
        )
        
        # Assert
        self.assertIsInstance(records, list)
        self.assertEqual(len(records), 3)
        # Vérifier que les montants correspondent aux tarifs fixes
        for record in records:
            if record.unit_type == UnitType.RESIDENTIAL:
                self.assertEqual(record.monthly_amount, Decimal('250.00'))
            elif record.unit_type == UnitType.COMMERCIAL:
                self.assertEqual(record.monthly_amount, Decimal('500.00'))
            elif record.unit_type == UnitType.PARKING:
                self.assertEqual(record.monthly_amount, Decimal('50.00'))

    def test_generate_financial_summary(self):
        """Test génération résumé financier"""
        # Arrange
        units = self.test_units
        
        # Act
        summary = self.financial_service.generate_financial_summary_functional(units)
        
        # Assert
        self.assertGreater(summary.total_monthly_income, Decimal('0'))
        self.assertEqual(summary.total_units, 3)
        self.assertEqual(summary.active_units, 3)
        self.assertGreater(summary.average_fees_per_unit, Decimal('0'))

    def test_group_by_type_functional(self):
        """Test groupement par type fonctionnel"""
        # Arrange
        units = self.test_units
        
        # Act
        groups = self.financial_service.group_by_type_functional(units)
        
        # Assert
        self.assertIn(UnitType.RESIDENTIAL, groups)
        self.assertIn(UnitType.COMMERCIAL, groups)
        self.assertIn(UnitType.PARKING, groups)
        self.assertEqual(len(groups[UnitType.RESIDENTIAL]), 1)
        self.assertEqual(len(groups[UnitType.COMMERCIAL]), 1)
        self.assertEqual(len(groups[UnitType.PARKING]), 1)

    def test_calculate_total_income_functional(self):
        """Test calcul revenu total fonctionnel"""
        # Arrange
        records = self.financial_service.calculate_monthly_fees_functional(self.test_units)
        
        # Act
        total = self.financial_service.calculate_total_income_functional(records)
        
        # Assert
        self.assertIsInstance(total, Decimal)
        self.assertGreater(total, Decimal('0'))

    def test_filter_by_amount_range_functional(self):
        """Test filtrage par montant fonctionnel"""
        # Arrange
        records = self.financial_service.calculate_monthly_fees_functional(self.test_units)
        min_amount = Decimal('100.00')
        max_amount = Decimal('300.00')
        
        # Act
        filtered = self.financial_service.filter_by_amount_range_functional(
            records, min_amount, max_amount
        )
        
        # Assert
        self.assertIsInstance(filtered, list)
        for record in filtered:
            self.assertGreaterEqual(record.monthly_amount, min_amount)
            self.assertLessEqual(record.monthly_amount, max_amount)

    def test_calculate_fees_with_inactive_units(self):
        """Test calcul avec unités inactives"""
        # Arrange
        units = self.test_units.copy()
        units.append(Unit(
            unit_number='103',
            owner_name='Test User',
            area=800.0,
            unit_type=UnitType.RESIDENTIAL,
            status=UnitStatus.MAINTENANCE,  # Unité inactive
            project_id='project_123'
        ))
        
        # Act
        records = self.financial_service.calculate_monthly_fees_functional(units)
        
        # Assert
        # Seules les unités vendues devraient être incluses
        self.assertEqual(len(records), 3)

    def test_financial_record_immutability(self):
        """Test immutabilité des enregistrements financiers"""
        # Arrange
        records = self.financial_service.calculate_monthly_fees_functional(self.test_units)
        
        # Act & Assert
        for record in records:
            # Les enregistrements doivent être immutables (frozen dataclass)
            with self.assertRaises(AttributeError):
                record.monthly_amount = Decimal('999.99')

    def test_financial_summary_immutability(self):
        """Test immutabilité du résumé financier"""
        # Arrange
        summary = self.financial_service.generate_financial_summary_functional(self.test_units)
        
        # Act & Assert
        # Le résumé doit être immutable (frozen dataclass)
        with self.assertRaises(AttributeError):
            summary.total_monthly_income = Decimal('999.99')

    def test_error_handling_empty_unit_list(self):
        """Test gestion d'erreur liste vide"""
        # Arrange
        empty_units = []
        
        # Act
        records = self.financial_service.calculate_monthly_fees_functional(empty_units)
        summary = self.financial_service.generate_financial_summary_functional(empty_units)
        
        # Assert
        self.assertEqual(len(records), 0)
        self.assertEqual(summary.total_monthly_income, Decimal('0.00'))
        self.assertEqual(summary.average_fees_per_unit, Decimal('0.00'))

    def test_functional_programming_concepts(self):
        """Test que les concepts de programmation fonctionnelle sont respectés"""
        # Arrange
        units = self.test_units.copy()
        original_units = [u for u in units]  # Copie pour vérifier immutabilité
        
        # Act
        records = self.financial_service.calculate_monthly_fees_functional(units)
        summary = self.financial_service.generate_financial_summary_functional(units)
        
        # Assert - Les données d'entrée ne doivent pas être modifiées
        self.assertEqual(len(units), len(original_units))
        for i, unit in enumerate(units):
            self.assertEqual(unit.unit_number, original_units[i].unit_number)
            self.assertEqual(unit.area, original_units[i].area)

    def test_calculation_consistency(self):
        """Test cohérence des calculs"""
        # Arrange
        units = self.test_units
        
        # Act - Même calcul plusieurs fois
        records1 = self.financial_service.calculate_monthly_fees_functional(units)
        records2 = self.financial_service.calculate_monthly_fees_functional(units)
        
        # Assert - Résultats identiques (fonction pure)
        self.assertEqual(len(records1), len(records2))
        for i, record in enumerate(records1):
            self.assertEqual(record.monthly_amount, records2[i].monthly_amount)
            self.assertEqual(record.unit_number, records2[i].unit_number)


if __name__ == '__main__':
    unittest.main()
