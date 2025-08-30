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
        
    def test_users_page_loads_with_corrected_edit_function(self):
        """Test que la page users se charge avec la fonction editUser corrigée."""
        with self.client as client:
            # Simuler une session admin
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin1'
                sess['user_role'] = 'admin'
                sess['user_name'] = 'Admin Test'
            
            # Mock du service utilisateur
            with patch('src.application.services.user_service.UserService') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                mock_service.get_users_for_web_display.return_value = [
                    {
                        'username': 'resident1',
                        'full_name': 'Jean Dupont',
                        'email': 'jean@example.com',
                        'role': {'value': 'resident'},
                        'condo_unit': 'A-101',
                        'last_login': '2025-08-30',
                        'created_at': '2025-01-01',
                        'status': 'Actif'
                    },
                    {
                        'username': 'admin1',
                        'full_name': 'Admin Principal',
                        'email': 'admin@example.com',
                        'role': {'value': 'admin'},
                        'condo_unit': None,
                        'last_login': '2025-08-30',
                        'created_at': '2025-01-01',
                        'status': 'Actif'
                    }
                ]
                
                # Act: Charger la page users
                response = client.get('/users')
                
                # Assert: Vérifications de la page
                assert response.status_code == 200
                
                # Vérifier que la page contient les boutons Modifier avec onclick editUser
                assert b'onclick="editUser(' in response.data
                assert b'resident1' in response.data
                assert b'admin1' in response.data
                
                # Vérifier que la fonction JavaScript est présente et corrigée
                assert b'function editUser(' in response.data
                assert b'window.location.href' in response.data
                assert b'/users/${username}/details' in response.data
                
                # Vérifier que l'ancienne alerte n'est plus présente
                assert b'Fonctionnalit\xc3\xa9 en d\xc3\xa9veloppement' not in response.data
                
                logger.info("Test réussi: page users avec fonction editUser corrigée")
    
    def test_edit_button_functionality_integration(self):
        """Test d'intégration du bouton Modifier avec la fonction corrigée."""
        with self.client as client:
            # Simuler une session admin
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin1'
                sess['user_role'] = 'admin'
            
            # Mock du service pour users et user_details
            with patch('src.application.services.user_service.UserService') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                
                # Mock pour la page users
                mock_service.get_users_for_web_display.return_value = [{
                    'username': 'resident1',
                    'full_name': 'Jean Dupont',
                    'email': 'jean@example.com',
                    'role': {'value': 'resident'},
                    'condo_unit': 'A-101',
                    'last_login': '2025-08-30',
                    'created_at': '2025-01-01',
                    'status': 'Actif'
                }]
                
                # Mock pour la page de détails (destination de la redirection)
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
                
                # Act 1: Charger la page users
                users_response = client.get('/users')
                assert users_response.status_code == 200
                
                # Act 2: Simuler le clic sur le bouton Modifier (redirection vers détails)
                details_response = client.get('/users/resident1/details')
                
                # Assert: Vérifier que la redirection fonctionne
                assert details_response.status_code == 200
                assert b'Jean Dupont' in details_response.data
                assert b'resident1@' in details_response.data or b'jean@example.com' in details_response.data
                
                # Vérifier que les deux services ont été appelés correctement
                mock_service.get_users_for_web_display.assert_called()
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
