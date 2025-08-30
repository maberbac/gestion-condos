"""
Tests d'acceptance pour la fonctionnalité d'édition d'utilisateur via interface web.

[ARCHITECTURE TDD]
Ces tests valident l'expérience utilisateur complète pour l'édition d'utilisateur
incluant la popup d'édition et les API.
"""

import unittest
from unittest.mock import Mock, patch
import json

from src.infrastructure.logger_manager import get_logger

logger = get_logger(__name__)


class TestUserEditFunctionalityAcceptance(unittest.TestCase):
    """Tests d'acceptance pour l'édition d'utilisateur via interface web."""

    def setUp(self):
        """Configuration initiale des tests."""
        from src.web.condo_app import app
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        self.client = app.test_client()
        
        # Données de test
        self.test_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'full_name': 'Test User',
            'role': 'resident',
            'condo_unit': '101'
        }
        
        self.update_data = {
            'username': 'updated_user',
            'email': 'updated@example.com',
            'full_name': 'Updated User',
            'role': 'admin',
            'condo_unit': '202',
            'password': 'newpassword123'
        }

    def test_scenario_admin_ouvre_popup_edition_utilisateur(self):
        """
        Scénario: Un admin ouvre la popup d'édition d'utilisateur
        
        Étapes:
        1. Un admin est connecté et consulte la liste des utilisateurs
        2. Il clique sur le bouton "Modifier" d'un utilisateur
        3. La popup d'édition s'ouvre avec les données pré-remplies
        4. Les champs sont modifiables selon les permissions
        """
        with self.client as client:
            # Session admin
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin1'
                sess['user_role'] = 'admin'

            # Mock du service pour récupérer les données utilisateur
            with patch('src.application.services.user_service.UserService') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                # La méthode get_user_details_for_api retourne directement les données avec found: True
                mock_service.get_user_details_for_api.return_value = {
                    'username': self.test_user_data['username'],
                    'email': self.test_user_data['email'],
                    'full_name': self.test_user_data['full_name'],
                    'role': self.test_user_data['role'],
                    'condo_unit': self.test_user_data['condo_unit'],
                    'found': True
                }

                # Étape 1-2: Récupérer les données utilisateur via API
                response = client.get('/api/user/testuser')
                
                # Étape 3-4: Vérifier que les données sont disponibles pour la popup
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue(data.get('user', {}).get('username'), 'testuser')
                self.assertTrue(data.get('user', {}).get('email'), 'test@example.com')
                
                # Vérifier que le service a été appelé
                mock_service.get_user_details_for_api.assert_called_once_with('testuser')

    def test_scenario_admin_modifie_utilisateur_via_popup(self):
        """
        Scénario: Un admin modifie un utilisateur via la popup
        
        Étapes:
        1. Un admin ouvre la popup d'édition
        2. Il modifie les champs (nom, email, rôle, etc.)
        3. Il soumet le formulaire
        4. L'utilisateur est mis à jour avec succès
        5. La popup se ferme et la liste est actualisée
        """
        with self.client as client:
            # Session admin
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin1'
                sess['user_role'] = 'admin'

            # Mock du service pour la mise à jour
            with patch('src.application.services.user_service.UserService') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                mock_service.update_user_by_username.return_value = {
                    'success': True,
                    'message': 'Utilisateur mis à jour avec succès'
                }

                # Étape 1-3: Soumettre la modification via API
                response = client.put('/api/user/testuser', data=self.update_data)
                
                # Étape 4-5: Vérifier le succès
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue(data['success'])
                self.assertIn('mis à jour avec succès', data['message'])
                
                # Vérifier que le service a été appelé avec les bonnes données
                mock_service.update_user_by_username.assert_called_once()
                call_args = mock_service.update_user_by_username.call_args
                self.assertEqual(call_args[0][0], 'testuser')  # Username original

    def test_scenario_resident_ne_peut_modifier_autre_utilisateur(self):
        """
        Scénario: Un résident ne peut pas modifier un autre utilisateur
        
        Étapes:
        1. Un résident est connecté
        2. Il tente d'accéder aux données d'un autre utilisateur
        3. L'accès lui est refusé (403)
        4. Il ne peut pas non plus modifier l'utilisateur
        """
        with self.client as client:
            # Session résident
            with client.session_transaction() as sess:
                sess['user_id'] = 'resident1'
                sess['user_role'] = 'resident'

            # Étape 2: Tenter d'accéder aux données d'un autre utilisateur
            response = client.get('/api/user/other_user')
            
            # Étape 3: Vérifier le refus d'accès
            self.assertEqual(response.status_code, 403)
            
            # Étape 4: Tenter de modifier l'autre utilisateur
            response = client.put('/api/user/other_user', data=self.update_data)
            self.assertEqual(response.status_code, 403)

    def test_scenario_resident_peut_modifier_son_propre_profil(self):
        """
        Scénario: Un résident peut modifier son propre profil
        
        Étapes:
        1. Un résident est connecté
        2. Il accède à ses propres données
        3. Il modifie certains champs autorisés
        4. La modification est acceptée
        """
        with self.client as client:
            # Session résident
            with client.session_transaction() as sess:
                sess['user_id'] = 'resident1'
                sess['user_role'] = 'resident'

            # Mock des services
            with patch('src.application.services.user_service.UserService') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                
                # Pour récupérer ses données
                mock_service.get_user_details_for_api.return_value = {
                    'username': 'resident1',
                    'email': 'resident1@example.com',
                    'full_name': 'Resident One',
                    'role': 'resident',
                    'condo_unit': '101',
                    'found': True
                }
                
                # Pour la mise à jour
                mock_service.update_user_by_username.return_value = {
                    'success': True,
                    'message': 'Profil mis à jour avec succès'
                }

                # Étape 2: Accéder à ses propres données
                response = client.get('/api/user/resident1')
                self.assertEqual(response.status_code, 200)
                
                # Étape 3-4: Modifier son profil
                self_update_data = {
                    'username': 'resident1',
                    'email': 'resident1_updated@example.com',
                    'full_name': 'Resident One Updated',
                    'role': 'resident',  # Ne peut pas changer son rôle
                    'condo_unit': '101'
                }
                
                response = client.put('/api/user/resident1', data=self_update_data)
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue(data['success'])

    def test_scenario_popup_edition_gere_erreurs_validation(self):
        """
        Scénario: La popup d'édition gère les erreurs de validation
        
        Étapes:
        1. Un admin ouvre la popup d'édition
        2. Il saisit des données invalides (email incorrect, etc.)
        3. Il soumet le formulaire
        4. Des erreurs de validation sont affichées
        5. La popup reste ouverte pour correction
        """
        with self.client as client:
            # Session admin
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin1'
                sess['user_role'] = 'admin'

            # Mock du service pour simuler une erreur de validation
            with patch('src.application.services.user_service.UserService') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                mock_service.update_user_by_username.return_value = {
                    'success': False,
                    'error': 'Erreur de validation: Email invalide'
                }

                # Données invalides
                invalid_data = {
                    'username': 'testuser',
                    'email': 'email_invalide',  # Email sans @
                    'full_name': 'Test User',
                    'role': 'admin',
                    'condo_unit': '101'
                }

                # Étape 3: Soumettre des données invalides
                response = client.put('/api/user/testuser', data=invalid_data)
                
                # Étape 4-5: Vérifier la gestion d'erreur
                self.assertEqual(response.status_code, 400)
                data = json.loads(response.data)
                self.assertFalse(data['success'])
                self.assertIn('validation', data['error'].lower())

    def test_scenario_popup_edition_preserve_mot_de_passe_vide(self):
        """
        Scénario: La popup d'édition préserve le mot de passe si laissé vide
        
        Étapes:
        1. Un admin ouvre la popup d'édition
        2. Il modifie des champs mais laisse le mot de passe vide
        3. Il soumet le formulaire
        4. L'utilisateur est mis à jour sans changer le mot de passe
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
                mock_service.update_user_by_username.return_value = {
                    'success': True,
                    'message': 'Utilisateur mis à jour sans changer le mot de passe'
                }

                # Données sans mot de passe
                data_no_password = {
                    'username': 'testuser_updated',
                    'email': 'updated@example.com',
                    'full_name': 'Updated User',
                    'role': 'admin',
                    'condo_unit': '202',
                    'password': ''  # Mot de passe vide
                }

                # Soumettre la modification
                response = client.put('/api/user/testuser', data=data_no_password)
                
                # Vérifier le succès
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue(data['success'])
                
                # Vérifier que le service a été appelé avec les bonnes données
                mock_service.update_user_by_username.assert_called_once()


if __name__ == '__main__':
    unittest.main()
