"""
Tests d'intégration pour les routes de gestion des condos.
"""

import unittest
from unittest.mock import patch
import sys
import os

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.web.condo_app import app
from src.application.services.project_service import ProjectService


class TestCondoRoutesIntegration(unittest.TestCase):
    """Tests d'intégration pour les routes de gestion des condos."""
    
    def setUp(self):
        """Configuration initiale pour chaque test."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Importer et initialiser les services
        from src.web.condo_app import ensure_services_initialized
        with self.app.app_context():
            ensure_services_initialized()
        
        # Configuration de session pour simuler un utilisateur connecté
        with self.client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'admin'
            sess['user_role'] = 'admin'

    @patch('src.web.condo_app.condo_service')
    def test_condos_list_get(self, mock_condo_service):
        """Test de récupération de la liste des condos."""
        # Mock du service pour retourner une liste de condos
        mock_condos = [
            {
                'unit_number': 'TEST-001',
                'owner_name': 'Test Owner',
                'square_feet': 850,
                'condo_type': 'residential',
                'status': 'active',
                'unit_type': 'residential'
            }
        ]
        mock_condo_service.get_all_condos.return_value = mock_condos
        mock_condo_service.get_statistics.return_value = {
            'total_condos': 1,
            'occupied': 1,
            'vacant': 0,
            'residential': 1,
            'commercial': 0,
            'parking': 0,
            'storage': 0,
            'total_revenue': 450
        }
        
        response = self.client.get('/condos')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Gestion des Condos', response.data)

    @patch('src.web.condo_app.condo_service')
    def test_condo_details_existing_unit(self, mock_condo_service):
        """Test accès aux détails d'un condo existant."""
        # Mock du service pour retourner une unité avec la structure dictionnaire attendue
        mock_condo = {
            'unit_number': 'TEST-001',
            'owner_name': 'Test Owner',
            'square_feet': 850,
            'unit_type': {'name': 'RESIDENTIAL'},
            'status': 'AVAILABLE',
            'monthly_fees': 450,
            'building_name': 'Test Building',
            'is_available': True,
            'type_icon': '🏠',
            'status_icon': '✅',
            'is_sold': False
        }
        
        mock_condo_service.get_condo_by_unit_number.return_value = mock_condo
        mock_condo_service.get_all_condos.return_value = [mock_condo]
        
        response = self.client.get('/condos/TEST-001/details')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'TEST-001', response.data)
        # Vérifier que les détails sont affichés
        self.assertIn(b'Test Owner', response.data)

    @patch('src.web.condo_app.condo_service.get_condo_by_unit_number')
    def test_condo_details_nonexistent_unit(self, mock_get_condo_by_unit_number):
        """Test accès aux détails d'un condo inexistant."""
        # Mock du service pour retourner None
        mock_get_condo_by_unit_number.return_value = None
        
        response = self.client.get('/condos/INEXISTANT-999')

        # Peut être une redirection vers la liste des condos ou une erreur 404
        self.assertIn(response.status_code, [302, 404])

    @patch('src.web.condo_app.condo_service')
    def test_edit_condo_get_form_existing(self, mock_condo_service):
        """Test de récupération du formulaire d'édition pour un condo existant."""
        # Mock du service pour retourner une unité existante
        mock_condo = {
            'unit_number': 'TEST-001',
            'owner_name': 'Test Owner',
            'square_feet': 850,
            'condo_type': 'residential',
            'status': 'active',
            'monthly_fees': 450,
            'building_name': 'Test Building',
            'is_sold': True
        }
        mock_condo_service.get_condo_by_unit_number.return_value = mock_condo
        
        response = self.client.get('/condos/TEST-001/edit')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'TEST-001', response.data)
        mock_condo_service.get_condo_by_unit_number.assert_called_once_with('TEST-001')

    @patch('src.web.condo_app.condo_service.get_condo_by_unit_number')
    def test_edit_condo_get_form_nonexistent(self, mock_get_condo_by_unit_number):
        """Test de récupération du formulaire d'édition pour un condo inexistant."""
        # Mock du service pour retourner None
        mock_get_condo_by_unit_number.return_value = None
        
        response = self.client.get('/condos/INEXISTANT-999/edit')

        # Doit rediriger ou retourner une erreur
        self.assertIn(response.status_code, [302, 404])

    @patch('src.web.condo_app.condo_service.get_condo_by_unit_number')
    @patch('src.web.condo_app.condo_service.update_condo')
    def test_edit_condo_post_valid_data(self, mock_update_condo, mock_get_condo_by_unit_number):
        """Test de soumission du formulaire d'édition avec données valides."""
        # Mock du service pour retourner une unité existante
        mock_condo = {
            'unit_number': 'TEST-001',
            'owner_name': 'Test Owner',
            'square_feet': 850,
            'condo_type': 'residential',
            'status': 'active'
        }
        mock_get_condo_by_unit_number.return_value = mock_condo
        mock_update_condo.return_value = True
        
        form_data = {
            'owner_name': 'Nouveau Propriétaire',
            'square_feet': '900',
            'condo_type': 'residential',
            'status': 'active'
        }
        
        response = self.client.post('/condos/TEST-001/edit', data=form_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        mock_update_condo.assert_called_once()

    @patch('src.web.condo_app.condo_service.get_condo_by_unit_number')
    def test_edit_condo_post_invalid_data(self, mock_get_condo_by_unit_number):
        """Test de soumission du formulaire d'édition avec données invalides."""
        # Mock du service pour retourner une unité existante
        mock_condo = {
            'unit_number': 'TEST-001',
            'owner_name': 'Test Owner',
            'square_feet': 850,
            'condo_type': 'residential',
            'status': 'active'
        }
        mock_get_condo_by_unit_number.return_value = mock_condo
        
        form_data = {
            'owner_name': '',  # Nom vide - invalide
            'square_feet': 'abc',  # Non numérique - invalide
            'condo_type': '',
            'status': ''
        }
        
        response = self.client.post('/condos/TEST-001/edit', data=form_data)

        # Doit retourner le formulaire avec erreurs ou rediriger
        self.assertIn(response.status_code, [200, 302])

    @patch('src.web.condo_app.condo_service')
    def test_add_condo_post_valid_data(self, mock_condo_service):
        """Test d'ajout d'un nouveau condo avec données valides."""
        mock_condo_service.create_condo.return_value = True
        
        form_data = {
            'unit_number': 'NEW-001',
            'owner_name': 'Nouveau Propriétaire',
            'square_feet': '800',
            'condo_type': 'residential',
            'status': 'active'
        }
        
        response = self.client.post('/condos/create', data=form_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        mock_condo_service.create_condo.assert_called_once()

    def test_add_condo_post_invalid_data(self):
        """Test d'ajout d'un nouveau condo avec données invalides."""
        form_data = {
            'unit_number': '',  # Numéro vide - invalide
            'owner_name': '',
            'square_feet': 'abc',
            'condo_type': '',
            'status': ''
        }
        
        response = self.client.post('/condos/create', data=form_data)

        # Doit retourner le formulaire avec erreurs ou rediriger
        self.assertIn(response.status_code, [200, 302])

    @patch('src.web.condo_app.condo_service.get_condo_by_unit_number')
    @patch('src.web.condo_app.condo_service.delete_condo')
    def test_delete_condo_existing_unit(self, mock_delete_condo, mock_get_condo_by_unit_number):
        """Test de suppression d'un condo existant."""
        # Mock du service pour retourner une unité existante
        mock_condo = {
            'unit_number': 'TEST-001',
            'owner_name': 'Test Owner',
            'square_feet': 850,
            'condo_type': 'residential',
            'status': 'active'
        }
        mock_get_condo_by_unit_number.return_value = mock_condo
        mock_delete_condo.return_value = True
        
        response = self.client.post('/condos/TEST-001/delete', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        mock_delete_condo.assert_called_once_with('TEST-001')

    @patch('src.web.condo_app.condo_service.get_condo_by_unit_number')
    def test_delete_condo_nonexistent_unit(self, mock_get_condo_by_unit_number):
        """Test de suppression d'un condo inexistant."""
        # Mock du service pour retourner None
        mock_get_condo_by_unit_number.return_value = None
        
        response = self.client.post('/condos/INEXISTANT-999/delete')

        # Doit rediriger ou retourner une erreur
        self.assertIn(response.status_code, [302, 404])


if __name__ == '__main__':
    unittest.main()
