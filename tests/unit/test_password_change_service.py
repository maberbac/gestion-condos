#!/usr/bin/env python3
"""
Tests unitaires pour le service de changement de mot de passe
Suit la méthodologie TDD pour valider la logique métier
"""

import unittest
import asyncio
import tempfile
import os
from unittest.mock import Mock, AsyncMock

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.infrastructure.logger_manager import get_logger
from src.domain.entities.user import User, UserRole
from src.domain.services.password_change_service import PasswordChangeService, PasswordChangeError
from src.domain.services.authentication_service import AuthenticationService
from src.adapters.user_file_adapter import UserFileAdapter

logger = get_logger(__name__)


class TestPasswordChangeService(unittest.TestCase):
    """Tests unitaires pour le service de changement de mot de passe."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        # Créer des mocks pour les dépendances
        self.mock_user_repository = Mock()
        self.mock_authentication_service = Mock()
        
        # Configurer les méthodes async
        self.mock_user_repository.update_user_password = AsyncMock()
        self.mock_authentication_service.authenticate = AsyncMock()
        
        # Créer le service avec les mocks
        self.password_service = PasswordChangeService(
            user_repository=self.mock_user_repository,
            authentication_service=self.mock_authentication_service
        )
        
        # Créer un utilisateur de test
        self.test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash=User.hash_password("ancien_password"),
            role=UserRole.RESIDENT,
            full_name="Test User",
            condo_unit="A-101"
        )
    
    def test_change_password_success(self):
        """Test de modification de mot de passe réussie."""
        # ARRANGE
        username = "testuser"
        current_password = "ancien_password"
        new_password = "nouveau_password123"
        
        # Mock des dépendances
        self.mock_authentication_service.authenticate.return_value = self.test_user
        self.mock_user_repository.update_user_password.return_value = True
        
        # ACT
        async def test_async():
            result = await self.password_service.change_password(
                username, current_password, new_password
            )
            
            # ASSERT
            self.assertTrue(result)
            self.mock_authentication_service.authenticate.assert_called_once_with(
                username, current_password
            )
            # Vérifier que le repository reçoit un hash, pas le mot de passe en clair
            self.mock_user_repository.update_user_password.assert_called_once()
            args, kwargs = self.mock_user_repository.update_user_password.call_args
            self.assertEqual(args[0], username)  # Premier argument est le username
            self.assertNotEqual(args[1], new_password)  # Deuxième argument n'est PAS le mot de passe en clair
            self.assertIn(":", args[1])  # Le hash contient ":" (hash:salt)
        
        asyncio.run(test_async())
    
    def test_change_password_invalid_current_password(self):
        """Test de modification avec mauvais mot de passe actuel."""
        # ARRANGE
        username = "testuser"
        wrong_current_password = "mauvais_password"
        new_password = "nouveau_password123"
        
        # Mock authentification échouée
        self.mock_authentication_service.authenticate.return_value = None
        
        # ACT & ASSERT
        async def test_async():
            with self.assertRaises(PasswordChangeError) as context:
                await self.password_service.change_password(
                    username, wrong_current_password, new_password
                )
            
            self.assertIn("Nom d'utilisateur ou mot de passe actuel incorrect", str(context.exception))
            self.mock_authentication_service.authenticate.assert_called_once_with(
                username, wrong_current_password
            )
            # Le repository ne doit pas être appelé
            self.mock_user_repository.update_user_password.assert_not_called()
        
        asyncio.run(test_async())
    
    def test_change_password_invalid_new_password(self):
        """Test de modification avec nouveau mot de passe invalide."""
        test_cases = [
            ("", "Le nouveau mot de passe ne peut pas être vide"),
            ("123", "au moins 6 caractères"),
            ("     ", "ne peut pas être vide"),
            ("password", "trop commun"),
        ]
        
        for invalid_password, expected_message in test_cases:
            with self.subTest(password=invalid_password):
                async def test_async():
                    with self.assertRaises(PasswordChangeError) as context:
                        await self.password_service.change_password(
                            "testuser", "ancien_password", invalid_password
                        )
                    
                    self.assertIn(expected_message, str(context.exception))
                    # Les services ne doivent pas être appelés pour les validations de base
                    if invalid_password in ["", "123", "     "]:
                        self.mock_authentication_service.authenticate.assert_not_called()
                
                asyncio.run(test_async())
                # Reset mocks pour le prochain test
                self.mock_authentication_service.reset_mock()
                self.mock_user_repository.reset_mock()
    
    def test_change_password_same_as_current(self):
        """Test de modification avec le même mot de passe."""
        # ARRANGE
        username = "testuser"
        current_password = "ancien_password"
        same_password = "ancien_password"
        
        # Mock authentification réussie
        self.mock_authentication_service.authenticate.return_value = self.test_user
        
        # ACT & ASSERT
        async def test_async():
            with self.assertRaises(PasswordChangeError) as context:
                await self.password_service.change_password(
                    username, current_password, same_password
                )
            
            self.assertIn("différent du mot de passe actuel", str(context.exception))
            self.mock_authentication_service.authenticate.assert_called_once_with(
                username, current_password
            )
            # Le repository ne doit pas être appelé
            self.mock_user_repository.update_user_password.assert_not_called()
        
        asyncio.run(test_async())
    
    def test_change_password_user_not_found(self):
        """Test de modification pour utilisateur inexistant."""
        # ARRANGE
        username = "inexistant"
        current_password = "password"
        new_password = "nouveau_password123"
        
        # Mock utilisateur non trouvé
        self.mock_authentication_service.authenticate.return_value = None
        
        # ACT & ASSERT
        async def test_async():
            with self.assertRaises(PasswordChangeError) as context:
                await self.password_service.change_password(
                    username, current_password, new_password
                )
            
            self.assertIn("Nom d'utilisateur ou mot de passe actuel incorrect", str(context.exception))
            self.mock_authentication_service.authenticate.assert_called_once_with(
                username, current_password
            )
        
        asyncio.run(test_async())
    
    def test_change_password_repository_error(self):
        """Test de gestion d'erreur du repository."""
        # ARRANGE
        username = "testuser"
        current_password = "ancien_password"
        new_password = "nouveau_password123"
        
        # Mock authentification réussie
        self.mock_authentication_service.authenticate.return_value = self.test_user
        # Mock erreur du repository
        self.mock_user_repository.update_user_password.side_effect = Exception("Erreur base de données")
        
        # ACT & ASSERT
        async def test_async():
            with self.assertRaises(PasswordChangeError) as context:
                await self.password_service.change_password(
                    username, current_password, new_password
                )
            
            self.assertIn("Erreur lors de la mise à jour", str(context.exception))
            self.mock_authentication_service.authenticate.assert_called_once_with(
                username, current_password
            )
            # Vérifier que le repository est appelé avec un hash
            self.mock_user_repository.update_user_password.assert_called_once()
            args, kwargs = self.mock_user_repository.update_user_password.call_args
            self.assertEqual(args[0], username)  # Premier argument est le username
            self.assertNotEqual(args[1], new_password)  # Deuxième argument n'est PAS le mot de passe en clair
        
        asyncio.run(test_async())
    
    def test_validate_password_strength_requirements(self):
        """Test de validation des exigences du nouveau mot de passe."""
        # ARRANGE
        test_cases = [
            ("", "ne peut pas être vide"),
            ("123", "au moins 6 caractères"),
            ("     ", "ne peut pas être vide"),
            ("password", "trop commun"),
            ("123456", "trop commun"),
            ("abcdef", None),  # Valide
            ("Password123!", None),  # Valide
        ]
        
        for password, expected_error in test_cases:
            with self.subTest(password=password):
                if expected_error:
                    with self.assertRaises(PasswordChangeError) as context:
                        self.password_service._validate_password_strength(password)
                    self.assertIn(expected_error, str(context.exception))
                else:
                    # Ne doit pas lever d'exception
                    try:
                        self.password_service._validate_password_strength(password)
                    except PasswordChangeError:
                        self.fail(f"Password '{password}' should be valid")
    
    def test_empty_username_validation(self):
        """Test de validation avec nom d'utilisateur vide."""
        async def test_async():
            with self.assertRaises(PasswordChangeError) as context:
                await self.password_service.change_password("", "password", "new_password123")
            
            self.assertIn("Le nom d'utilisateur ne peut pas être vide", str(context.exception))
        
        asyncio.run(test_async())
    
    def test_empty_current_password_validation(self):
        """Test de validation avec mot de passe actuel vide."""
        async def test_async():
            with self.assertRaises(PasswordChangeError) as context:
                await self.password_service.change_password("user", "", "new_password123")
            
            self.assertIn("Le mot de passe actuel ne peut pas être vide", str(context.exception))
        
        asyncio.run(test_async())


class TestPasswordChangeIntegration(unittest.TestCase):
    """Tests d'intégration pour le workflow complet de changement de mot de passe."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        # Créer un fichier temporaire pour les tests
        self.temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json')
        # Initialiser le fichier avec un JSON valide vide
        self.temp_file.write('{"users": []}')
        self.temp_file.close()
        
        # Configurer l'adapteur avec le fichier temporaire
        self.user_repository = UserFileAdapter(self.temp_file.name)
        self.authentication_service = AuthenticationService(self.user_repository)
        self.password_service = PasswordChangeService(
            user_repository=self.user_repository,
            authentication_service=self.authentication_service
        )
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        try:
            os.unlink(self.temp_file.name)
        except OSError:
            pass
    
    def test_full_password_change_workflow(self):
        """Test du workflow complet de changement de mot de passe."""
        async def test_async():
            # ARRANGE - Créer un utilisateur
            user = User(
                username="integration_user",
                email="integration@example.com",
                password_hash=User.hash_password("old_password_123"),
                role=UserRole.RESIDENT,
                full_name="Integration Test User",
                condo_unit="B-202"
            )
            await self.user_repository.save_user(user)
            
            # ACT - Changer le mot de passe
            result = await self.password_service.change_password(
                "integration_user",
                "old_password_123",
                "new_password_456"
            )
            
            # ASSERT - Vérifier le succès
            self.assertTrue(result)
            
            # ASSERT - Vérifier que l'ancien mot de passe ne fonctionne plus
            old_auth = await self.authentication_service.authenticate(
                "integration_user", "old_password_123"
            )
            self.assertIsNone(old_auth)
            
            # ASSERT - Vérifier que le nouveau mot de passe fonctionne
            new_auth = await self.authentication_service.authenticate(
                "integration_user", "new_password_456"
            )
            self.assertIsNotNone(new_auth)
            self.assertEqual(new_auth.username, "integration_user")
        
        asyncio.run(test_async())


if __name__ == '__main__':
    unittest.main()
