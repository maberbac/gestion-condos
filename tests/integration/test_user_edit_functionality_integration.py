"""
Tests d'intégration pour la fonctionnalité d'édition d'utilisateur.

[ARCHITECTURE TDD]
Ces tests valident l'intégration entre les couches pour l'édition d'utilisateur
avec base de données de test isolée.
"""

import unittest
import tempfile
import os
from unittest.mock import patch, Mock
from pathlib import Path

from src.infrastructure.logger_manager import get_logger

logger = get_logger(__name__)


class TestUserEditFunctionalityIntegration(unittest.TestCase):
    """Tests d'intégration pour l'édition d'utilisateur."""

    def setUp(self):
        """Configuration initiale des tests avec base de test isolée."""
        # Créer un répertoire temporaire pour les tests
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.test_dir, 'test_users.db')
        
        # Configuration de test
        self.test_config = {
            'database': {
                'type': 'sqlite',
                'path': self.test_db_path
            }
        }
        
        # Données de test
        self.test_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'full_name': 'Test User',
            'role': 'resident',
            'condo_unit': '101'
        }

    def tearDown(self):
        """Nettoyage après chaque test."""
        import shutil
        import gc
        import time
        
        # Forcer la collecte des objets pour libérer les connexions DB
        gc.collect()
        time.sleep(0.1)  # Petite pause pour permettre la fermeture des connexions
        
        if os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
            except PermissionError:
                # Sous Windows, les fichiers SQLite peuvent rester verrouillés
                # Ce n'est pas critique pour les tests
                pass

    def _create_test_user(self, repository, user_service, user_data):
        """Helper pour créer un utilisateur de test."""
        from src.domain.entities.user import User, UserRole
        
        # Créer l'entité utilisateur
        user_entity = User(
            username=user_data['username'],
            email=user_data['email'],
            password_hash=User.hash_password(user_data['password']),
            full_name=user_data['full_name'],
            role=UserRole(user_data['role']),
            condo_unit=user_data['condo_unit']
        )
        
        # Sauvegarder via le repository
        created = user_service._run_async_operation(
            repository.save_user, user_entity
        )
        return created

    @patch('src.adapters.user_repository_sqlite.UserRepositorySQLite._load_database_config')
    def test_integration_update_user_complete_flow(self, mock_load_config):
        """Test d'intégration complet de mise à jour d'utilisateur."""
        # Arrange
        mock_load_config.return_value = self.test_config
        
        from src.adapters.user_repository_sqlite import UserRepositorySQLite
        from src.application.services.user_service import UserService
        from src.domain.entities.user import UserRole
        
        # Initialiser le repository avec config de test
        repository = UserRepositorySQLite()
        user_service = UserService()
        user_service.user_repository = repository
        
        # Créer un utilisateur initial
        created = self._create_test_user(repository, user_service, self.test_user_data)
        self.assertTrue(created)
        
        # Données de mise à jour
        update_data = {
            'username': 'updated_testuser',
            'email': 'updated@example.com',
            'full_name': 'Updated Test User',
            'role': 'admin',
            'condo_unit': '202',
            'password': 'newpassword123'
        }
        
        # Act - Mettre à jour l'utilisateur
        result = user_service.update_user_by_username(
            self.test_user_data['username'], 
            update_data
        )
        
        # Assert
        self.assertTrue(result['success'])
        
        # Vérifier que l'utilisateur a été mis à jour
        updated_user = user_service.get_user_details_by_username('updated_testuser')
        self.assertIsNotNone(updated_user)
        self.assertEqual(updated_user.get('email'), 'updated@example.com')
        self.assertEqual(updated_user.get('full_name'), 'Updated Test User')
        self.assertEqual(updated_user.get('role'), 'admin')
        self.assertEqual(updated_user.get('condo_unit'), '202')
        
        # Vérifier que l'ancien nom d'utilisateur n'existe plus
        old_user = user_service.get_user_details_by_username(self.test_user_data['username'])
        self.assertIsNone(old_user)

    @patch('src.adapters.user_repository_sqlite.UserRepositorySQLite._load_database_config')
    def test_integration_update_user_partial_fields(self, mock_load_config):
        """Test mise à jour partielle d'un utilisateur."""
        # Arrange
        mock_load_config.return_value = self.test_config
        
        from src.adapters.user_repository_sqlite import UserRepositorySQLite
        from src.application.services.user_service import UserService
        from src.domain.entities.user import UserRole
        
        repository = UserRepositorySQLite()
        user_service = UserService()
        user_service.user_repository = repository
        
        # Créer un utilisateur initial
        created = self._create_test_user(repository, user_service, self.test_user_data)
        self.assertTrue(created)
        
        # Données de mise à jour partielle (seulement email et nom)
        update_data = {
            'username': self.test_user_data['username'],  # Même nom
            'email': 'partial_update@example.com',
            'full_name': 'Partial Update User',
            'role': 'resident',  # Même rôle
            'condo_unit': '101'  # Même unité
        }
        
        # Act
        result = user_service.update_user_by_username(
            self.test_user_data['username'], 
            update_data
        )
        
        # Assert
        self.assertTrue(result['success'])
        
        # Vérifier les changements
        updated_user = user_service.get_user_details_by_username(self.test_user_data['username'])
        self.assertEqual(updated_user.get('email'), 'partial_update@example.com')
        self.assertEqual(updated_user.get('full_name'), 'Partial Update User')
        self.assertEqual(updated_user.get('role'), 'resident')

    @patch('src.adapters.user_repository_sqlite.UserRepositorySQLite._load_database_config')
    def test_integration_update_user_invalid_data(self, mock_load_config):
        """Test mise à jour avec données invalides."""
        # Arrange
        mock_load_config.return_value = self.test_config
        
        from src.adapters.user_repository_sqlite import UserRepositorySQLite
        from src.application.services.user_service import UserService
        from src.domain.entities.user import UserRole
        
        repository = UserRepositorySQLite()
        user_service = UserService()
        user_service.user_repository = repository
        
        # Créer un utilisateur initial
        created = self._create_test_user(repository, user_service, self.test_user_data)
        self.assertTrue(created)
        
        # Données de mise à jour invalides (rôle incorrect)
        update_data = {
            'username': self.test_user_data['username'],
            'email': 'test@example.com',
            'full_name': 'Test User',
            'role': 'invalid_role',  # Rôle invalide
            'condo_unit': '101'
        }
        
        # Act
        result = user_service.update_user_by_username(
            self.test_user_data['username'], 
            update_data
        )
        
        # Assert
        self.assertFalse(result['success'])
        self.assertIn('validation', result['error'].lower())


if __name__ == '__main__':
    unittest.main()
