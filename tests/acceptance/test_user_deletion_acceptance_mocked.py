"""
Tests d'acceptance pour la fonctionnalité de suppression d'utilisateurs
Respecte les consignes de mocking - DONNÉES DE TEST ISOLÉES
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.web.condo_app import app
from src.domain.entities.user import User, UserRole


class TestUserDeletionAcceptanceMocked:
    
    def setup_method(self):
        """Configuration avant chaque test"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
    
    @patch('src.web.condo_app.user_service')
    def test_admin_can_delete_user_complete_workflow(self, mock_user_service):
        """Scénario : Un administrateur supprime un utilisateur avec workflow complet - DONNÉES MOCKÉES"""
        # Arrange - Simuler un administrateur connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['user_role'] = 'admin'
            sess['logged_in'] = True
            sess['user_name'] = 'Administrator'
        
        # Mock des données utilisateurs pour la liste
        mock_users = [
            User(username="admin", email="admin@test.com", password_hash="hash", 
                 role=UserRole.ADMIN, full_name="Admin User", condo_unit=""),
            User(username="test_user", email="test@test.com", password_hash="hash",
                 role=UserRole.RESIDENT, full_name="Test User", condo_unit="101")
        ]
        mock_user_service.get_all_users.return_value = mock_users
        mock_user_service.can_delete_user.return_value = True
        mock_user_service.delete_user_by_username.return_value = True
        
        # Act 1 - Consulter la liste des utilisateurs avec données mockées
        response = self.client.get('/users')
        assert response.status_code == 200
        
        # Act 2 - Le JavaScript doit déclencher la suppression
        # Simulation de l'appel AJAX fait par confirmDeleteUser()
        response = self.client.delete('/api/user/test_user')
        
        # Assert - La suppression devrait réussir avec données isolées
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'supprimé avec succès' in data['message']
        
        # Vérifier les appels mockés
        mock_user_service.can_delete_user.assert_called_with('admin', 'test_user')
        mock_user_service.delete_user_by_username.assert_called_with('test_user')
    
    @patch('src.web.condo_app.user_service')
    def test_resident_cannot_delete_users(self, mock_user_service):
        """Scénario : Un résident ne peut pas supprimer d'utilisateurs - PERMISSIONS MOCKÉES"""
        # Arrange - Simuler un résident connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'resident'
            sess['user_role'] = 'resident'
            sess['logged_in'] = True
            sess['user_name'] = 'Résident Test'
        
        # Act - Tentative de suppression par un résident
        response = self.client.delete('/api/user/test_user')
        
        # Assert - Doit être refusé sans toucher la base
        assert response.status_code in [403, 302]  # Refusé ou redirection
        
        # Vérifier qu'aucun service de suppression n'a été appelé
        mock_user_service.delete_user_by_username.assert_not_called()
    
    def test_delete_user_javascript_function_works(self):
        """Scénario : La fonction JavaScript confirmDeleteUser() fonctionne correctement"""
        # Arrange - Simuler un admin connecté pour récupérer la page
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['user_role'] = 'admin'
            sess['logged_in'] = True
            sess['user_name'] = 'Administrator'
        
        # Act - Récupérer la page users.html
        response = self.client.get('/users')
        
        # Assert - Vérifier que la page contient le JavaScript requis
        assert response.status_code == 200
        html_content = response.get_data(as_text=True)
        
        # Vérifier la présence de la fonction JavaScript AJAX
        assert 'confirmDeleteUser' in html_content
        assert 'fetch(' in html_content  # AJAX au lieu d'alert()
        assert '/api/user/' in html_content  # URL de l'endpoint
        assert 'DELETE' in html_content  # Méthode HTTP
    
    @patch('src.web.condo_app.user_service')
    def test_self_deletion_prevention_ui(self, mock_user_service):
        """Scénario : L'interface empêche l'auto-suppression - LOGIQUE MOCKÉE"""
        # Arrange - Simuler un admin connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['user_role'] = 'admin'
            sess['logged_in'] = True
            sess['user_name'] = 'Administrator'
        
        # Mock pour refuser l'auto-suppression
        mock_user_service.can_delete_user.return_value = False
        
        # Act - Tentative d'auto-suppression
        response = self.client.delete('/api/user/admin')
        
        # Assert - Doit être refusé avec message approprié
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'impossible' in data['error'].lower()
        
        # Vérifier les appels mockés
        mock_user_service.can_delete_user.assert_called_with('admin', 'admin')
        mock_user_service.delete_user_by_username.assert_not_called()
    
    def test_delete_confirmation_dialog(self):
        """Scénario : Une boîte de confirmation apparaît avant suppression"""
        # Arrange - Simuler un admin pour accéder à la page
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['user_role'] = 'admin'
            sess['logged_in'] = True
            sess['user_name'] = 'Administrator'
        
        # Act - Récupérer la page avec les boutons de suppression
        response = self.client.get('/users')
        
        # Assert - Vérifier la présence d'éléments de confirmation
        assert response.status_code == 200
        html_content = response.get_data(as_text=True)
        
        # Vérifier que le JavaScript inclut une confirmation
        assert 'confirm(' in html_content or 'confirmDeleteUser' in html_content
        assert 'Êtes-vous sûr' in html_content or 'confirmation' in html_content.lower()
    
    @patch('src.web.condo_app.user_service')
    def test_user_feedback_after_deletion(self, mock_user_service):
        """Scénario : L'utilisateur reçoit un feedback après suppression - RÉPONSE MOCKÉE"""
        # Arrange - Simuler un administrateur connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['user_role'] = 'admin'
            sess['logged_in'] = True
            sess['user_name'] = 'Administrator'
        
        # Mock pour simuler suppression réussie
        mock_user_service.can_delete_user.return_value = True
        mock_user_service.delete_user_by_username.return_value = True
        
        # Act - Supprimer un utilisateur avec service mocké
        response = self.client.delete('/api/user/test_user')
        
        # Assert - La réponse devrait contenir un message de succès
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'message' in data
        assert 'supprimé avec succès' in data['message']
        
        # Vérifier les appels mockés
        mock_user_service.can_delete_user.assert_called_with('admin', 'test_user')
        mock_user_service.delete_user_by_username.assert_called_with('test_user')
