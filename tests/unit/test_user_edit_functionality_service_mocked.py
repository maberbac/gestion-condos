"""
Tests unitaires pour la fonctionnalité d'édition d'utilisateur.

[ARCHITECTURE TDD]
Ces tests valident la logique métier de mise à jour d'utilisateur
dans UserService avec mocking complet des dépendances.
"""

import unittest
from unittest.mock import Mock, patch, AsyncMock
from src.infrastructure.logger_manager import get_logger

logger = get_logger(__name__)


class TestUserEditFunctionalityServiceMocked(unittest.TestCase):
    """Tests unitaires pour l'édition d'utilisateur avec mocks."""

    def setUp(self):
        """Configuration initiale des tests."""
        self.mock_repository = Mock()
        
        # Données de test
        self.existing_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'full_name': 'Test User',
            'role': 'resident',
            'condo_unit': '101',
            'password': 'password123'
        }
        
        self.update_data = {
            'username': 'testuser_updated',
            'email': 'updated@example.com',
            'full_name': 'Updated User',
            'role': 'admin',
            'condo_unit': '102',
            'password': 'newpassword123'
        }

    @patch('src.application.services.user_service.UserService._run_async_operation')
    def test_update_user_success_all_fields(self, mock_async_op):
        """Test mise à jour complète d'un utilisateur avec succès."""
        from src.application.services.user_service import UserService
        from src.domain.entities.user import User, UserRole
        
        # Arrange
        existing_user = Mock()
        existing_user.username = 'testuser'
        existing_user.email = 'test@example.com'
        existing_user.full_name = 'Test User'
        existing_user.role = UserRole.RESIDENT
        existing_user.condo_unit = '101'
        
        mock_async_op.side_effect = [
            existing_user,  # get_user_by_username pour utilisateur existant
            None,           # get_user_by_username pour nouveau nom (non existant)
            True            # update_user_by_username
        ]
        
        user_service = UserService()
        user_service.user_repository = self.mock_repository
        
        # Act
        result = user_service.update_user_by_username('testuser', self.update_data)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertIn('mis à jour avec succès', result['message'])
        self.assertEqual(mock_async_op.call_count, 3)

    @patch('src.application.services.user_service.UserService._run_async_operation')
    def test_update_user_not_found(self, mock_async_op):
        """Test mise à jour d'un utilisateur inexistant."""
        from src.application.services.user_service import UserService
        
        # Arrange
        mock_async_op.return_value = None  # Utilisateur non trouvé
        
        user_service = UserService()
        user_service.user_repository = self.mock_repository
        
        # Act
        result = user_service.update_user_by_username('nonexistent', self.update_data)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Utilisateur non trouvé')

    @patch('src.application.services.user_service.UserService._run_async_operation')
    def test_update_user_username_already_exists(self, mock_async_op):
        """Test mise à jour avec un nouveau nom d'utilisateur déjà existant."""
        from src.application.services.user_service import UserService
        from src.domain.entities.user import User, UserRole
        
        # Arrange
        existing_user = Mock()
        existing_user.username = 'testuser'
        existing_user.email = 'test@example.com'
        existing_user.role = UserRole.RESIDENT
        
        existing_new_user = Mock()
        existing_new_user.username = 'testuser_updated'
        
        mock_async_op.side_effect = [
            existing_user,      # get_user_by_username pour utilisateur existant
            existing_new_user   # get_user_by_username pour nouveau nom (existe déjà)
        ]
        
        user_service = UserService()
        user_service.user_repository = self.mock_repository
        
        # Act
        result = user_service.update_user_by_username('testuser', self.update_data)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertIn('existe déjà', result['error'])

    @patch('src.application.services.user_service.UserService._run_async_operation')
    def test_update_user_without_password(self, mock_async_op):
        """Test mise à jour sans changer le mot de passe."""
        from src.application.services.user_service import UserService
        from src.domain.entities.user import User, UserRole
        
        # Arrange
        existing_user = Mock()
        existing_user.username = 'testuser'
        existing_user.email = 'test@example.com'
        existing_user.role = UserRole.RESIDENT
        existing_user.password = 'existing_password_hash'
        
        update_data_no_password = self.update_data.copy()
        del update_data_no_password['password']
        
        mock_async_op.side_effect = [
            existing_user,  # get_user_by_username
            None,           # get_user_by_username pour nouveau nom
            True            # update_user_by_username
        ]
        
        user_service = UserService()
        user_service.user_repository = self.mock_repository
        
        # Act
        result = user_service.update_user_by_username('testuser', update_data_no_password)
        
        # Assert
        self.assertTrue(result['success'])

    @patch('src.application.services.user_service.UserService._run_async_operation')
    def test_update_user_validation_error(self, mock_async_op):
        """Test mise à jour avec erreur de validation."""
        from src.application.services.user_service import UserService
        from src.domain.entities.user import User, UserRole
        
        # Arrange
        existing_user = Mock()
        existing_user.username = 'testuser'
        existing_user.role = UserRole.RESIDENT
        
        mock_async_op.side_effect = [
            existing_user,  # get_user_by_username
            None,           # get_user_by_username pour nouveau nom
            ValueError("Erreur de validation")  # update_user_by_username
        ]
        
        user_service = UserService()
        user_service.user_repository = self.mock_repository
        
        # Act
        result = user_service.update_user_by_username('testuser', self.update_data)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertIn('Erreur de validation', result['error'])

    @patch('src.application.services.user_service.UserService._run_async_operation')
    def test_update_user_repository_failure(self, mock_async_op):
        """Test mise à jour avec échec du repository."""
        from src.application.services.user_service import UserService
        from src.domain.entities.user import User, UserRole
        
        # Arrange
        existing_user = Mock()
        existing_user.username = 'testuser'
        existing_user.role = UserRole.RESIDENT
        
        mock_async_op.side_effect = [
            existing_user,  # get_user_by_username
            None,           # get_user_by_username pour nouveau nom
            False           # update_user_by_username (échec)
        ]
        
        user_service = UserService()
        user_service.user_repository = self.mock_repository
        
        # Act
        result = user_service.update_user_by_username('testuser', self.update_data)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Échec de la mise à jour')


if __name__ == '__main__':
    unittest.main()
