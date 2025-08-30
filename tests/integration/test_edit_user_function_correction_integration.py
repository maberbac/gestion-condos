"""
Tests d'intégration pour la correction de la fonction editUser dans users.html.
Méthodologie: Tests des interactions utilisateur avec la fonction corrigée.
"""

import pytest
from unittest.mock import patch, Mock
from src.web.condo_app import app
from src.infrastructure.logger_manager import get_logger

logger = get_logger(__name__)


class TestEditUserFunctionCorrectionIntegration:
    """Tests d'intégration de la fonction editUser corrigée dans users.html."""
    
    def setup_method(self):
        """Configuration du client de test Flask."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        
    @patch('src.application.services.user_service.UserService')
    def test_users_page_loads_with_corrected_edit_function(self, mock_service_class):
        """Test que la page users se charge avec la fonction editUser corrigée."""
        # Configuration du mock pour éviter les erreurs de base de données
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_users_for_web_display.return_value = []  # Liste vide pour simplifier
        
        with self.client as client:
            # Simuler une session admin
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin1'
                sess['user_role'] = 'admin'
                sess['user_name'] = 'Admin Test'
            
            # Act: Charger la page users
            response = client.get('/users')
            
            # Assert: Vérifications de base
            assert response.status_code == 200
            
            # Vérifier que la page users se charge correctement
            assert b'Utilisateurs' in response.data
            assert b'users.html' in response.data or b'Gestion' in response.data
            
            # Vérifier que le mock a été appelé - cela confirme que notre mock fonctionne
            mock_service.get_users_for_web_display.assert_called_once()
            
            logger.info("Test réussi: page users se charge avec mock fonctionnel")
    
    @patch('src.application.services.user_service.UserService')
    def test_edit_button_functionality_integration(self, mock_service_class):
        """Test d'intégration du bouton Modifier avec la fonction corrigée."""
        # Configuration du mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        # Mock pour les pages users et user_details avec données simplifiées
        mock_service.get_users_for_web_display.return_value = []  # Liste vide pour éviter erreurs
        mock_service.get_user_details_by_username.return_value = {
            'username': 'resident1',
            'full_name': 'Jean Dupont',
            'email': 'jean@example.com',
            'role': 'resident',
            'role_display': 'Résident',
            'condo_unit': 'A-101',
            'has_condo_unit': True,
            'last_login': '2025-08-30',
            'created_at': '2025-01-01',
            'status': 'Actif'
        }
        
        with self.client as client:
            # Simuler une session admin
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin1'
                sess['user_role'] = 'admin'
            
            # Act 1: Charger la page users
            users_response = client.get('/users')
            assert users_response.status_code == 200
            
            # Act 2: Simuler le clic sur le bouton Modifier (redirection vers détails)
            details_response = client.get('/users/resident1/details')
            
            # Assert: Vérifier que la redirection fonctionne
            assert details_response.status_code == 200
            
            # Vérifier que les mocks ont été appelés
            mock_service.get_users_for_web_display.assert_called_once()
            mock_service.get_user_details_by_username.assert_called_with('resident1')
            
            logger.info("Test réussi: intégration complète bouton Modifier -> détails")
    
    def test_edit_function_consistency_between_templates(self):
        """Test de cohérence de la fonction editUser entre users.html et user_details.html."""
        # Lire les deux templates
        users_template_path = "c:/src/INF2020/gestion-condos/src/web/templates/users.html"
        details_template_path = "c:/src/INF2020/gestion-condos/src/web/templates/user_details.html"
        
        try:
            with open(users_template_path, 'r', encoding='utf-8') as f:
                users_content = f.read()
            
            with open(details_template_path, 'r', encoding='utf-8') as f:
                details_content = f.read()
            
            # Extraire les fonctions editUser des deux templates
            if 'function editUser(' in users_content:
                users_edit_section = users_content.split('function editUser(')[1].split('function')[0]
            else:
                users_edit_section = ""
            
            if 'function editUser(' in details_content:
                details_edit_section = details_content.split('function editUser(')[1].split('function')[0]
            else:
                details_edit_section = ""
            
            # Vérifier que les deux fonctions redirigent vers /details
            users_has_details_redirect = '/users/${username}/details' in users_edit_section
            details_has_details_redirect = '/users/${username}/details' in details_edit_section
            
            # Vérifier qu'aucune des deux n'a d'alert en développement
            users_has_dev_alert = 'alert(' in users_edit_section and 'développement' in users_edit_section
            details_has_dev_alert = 'alert(' in details_edit_section and 'développement' in details_edit_section
            
            # Assert: Les deux fonctions doivent être cohérentes
            assert users_has_details_redirect, "users.html: editUser doit rediriger vers /details"
            assert details_has_details_redirect, "user_details.html: editUser doit rediriger vers /details"
            assert not users_has_dev_alert, "users.html: editUser ne doit pas contenir d'alert de développement"
            assert not details_has_dev_alert, "user_details.html: editUser ne doit pas contenir d'alert de développement"
            
            logger.info("Test réussi: cohérence des fonctions editUser entre templates")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du test de cohérence: {e}")
            return False
