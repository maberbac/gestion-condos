#!/usr/bin/env python3
"""
Tests d'acceptance pour la création d'utilisateur.
Tests end-to-end de la fonctionnalité de création d'utilisateur via l'interface web.
"""

import pytest
import asyncio
import os
import tempfile
import shutil
from flask.testing import FlaskClient

import sys
sys.path.insert(0, os.path.abspath('.'))

from src.web.condo_app import app
from src.adapters.user_file_adapter import UserFileAdapter
from src.domain.entities.user import UserRole


class TestUserCreationAcceptance:
    """Tests d'acceptance pour la création d'utilisateur."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        # Créer un répertoire temporaire pour les tests
        self.temp_dir = tempfile.mkdtemp()
        self.users_file = os.path.join(self.temp_dir, "test_users.json")
        
        # Configurer l'application Flask pour les tests
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Créer un utilisateur admin pour les tests
        self.admin_username = "admin"
        self.admin_password = "admin123"
    
    def teardown_method(self):
        """Nettoyage après chaque test."""
        self.app_context.pop()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def login_as_admin(self):
        """Connexion en tant qu'administrateur."""
        response = self.client.post('/login', data={
            'username': self.admin_username,
            'password': self.admin_password
        }, follow_redirects=True)
        return response
    
    def test_access_user_creation_page_as_admin(self):
        """Test accès à la page de création d'utilisateur en tant qu'admin."""
        # Arrange - se connecter en tant qu'admin
        self.login_as_admin()
        
        # Act - accéder à la page de création
        response = self.client.get('/users/new')
        
        assert response.status_code == 200
        assert ("Nouvel Utilisateur".encode('utf-8') in response.data or 
                "Créer un nouvel utilisateur".encode('utf-8') in response.data)
    
    def test_access_user_creation_page_without_login(self):
        """Test accès refusé à la page de création sans connexion."""
        # Act - essayer d'accéder à la page sans connexion
        response = self.client.get('/users/new')
        
        # Assert - redirection vers login
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_access_user_creation_page_as_non_admin(self):
        """Test accès refusé pour un non-administrateur."""
        # Arrange - se connecter en tant que résident
        self.client.post('/login', data={
            'username': 'resident_test',
            'password': 'resident123'
        })
        
        # Act - essayer d'accéder à la page
        response = self.client.get('/users/new')
        
        # Assert - accès refusé
        assert response.status_code == 403 or response.status_code == 302
    
    def test_create_user_via_web_form_success(self):
        """Test création réussie d'utilisateur via formulaire web."""
        # Arrange - se connecter en tant qu'admin
        self.login_as_admin()
        
        # Act - soumettre le formulaire de création
        response = self.client.post('/users/new', data={
            'username': 'nouveau_user_web',
            'email': 'nouveau@web.com',
            'password': 'webpass123',
            'full_name': 'Utilisateur Créé via Web',
            'role': 'resident',
            'condo_unit': 'E-501'
        }, follow_redirects=True)
        
        # Assert
        assert response.status_code == 200
        assert ("Utilisateur créé avec succès".encode('utf-8') in response.data or 
                "créé avec succès".encode('utf-8') in response.data)
    
    def test_create_user_validation_errors_web(self):
        """Test gestion des erreurs de validation via web."""
        # Arrange - se connecter en tant qu'admin
        self.login_as_admin()
        
        # Act - soumettre avec données invalides
        response = self.client.post('/users/new', data={
            'username': '',  # Username vide
            'email': 'email_invalide',  # Email invalide
            'password': '123',  # Mot de passe trop court
            'full_name': '',  # Nom vide
            'role': 'resident',
            'condo_unit': ''  # Unité manquante pour résident
        })
        
        # Assert - erreurs affichées
        assert response.status_code == 400 or response.status_code == 200
        # Le formulaire devrait réafficher les erreurs
    
    def test_create_user_duplicate_username_web(self):
        """Test création avec nom d'utilisateur existant via web."""
        # Arrange - se connecter et créer un premier utilisateur
        self.login_as_admin()
        
        self.client.post('/users/new', data={
            'username': 'user_existant',
            'email': 'premier@test.com',
            'password': 'password123',
            'full_name': 'Premier Utilisateur',
            'role': 'resident',
            'condo_unit': 'A-101'
        })
        
        # Act - essayer de créer avec même username
        response = self.client.post('/users/new', data={
            'username': 'user_existant',  # Même username
            'email': 'deuxieme@test.com',
            'password': 'password456',
            'full_name': 'Deuxième Utilisateur',
            'role': 'guest'
        })
        
        # Assert - erreur de doublon
        assert response.status_code == 400 or response.status_code == 200
        assert ("déjà utilisé".encode('utf-8') in response.data or 
                "existe déjà".encode('utf-8') in response.data)
    
    def test_create_admin_user_web(self):
        """Test création d'un utilisateur administrateur via web."""
        # Arrange - se connecter en tant qu'admin
        self.login_as_admin()
        
        # Act - créer un nouveau admin
        response = self.client.post('/users/new', data={
            'username': 'nouveau_admin',
            'email': 'admin@nouveau.com',
            'password': 'adminpass123',
            'full_name': 'Nouvel Administrateur',
            'role': 'admin'
            # Pas d'unité pour admin
        }, follow_redirects=True)
        
        # Assert
        assert response.status_code == 200
        assert "Utilisateur créé avec succès".encode("utf-8") in response.data or "créé avec succès".encode("utf-8") in response.data
    
    def test_create_guest_user_web(self):
        """Test création d'un utilisateur invité via web."""
        # Arrange - se connecter en tant qu'admin
        self.login_as_admin()
        
        # Act - créer un invité
        response = self.client.post('/users/new', data={
            'username': 'invite_test',
            'email': 'invite@test.com',
            'password': 'invitepass123',
            'full_name': 'Utilisateur Invité',
            'role': 'guest'
            # Pas d'unité pour invité
        }, follow_redirects=True)
        
        # Assert
        assert response.status_code == 200
        assert "Utilisateur créé avec succès".encode("utf-8") in response.data or "créé avec succès".encode("utf-8") in response.data
    
    def test_user_creation_workflow_complete(self):
        """Test workflow complet de création d'utilisateur."""
        # 1. Connexion admin
        login_response = self.login_as_admin()
        assert login_response.status_code == 200
        
        # 2. Accès à la page de gestion des utilisateurs
        users_page = self.client.get('/users')
        assert users_page.status_code == 200
        
        # 3. Accès à la page de création
        create_page = self.client.get('/users/new')
        assert create_page.status_code == 200
        
        # 4. Création de l'utilisateur
        create_response = self.client.post('/users/new', data={
            'username': 'workflow_test',
            'email': 'workflow@test.com',
            'password': 'workflow123',
            'full_name': 'Test Workflow Complet',
            'role': 'resident',
            'condo_unit': 'F-601'
        }, follow_redirects=True)
        
        # 5. Vérification du succès
        assert create_response.status_code == 200
        assert "créé avec succès".encode("utf-8") in create_response.data
        
        # 6. Retour à la liste des utilisateurs
        users_list = self.client.get('/users')
        assert users_list.status_code == 200
        # L'utilisateur devrait apparaître dans la liste
    
    def test_form_modal_user_creation(self):
        """Test création d'utilisateur via modal JavaScript (si implémenté)."""
        # Arrange - se connecter en tant qu'admin
        self.login_as_admin()
        
        # Act - accéder à la page principale des utilisateurs
        response = self.client.get('/users')
        
        # Assert - vérifier que le modal est présent
        assert response.status_code == 200
        assert (b"createUserModal" in response.data or 
                "Créer un nouvel utilisateur".encode("utf-8") in response.data)


if __name__ == "__main__":
    # Exécuter les tests
    pytest.main([__file__, "-v"])
