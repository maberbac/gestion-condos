#!/usr/bin/env python3
"""
Tests d'intégration pour la modification de mot de passe
Validation du comportement avec adapteurs réels
"""

import unittest
import asyncio
import tempfile
import os
import sqlite3
import json
from datetime import datetime

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.infrastructure.logger_manager import get_logger
from src.domain.entities.user import User, UserRole
from src.domain.services.password_change_service import PasswordChangeService, PasswordChangeError
from src.domain.services.authentication_service import AuthenticationService
from src.adapters.user_file_adapter import UserFileAdapter
from src.adapters.user_repository_sqlite import UserRepositorySQLite

logger = get_logger(__name__)


class TestPasswordChangeFileIntegration(unittest.TestCase):
    """Tests d'intégration pour modification mot de passe avec adapteur fichier."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json')
        # Initialiser le fichier avec la structure JSON attendue par l'adapteur
        json.dump({"users": []}, self.temp_file)
        self.temp_file.close()
        
        self.user_repository = UserFileAdapter(users_file=self.temp_file.name)
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
    
    def test_password_change_with_file_adapter(self):
        """Test modification mot de passe avec adapteur fichier."""
        async def test_async():
            # ARRANGE - Créer utilisateur
            user = User(
                username="filetest",
                email="filetest@test.com",
                password_hash=User.hash_password("original123"),
                role=UserRole.RESIDENT,
                full_name="File Test User",
                condo_unit="C-303"
            )
            await self.user_repository.save_user(user)
            
            # ACT - Changer mot de passe
            result = await self.password_service.change_password(
                "filetest", "original123", "nouveau654"
            )
            
            # ASSERT
            self.assertTrue(result)
            
            # Vérifier persistance
            updated_user = await self.user_repository.get_user_by_username("filetest")
            self.assertIsNotNone(updated_user)
            self.assertTrue(User.verify_password("nouveau654", updated_user.password_hash))
            self.assertFalse(User.verify_password("original123", updated_user.password_hash))
        
        asyncio.run(test_async())


class TestPasswordChangeSQLiteIntegration(unittest.TestCase):
    """Tests d'intégration pour modification mot de passe avec SQLite."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Créer fichier de configuration temporaire
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        config_content = {
            "database": {
                "path": self.temp_db.name,
                "migrations_path": "data/migrations/"
            }
        }
        json.dump(config_content, self.temp_config)
        self.temp_config.close()
        
        # Initialiser la base de données manuellement pour les tests
        conn = sqlite3.connect(self.temp_db.name)
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
                last_login TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        self.user_repository = UserRepositorySQLite(config_path=self.temp_config.name)
        self.authentication_service = AuthenticationService(self.user_repository)
        self.password_service = PasswordChangeService(
            user_repository=self.user_repository,
            authentication_service=self.authentication_service
        )
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        try:
            os.unlink(self.temp_db.name)
        except OSError:
            pass
        try:
            os.unlink(self.temp_config.name)
        except OSError:
            pass
    
    def test_password_change_with_sqlite_adapter(self):
        """Test modification mot de passe avec adapteur SQLite."""
        async def test_async():
            # ARRANGE - Créer utilisateur
            user = User(
                username="sqlitetest",
                email="sqlitetest@test.com",
                password_hash=User.hash_password("sqlite123"),
                role=UserRole.ADMIN,
                full_name="SQLite Test User"
            )
            await self.user_repository.save_user(user)
            
            # ACT - Changer mot de passe
            result = await self.password_service.change_password(
                "sqlitetest", "sqlite123", "newsqlite789"
            )
            
            # ASSERT
            self.assertTrue(result)
            
            # Vérifier persistance en base
            conn = sqlite3.connect(self.temp_db.name)
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE username = ?", ("sqlitetest",))
            result_hash = cursor.fetchone()[0]
            conn.close()
            
            self.assertTrue(User.verify_password("newsqlite789", result_hash))
            self.assertFalse(User.verify_password("sqlite123", result_hash))
        
        asyncio.run(test_async())
    
    def test_password_change_concurrent_access(self):
        """Test modification concurrent de mots de passe."""
        async def test_async():
            # ARRANGE - Créer plusieurs utilisateurs
            users = [
                User(
                    username=f"concurrent{i}",
                    email=f"concurrent{i}@test.com",
                    password_hash=User.hash_password(f"password{i}"),
                    role=UserRole.RESIDENT,
                    full_name=f"Concurrent User {i}",
                    condo_unit=f"D-{400+i}"
                )
                for i in range(3)
            ]
            
            for user in users:
                await self.user_repository.save_user(user)
            
            # ACT - Modifications simultanées
            tasks = [
                self.password_service.change_password(
                    f"concurrent{i}", f"password{i}", f"newpass{i}"
                )
                for i in range(3)
            ]
            
            results = await asyncio.gather(*tasks)
            
            # ASSERT - Toutes réussies
            self.assertTrue(all(results))
            
            # Vérifier chaque changement
            for i in range(3):
                auth_result = await self.authentication_service.authenticate(
                    f"concurrent{i}", f"newpass{i}"
                )
                self.assertIsNotNone(auth_result)
        
        asyncio.run(test_async())


class TestPasswordChangeSecurityIntegration(unittest.TestCase):
    """Tests de sécurité pour la modification de mot de passe."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json')
        # Initialiser le fichier avec la structure JSON attendue par l'adapteur
        json.dump({"users": []}, self.temp_file)
        self.temp_file.close()
        
        self.user_repository = UserFileAdapter(users_file=self.temp_file.name)
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
    
    def test_password_hash_security(self):
        """Test de sécurité des hashs de mots de passe."""
        async def test_async():
            # ARRANGE
            user = User(
                username="securitytest",
                email="security@test.com",
                password_hash=User.hash_password("original123"),
                role=UserRole.RESIDENT,
                full_name="Security Test User",
                condo_unit="E-505"
            )
            await self.user_repository.save_user(user)
            
            # ACT - Plusieurs changements de mot de passe
            passwords = ["change1", "change2", "change3"]
            hashes = []
            
            current_password = "original123"
            for new_password in passwords:
                await self.password_service.change_password(
                    "securitytest", current_password, new_password
                )
                
                updated_user = await self.user_repository.get_user_by_username("securitytest")
                hashes.append(updated_user.password_hash)
                current_password = new_password
            
            # ASSERT - Tous les hashs doivent être différents
            self.assertEqual(len(set(hashes)), len(hashes), "Tous les hashs doivent être uniques")
            
            # Aucun hash ne doit contenir le mot de passe en clair
            for i, hash_value in enumerate(hashes):
                self.assertNotIn(passwords[i], hash_value)
                self.assertIn(":", hash_value)  # Doit contenir le salt
        
        asyncio.run(test_async())


if __name__ == '__main__':
    unittest.main()
