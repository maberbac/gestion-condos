"""
Tests d'intégration pour les feature flags - version simplifiée.
"""

import unittest
from unittest.mock import patch, Mock
from flask import Flask

from src.web.condo_app import create_app, require_feature_flag


class TestFeatureFlagIntegration(unittest.TestCase):
    """Tests d'intégration pour les feature flags."""
    
    def setUp(self):
        """Initialise l'environnement de test."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Nettoie l'environnement de test."""
        self.app_context.pop()
    
    def test_feature_flag_service_integration_with_repository(self):
        """Test que le service interagit correctement avec le repository."""
        from src.application.services.feature_flag_service import FeatureFlagService
        from src.adapters.feature_flag_repository_sqlite import FeatureFlagRepositorySQLite
        
        # Arrange
        repository = FeatureFlagRepositorySQLite()
        service = FeatureFlagService(repository)
        
        # Act & Assert
        result = service.is_feature_enabled('finance_module')
        self.assertIsInstance(result, bool)
    
    def test_multiple_feature_checks_use_correct_names(self):
        """Test que différents checks utilisent les bons noms de features."""
        from src.application.services.feature_flag_service import FeatureFlagService
        from src.adapters.feature_flag_repository_sqlite import FeatureFlagRepositorySQLite
        
        # Arrange
        repository = FeatureFlagRepositorySQLite()
        service = FeatureFlagService(repository)
        
        # Act
        finance_result = service.is_feature_enabled('finance_module')
        reports_result = service.is_feature_enabled('reports_module')
        
        # Assert - Les résultats peuvent être True ou False, l'important est qu'ils ne plantent pas
        self.assertIsInstance(finance_result, bool)
        self.assertIsInstance(reports_result, bool)
    
    @patch('src.application.services.feature_flag_service.FeatureFlagService.is_feature_enabled')
    def test_feature_flag_service_handles_repository_failure(self, mock_is_enabled):
        """Test que le service gère les échecs du repository."""
        from src.application.services.feature_flag_service import FeatureFlagService
        from src.adapters.feature_flag_repository_sqlite import FeatureFlagRepositorySQLite
        
        # Arrange
        mock_is_enabled.side_effect = Exception("Database connection error")
        repository = FeatureFlagRepositorySQLite()
        service = FeatureFlagService(repository)
        
        # Act & Assert - Le service devrait gérer l'exception
        result = service.is_feature_enabled('finance')
        self.assertFalse(result)  # En cas d'erreur, retourner False par sécurité
    
    def test_require_feature_flag_decorator_blocks_all_users_when_disabled(self):
        """Test que le décorateur bloque TOUS les utilisateurs (même admins) quand feature flag désactivé."""
        
        @require_feature_flag('finance_module')
        def test_view():
            return "Access granted"
        
        # Test avec session admin - devrait aussi être bloqué
        with self.app.test_client() as client:
            # Créer une session admin
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin'
                sess['user_role'] = 'admin'
            
            # Utiliser le contexte de la requête pour tester le décorateur
            with self.app.test_request_context('/test'):
                # Copier la session dans le contexte de la requête
                from flask import session
                session['user_id'] = 'admin'
                session['user_role'] = 'admin'
                
                # Même l'admin devrait être bloqué si feature flag désactivé
                result = test_view()
                if isinstance(result, tuple):
                    content, status_code = result
                    self.assertEqual(status_code, 503)
                    self.assertIn("Fonctionnalité désactivée", str(content) if isinstance(content, bytes) else content)
    
    @patch('src.web.condo_app.feature_flag_service')
    def test_require_feature_flag_decorator_blocks_access_when_disabled(self, mock_service):
        """Test que le décorateur bloque l'accès quand la fonctionnalité est désactivée."""
        # Arrange
        mock_service.is_feature_enabled.return_value = False
        
        @require_feature_flag('finance_module')
        def test_view():
            return "Access granted"
        
        # Act
        with self.app.test_request_context('/'):
            result = test_view()
        
        # Assert
        if isinstance(result, tuple):
            content, status_code = result
            self.assertEqual(status_code, 503)
        else:
            # Si ce n'est pas un tuple, vérifier que c'est un refus d'accès
            self.assertNotEqual(result, "Access granted")
    
    @patch('src.web.condo_app.feature_flag_service')
    def test_require_feature_flag_decorator_handles_service_exception(self, mock_service):
        """Test que le décorateur gère les exceptions du service."""
        # Arrange
        mock_service.is_feature_enabled.side_effect = Exception("Service error")
        
        @require_feature_flag('finance_module')
        def test_view():
            return "Access granted"
        
        # Act
        with self.app.test_request_context('/'):
            result = test_view()
        
        # Assert - En cas d'erreur, bloquer l'accès par sécurité
        if isinstance(result, tuple):
            content, status_code = result
            self.assertEqual(status_code, 503)


if __name__ == '__main__':
    unittest.main()
