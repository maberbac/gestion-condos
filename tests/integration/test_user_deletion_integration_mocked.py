"""
Tests d'intégration pour la fonctionnalité de suppression d'utilisateurs via Flask
Respecte les consignes strictes de mocking - AUCUNE INTERACTION DB RÉELLE
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.web.condo_app import app
from src.domain.entities.user import User, UserRole


class TestUserDeletionIntegrationMocked:
    
    def setup_method(self):
        """Configuration avant chaque test"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
    
    @patch('src.application.services.user_service.UserService')
    def test_delete_user_api_endpoint_success(self, mock_user_service_class):
        """Test de l'endpoint API DELETE /api/user/<username> - SERVICE MOCKÉ"""
        # Arrange - Simuler un administrateur connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['user_role'] = 'admin'
            sess['logged_in'] = True
            sess['user_name'] = 'Administrator'
        
        # Mock du service pour éviter interaction base de données
        mock_user_service = Mock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.can_delete_user.return_value = True
        mock_user_service.delete_user_by_username.return_value = True
        
        # Act - Test de l'API avec service complètement mocké
        response = self.client.delete('/api/user/test_user')
        
        # Assert - Validation sans interaction base de données réelle
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'supprimé avec succès' in data['message']
        
        # Vérifier que les mocks ont été appelés correctement
        mock_user_service.can_delete_user.assert_called_once_with('test_user', 'admin')
        mock_user_service.delete_user_by_username.assert_called_once_with('test_user')
    
    @patch('src.application.services.user_service.UserService')
    def test_delete_user_api_endpoint_not_found(self, mock_user_service_class):
        """Test de l'endpoint avec utilisateur inexistant - SERVICE MOCKÉ"""
        # Arrange - Simuler un administrateur connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['user_role'] = 'admin'
            sess['logged_in'] = True
            sess['user_name'] = 'Administrator'
            
        # Mock du service pour simuler utilisateur inexistant
        mock_user_service = Mock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.can_delete_user.return_value = True
        mock_user_service.delete_user_by_username.return_value = False  # Utilisateur non trouvé
        
        # Act - Test avec service mocké
        response = self.client.delete('/api/user/nonexistent_user')
        
        # Assert - Validation réponse 404 sans DB réelle
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'non trouvé' in data['error']
    
    @patch('src.application.services.user_service.UserService')
    def test_delete_user_authentication_required(self, mock_user_service_class):
        """Test d'authentification requise - AUCUNE INTERACTION DB"""
        # Mock setup même si pas utilisé
        mock_user_service = Mock()
        mock_user_service_class.return_value = mock_user_service
        
        # Act - Tentative sans session authentifiée
        response = self.client.delete('/api/user/test_user')
        
        # Assert - Doit retourner 401 ou redirection sans toucher la base
        assert response.status_code in [401, 302]  # 401 ou redirection login
        
        # Vérifier qu'aucun service n'a été appelé
        mock_user_service.delete_user_by_username.assert_not_called()
    
    @patch('src.application.services.user_service.UserService')
    def test_delete_user_admin_permission_required(self, mock_user_service_class):
        """Test de permission admin requise - MOCKING COMPLET"""
        # Mock setup même si pas utilisé
        mock_user_service = Mock()
        mock_user_service_class.return_value = mock_user_service
        
        # Arrange - Simuler un utilisateur non-admin connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'resident'
            sess['user_role'] = 'resident'
            sess['logged_in'] = True
            sess['user_name'] = 'Résident'
        
        # Act - Tentative avec permission insuffisante
        response = self.client.delete('/api/user/test_user')
        
        # Assert - Doit retourner 403 ou redirection sans interaction DB
        assert response.status_code in [403, 302]
        
        # Vérifier qu'aucun service n'a été appelé
        mock_user_service.delete_user_by_username.assert_not_called()
    
    @patch('src.application.services.user_service.UserService')
    def test_cannot_delete_self_via_api(self, mock_user_service_class):
        """Test d'empêchement de l'auto-suppression via API - SERVICE MOCKÉ"""
        # Arrange - Simuler un administrateur connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['user_role'] = 'admin'
            sess['logged_in'] = True
            sess['user_name'] = 'Administrator'
        
        # Mock du service pour refuser auto-suppression
        mock_user_service = Mock()
        mock_user_service_class.return_value = mock_user_service
        mock_user_service.can_delete_user.return_value = False
        
        # Act - Tentative d'auto-suppression
        response = self.client.delete('/api/user/admin')
        
        # Assert - Validation refus sans toucher DB
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'impossible' in data['error'].lower() or 'cannot delete' in data['error'].lower()
        
        # Vérifier les appels de service mockés
        mock_user_service.can_delete_user.assert_called_once_with('admin', 'admin')
        mock_user_service.delete_user_by_username.assert_not_called()
