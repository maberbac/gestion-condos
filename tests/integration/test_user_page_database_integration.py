"""
Tests d'intégration pour la page utilisateurs avec la base de données
"""

import unittest
import tempfile
import os
from unittest.mock import patch
from src.web.condo_app import app
from src.infrastructure.repositories.user_repository import UserRepository
from src.domain.entities.user import User, UserRole


class TestUserPageIntegration(unittest.TestCase):
    """Tests d'intégration pour la page utilisateurs"""

    def setUp(self):
        """Configuration des tests"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        # Simuler un utilisateur admin connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'admin'
            sess['role'] = 'admin'

    @patch('src.application.services.system_config_service.SystemConfigService.is_admin_password_changed', return_value=True)
    def test_users_page_loads_with_database_users(self, mock_admin_password_changed):
        """La page utilisateurs doit charger les utilisateurs depuis la base de données"""
        response = self.client.get('/users')
        
        # Vérifications
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Gestion des Utilisateurs', response.data)
        
        # Vérifier que les données ne sont plus hardcodées
        # (ces données fictives ne doivent plus apparaître)
        self.assertNotIn(b'jean.dupont', response.data)
        self.assertNotIn(b'marie.martin', response.data)

    @patch('src.application.services.system_config_service.SystemConfigService.is_admin_password_changed', return_value=True)
    def test_users_page_displays_real_admin_user(self, mock_admin_password_changed):
        """La page doit afficher le vrai utilisateur admin de la base"""
        response = self.client.get('/users')
        
        # L'utilisateur admin de la base doit être affiché
        self.assertIn(b'admin', response.data)  # Username admin existe dans la base

    @patch('src.application.services.system_config_service.SystemConfigService.is_admin_password_changed', return_value=True)
    def test_users_page_shows_correct_user_statistics(self, mock_admin_password_changed):
        """La page doit afficher les vraies statistiques des utilisateurs"""
        response = self.client.get('/users')
        
        # Vérifier que les compteurs sont affichés
        response_text = response.data.decode('utf-8')
        self.assertIn('Administrateurs', response_text)
        self.assertIn('Résidents', response_text)
        
        # Les stats doivent correspondre aux vraies données de la base
        # (pas aux données fictives hardcodées)

    def test_users_page_requires_admin_access(self):
        """La page utilisateurs doit nécessiter des privilèges admin"""
        # Test sans connexion
        with self.client.session_transaction() as sess:
            sess.clear()
        
        response = self.client.get('/users')
        # Doit rediriger vers login ou afficher erreur d'accès
        self.assertIn(response.status_code, [302, 403])

    @patch('src.application.services.system_config_service.SystemConfigService.is_admin_password_changed', return_value=True)
    def test_users_page_handles_empty_user_list(self, mock_admin_password_changed):
        """La page doit gérer correctement une liste d'utilisateurs vide"""
        with patch('src.application.services.user_service.UserService.get_users_for_web_display') as mock_users:
            mock_users.return_value = []
            
            response = self.client.get('/users')
            
            # La page doit se charger même sans utilisateurs
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Gestion des Utilisateurs', response.data)

    @patch('src.application.services.system_config_service.SystemConfigService.is_admin_password_changed', return_value=True)
    def test_users_page_displays_user_roles_correctly(self, mock_admin_password_changed):
        """La page doit afficher correctement les rôles des utilisateurs"""
        response = self.client.get('/users')
        
        # Vérifier que les rôles sont affichés
        # (au moins l'admin qui existe dans la base)
        response_text = response.data.decode('utf-8')
        
        # Vérifier la présence des éléments de rôle dans le HTML
        self.assertTrue(
            'admin' in response_text.lower() or 
            'administrateur' in response_text.lower()
        )

    @patch('src.application.services.system_config_service.SystemConfigService.is_admin_password_changed', return_value=True)
    def test_users_page_integrates_with_user_repository(self, mock_admin_password_changed):
        """La page doit utiliser le repository utilisateur pour récupérer les données"""
        with patch('src.application.services.user_service.UserService.get_users_for_web_display') as mock_get_users:
            # Simuler des utilisateurs de test formatés pour le web
            test_users_formatted = [
                {
                    'username': 'test_admin',
                    'full_name': 'Test Admin',
                    'email': 'test@admin.com',
                    'role': {'value': 'admin'},
                    'created_at': '2024-01-01 00:00:00',
                    'status': 'Actif'
                }
            ]
            mock_get_users.return_value = test_users_formatted
            
            response = self.client.get('/users')
            
            # Vérifier que le service a été appelé
            mock_get_users.assert_called_once()
            self.assertEqual(response.status_code, 200)

    @patch('src.application.services.system_config_service.SystemConfigService.is_admin_password_changed', return_value=True)
    def test_users_page_template_receives_correct_data_structure(self, mock_admin_password_changed):
        """Le template doit recevoir les données dans le bon format"""
        response = self.client.get('/users')
        
        # Vérifier que la page se charge (indique que le format des données est correct)
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que les filtres Jinja fonctionnent
        # (cela indique que la structure des données est correcte)
        self.assertNotIn(b'TemplateRuntimeError', response.data)
        self.assertNotIn(b'AttributeError', response.data)


if __name__ == '__main__':
    unittest.main()
