"""
Tests unitaires pour l'entité User.

[TDD - RED-GREEN-REFACTOR]
Ces tests valident la logique métier de l'entité User, incluant :
- Création et validation d'utilisateurs
- Gestion des mots de passe (hachage et vérification)
- Validation des rôles et permissions
- Sérialisation/désérialisation
"""

import unittest
from datetime import datetime
from src.domain.entities.user import User, UserRole, UserAuthenticationError, UserValidationError


class TestUserEntity(unittest.TestCase):
    """Tests unitaires pour l'entité User"""
    
    def setUp(self):
        """Configuration pour chaque test"""
        self.valid_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password_hash': User.hash_password('password123'),
            'role': UserRole.RESIDENT,
            'full_name': 'Test User',
            'condo_unit': 'A-101',
            'phone': '555-1234'
        }
    
    def test_user_creation_valid_data(self):
        """Test création d'utilisateur avec données valides"""
        # Arrange & Act
        user = User(**self.valid_user_data)
        
        # Assert
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, UserRole.RESIDENT)
        self.assertEqual(user.full_name, 'Test User')
        self.assertEqual(user.condo_unit, 'A-101')
        self.assertEqual(user.phone, '555-1234')
        self.assertTrue(user.is_active)
        self.assertIsInstance(user.created_at, datetime)
        self.assertIsNone(user.last_login)
    
    def test_user_creation_minimum_required_fields(self):
        """Test création d'utilisateur avec champs minimum requis"""
        # Arrange
        minimal_data = {
            'username': 'minimal',
            'email': 'minimal@test.com',
            'password_hash': User.hash_password('pass123'),
            'role': UserRole.GUEST,
            'full_name': 'Minimal User'
        }
        
        # Act
        user = User(**minimal_data)
        
        # Assert
        self.assertEqual(user.username, 'minimal')
        self.assertEqual(user.role, UserRole.GUEST)
        self.assertIsNone(user.condo_unit)
        self.assertIsNone(user.phone)
        self.assertTrue(user.is_active)
    
    def test_user_creation_invalid_username(self):
        """Test création avec nom d'utilisateur invalide"""
        # Arrange
        invalid_data = self.valid_user_data.copy()
        invalid_data['username'] = ''
        
        # Act & Assert
        with self.assertRaises(UserValidationError):
            User(**invalid_data)
    
    def test_user_creation_invalid_email(self):
        """Test création avec email invalide"""
        # Arrange
        invalid_data = self.valid_user_data.copy()
        invalid_data['email'] = 'invalid-email'
        
        # Act & Assert
        with self.assertRaises(UserValidationError):
            User(**invalid_data)
    
    def test_password_hashing(self):
        """Test hachage des mots de passe"""
        # Arrange
        password = 'testpassword123'
        
        # Act
        hash1 = User.hash_password(password)
        hash2 = User.hash_password(password)
        
        # Assert
        self.assertNotEqual(hash1, password)  # Hash différent du mot de passe
        self.assertNotEqual(hash1, hash2)     # Hashes différents (salt)
        self.assertTrue(len(hash1) > 0)       # Hash non vide
    
    def test_password_verification_correct(self):
        """Test vérification mot de passe correct"""
        # Arrange
        password = 'correctpassword'
        password_hash = User.hash_password(password)
        
        # Act
        is_valid = User.verify_password(password, password_hash)
        
        # Assert
        self.assertTrue(is_valid)
    
    def test_password_verification_incorrect(self):
        """Test vérification mot de passe incorrect"""
        # Arrange
        correct_password = 'correctpassword'
        wrong_password = 'wrongpassword'
        password_hash = User.hash_password(correct_password)
        
        # Act
        is_valid = User.verify_password(wrong_password, password_hash)
        
        # Assert
        self.assertFalse(is_valid)
    
    def test_user_roles_enum(self):
        """Test validation des rôles utilisateur"""
        # Act & Assert
        self.assertEqual(UserRole.ADMIN.value, 'admin')
        self.assertEqual(UserRole.RESIDENT.value, 'resident')
        self.assertEqual(UserRole.GUEST.value, 'guest')
    
    def test_user_permissions_admin(self):
        """Test permissions pour rôle ADMIN"""
        # Arrange
        admin_data = self.valid_user_data.copy()
        admin_data['role'] = UserRole.ADMIN
        user = User(**admin_data)
        
        # Act & Assert
        self.assertTrue(user.has_permission('read'))
        self.assertTrue(user.has_permission('write'))
        self.assertTrue(user.has_permission('delete'))
        self.assertTrue(user.has_permission('modify_finances'))
        self.assertTrue(user.has_permission('manage_users'))
    
    def test_user_permissions_resident(self):
        """Test permissions pour rôle RESIDENT"""
        # Arrange
        resident_data = self.valid_user_data.copy()
        resident_data['role'] = UserRole.RESIDENT
        user = User(**resident_data)
        
        # Act & Assert
        self.assertTrue(user.has_permission('read'))
        self.assertTrue(user.has_permission('write'))
        self.assertFalse(user.has_permission('delete'))
        self.assertFalse(user.has_permission('modify_finances'))
        self.assertFalse(user.has_permission('manage_users'))
    
    def test_user_permissions_guest(self):
        """Test permissions pour rôle GUEST"""
        # Arrange
        guest_data = self.valid_user_data.copy()
        guest_data['role'] = UserRole.GUEST
        user = User(**guest_data)
        
        # Act & Assert
        self.assertTrue(user.has_permission('read'))
        self.assertFalse(user.has_permission('write'))
        self.assertFalse(user.has_permission('delete'))
        self.assertFalse(user.has_permission('modify_finances'))
        self.assertFalse(user.has_permission('manage_users'))
    
    def test_user_serialization_to_dict(self):
        """Test sérialisation utilisateur vers dictionnaire"""
        # Arrange
        user = User(**self.valid_user_data)
        
        # Act
        user_dict = user.to_dict()
        
        # Assert
        self.assertIsInstance(user_dict, dict)
        self.assertEqual(user_dict['username'], 'testuser')
        self.assertEqual(user_dict['email'], 'test@example.com')
        self.assertEqual(user_dict['role'], 'resident')
        self.assertEqual(user_dict['full_name'], 'Test User')
        self.assertEqual(user_dict['condo_unit'], 'A-101')
        self.assertIn('created_at', user_dict)
        self.assertIn('is_active', user_dict)
        # Mot de passe ne doit pas être sérialisé en clair
        self.assertNotIn('password', user_dict)
    
    def test_user_deserialization_from_dict(self):
        """Test désérialisation utilisateur depuis dictionnaire"""
        # Arrange
        user_dict = {
            'username': 'deserialtest',
            'email': 'deserial@test.com',
            'password_hash': User.hash_password('password'),
            'role': 'admin',
            'full_name': 'Deserial Test',
            'condo_unit': 'B-202',
            'phone': '555-9999',
            'is_active': True,
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }
        
        # Act
        user = User.from_dict(user_dict)
        
        # Assert
        self.assertEqual(user.username, 'deserialtest')
        self.assertEqual(user.email, 'deserial@test.com')
        self.assertEqual(user.role, UserRole.ADMIN)
        self.assertEqual(user.full_name, 'Deserial Test')
        self.assertEqual(user.condo_unit, 'B-202')
        self.assertTrue(user.is_active)
    
    def test_user_update_last_login(self):
        """Test mise à jour dernière connexion"""
        # Arrange
        user = User(**self.valid_user_data)
        self.assertIsNone(user.last_login)
        
        # Act
        user.update_last_login()
        
        # Assert
        self.assertIsNotNone(user.last_login)
        self.assertIsInstance(user.last_login, datetime)
    
    def test_user_deactivation(self):
        """Test désactivation utilisateur"""
        # Arrange
        user = User(**self.valid_user_data)
        self.assertTrue(user.is_active)
        
        # Act
        user.deactivate()
        
        # Assert
        self.assertFalse(user.is_active)
    
    def test_user_reactivation(self):
        """Test réactivation utilisateur"""
        # Arrange
        user = User(**self.valid_user_data)
        user.deactivate()
        self.assertFalse(user.is_active)
        
        # Act
        user.activate()
        
        # Assert
        self.assertTrue(user.is_active)
    
    def test_user_string_representation(self):
        """Test représentation string de l'utilisateur"""
        # Arrange
        user = User(**self.valid_user_data)
        
        # Act
        user_str = str(user)
        
        # Assert
        self.assertIn('testuser', user_str)
        self.assertIn('resident', user_str)
    
    def test_user_equality(self):
        """Test égalité entre utilisateurs"""
        # Arrange
        user1 = User(**self.valid_user_data)
        user2_data = self.valid_user_data.copy()
        user2 = User(**user2_data)
        
        different_data = self.valid_user_data.copy()
        different_data['username'] = 'different'
        user3 = User(**different_data)
        
        # Act & Assert
        self.assertEqual(user1, user2)  # Mêmes données
        self.assertNotEqual(user1, user3)  # Données différentes
    
    def test_user_validation_edge_cases(self):
        """Test validation cas limites"""
        # Username trop court
        with self.assertRaises(UserValidationError):
            invalid_data = self.valid_user_data.copy()
            invalid_data['username'] = 'ab'
            User(**invalid_data)
        
        # Email sans @
        with self.assertRaises(UserValidationError):
            invalid_data = self.valid_user_data.copy()
            invalid_data['email'] = 'emailsansarobase.com'
            User(**invalid_data)
        
        # Nom complet vide
        with self.assertRaises(UserValidationError):
            invalid_data = self.valid_user_data.copy()
            invalid_data['full_name'] = ''
            User(**invalid_data)


if __name__ == '__main__':
    unittest.main()
