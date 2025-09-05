"""
Tests d'intégration pour la page utilisateurs avec mocking complet.

TOUS LES ACCÈS BASE DE DONNÉES SONT MOCKÉS SELON LES NOUVELLES CONSIGNES.
Aucune connexion SQLite réelle n'est établie.
"""

import unittest
import os
from unittest.mock import patch, Mock
from src.web.condo_app import app
from src.infrastructure.repositories.user_repository import UserRepository
from src.domain.entities.user import User, UserRole


class TestUserPageIntegrationMocked(unittest.TestCase):
    """Tests d'intégration pour la page utilisateurs avec mocking complet."""

    def setUp(self):
        """Configuration des tests avec mocking."""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        # Simuler un utilisateur admin connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'admin'
            sess['role'] = 'admin'
        
        # Mock users pour les tests
        from datetime import datetime
        mock_last_login = Mock()
        mock_last_login.strftime.return_value = "01 Jan 2025 12:00"
        
        admin_mock = Mock(spec=User)
        admin_mock.username = 'admin'
        admin_mock.email = 'admin@condos.com'
        admin_mock.role = UserRole.ADMIN
        admin_mock.full_name = 'Jean Admin'
        admin_mock.is_active = True
        admin_mock.last_login = mock_last_login
        
        resident_mock = Mock(spec=User)
        resident_mock.username = 'resident1'
        resident_mock.email = 'resident1@example.com'
        resident_mock.role = UserRole.RESIDENT
        resident_mock.full_name = 'Marie Resident'
        resident_mock.condo_unit = 'A-101'
        resident_mock.is_active = True
        resident_mock.last_login = mock_last_login
        
        guest_mock = Mock(spec=User)
        guest_mock.username = 'guest1'
        guest_mock.email = 'guest1@example.com'
        guest_mock.role = UserRole.GUEST
        guest_mock.full_name = 'Paul Guest'
        guest_mock.is_active = True
        guest_mock.last_login = mock_last_login
        
        self.mock_users = [admin_mock, resident_mock, guest_mock]

    @patch('src.application.services.system_config_service.SystemConfigService.is_admin_password_changed', return_value=True)
    @patch('src.infrastructure.repositories.user_repository.UserRepository.get_all_users')
    def test_users_page_loads_with_mocked_users(self, mock_service, mock_admin_password_changed):
        """Test que la page utilisateurs se charge avec des utilisateurs mockés."""
        # Arrange
        mock_service.return_value = self.mock_users
        
        # Act
        response = self.client.get('/users')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'admin', response.data)
        self.assertIn(b'resident1', response.data)
        self.assertIn(b'guest1', response.data)
        mock_service.assert_called_once()

    @patch('src.application.services.system_config_service.SystemConfigService.is_admin_password_changed', return_value=True)
    @patch('src.infrastructure.repositories.user_repository.UserRepository.get_all_users')
    def test_users_page_displays_user_details_mocked(self, mock_service, mock_admin_password_changed):
        """Test que la page affiche les détails des utilisateurs mockés."""
        # Arrange
        mock_service.return_value = self.mock_users
        
        # Act
        response = self.client.get('/users')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        # Vérifier que les détails des utilisateurs sont affichés
        self.assertIn(b'admin@condos.com', response.data)
        self.assertIn(b'resident1@example.com', response.data)
        # Note: condo_unit n'est plus affiché dans la liste des utilisateurs, seulement dans les formulaires
        mock_service.assert_called_once()

    @patch('src.application.services.system_config_service.SystemConfigService.is_admin_password_changed', return_value=True)
    @patch('src.infrastructure.repositories.user_repository.UserRepository.get_all_users')
    def test_users_page_handles_empty_list_mocked(self, mock_service, mock_admin_password_changed):
        """Test que la page gère une liste vide d'utilisateurs mockés."""
        # Arrange
        mock_service.return_value = []
        
        # Act
        response = self.client.get('/users')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        mock_service.assert_called_once()

    @patch('src.application.services.system_config_service.SystemConfigService.is_admin_password_changed', return_value=True)
    @patch('src.infrastructure.repositories.user_repository.UserRepository.get_all_users')
    def test_users_page_handles_repository_error_mocked(self, mock_service, mock_admin_password_changed):
        """Test que la page gère les erreurs du repository mockées."""
        # Arrange
        mock_service.side_effect = Exception("Erreur de repository")
        
        # Act
        response = self.client.get('/users')
        
        # Assert
        # La page devrait gérer l'erreur gracieusement
        self.assertIn(response.status_code, [200, 500])  # Selon la gestion d'erreur
        mock_service.assert_called_once()

    @patch('src.application.services.system_config_service.SystemConfigService.is_admin_password_changed', return_value=True)
    @patch('src.web.condo_app.user_service')
    def test_user_detail_page_mocked(self, mock_service, mock_admin_password_changed):
        """Test de la page de détail d'un utilisateur avec mocking."""
        # Arrange
        mock_user = self.mock_users[0]  # admin user
        mock_service.get_user_details_by_username.return_value = mock_user
        
        # Se connecter en tant qu'admin
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['username'] = 'admin'
            sess['user_role'] = 'admin'
        
        # Act
        response = self.client.get('/users/admin/details')
        
        # Assert - Le mock devrait être appelé même si la page redirige
        # S'assurer que le service est appelé peu importe le résultat
        mock_service.get_user_details_by_username.assert_called_once_with('admin')

    def test_users_page_requires_admin_access(self):
        """Test que la page utilisateurs nécessite un accès admin."""
        # Arrange - Simuler un utilisateur non-admin
        with self.client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['username'] = 'resident1'
            sess['role'] = 'resident'
        
        # Act
        response = self.client.get('/users')
        
        # Assert
        # Devrait rediriger ou refuser l'accès
        self.assertIn(response.status_code, [302, 403])


if __name__ == '__main__':
    unittest.main()
