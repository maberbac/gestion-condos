"""
Tests unitaires pour l'entité Condo
Tests pour valider la logique métier de base
"""
import unittest
import sys
import os
from decimal import Decimal
from datetime import datetime

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from domain.entities.condo import Condo, CondoType, CondoStatus


class TestCondoEntity(unittest.TestCase):
    """Tests unitaires pour la classe Condo"""
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.valid_condo_data = {
            'unit_number': '101',
            'owner_name': 'Jean Dupont',
            'square_feet': 850.0,
            'condo_type': CondoType.RESIDENTIAL,
            'status': CondoStatus.ACTIVE,
            'purchase_date': datetime(2020, 1, 15),
            'monthly_fees_base': None
        }
    
    def test_creation_condo_valide(self):
        """Création d'un condo avec données valides"""
        # Arrange & Act
        condo = Condo(**self.valid_condo_data)
        
        # Assert
        self.assertEqual(condo.unit_number, '101')
        self.assertEqual(condo.owner_name, 'Jean Dupont')
        self.assertEqual(condo.square_feet, 850.0)
        self.assertEqual(condo.condo_type, CondoType.RESIDENTIAL)
        self.assertEqual(condo.status, CondoStatus.ACTIVE)
        self.assertEqual(condo.purchase_date, datetime(2020, 1, 15))
    
    def test_unit_number_obligatoire(self):
        """Le numéro d'unité est obligatoire"""
        # Arrange
        invalid_data = self.valid_condo_data.copy()
        del invalid_data['unit_number']
        
        # Act & Assert
        with self.assertRaises(TypeError):
            Condo(**invalid_data)
    
    def test_unit_number_non_vide(self):
        """Le numéro d'unité ne peut pas être vide"""
        # Arrange
        invalid_data = self.valid_condo_data.copy()
        invalid_data['unit_number'] = ''
        
        # Act & Assert
        with self.assertRaises(ValueError):
            Condo(**invalid_data)
    
    def test_unit_number_longueur_max(self):
        """Le numéro d'unité ne peut pas dépasser 10 caractères"""
        # Arrange
        invalid_data = self.valid_condo_data.copy()
        invalid_data['unit_number'] = '12345678901'  # 11 caractères
        
        # Act & Assert
        with self.assertRaises(ValueError):
            Condo(**invalid_data)
    
    def test_square_feet_positive(self):
        """La superficie doit être positive"""
        # Arrange
        invalid_data = self.valid_condo_data.copy()
        invalid_data['square_feet'] = -10.5
        
        # Act & Assert
        with self.assertRaises(ValueError):
            Condo(**invalid_data)
    
    def test_square_feet_limite_max(self):
        """La superficie ne peut pas être anormalement grande"""
        # Arrange
        invalid_data = self.valid_condo_data.copy()
        invalid_data['square_feet'] = 15000.0  # Plus de 10000
        
        # Act & Assert
        with self.assertRaises(ValueError):
            Condo(**invalid_data)
    
    def test_owner_name_obligatoire(self):
        """Le nom du propriétaire est obligatoire"""
        # Arrange
        invalid_data = self.valid_condo_data.copy()
        invalid_data['owner_name'] = ''
        
        # Act & Assert
        with self.assertRaises(ValueError):
            Condo(**invalid_data)
    
    def test_calcul_frais_mensuels_residential(self):
        """Calcul correct des frais mensuels pour unité résidentielle"""
        # Arrange
        condo = Condo(**self.valid_condo_data)
        
        # Act
        frais = condo.calculate_monthly_fees()
        
        # Assert
        # 850 pieds carrés * 0.45$ = 382.50$
        expected = Decimal('382.50')
        self.assertEqual(frais, expected)
    
    def test_calcul_frais_mensuels_commercial(self):
        """Calcul correct des frais mensuels pour unité commerciale"""
        # Arrange
        data = self.valid_condo_data.copy()
        data['condo_type'] = CondoType.COMMERCIAL
        condo = Condo(**data)
        
        # Act
        frais = condo.calculate_monthly_fees()
        
        # Assert
        # 850 pieds carrés * 0.60$ = 510.00$
        expected = Decimal('510.00')
        self.assertEqual(frais, expected)
    
    def test_calcul_frais_mensuels_parking(self):
        """Calcul correct des frais mensuels pour stationnement"""
        # Arrange
        data = self.valid_condo_data.copy()
        data['condo_type'] = CondoType.PARKING
        data['square_feet'] = 200.0
        condo = Condo(**data)
        
        # Act
        frais = condo.calculate_monthly_fees()
        
        # Assert
        # 200 pieds carrés * 0.15$ = 30.00$
        expected = Decimal('30.00')
        self.assertEqual(frais, expected)
    
    def test_calcul_frais_mensuels_storage(self):
        """Calcul correct des frais mensuels pour entreposage"""
        # Arrange
        data = self.valid_condo_data.copy()
        data['condo_type'] = CondoType.STORAGE
        data['square_feet'] = 100.0
        condo = Condo(**data)
        
        # Act
        frais = condo.calculate_monthly_fees()
        
        # Assert
        # 100 pieds carrés * 0.25$ = 25.00$
        expected = Decimal('25.00')
        self.assertEqual(frais, expected)
    
    def test_frais_base_personnalises(self):
        """Utilisation des frais de base personnalisés"""
        # Arrange
        data = self.valid_condo_data.copy()
        data['monthly_fees_base'] = Decimal('500.00')
        condo = Condo(**data)
        
        # Act
        frais = condo.calculate_monthly_fees()
        
        # Assert
        self.assertEqual(frais, Decimal('500.00'))
    
    def test_calcul_frais_annuels(self):
        """Calcul des frais annuels"""
        # Arrange
        condo = Condo(**self.valid_condo_data)
        
        # Act
        frais_annuels = condo.calculate_annual_fees()
        
        # Assert
        expected = Decimal('382.50') * 12  # 4590.00$
        self.assertEqual(frais_annuels, expected)
    
    def test_is_active_true(self):
        """Vérification qu'une unité active est détectée"""
        # Arrange
        condo = Condo(**self.valid_condo_data)
        
        # Act & Assert
        self.assertTrue(condo.is_active())
    
    def test_is_active_false(self):
        """Vérification qu'une unité inactive est détectée"""
        # Arrange
        data = self.valid_condo_data.copy()
        data['status'] = CondoStatus.INACTIVE
        condo = Condo(**data)
        
        # Act & Assert
        self.assertFalse(condo.is_active())
    
    def test_is_commercial_true(self):
        """Détection d'une unité commerciale"""
        # Arrange
        data = self.valid_condo_data.copy()
        data['condo_type'] = CondoType.COMMERCIAL
        condo = Condo(**data)
        
        # Act & Assert
        self.assertTrue(condo.is_commercial())
    
    def test_is_commercial_false(self):
        """Détection d'une unité non-commerciale"""
        # Arrange
        condo = Condo(**self.valid_condo_data)
        
        # Act & Assert
        self.assertFalse(condo.is_commercial())
    
    def test_ownership_duration_avec_date(self):
        """Calcul de la durée de possession avec date"""
        # Arrange
        data = self.valid_condo_data.copy()
        # Date il y a environ 5 ans
        data['purchase_date'] = datetime(2020, 1, 1)
        condo = Condo(**data)
        
        # Act
        duration = condo.get_ownership_duration_years()
        
        # Assert
        self.assertIsNotNone(duration)
        self.assertGreater(duration, 5.0)  # Plus de 5 ans
        self.assertLess(duration, 6.0)     # Moins de 6 ans
    
    def test_ownership_duration_sans_date(self):
        """Durée de possession sans date d'achat"""
        # Arrange
        data = self.valid_condo_data.copy()
        data['purchase_date'] = None
        condo = Condo(**data)
        
        # Act
        duration = condo.get_ownership_duration_years()
        
        # Assert
        self.assertIsNone(duration)


if __name__ == '__main__':
    unittest.main()
