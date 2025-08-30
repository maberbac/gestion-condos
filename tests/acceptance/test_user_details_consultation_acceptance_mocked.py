"""
Tests d'acceptance pour la consultation des détails d'utilisateur.
Méthodologie: Tests end-to-end des scénarios utilisateur complets avec données contrôlées.
"""

import pytest
from unittest.mock import patch, Mock
import json
from src.web.condo_app import app
from src.infrastructure.logger_manager import get_logger

logger = get_logger(__name__)


class TestUserDetailsConsultationAcceptanceMocked:
    """Tests d'acceptance de la consultation des détails utilisateur avec données contrôlées."""
    
    def setup_method(self):
        """Configuration du client de test Flask."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Données de test standardisées
        self.test_users = {
            'admin1': {
                'username': 'admin1',
                'full_name': 'Admin Principal',
                'email': 'admin@condos.com',
                'role': 'admin',
                'role_display': 'Administrateur',
                'condo_unit': 'Non assigné',
                'has_condo_unit': False,
                'last_login': '2025-08-29 14:30:00',
                'created_at': '2025-01-15',
                'status': 'Actif'
            },
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
            },
            'resident2': {
                'username': 'resident2',
                'full_name': 'Marie Tremblay',
                'email': 'marie.tremblay@email.com',
                'role': 'resident',
                'role_display': 'Résident',
                'condo_unit': 'B-205',
                'has_condo_unit': True,
                'last_login': 'Jamais connecté',
                'created_at': '2025-03-10',
                'status': 'Actif'
            }
        }
    
    def test_scenario_admin_consulte_details_resident(self):
        """
        Scénario: Un administrateur consulte les détails d'un résident
        
        Étapes:
        1. L'admin se connecte et accède à la gestion des utilisateurs
        2. L'admin clique sur "Détails" pour un résident
        3. Le système affiche les informations complètes du résident
        4. L'admin peut voir les permissions et l'historique
        """
        with self.client as client:
            # Étape 1: Session admin
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin1'
                sess['user_role'] = 'admin'
                sess['user_name'] = 'Admin Principal'
            
            # Étape 2-3: Mock du service et consultation des détails
            with patch('src.application.services.user_service.UserService') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                mock_service.get_user_details_by_username.return_value = self.test_users['resident1']
                
                # Act: Consultation des détails
                response = client.get('/users/resident1/details')
                
                # Assert: Vérifications complètes
                assert response.status_code == 200
                
                # Vérifier les informations personnelles
                assert b'Jean Dupont' in response.data
                assert b'jean.dupont@email.com' in response.data
                assert b'resident1' in response.data
                
                # Vérifier les informations de propriété
                assert b'A-101' in response.data
                assert b'Propri\xc3\xa9taire' in response.data  # Propriétaire encodé UTF-8
                
                # Vérifier l'activité du compte
                assert b'2025-08-30 09:15:30' in response.data
                assert b'Actif' in response.data
                
                # Vérifier que le service a été appelé correctement
                mock_service.get_user_details_by_username.assert_called_once_with('resident1')
                
                logger.info("Scénario réussi: admin consulte détails résident")
    
    def test_scenario_resident_consulte_ses_propres_details(self):
        """
        Scénario: Un résident consulte ses propres détails
        
        Étapes:
        1. Le résident se connecte au système
        2. Le résident accède à ses détails via profile ou lien direct
        3. Le système affiche ses informations personnelles
        4. Le résident peut voir son statut et ses permissions
        """
        with self.client as client:
            # Étape 1: Session résident
            with client.session_transaction() as sess:
                sess['user_id'] = 'resident1'
                sess['user_role'] = 'resident'
                sess['user_name'] = 'Jean Dupont'
            
            # Étape 2-3: Mock du service et consultation
            with patch('src.application.services.user_service.UserService') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                mock_service.get_user_details_by_username.return_value = self.test_users['resident1']
                
                # Act: Consultation de ses propres détails
                response = client.get('/users/resident1/details')
                
                # Assert: Vérifications spécifiques résident
                assert response.status_code == 200
                assert b'Jean Dupont' in response.data
                assert b'A-101' in response.data
                
                # Vérifier les permissions résidents
                assert b'Consultation condos' in response.data
                assert b'Profil personnel' in response.data
                
                logger.info("Scénario réussi: résident consulte ses propres détails")
    
    def test_scenario_resident_tente_acces_details_autre_utilisateur(self):
        """
        Scénario: Un résident tente d'accéder aux détails d'un autre utilisateur
        
        Étapes:
        1. Le résident se connecte normalement
        2. Le résident tente d'accéder aux détails d'un autre utilisateur
        3. Le système refuse l'accès et redirige
        4. Un message d'erreur approprié est affiché
        """
        with self.client as client:
            # Étape 1: Session résident
            with client.session_transaction() as sess:
                sess['user_id'] = 'resident1'
                sess['user_role'] = 'resident'
                sess['user_name'] = 'Jean Dupont'
            
            # Étape 2: Tentative d'accès non autorisé
            response = client.get('/users/admin1/details')
            
            # Étape 3-4: Vérification du refus d'accès
            assert response.status_code == 302  # Redirection
            
            logger.info("Scénario réussi: résident bloqué pour accès non autorisé")
    
    def test_scenario_api_integration_pour_applications_externes(self):
        """
        Scénario: Intégration API pour une application externe
        
        Étapes:
        1. Application externe s'authentifie via session admin
        2. Application demande les détails via API REST
        3. Le système retourne les données en format JSON
        4. L'application peut traiter les données structurées
        """
        with self.client as client:
            # Étape 1: Session API avec permissions admin
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin1'
                sess['user_role'] = 'admin'
            
            # Étape 2-3: Mock du service et appel API
            with patch('src.application.services.user_service.UserService') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                api_data = self.test_users['resident2'].copy()
                api_data.update({
                    'found': True,
                    'details': {
                        'role_display': 'Résident',
                        'has_condo_unit': True,
                        'status': 'Actif'
                    }
                })
                mock_service.get_user_details_for_api.return_value = api_data
                
                # Act: Appel API
                response = client.get('/api/user/resident2')
                
                # Étape 4: Vérification des données JSON
                assert response.status_code == 200
                assert response.content_type == 'application/json'
                
                data = json.loads(response.data)
                assert data['username'] == 'resident2'
                assert data['full_name'] == 'Marie Tremblay'
                assert data['found'] is True
                assert 'details' in data
                
                mock_service.get_user_details_for_api.assert_called_once_with('resident2')
                
                logger.info("Scénario réussi: intégration API pour application externe")
    
    def test_scenario_gestion_utilisateur_inexistant(self):
        """
        Scénario: Gestion d'une demande pour un utilisateur inexistant
        
        Étapes:
        1. Un admin tente de consulter un utilisateur qui n'existe pas
        2. Le système détecte l'absence de l'utilisateur
        3. Une redirection appropriée est effectuée
        4. Un message informatif est présenté à l'admin
        """
        with self.client as client:
            # Étape 1: Session admin
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin1'
                sess['user_role'] = 'admin'
            
            # Étape 2: Mock simulant utilisateur inexistant
            with patch('src.application.services.user_service.UserService') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                mock_service.get_user_details_by_username.return_value = None
                
                # Act: Tentative de consultation
                response = client.get('/users/utilisateur_inexistant/details')
                
                # Étape 3-4: Vérification de la gestion d'erreur
                assert response.status_code == 302  # Redirection
                mock_service.get_user_details_by_username.assert_called_once_with('utilisateur_inexistant')
                
                logger.info("Scénario réussi: gestion utilisateur inexistant")
    
    def test_scenario_consultation_details_avec_permissions_complexes(self):
        """
        Scénario: Consultation détaillée des permissions selon le rôle
        
        Étapes:
        1. Admin consulte les détails d'un utilisateur admin
        2. Le système affiche toutes les permissions administratives
        3. Les permissions sont clairement distinguées (accordées vs refusées)
        4. L'interface reflète correctement le niveau d'accès
        """
        with self.client as client:
            # Étape 1: Session admin
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin1'
                sess['user_role'] = 'admin'
            
            # Étape 2: Mock du service pour utilisateur admin
            with patch('src.application.services.user_service.UserService') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                mock_service.get_user_details_by_username.return_value = self.test_users['admin1']
                
                # Act: Consultation détails admin
                response = client.get('/users/admin1/details')
                
                # Étape 3-4: Vérification des permissions admin
                assert response.status_code == 200
                
                # Vérifier les permissions administratives
                assert b'Administration compl\xc3\xa8te' in response.data  # Complète encodé UTF-8
                assert b'Gestion financi\xc3\xa8re' in response.data  # Financière encodé UTF-8
                assert b'Gestion utilisateurs' in response.data
                assert b'Acc\xc3\xa8s aux rapports' in response.data  # Accès encodé UTF-8
                
                # Vérifier le badge de rôle
                assert b'Administrateur' in response.data
                
                logger.info("Scénario réussi: consultation permissions complexes admin")
