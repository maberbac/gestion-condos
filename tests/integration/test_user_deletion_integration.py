"""
Tests d'intégration pour la fonctionnalité de suppression d'utilisateurs via Flask
Respecte les consignes strictes de mocking - AUCUNE INTERACTION DB RÉELLE
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.web.condo_app import app
from src.domain.entities.user import User, UserRole


class TestUserDeletionIntegration:
    
    def setup_method(self):
        """Configuration avant chaque test"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
        # Mock repository pour éviter toute interaction avec base réelle
        self.mock_repository = Mock()
    
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
        response = self.client.delete('/api/user/test_user')        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'message' in data
    
    def test_delete_user_api_endpoint_not_found(self):
        """Test de suppression d'un utilisateur inexistant via API"""
        # Arrange - Simuler un administrateur connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['user_role'] = 'admin'
            sess['logged_in'] = True
            sess['user_name'] = 'Administrator'
        
        # Act - Cette route n'existe pas encore, le test doit échouer
        response = self.client.delete('/api/user/nonexistent_user')
        
        # Assert
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_delete_user_authentication_required(self):
        """Test que l'authentification est requise pour supprimer"""
        # Act - Tentative de suppression sans authentification
        response = self.client.delete('/api/user/test_user')
        
        # Assert - Redirection vers login
        assert response.status_code == 302
    
    def test_delete_user_admin_permission_required(self):
        """Test que seuls les admins peuvent supprimer"""
        # Arrange - Simuler un résident connecté (pas admin)
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'resident'
            sess['user_role'] = 'resident'
            sess['logged_in'] = True
            sess['user_name'] = 'Resident User'
        
        # Act - Cette route n'existe pas encore, le test doit échouer
        response = self.client.delete('/api/user/test_user')
        
        # Assert - Accès refusé
        assert response.status_code == 403
    
    def test_cannot_delete_self_via_api(self):
        """Test d'empêchement de l'auto-suppression via API"""
        # Arrange - Simuler un administrateur connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['user_role'] = 'admin'
            sess['logged_in'] = True
            sess['user_name'] = 'Administrator'
        
        # Act - Tentative d'auto-suppression
        response = self.client.delete('/api/user/admin')
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'impossible' in data['error'].lower() or 'cannot delete' in data['error'].lower()
