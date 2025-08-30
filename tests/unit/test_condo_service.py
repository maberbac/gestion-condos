"""
Tests unitaires pour le service de gestion des condos.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.application.services.condo_service import CondoService
from src.domain.entities.condo import CondoType, CondoStatus


class TestCondoService(unittest.TestCase):
    """Tests pour le service de gestion des condos."""
    
    def setUp(self):
        """Configuration initiale pour chaque test."""
        self.service = CondoService()
    
    def test_get_all_condos_admin(self):
        """Test récupération de tous les condos pour un admin."""
        condos = self.service.get_all_condos('admin')
        
        # Vérifier qu'on a récupéré des condos
        self.assertGreater(len(condos), 0)
        
        # Vérifier la structure des données
        for condo in condos:
            self.assertIn('unit_number', condo)
            self.assertIn('owner_name', condo)
            self.assertIn('square_feet', condo)
            self.assertIn('unit_type', condo)
            self.assertIn('monthly_fees', condo)
            self.assertIn('type_icon', condo)
            self.assertIn('status_icon', condo)
    
    def test_get_all_condos_resident(self):
        """Test récupération des condos pour un résident."""
        condos = self.service.get_all_condos('resident')
        
        # Vérifier que seuls les condos résidentiels et commerciaux sont visibles
        for condo in condos:
            self.assertIn(condo['unit_type']['name'], ['RESIDENTIAL', 'COMMERCIAL'])
    
    def test_get_all_condos_guest(self):
        """Test récupération des condos pour un invité."""
        condos = self.service.get_all_condos('guest')
        
        # Vérifier que seuls les condos disponibles sont visibles
        for condo in condos:
            self.assertTrue(condo['is_available'])
    
    def test_get_condo_by_unit_number_found(self):
        """Test récupération d'un condo existant par numéro d'unité."""
        condo = self.service.get_condo_by_unit_number('A-101')
        
        self.assertIsNotNone(condo)
        self.assertEqual(condo['unit_number'], 'A-101')
        self.assertIn('owner_name', condo)
        self.assertIn('square_feet', condo)
    
    def test_get_condo_by_unit_number_not_found(self):
        """Test récupération d'un condo inexistant."""
        condo = self.service.get_condo_by_unit_number('Z-999')
        
        self.assertIsNone(condo)
    
    def test_create_condo_success(self):
        """Test création réussie d'un nouveau condo."""
        initial_count = len(self.service._demo_condos)
        
        condo_data = {
            'unit_number': 'TEST-001',
            'owner_name': 'Test Owner',
            'square_feet': 800,
            'condo_type': 'residential',
            'status': 'active',
            'monthly_fees': 450,
            'building_name': 'Test Building',
            'is_sold': False
        }
        
        result = self.service.create_condo(condo_data)
        
        self.assertTrue(result)
        self.assertEqual(len(self.service._demo_condos), initial_count + 1)
        
        # Vérifier que le condo a été ajouté
        created_condo = self.service.get_condo_by_unit_number('TEST-001')
        self.assertIsNotNone(created_condo)
        self.assertEqual(created_condo['owner_name'], 'Test Owner')
    
    def test_create_condo_duplicate_unit_number(self):
        """Test création d'un condo avec un numéro d'unité existant."""
        condo_data = {
            'unit_number': 'A-101',  # Numéro existant
            'owner_name': 'Test Owner',
            'square_feet': 800,
            'condo_type': 'residential',
            'status': 'active',
            'monthly_fees': 450
        }
        
        result = self.service.create_condo(condo_data)
        
        self.assertFalse(result)
    
    def test_create_condo_missing_unit_number(self):
        """Test création d'un condo sans numéro d'unité."""
        condo_data = {
            'owner_name': 'Test Owner',
            'square_feet': 800,
            'condo_type': 'residential',
            'status': 'active',
            'monthly_fees': 450
        }
        
        result = self.service.create_condo(condo_data)
        
        self.assertFalse(result)
    
    def test_update_condo_success(self):
        """Test modification réussie d'un condo existant."""
        original_condo = self.service.get_condo_by_unit_number('A-101')
        original_owner = original_condo['owner_name']
        
        update_data = {
            'owner_name': 'Updated Owner',
            'square_feet': 900,
            'monthly_fees': 500
        }
        
        result = self.service.update_condo('A-101', update_data)
        
        self.assertTrue(result)
        
        # Vérifier que les modifications ont été appliquées
        updated_condo = self.service.get_condo_by_unit_number('A-101')
        self.assertEqual(updated_condo['owner_name'], 'Updated Owner')
        self.assertEqual(updated_condo['square_feet'], 900)
        self.assertEqual(updated_condo['monthly_fees'], 500)
    
    def test_update_condo_not_found(self):
        """Test modification d'un condo inexistant."""
        update_data = {
            'owner_name': 'Updated Owner'
        }
        
        result = self.service.update_condo('Z-999', update_data)
        
        self.assertFalse(result)
    
    def test_delete_condo_success(self):
        """Test suppression réussie d'un condo."""
        # Créer un condo temporaire pour le test
        self.service.create_condo({
            'unit_number': 'TEMP-001',
            'owner_name': 'Temp Owner',
            'square_feet': 800,
            'condo_type': 'residential',
            'monthly_fees': 400
        })
        
        initial_count = len(self.service._demo_condos)
        
        result = self.service.delete_condo('TEMP-001')
        
        self.assertTrue(result)
        self.assertEqual(len(self.service._demo_condos), initial_count - 1)
        
        # Vérifier que le condo n'existe plus
        deleted_condo = self.service.get_condo_by_unit_number('TEMP-001')
        self.assertIsNone(deleted_condo)
    
    def test_delete_condo_not_found(self):
        """Test suppression d'un condo inexistant."""
        initial_count = len(self.service._demo_condos)
        
        result = self.service.delete_condo('Z-999')
        
        self.assertFalse(result)
        self.assertEqual(len(self.service._demo_condos), initial_count)
    
    def test_get_statistics(self):
        """Test calcul des statistiques des condos."""
        stats = self.service.get_statistics()
        
        # Vérifier que les statistiques contiennent les bonnes clés
        expected_keys = [
            'total_condos', 'occupied', 'vacant',
            'residential', 'commercial', 'parking',
            'total_monthly_revenue', 'total_area', 'average_area'
        ]
        
        for key in expected_keys:
            self.assertIn(key, stats)
        
        # Vérifier la cohérence des données
        self.assertEqual(stats['total_condos'], stats['occupied'] + stats['vacant'])
        self.assertGreaterEqual(stats['total_area'], 0)
        self.assertGreaterEqual(stats['average_area'], 0)
    
    def test_get_type_icon(self):
        """Test récupération des icônes par type."""
        # Test avec chaque type de condo
        residential_icon = self.service._get_type_icon(CondoType.RESIDENTIAL)
        self.assertEqual(residential_icon, '🏠')
        
        commercial_icon = self.service._get_type_icon(CondoType.COMMERCIAL)
        self.assertEqual(commercial_icon, '🏢')
        
        parking_icon = self.service._get_type_icon(CondoType.PARKING)
        self.assertEqual(parking_icon, '🚗')
        
        storage_icon = self.service._get_type_icon(CondoType.STORAGE)
        self.assertEqual(storage_icon, '📦')
    
    def test_get_status_icon(self):
        """Test récupération des icônes par statut."""
        # Test avec chaque statut
        active_icon = self.service._get_status_icon(CondoStatus.ACTIVE)
        self.assertEqual(active_icon, '✅')
        
        inactive_icon = self.service._get_status_icon(CondoStatus.INACTIVE)
        self.assertEqual(inactive_icon, '❌')
        
        maintenance_icon = self.service._get_status_icon(CondoStatus.MAINTENANCE)
        self.assertEqual(maintenance_icon, '🔧')
        
        sold_icon = self.service._get_status_icon(CondoStatus.SOLD)
        self.assertEqual(sold_icon, '💰')


if __name__ == '__main__':
    unittest.main()
