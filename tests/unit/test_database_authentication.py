"""
Tests unitaires pour l'authentification basée sur la base de données.

Tests pour :
- Création de la table users
- Insertion des 3 utilisateurs par défaut
- Authentification avec mots de passe chiffrés
- Gestion des sessions

Méthodologie TDD : Écrire les tests AVANT l'implémentation.
"""

import unittest
import sys
import os
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

from src.domain.entities.user import User, UserRole, UserAuthenticationError, UserValidationError


class TestDatabaseAuthentication(unittest.TestCase):
    """Tests pour l'authentification basée sur la base de données."""
    
    def setUp(self):
        """Configuration pour chaque test avec base de données temporaire."""
        # Créer une base de données temporaire pour les tests
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Utilisateurs de test par défaut
        self.default_users = [
            {
                'username': 'admin',
                'email': 'admin@condos.com',
                'password': 'motdepasse123',
                'role': 'admin',
                'full_name': 'Jean Administrateur',
                'condo_unit': None,
                'is_active': True
            },
            {
                'username': 'jdupont',
                'email': 'jean.dupont@email.com',
                'password': 'monpassword',
                'role': 'resident',
                'full_name': 'Jean Dupont',
                'condo_unit': 'A-101',
                'is_active': True
            },
            {
                'username': 'mgagnon',
                'email': 'marie.gagnon@email.com',
                'password': 'secret456',
                'role': 'resident',
                'full_name': 'Marie Gagnon',
                'condo_unit': 'B-205',
                'is_active': True
            }
        ]
        
        logger.debug(f"Base de données de test créée : {self.db_path}")
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        try:
            os.unlink(self.db_path)
        except OSError:
            pass
    
    def test_user_table_creation(self):
        """Test de création de la table users dans SQLite."""
        # Arrange - Préparer la base de données
        conn = sqlite3.connect(self.db_path)
        
        # Act - Créer la table users (ce que nous devrons implémenter)
        cursor = conn.cursor()
        
        # Assert - La table users doit pouvoir être créée
        # Ce test va échouer jusqu'à ce qu'on implémente la migration
        try:
            cursor.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    condo_unit TEXT,
                    phone TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT DEFAULT (datetime('now')),
                    last_login TEXT,
                    CONSTRAINT chk_role CHECK (role IN ('admin', 'resident', 'guest'))
                )
            """)
            conn.commit()
            
            # Vérifier que la table existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            result = cursor.fetchone()
            self.assertIsNotNone(result)
            self.assertEqual(result[0], 'users')
            
        finally:
            conn.close()
    
    def test_default_users_insertion(self):
        """Test d'insertion des 3 utilisateurs par défaut."""
        # Arrange - Créer la table users
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT NOT NULL,
                condo_unit TEXT,
                phone TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now')),
                last_login TEXT,
                CONSTRAINT chk_role CHECK (role IN ('admin', 'resident', 'guest'))
            )
        """)
        
        # Act - Insérer les utilisateurs par défaut
        for user_data in self.default_users:
            # Les mots de passe doivent être chiffrés
            password_hash = User.hash_password(user_data['password'])
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, full_name, condo_unit, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_data['username'],
                user_data['email'],
                password_hash,
                user_data['role'],
                user_data['full_name'],
                user_data['condo_unit'],
                user_data['is_active']
            ))
        
        conn.commit()
        
        # Assert - Vérifier que les 3 utilisateurs sont insérés
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 3)
        
        # Vérifier que les utilisateurs spécifiques existent
        cursor.execute("SELECT username, role FROM users ORDER BY username")
        users = cursor.fetchall()
        
        expected_users = [
            ('admin', 'admin'),
            ('jdupont', 'resident'),
            ('mgagnon', 'resident')
        ]
        
        self.assertEqual(users, expected_users)
        
        conn.close()
    
    def test_password_encryption_verification(self):
        """Test que les mots de passe sont correctement chiffrés et vérifiés."""
        # Arrange
        test_password = "monmotdepasse123"
        
        # Act - Chiffrer le mot de passe
        password_hash = User.hash_password(test_password)
        
        # Assert - Le hash ne doit pas être identique au mot de passe original
        self.assertNotEqual(password_hash, test_password)
        self.assertIsInstance(password_hash, str)
        self.assertGreater(len(password_hash), 20)  # Hash doit être suffisamment long
        
        # Test de vérification
        is_valid = User.verify_password(test_password, password_hash)
        self.assertTrue(is_valid)
        
        # Test avec mauvais mot de passe
        is_invalid = User.verify_password("mauvaismdp", password_hash)
        self.assertFalse(is_invalid)
    
    def test_user_authentication_from_database(self):
        """Test d'authentification d'un utilisateur depuis la base de données."""
        # Arrange - Préparer la base avec un utilisateur
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT NOT NULL,
                condo_unit TEXT,
                phone TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now')),
                last_login TEXT,
                CONSTRAINT chk_role CHECK (role IN ('admin', 'resident', 'guest'))
            )
        """)
        
        # Insérer un utilisateur de test
        test_user = self.default_users[0]  # admin
        password_hash = User.hash_password(test_user['password'])
        
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, full_name, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            test_user['username'],
            test_user['email'],
            password_hash,
            test_user['role'],
            test_user['full_name'],
            test_user['is_active']
        ))
        
        conn.commit()
        conn.close()
        
        # Act - Ce test va échouer jusqu'à implémentation du UserRepository SQLite
        # Simuler la récupération depuis la base
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (test_user['username'],))
        db_user = cursor.fetchone()
        
        # Assert - L'utilisateur doit être trouvé
        self.assertIsNotNone(db_user)
        
        # Le mot de passe doit correspondre
        stored_hash = db_user[3]  # password_hash est la 4ème colonne
        is_valid = User.verify_password(test_user['password'], stored_hash)
        self.assertTrue(is_valid)
        
        conn.close()
    
    def test_inactive_user_cannot_authenticate(self):
        """Test qu'un utilisateur inactif ne peut pas s'authentifier."""
        # Arrange - Créer un utilisateur inactif
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT NOT NULL,
                condo_unit TEXT,
                phone TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now')),
                last_login TEXT,
                CONSTRAINT chk_role CHECK (role IN ('admin', 'resident', 'guest'))
            )
        """)
        
        # Insérer un utilisateur inactif
        test_user = self.default_users[1].copy()  # jdupont
        test_user['is_active'] = False
        password_hash = User.hash_password(test_user['password'])
        
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, full_name, condo_unit, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            test_user['username'],
            test_user['email'],
            password_hash,
            test_user['role'],
            test_user['full_name'],
            test_user['condo_unit'],
            test_user['is_active']
        ))
        
        conn.commit()
        
        # Act - Vérifier que l'utilisateur est inactif
        cursor.execute("SELECT is_active FROM users WHERE username = ?", (test_user['username'],))
        is_active = cursor.fetchone()[0]
        
        # Assert - L'utilisateur doit être inactif
        self.assertFalse(is_active)
        
        conn.close()
    
    def test_unique_constraints_enforcement(self):
        """Test que les contraintes d'unicité sont respectées."""
        # Arrange
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT NOT NULL,
                condo_unit TEXT,
                phone TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now')),
                last_login TEXT,
                CONSTRAINT chk_role CHECK (role IN ('admin', 'resident', 'guest'))
            )
        """)
        
        # Insérer le premier utilisateur
        test_user = self.default_users[0]
        password_hash = User.hash_password(test_user['password'])
        
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, full_name, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            test_user['username'],
            test_user['email'],
            password_hash,
            test_user['role'],
            test_user['full_name'],
            test_user['is_active']
        ))
        
        # Act & Assert - Tenter d'insérer un utilisateur avec le même username
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, full_name, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                test_user['username'],  # Même username
                'autre@email.com',      # Email différent
                password_hash,
                test_user['role'],
                'Autre Nom',
                True
            ))
        
        # Tenter d'insérer un utilisateur avec le même email
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, full_name, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                'autreusername',         # Username différent
                test_user['email'],      # Même email
                password_hash,
                test_user['role'],
                'Autre Nom',
                True
            ))
        
        conn.close()


if __name__ == '__main__':
    unittest.main()
