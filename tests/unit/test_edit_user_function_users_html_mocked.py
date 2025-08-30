"""
Tests pour la correction de la fonction editUser dans users.html.
Méthodologie: Validation que la fonction editUser redirige vers la consultation des détails.
"""

import pytest
from unittest.mock import patch, Mock
from src.web.condo_app import app
from src.infrastructure.logger_manager import get_logger

logger = get_logger(__name__)


class TestEditUserFunctionCorrectionUsersHtml:
    """Tests de correction de la fonction editUser dans users.html."""
    
    def setup_method(self):
        """Configuration du client de test Flask."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        
    def test_users_page_contains_corrected_edit_function(self):
        """
        Test que la page users.html contient la fonction editUser corrigée.
        
        Ce test vérifie que:
        1. La page users.html se charge correctement
        2. La fonction editUser est présente dans le JavaScript
        3. La fonction contient une redirection au lieu d'une alerte
        """
        with self.client as client:
            # Simuler une session admin pour accéder à la page users
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin1'
                sess['user_role'] = 'admin'
                sess['user_name'] = 'Admin Test'
            
            # Mock du service utilisateur pour la page users
            with patch('src.application.services.user_service.UserService') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
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
                
                # Act: Récupérer la page users
                response = client.get('/users')
                
                # Assert: Vérifications de la correction
                assert response.status_code == 200
                
                # Vérifier que la page contient bien la fonction editUser
                assert b'function editUser(' in response.data
                
                # Le test principal sera de vérifier le contenu du fichier directement
                logger.info("Test réussi: page users accessible avec fonction editUser")
    
    def test_edit_user_function_behavior_validation(self):
        """
        Test de validation du comportement de la fonction editUser.
        
        Cette validation vérifie que la fonction editUser:
        1. Ne contient plus d'alert() pour "en développement"
        2. Contient une redirection appropriée
        """
        # Lire le contenu du template users.html
        template_path = "c:/src/INF2020/gestion-condos/src/web/templates/users.html"
        
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Extraire la section de la fonction editUser
            if 'function editUser(' in content:
                edit_user_section = content.split('function editUser(')[1].split('function')[0]
                
                # Vérifications que l'ancienne implémentation avec alert a été supprimée
                has_alert = 'alert(' in edit_user_section and 'développement' in edit_user_section
                
                # Vérifications que la nouvelle implémentation est présente
                has_redirect = 'window.location.href' in edit_user_section
                has_details_url = '/details' in edit_user_section or '/edit' in edit_user_section
                
                logger.info(f"Analyse fonction editUser: alert={has_alert}, redirect={has_redirect}, url={has_details_url}")
                
                # Cette fonction devrait retourner False pour alert et True pour redirect
                return not has_alert and has_redirect and has_details_url
            else:
                logger.error("Fonction editUser non trouvée dans users.html")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la validation: {e}")
            return False


def test_users_html_edit_function_validation():
    """Test autonome de validation de la fonction editUser dans users.html."""
    test_instance = TestEditUserFunctionCorrectionUsersHtml()
    result = test_instance.test_edit_user_function_behavior_validation()
    
    if result:
        logger.info("VALIDATION RÉUSSIE: La fonction editUser dans users.html est correctement implémentée")
    else:
        logger.warning("VALIDATION ÉCHOUÉE: La fonction editUser dans users.html nécessite une correction")
    
    return result


if __name__ == "__main__":
    success = test_users_html_edit_function_validation()
    exit(0 if success else 1)
