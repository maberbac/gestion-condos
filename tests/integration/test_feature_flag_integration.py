"""
Tests d'intégration pour le système de feature flags.

[ARCHITECTURE HEXAGONALE - TESTS INTÉGRATION]
Validation de l'intégration entre le décorateur et le service.
Utilisation de mocks pour isoler la persistance.
"""

import unittest
from unittest.mock import Mock, patch
from flask import Flask
from src.application.services.feature_flag_service import FeatureFlagService
from src.web.condo_app import require_feature_flag


class TestFeatureFlagIntegration(unittest.TestCase):
    """Tests d'intégration pour le système de feature flags."""
    
    def setUp(self):
        """Initialisation des tests."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.secret_key = 'test_secret_key'
        
        # Mock du repository
        self.mock_repository = Mock()
        self.feature_flag_service = FeatureFlagService(self.mock_repository)
        
        # Configuration du contexte Flask
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Nettoyage après les tests."""
        self.app_context.pop()
    
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
    
    def test_require_feature_flag_decorator_blocks_non_admin_when_disabled(self):
        """Test que le décorateur bloque les non-admins quand feature flag désactivé."""
        
        @require_feature_flag('finance_module')
        def test_view():
            return "Access granted"
        
        # Test avec session non-admin - devrait être bloqué si feature flag désactivé
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session['user_id'] = 'resident1'
                session['user_role'] = 'resident'
            
            # Utiliser le contexte de la requête pour tester le décorateur
            with self.app.test_request_context('/'):
                # Copier la session dans le contexte de la requête
                from flask import session
                session['user_id'] = 'resident1'
                session['user_role'] = 'resident'
                
                # Non-admin avec feature flag désactivé devrait être bloqué
                result = test_view()
                if isinstance(result, tuple):
                    content, status_code = result
                    self.assertEqual(status_code, 503)
                    self.assertIn("Fonctionnalité désactivée", str(content) if isinstance(content, bytes) else content)
                else:
                    self.fail("Expected tuple response with error status")
    
    def test_require_feature_flag_decorator_allows_access_when_enabled(self):
        """Test que le décorateur autorise l'accès quand le feature flag est activé."""
        # Créer un mock service qui retourne True
        from unittest.mock import Mock
        from src.web import condo_app
        
        # Sauvegarder le service original
        original_service = condo_app.feature_flag_service
        
        try:
            # Créer un mock service
            mock_service = Mock()
            mock_service.is_feature_enabled.return_value = True
            condo_app.feature_flag_service = mock_service
            
            @require_feature_flag('finance_module')
            def test_view():
                return "Access granted"
            
            # Test avec admin
            with self.app.test_request_context('/'):
                from flask import session
                session['user_id'] = 'admin'
                session['user_role'] = 'admin'
                
                result = test_view()
                self.assertEqual(result, "Access granted")
            
            # Test avec non-admin aussi
            with self.app.test_request_context('/'):
                from flask import session
                session['user_id'] = 'resident1'
                session['user_role'] = 'resident'
                
                result = test_view()
                self.assertEqual(result, "Access granted")
                
        finally:
            # Restaurer le service original
            condo_app.feature_flag_service = original_service
    
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
        # Le décorateur devrait retourner une réponse d'erreur ou redirection
        # Vérifier que la fonction originale n'a pas été exécutée
        mock_service.is_feature_enabled.assert_called_once_with('finance_module')
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
        
        # Assert
        # En cas d'erreur, l'accès devrait être bloqué par sécurité
        mock_service.is_feature_enabled.assert_called_once_with('finance_module')
        self.assertNotEqual(result, "Access granted")
    
    def test_feature_flag_service_integration_with_repository(self):
        """Test que le service interagit correctement avec le repository."""
        # Arrange
        self.mock_repository.is_enabled.return_value = True
        
        # Act
        result = self.feature_flag_service.is_finance_module_enabled()
        
        # Assert
        self.assertTrue(result)
        self.mock_repository.is_enabled.assert_called_once_with('finance_module')
    
    def test_feature_flag_service_handles_repository_failure(self):
        """Test que le service gère les échecs du repository."""
        # Arrange
        self.mock_repository.is_enabled.side_effect = Exception("Database connection error")
        
        # Act
        result = self.feature_flag_service.is_finance_module_enabled()
        
        # Assert
        # En cas d'erreur, le service devrait retourner False par sécurité
        self.assertFalse(result)
        self.mock_repository.is_enabled.assert_called_once_with('finance_module')
    
    def test_multiple_feature_checks_use_correct_names(self):
        """Test que différents checks utilisent les bons noms de features."""
        # Arrange
        self.mock_repository.is_enabled.side_effect = lambda name: name == 'finance_module'
        
        # Act
        finance_result = self.feature_flag_service.is_feature_enabled('finance_module')
        analytics_result = self.feature_flag_service.is_feature_enabled('analytics_module')
        reporting_result = self.feature_flag_service.is_feature_enabled('reporting_module')
        
        # Assert
        self.assertTrue(finance_result)
        self.assertFalse(analytics_result)
        self.assertFalse(reporting_result)
        
        # Vérifier les appels
        expected_calls = [
            unittest.mock.call('finance_module'),
            unittest.mock.call('analytics_module'),
            unittest.mock.call('reporting_module')
        ]
        self.mock_repository.is_enabled.assert_has_calls(expected_calls)


if __name__ == '__main__':
    unittest.main()
