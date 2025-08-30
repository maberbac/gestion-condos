#!/usr/bin/env python3
"""
Tests d'acceptance pour la modification de mot de passe
Scénarios utilisateur complets
"""

import unittest
import asyncio
import tempfile
import os
import sqlite3

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.infrastructure.logger_manager import get_logger
from src.domain.entities.user import User, UserRole
from src.domain.services.password_change_service import PasswordChangeService, PasswordChangeError
from src.domain.services.authentication_service import AuthenticationService
from src.adapters.user_file_adapter import UserFileAdapter
from src.adapters.user_repository_sqlite import UserRepositorySQLite

logger = get_logger(__name__)


class TestPasswordChangeAcceptance(unittest.TestCase):
    """Tests d'acceptance pour les scénarios de modification de mot de passe."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json')
        # Initialiser le fichier avec un JSON valide vide
        self.temp_file.write('{"users": []}')
        self.temp_file.close()
        
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
    
    def test_scenario_resident_changes_password_successfully(self):
        """
        Scénario: Un résident change son mot de passe avec succès
        
        GIVEN: Un résident authentifié dans le système
        WHEN: Il fournit son mot de passe actuel et un nouveau mot de passe valide
        THEN: Son mot de passe est mis à jour et il peut se connecter avec le nouveau
        """
        logger.info("Scénario: Résident change son mot de passe avec succès")
        
        async def test_async():
            # GIVEN - Un résident existe dans le système
            resident = User(
                username="resident_marie",
                email="marie@condos.com",
                password_hash=User.hash_password("ancien_mdp_marie"),
                role=UserRole.RESIDENT,
                full_name="Marie Tremblay",
                condo_unit="A-205"
            )
            await self.user_repository.save_user(resident)
            logger.info("Résident Marie créé avec mot de passe initial")
            
            # WHEN - Elle change son mot de passe
            result = await self.password_service.change_password(
                "resident_marie",
                "ancien_mdp_marie",
                "nouveau_mdp_securise123"
            )
            
            # THEN - Le changement est réussi
            self.assertTrue(result)
            logger.info("Changement de mot de passe réussi")
            
            # THEN - Elle ne peut plus se connecter avec l'ancien mot de passe
            old_auth = await self.authentication_service.authenticate(
                "resident_marie", "ancien_mdp_marie"
            )
            self.assertIsNone(old_auth)
            logger.info("Ancien mot de passe rejeté - sécurité validée")
            
            # THEN - Elle peut se connecter avec le nouveau mot de passe
            new_auth = await self.authentication_service.authenticate(
                "resident_marie", "nouveau_mdp_securise123"
            )
            self.assertIsNotNone(new_auth)
            self.assertEqual(new_auth.username, "resident_marie")
            logger.info("Authentification avec nouveau mot de passe réussie")
        
        asyncio.run(test_async())
    
    def test_scenario_admin_changes_password_maintains_access(self):
        """
        Scénario: Un administrateur change son mot de passe et maintient ses privilèges
        
        GIVEN: Un administrateur avec privilèges élevés
        WHEN: Il change son mot de passe
        THEN: Il conserve ses privilèges et peut accéder aux fonctions admin
        """
        logger.info("Scénario: Admin change mot de passe et conserve privilèges")
        
        async def test_async():
            # GIVEN - Un administrateur
            admin = User(
                username="admin_john",
                email="john@condos.com",
                password_hash=User.hash_password("admin_password_123"),
                role=UserRole.ADMIN,
                full_name="John Administrator"
            )
            await self.user_repository.save_user(admin)
            logger.info("Administrateur John créé")
            
            # WHEN - Il change son mot de passe
            result = await self.password_service.change_password(
                "admin_john",
                "admin_password_123",
                "super_secure_admin_456"
            )
            
            # THEN - Changement réussi
            self.assertTrue(result)
            
            # THEN - Il peut toujours s'authentifier avec rôle admin
            auth_result = await self.authentication_service.authenticate(
                "admin_john", "super_secure_admin_456"
            )
            self.assertIsNotNone(auth_result)
            self.assertEqual(auth_result.role, UserRole.ADMIN)
            logger.info("Privilèges administrateur conservés après changement de mot de passe")
        
        asyncio.run(test_async())
    
    def test_scenario_user_fails_with_wrong_current_password(self):
        """
        Scénario: Un utilisateur échoue à changer son mot de passe avec un mauvais mot de passe actuel
        
        GIVEN: Un utilisateur dans le système
        WHEN: Il fournit un mauvais mot de passe actuel
        THEN: Le changement est refusé et son mot de passe reste inchangé
        """
        logger.info("Scénario: Échec changement avec mauvais mot de passe actuel")
        
        async def test_async():
            # GIVEN - Un utilisateur
            user = User(
                username="user_paul",
                email="paul@condos.com",
                password_hash=User.hash_password("password_paul_correct"),
                role=UserRole.RESIDENT,
                full_name="Paul Resident",
                condo_unit="B-310"
            )
            await self.user_repository.save_user(user)
            logger.info("Utilisateur Paul créé")
            
            # WHEN - Il fournit un mauvais mot de passe actuel
            with self.assertRaises(PasswordChangeError) as context:
                await self.password_service.change_password(
                    "user_paul",
                    "mauvais_mot_de_passe",
                    "nouveau_password_123"
                )
            
            # THEN - Erreur appropriée
            self.assertIn("Nom d'utilisateur ou mot de passe actuel incorrect", str(context.exception))
            logger.info("Changement refusé avec message d'erreur approprié")
            
            # THEN - Son mot de passe original fonctionne toujours
            auth_result = await self.authentication_service.authenticate(
                "user_paul", "password_paul_correct"
            )
            self.assertIsNotNone(auth_result)
            logger.info("Mot de passe original toujours valide - sécurité maintenue")
        
        asyncio.run(test_async())
    
    def test_scenario_user_provides_weak_new_password(self):
        """
        Scénario: Un utilisateur tente d'utiliser un mot de passe faible
        
        GIVEN: Un utilisateur authentifié
        WHEN: Il fournit un nouveau mot de passe trop faible
        THEN: Le changement est refusé avec message explicatif
        """
        logger.info("Scénario: Rejet mot de passe faible")
        
        async def test_async():
            # GIVEN - Un utilisateur
            user = User(
                username="user_sophie",
                email="sophie@condos.com",
                password_hash=User.hash_password("good_password_123"),
                role=UserRole.RESIDENT,
                full_name="Sophie Resident",
                condo_unit="C-405"
            )
            await self.user_repository.save_user(user)
            logger.info("Utilisatrice Sophie créée")
            
            # WHEN - Elle tente d'utiliser un mot de passe faible
            weak_passwords = ["123", "abc", ""]
            
            for weak_password in weak_passwords:
                with self.subTest(weak_password=weak_password):
                    with self.assertRaises(PasswordChangeError):
                        await self.password_service.change_password(
                            "user_sophie",
                            "good_password_123",
                            weak_password
                        )
            
            logger.info("Tous les mots de passe faibles rejetés")
            
            # THEN - Son mot de passe original reste valide
            auth_result = await self.authentication_service.authenticate(
                "user_sophie", "good_password_123"
            )
            self.assertIsNotNone(auth_result)
            logger.info("Mot de passe original préservé")
        
        asyncio.run(test_async())
    
    def test_scenario_multiple_users_change_passwords_independently(self):
        """
        Scénario: Plusieurs utilisateurs changent leurs mots de passe indépendamment
        
        GIVEN: Plusieurs utilisateurs dans le système
        WHEN: Chacun change son mot de passe
        THEN: Chaque changement est isolé et sécurisé
        """
        logger.info("Scénario: Changements multiples indépendants")
        
        async def test_async():
            # GIVEN - Plusieurs utilisateurs
            users_data = [
                ("user1", "password123", "newpassword1", "A-100"),
                ("user2", "password456", "newpassword2", "B-200"),
                ("user3", "password789", "newpassword3", "C-300"),
            ]
            
            for username, password, _, unit in users_data:
                user = User(
                    username=username,
                    email=f"{username}@condos.com",
                    password_hash=User.hash_password(password),
                    role=UserRole.RESIDENT,
                    full_name=f"User {username.upper()}",
                    condo_unit=unit
                )
                await self.user_repository.save_user(user)
            
            logger.info("Trois utilisateurs créés")
            
            # WHEN - Chacun change son mot de passe
            for username, old_pass, new_pass, _ in users_data:
                result = await self.password_service.change_password(
                    username, old_pass, new_pass
                )
                self.assertTrue(result)
            
            logger.info("Tous les changements de mots de passe réussis")
            
            # THEN - Chaque utilisateur peut s'authentifier avec son nouveau mot de passe
            for username, _, new_pass, _ in users_data:
                auth_result = await self.authentication_service.authenticate(
                    username, new_pass
                )
                self.assertIsNotNone(auth_result)
                self.assertEqual(auth_result.username, username)
            
            # THEN - Aucun utilisateur ne peut s'authentifier avec les anciens mots de passe
            for username, old_pass, _, _ in users_data:
                auth_result = await self.authentication_service.authenticate(
                    username, old_pass
                )
                self.assertIsNone(auth_result)
            
            logger.info("Isolation des changements validée - sécurité garantie")
        
        asyncio.run(test_async())


if __name__ == '__main__':
    unittest.main()
