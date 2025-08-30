"""
Tests d'intégration pour l'authentification avec mocking complet.

Tests pour :
- UserRepository avec authentification (mockée)
- AuthenticationService avec mocks
- Intégration complète sans base de données réelle

TOUS LES ACCÈS BASE DE DONNÉES SONT MOCKÉS SELON LES NOUVELLES CONSIGNES.
Aucune connexion SQLite réelle n'est établie.
"""

import unittest
import sys
import os
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

from src.domain.entities.user import User, UserRole
from src.domain.services.authentication_service import AuthenticationService


class TestAuthenticationIntegrationMocked(unittest.TestCase):
    """Tests d'intégration pour l'authentification avec mocking complet."""
    
    def setUp(self):
        """Configuration pour chaque test avec mocks complets."""
        # Mock configuration (aucune base de données réelle)
        self.mock_config = {
            "database": {
                "type": "sqlite",
                "name": "mock.db",
                "path": "/mock/path/mock.db",
                "migrations_path": "mock/migrations/"
            }
        }
        
        # Utilisateurs de test (objets simulés) - définis en premier
        self.admin_user = User(
            username="admin",
            email="admin@test.com", 
            password_hash="$2b$12$hashedpassword",
            role=UserRole.ADMIN,
            full_name="Administrator",
            is_active=True
        )
        
        self.resident_user = User(
            username="resident1",
            email="resident@test.com",
            password_hash="$2b$12$hashedpassword2", 
            role=UserRole.RESIDENT,
            full_name="Resident User",
            condo_unit="A-101",
            is_active=True
        )
        
        self.inactive_user = User(
            username="inactive",
            email="inactive@test.com",
            password_hash="$2b$12$hashedpassword3",
            role=UserRole.RESIDENT, 
            full_name="Inactive User",
            condo_unit="B-202",
            is_active=False
        )

        # Mock repository avec coroutines async
        self.mock_repository = Mock()
        
        # Créer des mocks async pour les méthodes du repository
        async def mock_get_user_by_username(username):
            if username == "admin":
                return self.admin_user
            elif username == "resident1":
                return self.resident_user
            elif username == "inactive":
                return self.inactive_user
            else:
                return None
        
        async def mock_save_user(user):
            return user
            
        async def mock_update_user(user):
            return user
        
        self.mock_repository.get_user_by_username = mock_get_user_by_username
        self.mock_repository.get_user_by_email = Mock()
        self.mock_repository.save_user = mock_save_user
        self.mock_repository.update_user = mock_update_user
        
        # Mock authentication service
        self.mock_auth_service = AuthenticationService(self.mock_repository)
    
    def tearDown(self):
        """Nettoyage après chaque test (aucun fichier réel à supprimer)."""
        pass
    
    @patch('src.domain.entities.user.User.verify_password', return_value=True)
    def test_authenticate_admin_user_success_mocked(self, mock_verify):
        """Test d'authentification admin réussie avec mocking."""
        # Act
        result = asyncio.run(self.mock_auth_service.authenticate('admin', 'motdepasse123'))
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.username, 'admin')
        self.assertEqual(result.role, UserRole.ADMIN)
    
    @patch('src.domain.entities.user.User.verify_password', return_value=True)
    def test_authenticate_resident_user_success_mocked(self, mock_verify):
        """Test d'authentification résident réussie avec mocking."""
        # Act
        result = asyncio.run(self.mock_auth_service.authenticate('resident1', 'password456'))
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.username, 'resident1')
        self.assertEqual(result.role, UserRole.RESIDENT)
    
    @patch('src.domain.entities.user.User.verify_password', return_value=False)
    def test_authenticate_wrong_password_mocked(self, mock_verify):
        """Test d'authentification avec mauvais mot de passe."""
        # Act
        result = asyncio.run(self.mock_auth_service.authenticate('admin', 'mauvais_motdepasse'))
        
        # Assert
        self.assertIsNone(result)
    
    def test_authenticate_invalid_user_mocked(self):
        """Test d'authentification utilisateur invalide avec mocking."""
        # Act
        result = asyncio.run(self.mock_auth_service.authenticate('inexistant', 'motdepasse'))
        
        # Assert
        self.assertIsNone(result)
    
    @patch('src.domain.entities.user.User.verify_password', return_value=True)
    def test_authenticate_inactive_user_mocked(self, mock_verify):
        """Test d'authentification utilisateur inactif."""
        # Act
        result = asyncio.run(self.mock_auth_service.authenticate('inactive', 'motdepasse'))
        
        # Assert
        self.assertIsNone(result)
    
    @patch('src.domain.entities.user.User.verify_password', return_value=True)
    def test_role_based_authentication_mocked(self, mock_verify):
        """Test d'authentification basée sur les rôles avec mocking."""
        # Test admin
        result = asyncio.run(self.mock_auth_service.authenticate('admin', 'motdepasse'))
        self.assertIsNotNone(result)
        self.assertEqual(result.role, UserRole.ADMIN)
        
        # Test resident
        result = asyncio.run(self.mock_auth_service.authenticate('resident1', 'motdepasse'))
        self.assertIsNotNone(result)
        self.assertEqual(result.role, UserRole.RESIDENT)


if __name__ == '__main__':
    unittest.main()
