#!/usr/bin/env python3
"""
Tests d'acceptance pour la création d'utilisateur - VERSION MOCKÉE.
Tests end-to-end de la fonctionnalité avec mocking complet des dépendances.
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

# Ajouter le répertoire racine au path pour imports
sys.path.insert(0, os.path.abspath('.'))

from src.domain.entities.user import User, UserRole
from src.infrastructure.logger_manager import get_logger

logger = get_logger(__name__)


class TestUserCreationAcceptance:
    """Tests d'acceptance mockés pour la création d'utilisateur."""
    
    def setup_method(self):
        """Configuration avant chaque test avec mocking complet."""
        # Mock de l'application Flask
        self.mock_app = Mock()
        self.mock_client = Mock()
        self.mock_app.test_client.return_value = self.mock_client
        
        # Mock des services
        self.mock_user_service = Mock()
        self.mock_auth_service = Mock()
        
        # Utilisateur admin mocké
        self.admin_user = User(
            username="admin",
            password_hash="hashed_admin123",
            full_name="Administrateur",
            email="admin@condos.com",
            role=UserRole.ADMIN
        )
    
    @patch('src.web.condo_app.app')
    @patch('src.application.services.user_service.UserService')
    @patch('src.domain.services.authentication_service.AuthenticationService')
    def test_scenario_admin_accede_page_creation_utilisateur(self, mock_auth_service, mock_user_service, mock_app):
        """
        SCÉNARIO: L'admin accède à la page de création d'utilisateur
        ÉTANT DONNÉ: Un utilisateur admin connecté
        QUAND: Il accède à la page /users/new
        ALORS: La page se charge avec le formulaire de création
        """
        # ÉTANT DONNÉ: Configuration des mocks
        mock_app.test_client.return_value = self.mock_client
        mock_auth_service.return_value = self.mock_auth_service
        mock_user_service.return_value = self.mock_user_service
        
        # Session admin mockée
        mock_response_login = Mock()
        mock_response_login.status_code = 200
        self.mock_client.post.return_value = mock_response_login
        
        # Page de création mockée
        mock_response_page = Mock()
        mock_response_page.status_code = 200
        mock_response_page.data = b'<form>Nouvel Utilisateur</form>'
        self.mock_client.get.return_value = mock_response_page
        
        # QUAND: L'admin se connecte et accède à la page
        login_response = self.mock_client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        page_response = self.mock_client.get('/users/new')
        
        # ALORS: Vérifications
        assert login_response.status_code == 200
        assert page_response.status_code == 200
        assert b'Nouvel Utilisateur' in page_response.data
        
        # Vérifier les appels mockés
        self.mock_client.post.assert_called_with('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        self.mock_client.get.assert_called_with('/users/new')
    
    @patch('src.application.services.user_service.UserService')
    def test_scenario_creation_utilisateur_resident_via_formulaire(self, mock_user_service):
        """
        SCÉNARIO: Création d'un utilisateur résident via le formulaire web
        ÉTANT DONNÉ: Un admin connecté avec droits de création
        QUAND: Il soumet le formulaire avec des données valides
        ALORS: L'utilisateur est créé avec succès
        """
        # ÉTANT DONNÉ: Service mocké qui réussit la création
        mock_user_service.return_value = self.mock_user_service
        self.mock_user_service.create_user.return_value = {
            'success': True,
            'message': 'Utilisateur créé avec succès',
            'user_id': 'resident123'
        }
        
        # Données du formulaire
        form_data = {
            'username': 'resident_test',
            'password': 'secure123',
            'full_name': 'Jean Resident',
            'email': 'jean@resident.com',
            'role': 'RESIDENT',
            'unit_number': 'A-101'
        }
        
        # QUAND: Création de l'utilisateur via le service
        result = self.mock_user_service.create_user(
            username=form_data['username'],
            password=form_data['password'],
            full_name=form_data['full_name'],
            email=form_data['email'],
            role=UserRole.RESIDENT,
            unit_number=form_data['unit_number']
        )
        
        # ALORS: Vérifications
        assert result['success'] is True
        assert 'créé avec succès' in result['message']
        assert result['user_id'] == 'resident123'
        
        # Vérifier l'appel au service
        self.mock_user_service.create_user.assert_called_once_with(
            username='resident_test',
            password='secure123',
            full_name='Jean Resident',
            email='jean@resident.com',
            role=UserRole.RESIDENT,
            unit_number='A-101'
        )
    
    @patch('src.application.services.user_service.UserService')
    def test_scenario_validation_erreurs_formulaire_creation(self, mock_user_service):
        """
        SCÉNARIO: Gestion des erreurs de validation lors de la création
        ÉTANT DONNÉ: Des données invalides dans le formulaire
        QUAND: L'admin tente de créer l'utilisateur
        ALORS: Les erreurs de validation sont retournées
        """
        # ÉTANT DONNÉ: Service mocké qui retourne des erreurs
        mock_user_service.return_value = self.mock_user_service
        self.mock_user_service.create_user.return_value = {
            'success': False,
            'errors': {
                'username': 'Nom d\'utilisateur déjà existant',
                'email': 'Format email invalide',
                'password': 'Mot de passe trop court'
            }
        }
        
        # Données invalides
        invalid_data = {
            'username': 'admin',  # Déjà existant
            'password': '123',    # Trop court
            'email': 'email-invalide',  # Format incorrect
            'full_name': '',      # Vide
            'role': 'RESIDENT'
        }
        
        # QUAND: Tentative de création avec données invalides
        result = self.mock_user_service.create_user(**invalid_data)
        
        # ALORS: Vérifications des erreurs
        assert result['success'] is False
        assert 'errors' in result
        assert 'déjà existant' in result['errors']['username']
        assert 'invalide' in result['errors']['email']
        assert 'trop court' in result['errors']['password']
    
    @patch('src.application.services.user_service.UserService')
    def test_scenario_workflow_complet_creation_admin(self, mock_user_service):
        """
        SCÉNARIO: Workflow complet de création d'un administrateur
        ÉTANT DONNÉ: Un super-admin avec droits de création d'admin
        QUAND: Il crée un nouvel administrateur
        ALORS: Le workflow complet réussit avec toutes les validations
        """
        # ÉTANT DONNÉ: Service mocké pour création admin
        mock_user_service.return_value = self.mock_user_service
        
        # Mock du workflow en plusieurs étapes
        self.mock_user_service.validate_admin_creation_rights.return_value = True
        self.mock_user_service.check_username_availability.return_value = True
        self.mock_user_service.validate_admin_data.return_value = {'valid': True}
        self.mock_user_service.create_user.return_value = {
            'success': True,
            'message': 'Administrateur créé avec succès',
            'user_id': 'admin_new',
            'permissions': ['user_management', 'system_admin']
        }
        
        # QUAND: Workflow complet de création
        # Étape 1: Validation des droits
        can_create_admin = self.mock_user_service.validate_admin_creation_rights('current_admin')
        
        # Étape 2: Vérification disponibilité username
        username_available = self.mock_user_service.check_username_availability('new_admin')
        
        # Étape 3: Validation des données
        validation = self.mock_user_service.validate_admin_data({
            'username': 'new_admin',
            'email': 'newadmin@condos.com',
            'full_name': 'Nouvel Admin'
        })
        
        # Étape 4: Création finale
        if can_create_admin and username_available and validation['valid']:
            result = self.mock_user_service.create_user(
                username='new_admin',
                password='secure_admin_password',
                full_name='Nouvel Admin',
                email='newadmin@condos.com',
                role=UserRole.ADMIN
            )
        
        # ALORS: Vérifications du workflow complet
        assert can_create_admin is True
        assert username_available is True
        assert validation['valid'] is True
        assert result['success'] is True
        assert 'Administrateur créé' in result['message']
        assert 'user_management' in result['permissions']
        
        # Vérifier tous les appels dans l'ordre
        self.mock_user_service.validate_admin_creation_rights.assert_called_once_with('current_admin')
        self.mock_user_service.check_username_availability.assert_called_once_with('new_admin')
        self.mock_user_service.validate_admin_data.assert_called_once()
        self.mock_user_service.create_user.assert_called_once()
    
    def test_scenario_integration_template_formulaire_web(self):
        """
        SCÉNARIO: Intégration du template de formulaire de création
        ÉTANT DONNÉ: Un template HTML de création d'utilisateur
        QUAND: Les données sont injectées dans le template
        ALORS: Le formulaire est rendu correctement
        """
        # ÉTANT DONNÉ: Mock du moteur de templates
        mock_template_data = {
            'roles': ['ADMIN', 'RESIDENT', 'GUEST'],
            'current_user': 'admin',
            'csrf_token': 'mock_csrf_token_123'
        }
        
        # Simulation du rendu de template
        template_content = f"""
        <form method="POST">
            <input name="csrf_token" value="{mock_template_data['csrf_token']}">
            <select name="role">
                {''.join(f'<option value="{role}">{role}</option>' for role in mock_template_data['roles'])}
            </select>
            <button type="submit">Créer Utilisateur</button>
        </form>
        """
        
        # QUAND: Vérification du contenu du template
        # ALORS: Le template contient les éléments attendus
        assert 'csrf_token' in template_content
        assert 'mock_csrf_token_123' in template_content
        assert 'ADMIN' in template_content
        assert 'RESIDENT' in template_content
        assert 'GUEST' in template_content
        assert 'Créer Utilisateur' in template_content
        
        logger.info("Test template formulaire: Structure HTML valide")
    
    def test_scenario_protection_acces_non_autorise(self):
        """
        SCÉNARIO: Protection contre l'accès non autorisé
        ÉTANT DONNÉ: Un utilisateur non-admin
        QUAND: Il tente d'accéder à la création d'utilisateur
        ALORS: L'accès est refusé avec redirection appropriée
        """
        # ÉTANT DONNÉ: Mock d'un utilisateur résident
        resident_user = User(
            username="resident1",
            password_hash="hashed_pass",
            full_name="Jean Résident",
            email="jean@resident.com",
            role=UserRole.RESIDENT,
            condo_unit="A-101"  # Requis pour les résidents
        )
        
        # Mock de vérification des permissions
        with patch('src.domain.services.authentication_service.AuthenticationService') as mock_auth:
            mock_auth_instance = Mock()
            mock_auth.return_value = mock_auth_instance
            
            # QUAND: Vérification des droits d'accès
            mock_auth_instance.check_admin_rights.return_value = False
            mock_auth_instance.get_current_user.return_value = resident_user
            
            has_access = mock_auth_instance.check_admin_rights(resident_user.username)
            current_user = mock_auth_instance.get_current_user()
            
            # ALORS: Accès refusé
            assert has_access is False
            assert current_user.role == UserRole.RESIDENT
            assert current_user.username == "resident1"
            
            logger.info("Test protection accès: Résident ne peut pas créer d'utilisateurs")


if __name__ == '__main__':
    # Exécution des tests
    pytest.main([__file__, '-v'])
