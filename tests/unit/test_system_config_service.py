"""
Tests unitaires pour SystemConfigService

Tests utilisant TDD (Red-Green-Refactor) pour le service de configuration système,
avec mocking complet des dépendances.
"""

import unittest
from unittest.mock import Mock, patch
import asyncio

from src.application.services.system_config_service import SystemConfigService
from src.adapters.system_config_repository_sqlite import SystemConfigRepositorySQLite, SystemConfigRepositorySQLiteError

class TestSystemConfigService(unittest.TestCase):
    """Tests unitaires pour le service de configuration système."""

    def setUp(self):
        """Configuration avant chaque test."""
        # Mock du repository
        self.mock_repository = Mock(spec=SystemConfigRepositorySQLite)
        
        # Service sous test avec mock
        self.service = SystemConfigService(self.mock_repository)

    def test_is_admin_password_changed_returns_true_when_config_exists_and_true(self):
        """Test que is_admin_password_changed retourne True quand la config existe et vaut True."""
        # ARRANGE
        self.mock_repository.get_boolean_config.return_value = True
        
        # ACT
        result = self.service.is_admin_password_changed()
        
        # ASSERT
        self.assertTrue(result)
        self.mock_repository.get_boolean_config.assert_called_once_with('admin_password_changed', False)

    def test_is_admin_password_changed_returns_false_when_config_not_exists(self):
        """Test que is_admin_password_changed retourne False quand la config n'existe pas."""
        # ARRANGE
        self.mock_repository.get_boolean_config.return_value = False
        
        # ACT
        result = self.service.is_admin_password_changed()
        
        # ASSERT
        self.assertFalse(result)
        self.mock_repository.get_boolean_config.assert_called_once_with('admin_password_changed', False)

    def test_is_admin_password_changed_returns_false_on_repository_error(self):
        """Test que is_admin_password_changed retourne False en cas d'erreur repository."""
        # ARRANGE
        self.mock_repository.get_boolean_config.side_effect = Exception("Erreur base de données")
        
        # ACT
        result = self.service.is_admin_password_changed()
        
        # ASSERT
        self.assertFalse(result)

    def test_mark_admin_password_changed_success(self):
        """Test de marquage réussi du changement de mot de passe admin."""
        # ARRANGE
        self.mock_repository.set_boolean_config.return_value = True
        
        # ACT
        result = self.service.mark_admin_password_changed()
        
        # ASSERT
        self.assertTrue(result)
        self.mock_repository.set_boolean_config.assert_called_once_with(
            'admin_password_changed', 
            True, 
            'Indique si l\'administrateur a changé son mot de passe par défaut'
        )

    def test_mark_admin_password_changed_failure(self):
        """Test d'échec du marquage du changement de mot de passe admin."""
        # ARRANGE
        self.mock_repository.set_boolean_config.return_value = False
        
        # ACT
        result = self.service.mark_admin_password_changed()
        
        # ASSERT
        self.assertFalse(result)
        self.mock_repository.set_boolean_config.assert_called_once()

    def test_mark_admin_password_changed_exception(self):
        """Test du marquage avec exception du repository."""
        # ARRANGE
        self.mock_repository.set_boolean_config.side_effect = Exception("Erreur DB")
        
        # ACT
        result = self.service.mark_admin_password_changed()
        
        # ASSERT
        self.assertFalse(result)

    def test_reset_admin_password_status_success(self):
        """Test de remise à zéro réussie du statut admin password."""
        # ARRANGE
        self.mock_repository.set_boolean_config.return_value = True
        
        # ACT
        result = self.service.reset_admin_password_status()
        
        # ASSERT
        self.assertTrue(result)
        self.mock_repository.set_boolean_config.assert_called_once_with(
            'admin_password_changed', 
            False, 
            'Indique si l\'administrateur a changé son mot de passe par défaut'
        )

    def test_is_system_setup_completed_when_admin_password_changed(self):
        """Test que is_system_setup_completed retourne True quand admin password changé."""
        # ARRANGE
        self.mock_repository.get_boolean_config.return_value = True
        
        # ACT
        result = self.service.is_system_setup_completed()
        
        # ASSERT
        self.assertTrue(result)

    def test_is_system_setup_completed_when_admin_password_not_changed(self):
        """Test que is_system_setup_completed retourne False quand admin password non changé."""
        # ARRANGE
        self.mock_repository.get_boolean_config.return_value = False
        
        # ACT
        result = self.service.is_system_setup_completed()
        
        # ASSERT
        self.assertFalse(result)

    def test_get_system_setup_status_complete_setup(self):
        """Test du statut de setup quand setup terminé."""
        # ARRANGE
        self.mock_repository.get_boolean_config.return_value = True
        
        # ACT
        result = self.service.get_system_setup_status()
        
        # ASSERT
        expected = {
            'admin_password_changed': True,
            'setup_completed': True
        }
        self.assertEqual(result, expected)

    def test_get_system_setup_status_incomplete_setup(self):
        """Test du statut de setup quand setup non terminé."""
        # ARRANGE
        self.mock_repository.get_boolean_config.return_value = False
        
        # ACT
        result = self.service.get_system_setup_status()
        
        # ASSERT
        expected = {
            'admin_password_changed': False,
            'setup_completed': False
        }
        self.assertEqual(result, expected)

    def test_get_config_value_success(self):
        """Test de récupération réussie d'une valeur de configuration."""
        # ARRANGE
        expected_value = "test_value"
        self.mock_repository.get_config_value.return_value = expected_value
        
        # ACT
        result = self.service.get_config_value("test_key")
        
        # ASSERT
        self.assertEqual(result, expected_value)
        self.mock_repository.get_config_value.assert_called_once_with("test_key")

    def test_get_config_value_exception(self):
        """Test de récupération avec exception du repository."""
        # ARRANGE
        self.mock_repository.get_config_value.side_effect = Exception("Erreur DB")
        
        # ACT
        result = self.service.get_config_value("test_key")
        
        # ASSERT
        self.assertIsNone(result)

    def test_set_config_value_success(self):
        """Test de définition réussie d'une valeur de configuration."""
        # ARRANGE
        self.mock_repository.set_config_value.return_value = True
        
        # ACT
        result = self.service.set_config_value("test_key", "test_value", "string", "Description test")
        
        # ASSERT
        self.assertTrue(result)
        self.mock_repository.set_config_value.assert_called_once_with(
            "test_key", "test_value", "string", "Description test"
        )

    def test_get_boolean_config_success(self):
        """Test de récupération réussie d'une configuration booléenne."""
        # ARRANGE
        self.mock_repository.get_boolean_config.return_value = True
        
        # ACT
        result = self.service.get_boolean_config("test_flag", False)
        
        # ASSERT
        self.assertTrue(result)
        self.mock_repository.get_boolean_config.assert_called_once_with("test_flag", False)

    def test_set_boolean_config_success(self):
        """Test de définition réussie d'une configuration booléenne."""
        # ARRANGE
        self.mock_repository.set_boolean_config.return_value = True
        
        # ACT
        result = self.service.set_boolean_config("test_flag", True, "Description test")
        
        # ASSERT
        self.assertTrue(result)
        self.mock_repository.set_boolean_config.assert_called_once_with("test_flag", True, "Description test")

    def test_delete_config_success(self):
        """Test de suppression réussie d'une configuration."""
        # ARRANGE
        self.mock_repository.delete_config.return_value = True
        
        # ACT
        result = self.service.delete_config("test_key")
        
        # ASSERT
        self.assertTrue(result)
        self.mock_repository.delete_config.assert_called_once_with("test_key")

    def test_get_all_system_configs_success(self):
        """Test de récupération de toutes les configurations système."""
        # ARRANGE
        mock_configs = [
            {'config_key': 'key1', 'config_value': 'value1', 'config_type': 'string'},
            {'config_key': 'key2', 'config_value': 'value2', 'config_type': 'string'}
        ]
        self.mock_repository.get_all_configs.return_value = mock_configs
        
        # ACT
        result = self.service.get_all_system_configs()
        
        # ASSERT
        expected = {
            'key1': {'config_key': 'key1', 'config_value': 'value1', 'config_type': 'string'},
            'key2': {'config_key': 'key2', 'config_value': 'value2', 'config_type': 'string'}
        }
        self.assertEqual(result, expected)

    def test_get_all_system_configs_exception(self):
        """Test de récupération avec exception."""
        # ARRANGE
        self.mock_repository.get_all_configs.side_effect = Exception("Erreur DB")
        
        # ACT
        result = self.service.get_all_system_configs()
        
        # ASSERT
        self.assertEqual(result, {})

    def test_validate_system_security_admin_password_changed(self):
        """Test de validation de sécurité avec mot de passe admin changé."""
        # ARRANGE
        self.mock_repository.get_boolean_config.return_value = True
        
        # ACT
        result = self.service.validate_system_security()
        
        # ASSERT
        expected = {
            'admin_password_changed': True,
            'security_level': 'HIGH',
            'recommendations': []
        }
        self.assertEqual(result, expected)

    def test_validate_system_security_admin_password_not_changed(self):
        """Test de validation de sécurité avec mot de passe admin non changé."""
        # ARRANGE
        self.mock_repository.get_boolean_config.return_value = False
        
        # ACT
        result = self.service.validate_system_security()
        
        # ASSERT
        expected = {
            'admin_password_changed': False,
            'security_level': 'LOW',
            'recommendations': ['Changer le mot de passe administrateur par défaut immédiatement']
        }
        self.assertEqual(result, expected)

    def test_service_initialization_with_default_repository(self):
        """Test d'initialisation du service avec repository par défaut."""
        # ACT & ASSERT - Ne doit pas lever d'exception
        with patch('src.application.services.system_config_service.SystemConfigRepositorySQLite'):
            service = SystemConfigService()
            self.assertIsNotNone(service)

if __name__ == '__main__':
    unittest.main()
