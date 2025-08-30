"""
Tests unitaires pour la gestion des utilisateurs depuis la base de données
"""

import unittest
from unittest.mock import patch, MagicMock
from src.domain.entities.user import User, UserRole
from src.infrastructure.repositories.user_repository import UserRepository
from src.application.services.user_service import UserService


class TestUserPageDatabaseIntegration(unittest.TestCase):
    """Tests pour l'intégration de la page utilisateurs avec la base de données"""

    def setUp(self):
        """Configuration des tests"""
        self.user_repository = UserRepository()
        self.user_service = UserService(self.user_repository)

    def test_user_service_get_all_users_returns_list(self):
        """Le service utilisateur doit retourner une liste d'utilisateurs depuis la base"""
        users = self.user_service.get_all_users()
        
        # Vérifications
        self.assertIsInstance(users, list)
        if users:  # Si des utilisateurs existent
            self.assertIsInstance(users[0], User)

    def test_user_service_get_users_with_statistics(self):
        """Le service doit calculer les statistiques des utilisateurs par rôle"""
        stats = self.user_service.get_user_statistics()
        
        # Vérifications
        self.assertIsInstance(stats, dict)
        self.assertIn('admin_count', stats)
        self.assertIn('resident_count', stats)
        self.assertIn('total_count', stats)
        
        # Les compteurs doivent être des entiers non négatifs
        self.assertIsInstance(stats['admin_count'], int)
        self.assertIsInstance(stats['resident_count'], int)
        self.assertIsInstance(stats['total_count'], int)
        self.assertGreaterEqual(stats['admin_count'], 0)
        self.assertGreaterEqual(stats['resident_count'], 0)
        self.assertGreaterEqual(stats['total_count'], 0)

    def test_user_service_format_users_for_web_display(self):
        """Le service doit formater les utilisateurs pour l'affichage web"""
        formatted_users = self.user_service.get_users_for_web_display()
        
        # Vérifications
        self.assertIsInstance(formatted_users, list)
        
        if formatted_users:  # Si des utilisateurs existent
            user = formatted_users[0]
            # Vérifier que les champs requis pour le template sont présents
            required_fields = ['username', 'full_name', 'email', 'role', 'created_at']
            for field in required_fields:
                self.assertIn(field, user)
            
            # Vérifier le format du rôle (pour compatibilité template)
            self.assertIn('value', user['role'])

    @patch('src.application.services.user_service.UserService.get_all_users')
    def test_user_service_handles_empty_database(self, mock_get_users):
        """Le service doit gérer correctement une base de données vide"""
        # Simuler une base vide
        mock_get_users.return_value = []
        
        stats = self.user_service.get_user_statistics()
        formatted_users = self.user_service.get_users_for_web_display()
        
        # Vérifications
        self.assertEqual(stats['total_count'], 0)
        self.assertEqual(stats['admin_count'], 0)
        self.assertEqual(stats['resident_count'], 0)
        self.assertEqual(formatted_users, [])

    def test_user_repository_get_all_connects_to_database(self):
        """Le repository doit se connecter à la base de données SQLite via le service"""
        # Utiliser le service au lieu d'appeler directement le repository
        users = self.user_service.get_all_users()
        
        # Vérifications basiques
        self.assertIsInstance(users, list)
        # Si des utilisateurs existent, vérifier leur structure
        if users:
            user = users[0]
            self.assertIsInstance(user, User)
            self.assertTrue(hasattr(user, 'username'))
            self.assertTrue(hasattr(user, 'full_name'))
            self.assertTrue(hasattr(user, 'email'))
            self.assertTrue(hasattr(user, 'role'))

    def test_user_entity_role_enum_compatibility(self):
        """Les rôles d'utilisateur doivent être compatibles avec le template"""
        # Tester les valeurs d'enum attendues
        admin_role = UserRole.ADMIN
        resident_role = UserRole.RESIDENT
        
        # Les valeurs doivent correspondre à ce qu'attend le template
        self.assertEqual(admin_role.value, 'admin')
        self.assertEqual(resident_role.value, 'resident')

    def test_user_service_filters_users_by_role(self):
        """Le service doit pouvoir filtrer les utilisateurs par rôle"""
        admin_users = self.user_service.get_users_by_role(UserRole.ADMIN)
        resident_users = self.user_service.get_users_by_role(UserRole.RESIDENT)
        
        # Vérifications
        self.assertIsInstance(admin_users, list)
        self.assertIsInstance(resident_users, list)
        
        # Vérifier que tous les utilisateurs retournés ont le bon rôle
        for user in admin_users:
            self.assertEqual(user.role, UserRole.ADMIN)
        
        for user in resident_users:
            self.assertEqual(user.role, UserRole.RESIDENT)


if __name__ == '__main__':
    unittest.main()
