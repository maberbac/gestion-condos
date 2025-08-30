"""
Tests unitaires pour FinancialService.

[TDD - RED-GREEN-REFACTOR]
Ces tests valident la logique métier des calculs financiers, incluant :
- Calculs de frais mensuels et annuels
- Calculs de taxes et charges spéciales
- Répartition des coûts entre résidents
- Validation des montants et règles métier
"""

import unittest
from decimal import Decimal
from datetime import datetime, date
from unittest.mock import Mock, patch

from src.domain.services.financial_service import FinancialService
from src.domain.entities.condo import Condo, CondoType, CondoStatus
from src.domain.entities.user import User, UserRole


class TestFinancialService(unittest.TestCase):
    """Tests unitaires pour FinancialService"""
    
    def setUp(self):
        """Configuration pour chaque test"""
        self.financial_service = FinancialService()
        
        # Données de test pour condos
        self.test_condos = [
            Condo(
                unit_number='101',
                owner_name='Jean Dupont',
                square_feet=850.0,
                condo_type=CondoType.RESIDENTIAL,
                status=CondoStatus.ACTIVE,
                monthly_fees_base=350.0
            ),
            Condo(
                unit_number='102',
                owner_name='Marie Martin',
                square_feet=950.0,
                condo_type=CondoType.RESIDENTIAL,
                status=CondoStatus.ACTIVE,
                monthly_fees_base=400.0
            ),
            Condo(
                unit_number='201',
                owner_name='Commercial Corp',
                square_feet=1200.0,
                condo_type=CondoType.COMMERCIAL,
                status=CondoStatus.ACTIVE,
                monthly_fees_base=600.0
            )
        ]
        
        # Configuration de taux de test
        self.test_rates = {
            'tax_rate': 0.15,
            'special_assessment_rate': 0.05,
            'management_fee_rate': 0.08,
            'reserve_fund_rate': 0.12
        }
    
    def test_calculate_monthly_fees_basic(self):
        """Test calcul frais mensuels de base"""
        # Arrange
        condo = self.test_condos[0]  # 850 sq ft, $350 base
        
        # Act
        monthly_fees = self.financial_service.calculate_monthly_fees(condo)
        
        # Assert
        self.assertIsInstance(monthly_fees, (float, Decimal))
        self.assertGreater(monthly_fees, 0)
        self.assertEqual(monthly_fees, 350.0)
    
    def test_calculate_monthly_fees_with_taxes(self):
        """Test calcul frais mensuels avec taxes"""
        # Arrange
        condo = self.test_condos[0]
        
        # Act
        monthly_fees_with_tax = self.financial_service.calculate_monthly_fees_with_taxes(
            condo, self.test_rates['tax_rate']
        )
        
        # Assert
        expected = 350.0 * (1 + self.test_rates['tax_rate'])
        self.assertAlmostEqual(monthly_fees_with_tax, expected, places=2)
    
    def test_calculate_annual_fees(self):
        """Test calcul frais annuels"""
        # Arrange
        condo = self.test_condos[0]
        
        # Act
        annual_fees = self.financial_service.calculate_annual_fees(condo)
        
        # Assert
        expected = 350.0 * 12
        self.assertEqual(annual_fees, expected)
    
    def test_calculate_total_building_fees(self):
        """Test calcul total frais immeuble"""
        # Act
        total_fees = self.financial_service.calculate_total_building_fees(self.test_condos)
        
        # Assert
        expected = 350.0 + 400.0 + 600.0  # Somme des frais de base
        self.assertEqual(total_fees, expected)
    
    def test_calculate_fees_by_square_footage(self):
        """Test calcul frais basé sur superficie"""
        # Arrange
        condo = self.test_condos[0]  # 850 sq ft
        rate_per_sqft = 0.50
        
        # Act
        fees = self.financial_service.calculate_fees_by_square_footage(condo, rate_per_sqft)
        
        # Assert
        expected = 850.0 * 0.50
        self.assertEqual(fees, expected)
    
    def test_calculate_special_assessment(self):
        """Test calcul évaluation spéciale"""
        # Arrange
        total_assessment = 50000.0
        condo = self.test_condos[0]
        total_building_sqft = sum(c.square_feet for c in self.test_condos)
        
        # Act
        assessment = self.financial_service.calculate_special_assessment(
            condo, total_assessment, total_building_sqft
        )
        
        # Assert
        expected = (condo.square_feet / total_building_sqft) * total_assessment
        self.assertAlmostEqual(assessment, expected, places=2)
    
    def test_calculate_management_fees(self):
        """Test calcul frais de gestion"""
        # Arrange
        base_fees = 350.0
        management_rate = self.test_rates['management_fee_rate']
        
        # Act
        management_fees = self.financial_service.calculate_management_fees(
            base_fees, management_rate
        )
        
        # Assert
        expected = base_fees * management_rate
        self.assertEqual(management_fees, expected)
    
    def test_calculate_reserve_fund_contribution(self):
        """Test calcul contribution fonds de réserve"""
        # Arrange
        condo = self.test_condos[0]
        reserve_rate = self.test_rates['reserve_fund_rate']
        
        # Act
        reserve_contribution = self.financial_service.calculate_reserve_fund_contribution(
            condo, reserve_rate
        )
        
        # Assert
        expected = condo.monthly_fees_base * reserve_rate
        self.assertEqual(reserve_contribution, expected)
    
    def test_calculate_comprehensive_monthly_bill(self):
        """Test calcul facture mensuelle complète"""
        # Arrange
        condo = self.test_condos[0]
        
        # Act
        bill = self.financial_service.calculate_comprehensive_monthly_bill(
            condo, self.test_rates
        )
        
        # Assert
        self.assertIsInstance(bill, dict)
        self.assertIn('base_fees', bill)
        self.assertIn('taxes', bill)
        self.assertIn('management_fees', bill)
        self.assertIn('reserve_fund', bill)
        self.assertIn('total', bill)
        
        # Vérifier cohérence des calculs
        expected_total = (
            bill['base_fees'] + 
            bill['taxes'] + 
            bill['management_fees'] + 
            bill['reserve_fund']
        )
        self.assertAlmostEqual(bill['total'], expected_total, places=2)
    
    def test_calculate_fees_by_condo_type_residential(self):
        """Test calcul frais par type - résidentiel"""
        # Arrange
        condo = self.test_condos[0]  # Résidentiel
        
        # Act
        fees = self.financial_service.calculate_fees_by_type(condo)
        
        # Assert
        # Les frais résidentiels utilisent le taux de base
        self.assertEqual(fees, condo.monthly_fees_base)
    
    def test_calculate_fees_by_condo_type_commercial(self):
        """Test calcul frais par type - commercial"""
        # Arrange
        condo = self.test_condos[2]  # Commercial
        
        # Act
        fees = self.financial_service.calculate_fees_by_type(condo)
        
        # Assert
        # Les frais commerciaux ont un multiplicateur
        expected = condo.monthly_fees_base * 1.25  # 25% de plus
        self.assertEqual(fees, expected)
    
    def test_calculate_proration_for_partial_month(self):
        """Test calcul prorata pour mois partiel"""
        # Arrange
        monthly_fees = 350.0
        days_in_month = 30
        days_occupied = 15
        
        # Act
        prorated_fees = self.financial_service.calculate_proration(
            monthly_fees, days_occupied, days_in_month
        )
        
        # Assert
        expected = (monthly_fees / days_in_month) * days_occupied
        self.assertEqual(prorated_fees, expected)
    
    def test_calculate_late_payment_penalty(self):
        """Test calcul pénalité retard de paiement"""
        # Arrange
        overdue_amount = 500.0
        days_late = 15
        penalty_rate = 0.02  # 2% par mois
        
        # Act
        penalty = self.financial_service.calculate_late_payment_penalty(
            overdue_amount, days_late, penalty_rate
        )
        
        # Assert
        # Calcul prorata mensuel
        monthly_penalty = overdue_amount * penalty_rate
        expected = (monthly_penalty / 30) * days_late
        self.assertAlmostEqual(penalty, expected, places=2)
    
    def test_calculate_budget_variance(self):
        """Test calcul écart budgétaire"""
        # Arrange
        budgeted_amount = 1000.0
        actual_amount = 1150.0
        
        # Act
        variance = self.financial_service.calculate_budget_variance(
            budgeted_amount, actual_amount
        )
        
        # Assert
        expected_variance = actual_amount - budgeted_amount
        expected_percentage = (expected_variance / budgeted_amount) * 100
        
        self.assertEqual(variance['amount'], expected_variance)
        self.assertEqual(variance['percentage'], expected_percentage)
        self.assertEqual(variance['status'], 'over_budget')
    
    def test_validate_payment_amount_valid(self):
        """Test validation montant paiement valide"""
        # Arrange
        payment_amount = 350.0
        expected_amount = 350.0
        tolerance = 0.01
        
        # Act
        is_valid = self.financial_service.validate_payment_amount(
            payment_amount, expected_amount, tolerance
        )
        
        # Assert
        self.assertTrue(is_valid)
    
    def test_validate_payment_amount_invalid(self):
        """Test validation montant paiement invalide"""
        # Arrange
        payment_amount = 300.0
        expected_amount = 350.0
        tolerance = 0.01
        
        # Act
        is_valid = self.financial_service.validate_payment_amount(
            payment_amount, expected_amount, tolerance
        )
        
        # Assert
        self.assertFalse(is_valid)
    
    def test_generate_financial_summary_for_building(self):
        """Test génération résumé financier immeuble"""
        # Act
        summary = self.financial_service.generate_building_financial_summary(
            self.test_condos, self.test_rates
        )
        
        # Assert
        self.assertIsInstance(summary, dict)
        self.assertIn('total_units', summary)
        self.assertIn('total_monthly_revenue', summary)
        self.assertIn('total_annual_revenue', summary)
        self.assertIn('breakdown_by_type', summary)
        self.assertIn('reserve_fund_total', summary)
        
        self.assertEqual(summary['total_units'], len(self.test_condos))
        self.assertGreater(summary['total_monthly_revenue'], 0)
    
    def test_calculate_debt_to_income_ratio(self):
        """Test calcul ratio dette/revenu"""
        # Arrange
        monthly_debt = 500.0
        monthly_income = 2000.0
        
        # Act
        ratio = self.financial_service.calculate_debt_to_income_ratio(
            monthly_debt, monthly_income
        )
        
        # Assert
        expected = (monthly_debt / monthly_income) * 100
        self.assertEqual(ratio, expected)
    
    def test_error_handling_zero_division(self):
        """Test gestion d'erreur division par zéro"""
        # Act & Assert
        with self.assertRaises(ValueError):
            self.financial_service.calculate_debt_to_income_ratio(500.0, 0.0)
    
    def test_error_handling_negative_amounts(self):
        """Test gestion d'erreur montants négatifs"""
        # Act & Assert
        with self.assertRaises(ValueError):
            self.financial_service.calculate_monthly_fees_with_taxes(
                self.test_condos[0], -0.15  # Taux négatif
            )
    
    def test_rounding_precision_currency(self):
        """Test précision arrondi pour montants monétaires"""
        # Arrange
        condo = self.test_condos[0]
        tax_rate = 0.123456  # Taux avec beaucoup de décimales
        
        # Act
        fees_with_tax = self.financial_service.calculate_monthly_fees_with_taxes(
            condo, tax_rate
        )
        
        # Assert
        # Doit être arrondi à 2 décimales pour monnaie
        self.assertEqual(len(str(fees_with_tax).split('.')[1]), 2)
    
    def test_functional_programming_fee_calculations(self):
        """Test programmation fonctionnelle dans calculs de frais"""
        # Act
        # Utilisation de map pour calculer frais de tous les condos
        all_monthly_fees = list(map(
            self.financial_service.calculate_monthly_fees, 
            self.test_condos
        ))
        
        # Utilisation de filter pour condos résidentiels
        residential_condos = list(filter(
            lambda c: c.condo_type == CondoType.RESIDENTIAL, 
            self.test_condos
        ))
        
        # Assert
        self.assertEqual(len(all_monthly_fees), len(self.test_condos))
        self.assertEqual(len(residential_condos), 2)
        self.assertTrue(all(isinstance(fee, (int, float)) for fee in all_monthly_fees))


if __name__ == '__main__':
    unittest.main()
