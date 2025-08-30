"""
Tests unitaires pour UserFileAdapter.

[TDD - RED-GREEN-REFACTOR]
Ces tests valident l'implémentation de l'adapter pour la persistance
des utilisateurs en fichiers JSON, incluant :
- Opérations CRUD asynchrones
- Gestion d'erreurs de fichiers
- Cache et performance
- Validation des données
"""

import unittest
import asyncio
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, mock_open, AsyncMock

from src.adapters.user_file_adapter import UserFileAdapter
from src.domain.entities.user import User, UserRole, UserAuthenticationError, UserValidationError
from src.ports.user_repository import UserRepositoryPort


class TestUserFileAdapter(unittest.TestCase):
    """Tests unitaires pour UserFileAdapter"""
    
    def setUp(self):
        """Configuration pour chaque test"""
        # Créer un répertoire temporaire pour les tests
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test_users.json')
        self.adapter = UserFileAdapter(self.test_file)
        
        # Données de test
        self.test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash=User.hash_password('password123'),
            role=UserRole.RESIDENT,
            full_name='Test User',
            condo_unit='A-101'
        )
        
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
                password_hash=User.hash_password('pass123'),
                role=UserRole.RESIDENT,
                full_name='Resident One',
                condo_unit='B-202'
            )
        ]
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        # Supprimer les fichiers temporaires
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        
        # Nettoyer le répertoire temporaire avec tous ses contenus
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_adapter_implements_port_interface(self):
        """Test que l'adapter implémente correctement l'interface du port"""
        # Assert
        self.assertIsInstance(self.adapter, UserRepositoryPort)
        
        # Vérifier que toutes les méthodes du port sont implémentées
        port_methods = [
            'get_all_users', 'get_user_by_username', 'get_user_by_email',
            'save_user', 'save_users', 'delete_user', 'user_exists',
            'get_users_by_role', 'update_user_password', 'initialize_default_users'
        ]
        
        for method in port_methods:
            self.assertTrue(hasattr(self.adapter, method))
            self.assertTrue(callable(getattr(self.adapter, method)))
    
    def test_initialization_creates_directory(self):
        """Test que l'initialisation crée le répertoire si nécessaire"""
        # Arrange
        new_dir = os.path.join(self.temp_dir, 'new_dir')
        new_file = os.path.join(new_dir, 'users.json')
        
        # Act
        adapter = UserFileAdapter(new_file)
        
        # Assert
        self.assertTrue(os.path.exists(new_dir))
    
    def test_save_users_creates_file_with_correct_structure(self):
        """Test sauvegarde utilisateurs crée fichier avec structure correcte"""
        # Arrange & Act
        result = asyncio.run(self.adapter.save_users(self.test_users))
        
        # Assert
        self.assertEqual(result, self.test_users)
        self.assertTrue(os.path.exists(self.test_file))
        
        # Vérifier structure du fichier
        with open(self.test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIn('users', data)
        self.assertIn('last_updated', data)
        self.assertIn('total_users', data)
        self.assertEqual(data['total_users'], len(self.test_users))
        self.assertEqual(len(data['users']), len(self.test_users))
    
    def test_get_all_users_empty_file(self):
        """Test récupération utilisateurs fichier vide"""
        # Act
        users = asyncio.run(self.adapter.get_all_users())
        
        # Assert
        self.assertEqual(users, [])
    
    def test_get_all_users_with_data(self):
        """Test récupération utilisateurs avec données"""
        # Arrange
        asyncio.run(self.adapter.save_users(self.test_users))
        
        # Act
        users = asyncio.run(self.adapter.get_all_users())
        
        # Assert
        self.assertEqual(len(users), len(self.test_users))
        self.assertEqual(users[0].username, 'admin')
        self.assertEqual(users[1].username, 'resident1')
    
    def test_get_user_by_username_found(self):
        """Test recherche utilisateur par nom - trouvé"""
        # Arrange
        asyncio.run(self.adapter.save_users(self.test_users))
        
        # Act
        user = asyncio.run(self.adapter.get_user_by_username('admin'))
        
        # Assert
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'admin')
        self.assertEqual(user.role, UserRole.ADMIN)
    
    def test_get_user_by_username_not_found(self):
        """Test recherche utilisateur par nom - non trouvé"""
        # Arrange
        asyncio.run(self.adapter.save_users(self.test_users))
        
        # Act
        user = asyncio.run(self.adapter.get_user_by_username('inexistant'))
        
        # Assert
        self.assertIsNone(user)
    
    def test_get_user_by_email_found(self):
        """Test recherche utilisateur par email - trouvé"""
        # Arrange
        asyncio.run(self.adapter.save_users(self.test_users))
        
        # Act
        user = asyncio.run(self.adapter.get_user_by_email('admin@test.com'))
        
        # Assert
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'admin@test.com')
        self.assertEqual(user.username, 'admin')
    
    def test_get_user_by_email_not_found(self):
        """Test recherche utilisateur par email - non trouvé"""
        # Arrange
        asyncio.run(self.adapter.save_users(self.test_users))
        
        # Act
        user = asyncio.run(self.adapter.get_user_by_email('inexistant@test.com'))
        
        # Assert
        self.assertIsNone(user)
    
    def test_save_user_new_user(self):
        """Test sauvegarde nouvel utilisateur"""
        # Act
        saved_user = asyncio.run(self.adapter.save_user(self.test_user))
        
        # Assert
        self.assertEqual(saved_user, self.test_user)
        
        # Vérifier que l'utilisateur est bien sauvé
        users = asyncio.run(self.adapter.get_all_users())
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].username, 'testuser')
    
    def test_save_user_update_existing(self):
        """Test mise à jour utilisateur existant"""
        # Arrange
        asyncio.run(self.adapter.save_user(self.test_user))
        
        # Modifier l'utilisateur
        updated_user = User(
            username=self.test_user.username,
            email=self.test_user.email,
            password_hash=self.test_user.password_hash,
            role=self.test_user.role,
            full_name='Updated Name',
            condo_unit=self.test_user.condo_unit
        )
        
        # Act
        saved_user = asyncio.run(self.adapter.save_user(updated_user))
        
        # Assert
        self.assertEqual(saved_user.full_name, 'Updated Name')
        
        # Vérifier qu'il n'y a toujours qu'un utilisateur
        users = asyncio.run(self.adapter.get_all_users())
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].full_name, 'Updated Name')
    
    def test_delete_user_existing(self):
        """Test suppression utilisateur existant"""
        # Arrange
        asyncio.run(self.adapter.save_users(self.test_users))
        
        # Act
        result = asyncio.run(self.adapter.delete_user('admin'))
        
        # Assert
        self.assertTrue(result)
        
        # Vérifier que l'utilisateur est supprimé
        users = asyncio.run(self.adapter.get_all_users())
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].username, 'resident1')
    
    def test_delete_user_not_existing(self):
        """Test suppression utilisateur inexistant"""
        # Arrange
        asyncio.run(self.adapter.save_users(self.test_users))
        
        # Act
        result = asyncio.run(self.adapter.delete_user('inexistant'))
        
        # Assert
        self.assertFalse(result)
        
        # Vérifier que rien n'a été supprimé
        users = asyncio.run(self.adapter.get_all_users())
        self.assertEqual(len(users), 2)
    
    def test_user_exists_true(self):
        """Test vérification existence utilisateur - existe"""
        # Arrange
        asyncio.run(self.adapter.save_user(self.test_user))
        
        # Act
        exists = asyncio.run(self.adapter.user_exists('testuser'))
        
        # Assert
        self.assertTrue(exists)
    
    def test_user_exists_false(self):
        """Test vérification existence utilisateur - n'existe pas"""
        # Act
        exists = asyncio.run(self.adapter.user_exists('inexistant'))
        
        # Assert
        self.assertFalse(exists)
    
    def test_get_users_by_role(self):
        """Test récupération utilisateurs par rôle"""
        # Arrange
        asyncio.run(self.adapter.save_users(self.test_users))
        
        # Act
        admins = asyncio.run(self.adapter.get_users_by_role(UserRole.ADMIN))
        residents = asyncio.run(self.adapter.get_users_by_role(UserRole.RESIDENT))
        
        # Assert
        self.assertEqual(len(admins), 1)
        self.assertEqual(admins[0].username, 'admin')
        self.assertEqual(len(residents), 1)
        self.assertEqual(residents[0].username, 'resident1')
    
    def test_update_user_password_existing_user(self):
        """Test mise à jour mot de passe utilisateur existant"""
        # Arrange
        asyncio.run(self.adapter.save_user(self.test_user))
        new_password_hash = User.hash_password('newpassword')
        
        # Act
        result = asyncio.run(self.adapter.update_user_password('testuser', new_password_hash))
        
        # Assert
        self.assertTrue(result)
        
        # Vérifier que le mot de passe a été mis à jour
        user = asyncio.run(self.adapter.get_user_by_username('testuser'))
        self.assertEqual(user.password_hash, new_password_hash)
    
    def test_update_user_password_nonexisting_user(self):
        """Test mise à jour mot de passe utilisateur inexistant"""
        # Act
        result = asyncio.run(self.adapter.update_user_password('inexistant', 'newhash'))
        
        # Assert
        self.assertFalse(result)
    
    def test_initialize_default_users_empty_file(self):
        """Test initialisation utilisateurs par défaut fichier vide"""
        # Act
        asyncio.run(self.adapter.initialize_default_users())
        
        # Assert
        users = asyncio.run(self.adapter.get_all_users())
        self.assertGreater(len(users), 0)
        
        # Vérifier qu'il y a au moins un admin
        admin_users = [u for u in users if u.role == UserRole.ADMIN]
        self.assertGreater(len(admin_users), 0)
    
    def test_initialize_default_users_existing_file(self):
        """Test initialisation utilisateurs par défaut fichier existant"""
        # Arrange
        asyncio.run(self.adapter.save_user(self.test_user))
        initial_count = len(asyncio.run(self.adapter.get_all_users()))
        
        # Act
        asyncio.run(self.adapter.initialize_default_users())
        
        # Assert
        # Ne doit pas ajouter d'utilisateurs si le fichier existe déjà
        users = asyncio.run(self.adapter.get_all_users())
        self.assertEqual(len(users), initial_count)
    
    def test_cache_functionality(self):
        """Test fonctionnalité de cache"""
        # Arrange
        asyncio.run(self.adapter.save_users(self.test_users))
        
        # Premier appel - charge du fichier
        users1 = asyncio.run(self.adapter.get_all_users())
        
        # Deuxième appel - doit utiliser le cache
        users2 = asyncio.run(self.adapter.get_all_users())
        
        # Assert
        self.assertEqual(users1, users2)
        self.assertEqual(len(users1), len(self.test_users))
    
    def test_error_handling_file_not_found(self):
        """Test gestion d'erreur fichier non trouvé"""
        # Act
        users = asyncio.run(self.adapter.get_all_users())
        
        # Assert
        # Doit retourner liste vide sans lever d'exception
        self.assertEqual(users, [])
    
    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_error_handling_permission_error(self, mock_open, mock_exists):
        """Test gestion d'erreur permission refusée"""
        # Force le cache à être dirty pour déclencher le rechargement
        self.adapter._cache_dirty = True
        
        # Act & Assert - On accepte soit UserAuthenticationError soit PermissionError
        with self.assertRaises((UserAuthenticationError, PermissionError)):
            asyncio.run(self.adapter.get_all_users())
    
    def test_error_handling_invalid_json(self):
        """Test gestion d'erreur JSON invalide"""
        # Arrange - Créer fichier avec JSON invalide
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write('invalid json content')
        
        # Act & Assert
        with self.assertRaises(UserAuthenticationError):
            asyncio.run(self.adapter.get_all_users())
    
    def test_error_handling_invalid_user_data(self):
        """Test gestion d'erreur données utilisateur invalides"""
        # Arrange - Créer fichier avec données utilisateur invalides
        invalid_data = {
            'users': [
                {
                    'username': '',  # Username invalide
                    'email': 'invalid',
                    'role': 'invalid_role'
                }
            ],
            'last_updated': '2023-01-01T00:00:00',
            'total_users': 1
        }
        
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(invalid_data, f)
        
        # Act
        users = asyncio.run(self.adapter.get_all_users())
        
        # Assert
        # Doit ignorer les utilisateurs invalides
        self.assertEqual(len(users), 0)


if __name__ == '__main__':
    unittest.main()
