"""
Tests d'intégration pour les détails d'utilisateur - TDD Phase RED
"""

import pytest
from unittest.mock import patch, Mock
from flask import Flask
import json
from src.web.condo_app import app


class TestUserDetailsIntegration:
    """Tests d'intégration pour l'API des détails utilisateur"""
    
    def setup_method(self):
        """Configuration pour chaque test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
    def test_api_user_details_returns_real_database_data(self):
        """Test que l'API /api/user/<username> retourne de vraies données de la base"""
        # Simuler une session utilisateur connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['user_role'] = 'admin'  # Utiliser 'admin' au lieu de 'ADMIN'
            sess['logged_in'] = True
        
        # Act - Tester avec l'utilisateur admin qui existe
        response = self.client.get('/api/user/admin')
        
        # Assert - L'API devrait maintenant retourner de vraies données
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Vérifier que les données ne sont plus factices
        assert data['found'] is True
        assert 'error' not in data
        assert data['username'] == 'admin'
        assert data['email'] != 'admin@example.com', "Les données devraient venir de la base de données"
        assert 'details' in data
    
    def test_api_user_details_handles_user_not_found(self):
        """Test que l'API gère les utilisateurs non trouvés"""
        # Simuler une session utilisateur connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['user_role'] = 'admin'  # Utiliser 'admin' au lieu de 'ADMIN'
            sess['logged_in'] = True
        
        # Act - Tester avec un utilisateur inexistant
        response = self.client.get('/api/user/inexistant')
        
        # Assert - L'API devrait maintenant retourner 404 pour utilisateur non trouvé
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Utilisateur non trouvé'
    
    def test_api_user_details_requires_authentication(self):
        """Test que l'API nécessite une authentification"""
        # Act - Accéder sans session
        response = self.client.get('/api/user/admin')
        
        # Assert - L'API devrait maintenant rediriger (302) vers la page de login
        assert response.status_code == 302
        assert 'login' in response.location or 'redirect' in response.headers.get('Location', '')
    
    def test_view_user_details_javascript_function_calls_api(self):
        """Test que la fonction JavaScript viewUserDetails() redirige vers la page de détails"""
        # Simuler une session utilisateur connecté avec les bonnes permissions
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['user_role'] = 'admin'  # Utiliser 'admin' au lieu de 'ADMIN'
            sess['logged_in'] = True
            sess['user_name'] = 'Administrator'
        
        # Act - Récupérer la page users pour vérifier que viewUserDetails est présent
        response = self.client.get('/users')
        
        # Assert - Vérifier que la fonction JavaScript est présente
        assert response.status_code == 200
        html_content = response.data.decode('utf-8')
        assert 'viewUserDetails' in html_content
        # Vérifier que la fonction redirige maintenant vers la page de détails
        assert '/users/${username}/details' in html_content


if __name__ == "__main__":
    pytest.main([__file__])
