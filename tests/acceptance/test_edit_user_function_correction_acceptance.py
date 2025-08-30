"""
Tests d'acceptance pour la correction de la fonction editUser.
Méthodologie: Tests end-to-end des scénarios utilisateur avec la fonction corrigée.
"""

import pytest
from unittest.mock import patch, Mock
from src.web.condo_app import app
from src.infrastructure.logger_manager import get_logger

logger = get_logger(__name__)


class TestEditUserFunctionCorrectionAcceptance:
    """Tests d'acceptance de la correction de la fonction editUser."""
    
    def setup_method(self):
        """Configuration du client de test Flask."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Données de test cohérentes
        self.test_users = [
            {
                'username': 'resident1',
                'full_name': 'Jean Dupont',
                'email': 'jean.dupont@email.com',
                'role': {'value': 'resident'},
                'condo_unit': 'A-101',
                'last_login': '2025-08-30 09:15:30',
                'created_at': '2025-02-20',
                'status': 'Actif'
            },
            {
                'username': 'admin1',
                'full_name': 'Admin Principal',
                'email': 'admin@condos.com',
                'role': {'value': 'admin'},
                'condo_unit': None,
                'last_login': '2025-08-29 14:30:00',
                'created_at': '2025-01-15',
                'status': 'Actif'
            }
        ]
        
        self.test_user_details = {
            'resident1': {
                'username': 'resident1',
                'full_name': 'Jean Dupont',
                'email': 'jean.dupont@email.com',
                'role': 'resident',
                'role_display': 'Résident',
                'condo_unit': 'A-101',
                'has_condo_unit': True,
                'last_login': '2025-08-30 09:15:30',
                'created_at': '2025-02-20',
                'status': 'Actif'
            }
        }
    
    def test_scenario_admin_clique_modifier_utilisateur_dans_liste(self):
        """
        Scénario: Un admin clique sur "Modifier" dans la liste des utilisateurs
        
        Étapes:
        1. L'admin accède à la page de gestion des utilisateurs (/users)
        2. L'admin voit la liste des utilisateurs avec boutons d'action
        3. L'admin clique sur le bouton "Modifier" d'un utilisateur
        4. Le système redirige vers la page de détails de l'utilisateur
        5. L'admin peut consulter toutes les informations de l'utilisateur
        """
        with self.client as client:
            # Étape 1: Session admin
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin1'
                sess['user_role'] = 'admin'
                sess['user_name'] = 'Admin Principal'
            
            # Mock des services pour l'ensemble du scénario
            with patch('src.application.services.user_service.UserService') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                
                # Mock pour la page users
                mock_service.get_users_for_web_display.return_value = self.test_users
                
                # Mock pour la page de détails
                mock_service.get_user_details_by_username.return_value = self.test_user_details['resident1']
                
                # Étape 2: Accès à la page de gestion des utilisateurs
                users_response = client.get('/users')
                assert users_response.status_code == 200
                
                # Vérifier que la liste des utilisateurs est affichée
                assert b'Jean Dupont' in users_response.data
                assert b'resident1' in users_response.data
                
                # Vérifier que les boutons "Modifier" sont présents avec la fonction corrigée
                assert b'onclick="editUser(' in users_response.data
                assert b'function editUser(' in users_response.data
                assert b'window.location.href' in users_response.data
                
                # Étape 3-4: Simuler le clic sur "Modifier" (redirection vers détails)
                details_response = client.get('/users/resident1/details')
                
                # Étape 5: Vérifier que la page de détails s'affiche correctement
                assert details_response.status_code == 200
                assert b'Jean Dupont' in details_response.data
                assert b'jean.dupont@email.com' in details_response.data
                assert b'A-101' in details_response.data
                assert b'R\xc3\xa9sident' in details_response.data  # Résident encodé UTF-8
                
                # Vérifier que les services ont été appelés correctement
                mock_service.get_users_for_web_display.assert_called()
                mock_service.get_user_details_by_username.assert_called_with('resident1')
                
                logger.info("Scénario réussi: admin clique Modifier -> consultation détails")
    
    def test_scenario_fonction_edit_user_ne_bloque_plus_interface(self):
        """
        Scénario: La fonction editUser ne bloque plus l'interface avec des alertes
        
        Étapes:
        1. Un admin accède à la page users
        2. L'admin voit les boutons "Modifier" sur chaque utilisateur
        3. La fonction editUser est présente et opérationnelle
        4. Aucune alerte de "fonctionnalité en développement" n'est présente
        5. La fonction redirige correctement vers les détails
        """
        with self.client as client:
            # Étape 1: Session admin
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin1'
                sess['user_role'] = 'admin'
            
            # Mock du service
            with patch('src.application.services.user_service.UserService') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                mock_service.get_users_for_web_display.return_value = self.test_users
                
                # Étape 2-3: Charger la page users
                response = client.get('/users')
                assert response.status_code == 200
                
                # Étape 4: Vérifier l'absence d'alertes de développement
                assert b'Fonctionnalit\xc3\xa9 en d\xc3\xa9veloppement' not in response.data
                assert b'en d\xc3\xa9veloppement' not in response.data
                
                # Étape 5: Vérifier que la fonction redirige vers les détails
                assert b'function editUser(' in response.data
                assert b'/users/${username}/details' in response.data
                
                # Vérifier que les boutons sont toujours présents et fonctionnels
                assert b'onclick="editUser(' in response.data
                assert b'btn-text">Modifier</span>' in response.data
                
                logger.info("Scénario réussi: fonction editUser ne bloque plus l'interface")
    
    def test_scenario_coherence_experience_utilisateur_entre_pages(self):
        """
        Scénario: Cohérence de l'expérience utilisateur entre pages users et user_details
        
        Étapes:
        1. Un admin navigue entre la liste des utilisateurs et les détails
        2. Les boutons "Modifier" dans les deux pages ont le même comportement
        3. L'expérience utilisateur est cohérente et fluide
        4. Aucune alerte parasite n'interrompt la navigation
        """
        with self.client as client:
            # Session admin
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin1'
                sess['user_role'] = 'admin'

            # Mock des services
            with patch('src.application.services.user_service.UserService') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                mock_service.get_users_for_web_display.return_value = self.test_users
                mock_service.get_user_details_by_username.return_value = self.test_user_details['resident1']
                
                # Étape 1: Navigation users -> détails
                users_response = client.get('/users')
                assert users_response.status_code == 200
                
                details_response = client.get('/users/resident1/details')
                assert details_response.status_code == 200
                
                # Étape 2-3: Vérifier la cohérence des fonctions editUser
                # Dans users.html
                assert b'function editUser(' in users_response.data
                assert b'/users/${username}/details' in users_response.data
                
                # Dans user_details.html
                assert b'function editUser(' in details_response.data
                assert b'/users/${username}/details' in details_response.data
                
                # Étape 4: Vérifier l'absence d'alertes parasites
                assert b'alert(' not in users_response.data.split(b'function editUser(')[1].split(b'function')[0]
                assert b'alert(' not in details_response.data.split(b'function editUser(')[1].split(b'function')[0]
                
                # Vérifier que les boutons "Modifier" sont présents dans les deux pages
                assert b'onclick="editUser(' in users_response.data
                # Utiliser une vérification plus flexible pour user_details.html à cause de l'encodage UTF-8
                details_content = details_response.data.decode('utf-8')
                assert 'onclick="editUser(' in details_content
                
                logger.info("Scénario réussi: cohérence expérience utilisateur entre pages")
    
    def test_scenario_regression_aucune_fonctionnalite_cassee(self):
        """
        Scénario: Test de régression - aucune fonctionnalité existante n'est cassée
        
        Étapes:
        1. Vérifier que toutes les autres fonctions JavaScript sont intactes
        2. Vérifier que les autres boutons fonctionnent toujours
        3. Vérifier que la suppression d'utilisateur fonctionne toujours
        4. Vérifier que la création d'utilisateur fonctionne toujours
        """
        with self.client as client:
            # Session admin
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin1'
                sess['user_role'] = 'admin'
            
            # Mock du service
            with patch('src.application.services.user_service.UserService') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                mock_service.get_users_for_web_display.return_value = self.test_users
                
                # Charger la page users
                response = client.get('/users')
                assert response.status_code == 200
                
                # Étape 1-2: Vérifier que les autres fonctions JavaScript sont présentes
                assert b'function viewUserDetails(' in response.data
                assert b'function confirmDeleteUser(' in response.data
                assert b'function showCreateUserModal(' in response.data
                assert b'function hideCreateUserModal(' in response.data
                assert b'function createUser(' in response.data
                
                # Étape 3: Vérifier que la fonction de suppression est toujours fonctionnelle
                delete_section = response.data.split(b'function confirmDeleteUser(')[1].split(b'function')[0]
                assert b'fetch(' in delete_section
                assert b'DELETE' in delete_section
                
                # Étape 4: Vérifier que la création d'utilisateur est toujours présente
                assert b'createUserModal' in response.data
                assert b'createUserForm' in response.data
                
                # Vérifier que les boutons d'action sont tous présents
                assert b'btn-text">D\xc3\xa9tails</span>' in response.data
                assert b'btn-text">Modifier</span>' in response.data
                assert b'btn-text">Supprimer</span>' in response.data
                
                logger.info("Scénario réussi: aucune régression détectée")
