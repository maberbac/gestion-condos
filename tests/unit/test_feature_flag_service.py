"""
Tests unitaires pour FeatureFlagService.

[ARCHITECTURE HEXAGONALE - TESTS UNITAIRES]
Validation de la logique métier du service de feature flags (lecture seule).
Utilisation de mocks pour isoler complètement la logique de test.
"""

import unittest
from unittest.mock import Mock
from src.application.services.feature_flag_service import FeatureFlagService


class TestFeatureFlagService(unittest.TestCase):
    """Tests unitaires pour FeatureFlagService."""
    
    def setUp(self):
        """Initialisation des tests."""
        self.mock_repository = Mock()
        self.service = FeatureFlagService(self.mock_repository)
    
    def test_is_finance_module_enabled_returns_repository_result(self):
        """Test que is_finance_module_enabled retourne le résultat du repository."""
        # Arrange
        self.mock_repository.is_enabled.return_value = True
        
        # Act
        result = self.service.is_finance_module_enabled()
        
        # Assert
        self.assertTrue(result)
        self.mock_repository.is_enabled.assert_called_once_with('finance_module')
    
    def test_is_finance_module_enabled_when_disabled(self):
        """Test que is_finance_module_enabled retourne False quand désactivé."""
        # Arrange
        self.mock_repository.is_enabled.return_value = False
        
        # Act
        result = self.service.is_finance_module_enabled()
        
        # Assert
        self.assertFalse(result)
        self.mock_repository.is_enabled.assert_called_once_with('finance_module')
    
    def test_is_finance_module_enabled_handles_exception(self):
        """Test que is_finance_module_enabled gère les exceptions du repository."""
        # Arrange
        self.mock_repository.is_enabled.side_effect = Exception("Database error")
        
        # Act
        result = self.service.is_finance_module_enabled()
        
        # Assert
        self.assertFalse(result)
        self.mock_repository.is_enabled.assert_called_once_with('finance_module')
    
    def test_is_feature_enabled_calls_repository_with_correct_name(self):
        """Test que is_feature_enabled appelle le repository avec le bon nom."""
        # Arrange
        feature_name = 'analytics_module'
        self.mock_repository.is_enabled.return_value = True
        
        # Act
        result = self.service.is_feature_enabled(feature_name)
        
        # Assert
        self.assertTrue(result)
        self.mock_repository.is_enabled.assert_called_once_with(feature_name)
    
    def test_is_feature_enabled_when_disabled(self):
        """Test que is_feature_enabled retourne False quand désactivé."""
        # Arrange
        feature_name = 'reporting_module'
        self.mock_repository.is_enabled.return_value = False
        
        # Act
        result = self.service.is_feature_enabled(feature_name)
        
        # Assert
        self.assertFalse(result)
        self.mock_repository.is_enabled.assert_called_once_with(feature_name)
    
    def test_is_feature_enabled_handles_exception(self):
        """Test que is_feature_enabled gère les exceptions du repository."""
        # Arrange
        feature_name = 'test_feature'
        self.mock_repository.is_enabled.side_effect = Exception("Connection error")
        
        # Act
        result = self.service.is_feature_enabled(feature_name)
        
        # Assert
        self.assertFalse(result)
        self.mock_repository.is_enabled.assert_called_once_with(feature_name)


if __name__ == '__main__':
    unittest.main()
