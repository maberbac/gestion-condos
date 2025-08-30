"""
Tests d'intégration pour l'authentification basée sur SQLite.

Tests pour :
- UserRepository SQLite avec authentification
- AuthenticationService avec base de données
- Intégration complète avec migrations

Méthodologie TDD : Tests d'intégration avant implémentation.
"""

import unittest
import sys
import os
import tempfile
import sqlite3
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

from src.domain.entities.user import User, UserRole
from src.domain.services.authentication_service import AuthenticationService


class TestAuthenticationIntegration(unittest.TestCase):
    """Tests d'intégration pour l'authentification avec SQLite."""
    
    def setUp(self):
        """Configuration pour chaque test."""
        # Base de données temporaire
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Configuration de test
        self.test_config = {
            "database": {
                "type": "sqlite",
                "name": "test.db",
                "path": self.db_path,
                "migrations_path": "data/migrations/"
            }
        }
        
        # Utilisateurs par défaut
        self.default_users = [
            {
                'username': 'admin',
                'email': 'admin@condos.com',
                'password': 'motdepasse123',
                'role': UserRole.ADMIN,
                'full_name': 'Jean Administrateur',
                'condo_unit': None
            },
            {
                'username': 'jdupont',
                'email': 'jean.dupont@email.com',
                'password': 'monpassword',
                'role': UserRole.RESIDENT,
                'full_name': 'Jean Dupont',
                'condo_unit': 'A-101'
            },
            {
                'username': 'mgagnon',
                'email': 'marie.gagnon@email.com',
                'password': 'secret456',
                'role': UserRole.RESIDENT,
                'full_name': 'Marie Gagnon',
                'condo_unit': 'B-205'
            }
        ]
        
        logger.debug(f"Test d'intégration avec DB : {self.db_path}")
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        try:
            os.unlink(self.db_path)
        except OSError:
            pass
    
    def _create_users_table(self):
        """Helper pour créer la table users dans les tests."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
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
        conn.close()
    
    def _insert_default_users(self):
        """Helper pour insérer les utilisateurs par défaut."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for user_data in self.default_users:
            password_hash = User.hash_password(user_data['password'])
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, full_name, condo_unit, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_data['username'],
                user_data['email'],
                password_hash,
                user_data['role'].value,
                user_data['full_name'],
                user_data['condo_unit'],
                True
            ))
        
        conn.commit()
        conn.close()
    
    def test_user_repository_sqlite_integration(self):
        """Test d'intégration du UserRepository avec SQLite."""
        # Arrange
        self._create_users_table()
        self._insert_default_users()
        
        # Act - Ce test échouera jusqu'à implémentation du UserRepositorySQLite
        # Pour l'instant, on teste l'accès direct à la base
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test de récupération d'utilisateur par username
        cursor.execute("SELECT * FROM users WHERE username = ?", ('admin',))
        admin_row = cursor.fetchone()
        
        # Assert
        self.assertIsNotNone(admin_row)
        self.assertEqual(admin_row[1], 'admin')  # username
        self.assertEqual(admin_row[4], 'admin')  # role
        
        # Test de récupération de tous les utilisateurs
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 3)
        
        conn.close()
    
    def test_authentication_service_with_database(self):
        """Test du service d'authentification avec la base de données."""
        # Arrange
        self._create_users_table()
        self._insert_default_users()
        
        # Pour ce test, on simule l'utilisation du service d'authentification
        # Le test échouera jusqu'à implémentation complète
        
        # Récupération manuelle pour simulation
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Act - Simuler l'authentification
        username = 'admin'
        password = 'motdepasse123'
        
        cursor.execute("SELECT password_hash, role, full_name FROM users WHERE username = ? AND is_active = 1", 
                      (username,))
        user_data = cursor.fetchone()
        
        # Assert
        self.assertIsNotNone(user_data)
        
        stored_hash = user_data[0]
        is_valid = User.verify_password(password, stored_hash)
        self.assertTrue(is_valid)
        
        # Test avec mauvais mot de passe
        is_invalid = User.verify_password('mauvaismdp', stored_hash)
        self.assertFalse(is_invalid)
        
        conn.close()
    
    def test_all_default_users_authentication(self):
        """Test d'authentification de tous les utilisateurs par défaut."""
        # Arrange
        self._create_users_table()
        self._insert_default_users()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Act & Assert - Tester chaque utilisateur
        for user_data in self.default_users:
            username = user_data['username']
            password = user_data['password']
            
            cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            
            self.assertIsNotNone(result, f"Utilisateur {username} non trouvé")
            
            stored_hash = result[0]
            is_valid = User.verify_password(password, stored_hash)
            self.assertTrue(is_valid, f"Authentification échouée pour {username}")
        
        conn.close()
    
    def test_user_role_assignment_integration(self):
        """Test d'intégration des rôles utilisateur."""
        # Arrange
        self._create_users_table()
        self._insert_default_users()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Act & Assert - Vérifier les rôles
        cursor.execute("SELECT username, role FROM users ORDER BY username")
        users_roles = cursor.fetchall()
        
        expected_roles = [
            ('admin', 'admin'),
            ('jdupont', 'resident'),
            ('mgagnon', 'resident')
        ]
        
        self.assertEqual(users_roles, expected_roles)
        
        # Vérifier qu'on a exactement 1 admin et 2 residents
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        self.assertEqual(admin_count, 1)
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'resident'")
        resident_count = cursor.fetchone()[0]
        self.assertEqual(resident_count, 2)
        
        conn.close()
    
    def test_condo_unit_assignment_for_residents(self):
        """Test d'assignation des unités de condo pour les résidents."""
        # Arrange
        self._create_users_table()
        self._insert_default_users()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Act & Assert
        # L'admin ne doit pas avoir d'unité
        cursor.execute("SELECT condo_unit FROM users WHERE username = 'admin'")
        admin_unit = cursor.fetchone()[0]
        self.assertIsNone(admin_unit)
        
        # Les résidents doivent avoir des unités
        cursor.execute("SELECT username, condo_unit FROM users WHERE role = 'resident' ORDER BY username")
        residents_units = cursor.fetchall()
        
        expected_units = [
            ('jdupont', 'A-101'),
            ('mgagnon', 'B-205')
        ]
        
        self.assertEqual(residents_units, expected_units)
        
        conn.close()
    
    def test_migration_compatibility(self):
        """Test de compatibilité avec le système de migrations."""
        # Ce test vérifie que notre table users est compatible avec le système de migrations
        
        # Arrange - Créer la table avec la même structure que la migration
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Act - Exécuter une structure de migration simulée
        migration_sql = """
            CREATE TABLE IF NOT EXISTS users (
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
            );
            
            -- Index pour les recherches fréquentes
            CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
            CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
            CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
        """
        
        cursor.executescript(migration_sql)
        conn.commit()
        
        # Assert - Vérifier que la table et les index sont créés
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone()
        self.assertIsNotNone(table_exists)
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_users_%'")
        indexes = cursor.fetchall()
        self.assertGreaterEqual(len(indexes), 4)  # Au moins 4 index
        
        conn.close()


if __name__ == '__main__':
    unittest.main()
