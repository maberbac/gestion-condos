"""
Tests d'acceptance pour la fonctionnalité de suppression d'utilisateurs
Phase RED du cycle TDD - Ces tests échouent initialement
"""

import pytest
import tempfile
import os
from src.web.condo_app import app
from src.infrastructure.config_manager import ConfigurationManager


class TestUserDeletionAcceptance:
    
    def setup_method(self):
        """Configuration avant chaque test"""
        # Configuration test avec base de données temporaire
        self.test_db_fd, self.test_db_path = tempfile.mkstemp(suffix='.db')
        
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        self.client = app.test_client()
        self._setup_test_environment()
    
    def teardown_method(self):
        """Nettoyage après chaque test"""
        os.close(self.test_db_fd)
        os.unlink(self.test_db_path)
    
    def _setup_test_environment(self):
        """Configuration de l'environnement de test"""
        pass
    
    def test_admin_can_delete_user_complete_workflow(self):
        """Scénario : Un administrateur supprime un utilisateur avec workflow complet"""
        # Arrange - Simuler un administrateur connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['user_role'] = 'admin'
            sess['logged_in'] = True
            sess['user_name'] = 'Administrator'
        
        # Act 1 - Consulter la liste des utilisateurs
        response = self.client.get('/users')
        assert response.status_code == 200
        
        # Act 2 - Le JavaScript doit déclencher la suppression
        # Simulation de l'appel AJAX fait par confirmDeleteUser()
        response = self.client.delete('/api/user/maberbache1')
        
        # Assert - La suppression devrait réussir
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Act 3 - Vérifier que l'utilisateur n'apparaît plus dans la liste
        response = self.client.get('/users')
        html_content = response.data.decode('utf-8')
        assert 'test_user' not in html_content
    
    def test_resident_cannot_delete_users(self):
        """Scénario : Un résident ne peut pas supprimer d'utilisateurs"""
        # Arrange - Simuler un résident connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'maberbache1'
            sess['user_role'] = 'resident'
            sess['logged_in'] = True
            sess['user_name'] = 'Resident User'
        
        # Act - Tenter de supprimer un utilisateur
        response = self.client.delete('/api/user/admin')
        
        # Assert - Accès refusé
        assert response.status_code == 403
    
    def test_delete_user_javascript_function_works(self):
        """Scénario : La fonction JavaScript confirmDeleteUser() fonctionne"""
        # Arrange - Simuler un administrateur connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['user_role'] = 'admin'
            sess['logged_in'] = True
            sess['user_name'] = 'Administrator'
        
        # Act - Récupérer la page users et vérifier la fonction JavaScript
        response = self.client.get('/users')
        html_content = response.data.decode('utf-8')
        
        # Assert - Vérifier que la fonction fait maintenant un appel AJAX au lieu d'alert()
        assert response.status_code == 200
        assert 'confirmDeleteUser' in html_content
        assert 'fetch(' in html_content or 'XMLHttpRequest' in html_content, "La fonction doit faire un appel AJAX"
    
    def test_self_deletion_prevention_ui(self):
        """Scénario : L'interface empêche l'auto-suppression"""
        # Arrange - Simuler un administrateur connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['user_role'] = 'admin'
            sess['logged_in'] = True
            sess['user_name'] = 'Administrator'
        
        # Act - Consulter la page users
        response = self.client.get('/users')
        html_content = response.data.decode('utf-8')
        
        # Assert - Le bouton de suppression ne devrait pas être présent pour l'utilisateur connecté
        assert response.status_code == 200
        # La logique Jinja {% if user.username != session.user_id %} devrait masquer le bouton
        assert 'confirmDeleteUser(\'admin\')' not in html_content
    
    def test_delete_confirmation_dialog(self):
        """Scénario : Un dialogue de confirmation apparaît avant suppression"""
        # Arrange - Simuler un administrateur connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['user_role'] = 'admin'
            sess['logged_in'] = True
            sess['user_name'] = 'Administrator'
        
        # Act - Récupérer la page users
        response = self.client.get('/users')
        html_content = response.data.decode('utf-8')
        
        # Assert - Vérifier qu'il y a une confirmation avant suppression
        assert response.status_code == 200
        assert 'confirm(' in html_content, "Il devrait y avoir une confirmation avant suppression"
        assert 'Cette action est irréversible' in html_content, "Le message de confirmation devrait être présent"
    
    def test_user_feedback_after_deletion(self):
        """Scénario : L'utilisateur reçoit un feedback après suppression"""
        # Arrange - Simuler un administrateur connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['user_role'] = 'admin'
            sess['logged_in'] = True
            sess['user_name'] = 'Administrator'
        
        # Act - Supprimer un utilisateur qui n'a pas encore été supprimé
        response = self.client.delete('/api/user/maberbache')
        
        # Assert - La réponse devrait contenir un message de succès
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert 'supprimé' in data['message'].lower() or 'deleted' in data['message'].lower()
