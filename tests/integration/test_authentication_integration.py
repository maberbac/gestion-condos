"""
Tests d'intégration pour l'architecture hexagonale d'authentification.

[TDD - RED-GREEN-REFACTOR]
Ces tests valident l'intégration entre :
- AuthenticationService (domaine)
- UserFileAdapter (adaptateur)
- UserRepositoryPort (port)
- Injection de dépendances
"""

import unittest
import asyncio
import tempfile
import os
from unittest.mock import Mock, AsyncMock, patch

from src.domain.services.authentication_service import (
    AuthenticationService, 
    SessionExpiredError
)
from src.adapters.user_file_adapter import UserFileAdapter
from src.domain.entities.user import User, UserRole, UserAuthenticationError, UserValidationError


class TestAuthenticationIntegration(unittest.TestCase):
    """Tests d'intégration pour l'architecture hexagonale d'authentification"""
    
    def setUp(self):
        """Configuration pour chaque test"""
        # Créer répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test_users.json')
        
        # [ARCHITECTURE HEXAGONALE] Injection de dépendances
        self.user_repository = UserFileAdapter(self.test_file)
        self.auth_service = AuthenticationService(self.user_repository)
        
        # Données de test
        self.test_users = [
            User(
                username='admin',
                email='admin@test.com',
                password_hash=User.hash_password('admin123'),
                role=UserRole.ADMIN,
                full_name='Admin User'
            ),
            User(
                username='resident1',
                email='resident1@test.com',
                password_hash=User.hash_password('resident123'),
                role=UserRole.RESIDENT,
                full_name='Resident One',
                condo_unit='A-101'
            ),
            User(
                username='guest1',
                email='guest1@test.com',
                password_hash=User.hash_password('guest123'),
                role=UserRole.GUEST,
                full_name='Guest One'
            )
        ]
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        
        # Nettoyer le répertoire temporaire avec tous ses contenus
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_hexagonal_architecture_dependency_injection(self):
        """Test injection de dépendances architecture hexagonale"""
        # Assert
        # Vérifier que le service utilise bien le port injecté
        self.assertIs(self.auth_service.user_repository, self.user_repository)
        self.assertIsInstance(self.auth_service.user_repository, UserFileAdapter)
        
        # Vérifier que le service ne dépend pas directement des détails d'implémentation
        self.assertFalse(hasattr(self.auth_service, 'users_file'))
        self.assertFalse(hasattr(self.auth_service, '_load_users'))
    
    def test_service_initialization_with_adapter(self):
        """Test initialisation service avec adaptateur"""
        # Act
        result = asyncio.run(self.auth_service.initialize())
        
        # Assert
        # Vérifier que l'initialisation s'est bien passée
        self.assertIsNone(result)  # initialize() ne retourne rien
        
        # Vérifier que des utilisateurs par défaut ont été créés
        users = asyncio.run(self.user_repository.get_all_users())
        self.assertGreater(len(users), 0)
        
        # Vérifier qu'il y a au moins un admin
        admin_users = [u for u in users if u.role == UserRole.ADMIN]
        self.assertGreater(len(admin_users), 0)
    
    def test_full_authentication_workflow(self):
        """Test workflow complet d'authentification"""
        # Arrange
        asyncio.run(self.user_repository.save_users(self.test_users))
        
        # Act 1: Authentification réussie
        auth_user = asyncio.run(self.auth_service.authenticate('admin', 'admin123'))
        
        # Assert 1
        self.assertIsNotNone(auth_user)
        self.assertEqual(auth_user.username, 'admin')
        self.assertEqual(auth_user.role, UserRole.ADMIN)
        self.assertIsNotNone(auth_user.last_login)
        
        # Act 2: Création de session
        session_token = self.auth_service.create_session(auth_user)
        
        # Assert 2
        self.assertIsNotNone(session_token)
        self.assertIsInstance(session_token, str)
        
        # Act 3: Récupération session
        session_data = self.auth_service.get_user_from_session(session_token)
        
        # Assert 3
        self.assertIsNotNone(session_data)
        self.assertEqual(session_data['user_id'], 'admin')
        self.assertEqual(session_data['role'], 'admin')
        
        # Act 4: Suppression session
        self.auth_service.clear_session(session_token)
        
        # Assert 4
        session_data_after_clear = self.auth_service.get_user_from_session(session_token)
        self.assertIsNone(session_data_after_clear)
    
    def test_authentication_failure_workflow(self):
        """Test workflow d'authentification échouée"""
        # Arrange
        asyncio.run(self.user_repository.save_users(self.test_users))
        
        # Act 1: Utilisateur inexistant
        result1 = asyncio.run(self.auth_service.authenticate('inexistant', 'password'))
        
        # Assert 1
        self.assertIsNone(result1)
        
        # Act 2: Mot de passe incorrect
        result2 = asyncio.run(self.auth_service.authenticate('admin', 'wrongpassword'))
        
        # Assert 2
        self.assertIsNone(result2)
        
        # Act 3: Données vides
        result3 = asyncio.run(self.auth_service.authenticate('', ''))
        
        # Assert 3
        self.assertIsNone(result3)
    
    def test_adapter_swapping_capability(self):
        """Test capacité d'échange d'adaptateurs (flexibilité architecture)"""
        # Arrange
        # Créer un mock adapter
        mock_adapter = AsyncMock()
        mock_adapter.get_user_by_username.return_value = self.test_users[0]
        mock_adapter.save_user.return_value = self.test_users[0]
        mock_adapter.initialize_default_users.return_value = None
        
        # Créer un nouveau service avec l'adaptateur mocké
        mock_auth_service = AuthenticationService(mock_adapter)
        
        # Act
        result = asyncio.run(mock_auth_service.authenticate('admin', 'admin123'))
        
        # Assert
        # Vérifier que le service fonctionne avec l'adaptateur mocké
        self.assertIsNotNone(result)
        mock_adapter.get_user_by_username.assert_called_once_with('admin')
    
    def test_concurrent_operations_integration(self):
        """Test opérations concurrentes avec architecture async"""
        # Arrange
        asyncio.run(self.user_repository.save_users(self.test_users))
        
        async def concurrent_auth_operations():
            # Opérations parallèles
            tasks = [
                self.auth_service.authenticate('admin', 'admin123'),
                self.auth_service.authenticate('resident1', 'resident123'),
                self.auth_service.authenticate('guest1', 'guest123')
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
        
        # Act
        results = asyncio.run(concurrent_auth_operations())
        
        # Assert
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIsNotNone(result)
            self.assertIsInstance(result, User)
    
    def test_error_propagation_through_layers(self):
        """Test propagation d'erreurs à travers les couches"""
        # Arrange - Créer adaptateur qui lève des erreurs
        error_adapter = Mock()
        error_adapter.get_user_by_username = AsyncMock(
            side_effect=UserAuthenticationError("Adapter error")
        )
        error_auth_service = AuthenticationService(error_adapter)
        
        # Act & Assert
        with self.assertRaises(UserAuthenticationError):
            asyncio.run(error_auth_service.authenticate('test', 'password'))
    
    def test_data_consistency_across_operations(self):
        """Test cohérence des données entre opérations"""
        # Arrange
        asyncio.run(self.auth_service.initialize())
        
        # Act 1: Créer utilisateur via service
        new_user = User(
            username='newuser',
            email='new@test.com',
            password_hash=User.hash_password('newpass'),
            role=UserRole.RESIDENT,
            full_name='New User',
            condo_unit='B-202'
        )
        
        saved_user = asyncio.run(self.user_repository.save_user(new_user))
        
        # Act 2: Authentifier le nouvel utilisateur
        auth_result = asyncio.run(self.auth_service.authenticate('newuser', 'newpass'))
        
        # Assert
        self.assertIsNotNone(auth_result)
        self.assertEqual(auth_result.username, saved_user.username)
        self.assertEqual(auth_result.email, saved_user.email)
        
        # Vérifier que last_login a été mis à jour
        self.assertIsNotNone(auth_result.last_login)
        self.assertIsNone(saved_user.last_login)  # Original n'avait pas de last_login
    
    def test_session_management_integration(self):
        """Test intégration gestion de sessions"""
        # Arrange
        asyncio.run(self.user_repository.save_users(self.test_users))
        admin_user = asyncio.run(self.auth_service.authenticate('admin', 'admin123'))
        
        # Act: Créer plusieurs sessions
        session1 = self.auth_service.create_session(admin_user)
        session2 = self.auth_service.create_session(admin_user)
        
        # Assert: Sessions différentes
        self.assertNotEqual(session1, session2)
        
        # Vérifier que les deux sessions sont valides
        data1 = self.auth_service.get_user_from_session(session1)
        data2 = self.auth_service.get_user_from_session(session2)
        
        self.assertIsNotNone(data1)
        self.assertIsNotNone(data2)
        self.assertEqual(data1['user_id'], data2['user_id'])
    
    def test_role_based_operations_integration(self):
        """Test intégration opérations basées sur les rôles"""
        # Arrange
        asyncio.run(self.user_repository.save_users(self.test_users))
        
        # Act: Authentifier différents rôles
        admin = asyncio.run(self.auth_service.authenticate('admin', 'admin123'))
        resident = asyncio.run(self.auth_service.authenticate('resident1', 'resident123'))
        guest = asyncio.run(self.auth_service.authenticate('guest1', 'guest123'))
        
        # Assert: Permissions différentes selon rôles
        self.assertTrue(admin.has_permission('manage_users'))
        self.assertFalse(resident.has_permission('manage_users'))
        self.assertFalse(guest.has_permission('manage_users'))
        
        self.assertTrue(admin.has_permission('write'))
        self.assertTrue(resident.has_permission('write'))
        self.assertFalse(guest.has_permission('write'))
    
    def test_performance_with_multiple_users(self):
        """Test performance avec multiple utilisateurs"""
        # Arrange - Créer beaucoup d'utilisateurs
        many_users = []
        for i in range(100):
            user = User(
                username=f'user{i}',
                email=f'user{i}@test.com',
                password_hash=User.hash_password(f'password{i}'),
                role=UserRole.RESIDENT,
                full_name=f'User {i}',
                condo_unit=f'C-{100+i}'
            )
            many_users.append(user)
        
        asyncio.run(self.user_repository.save_users(many_users))
        
        # Act - Authentification avec cache
        import time
        start_time = time.time()
        
        result = asyncio.run(self.auth_service.authenticate('user50', 'password50'))
        
        end_time = time.time()
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.username, 'user50')
        
        # Performance raisonnable (moins de 1 seconde)
        self.assertLess(end_time - start_time, 1.0)
    
    def test_configuration_integration(self):
        """Test intégration avec configuration système"""
        # Arrange
        custom_file = os.path.join(self.temp_dir, 'custom_users.json')
        custom_adapter = UserFileAdapter(custom_file)
        custom_service = AuthenticationService(custom_adapter)
        
        # Act
        asyncio.run(custom_service.initialize())
        
        # Assert
        # Vérifier que le fichier personnalisé a été créé
        self.assertTrue(os.path.exists(custom_file))
        
        # Vérifier que les utilisateurs par défaut sont dans le bon fichier
        users = asyncio.run(custom_adapter.get_all_users())
        self.assertGreater(len(users), 0)


if __name__ == '__main__':
    unittest.main()
