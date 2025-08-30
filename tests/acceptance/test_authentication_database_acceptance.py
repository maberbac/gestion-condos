"""
Tests d'acceptance pour l'authentification basée sur la base de données.

Scénarios utilisateur :
- Un administrateur s'authentifie avec ses identifiants
- Un résident s'authentifie avec ses identifiants  
- Un utilisateur avec mauvais identifiants ne peut pas s'authentifier
- Les mots de passe sont sécurisés dans la base de données
"""

import unittest
import sys
import os
import tempfile
import sqlite3
from pathlib import Path

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

from src.domain.entities.user import User, UserRole


class TestAuthenticationDatabaseAcceptance(unittest.TestCase):
    """Tests d'acceptance pour l'authentification avec base de données."""
    
    def setUp(self):
        """Configuration pour chaque test d'acceptance."""
        # Base de données temporaire pour les tests
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Données des 3 utilisateurs par défaut
        self.users_data = [
            {
                'username': 'admin',
                'email': 'admin@condos.com',
                'password': 'motdepasse123',
                'role': 'admin',
                'full_name': 'Jean Administrateur',
                'condo_unit': None
            },
            {
                'username': 'jdupont',
                'email': 'jean.dupont@email.com',
                'password': 'monpassword',
                'role': 'resident',
                'full_name': 'Jean Dupont',
                'condo_unit': 'A-101'
            },
            {
                'username': 'mgagnon',
                'email': 'marie.gagnon@email.com',
                'password': 'secret456',
                'role': 'resident',
                'full_name': 'Marie Gagnon',
                'condo_unit': 'B-205'
            }
        ]
        
        self._setup_database_with_users()
        logger.debug(f"Test d'acceptance avec base de données : {self.db_path}")
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        try:
            os.unlink(self.db_path)
        except OSError:
            pass
    
    def _setup_database_with_users(self):
        """Prépare la base de données avec les utilisateurs par défaut."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Créer la table users
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
        
        # Insérer les utilisateurs avec mots de passe chiffrés
        for user_data in self.users_data:
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
                True
            ))
        
        conn.commit()
        conn.close()
    
    def test_scenario_admin_authentication_success(self):
        """
        Scénario: Un administrateur s'authentifie avec succès
        
        GIVEN: Le système a un utilisateur administrateur dans la base de données
        WHEN: L'administrateur fournit ses identifiants corrects
        THEN: L'authentification réussit et retourne les informations de l'admin
        """
        logger.info("Scénario: Authentification réussie de l'administrateur")
        
        # GIVEN - L'admin existe dans la base
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin' AND role = 'admin'")
        admin_exists = cursor.fetchone()[0]
        self.assertEqual(admin_exists, 1, "L'administrateur doit exister dans la base")
        
        # WHEN - L'admin fournit ses identifiants
        username = 'admin'
        password = 'motdepasse123'
        
        cursor.execute("""
            SELECT id, username, email, password_hash, role, full_name, condo_unit, is_active 
            FROM users WHERE username = ? AND is_active = 1
        """, (username,))
        
        user_record = cursor.fetchone()
        
        # THEN - L'authentification doit réussir
        self.assertIsNotNone(user_record, "L'utilisateur admin doit être trouvé")
        
        stored_hash = user_record[3]
        is_authenticated = User.verify_password(password, stored_hash)
        self.assertTrue(is_authenticated, "Le mot de passe admin doit être valide")
        
        # Vérifier les informations de l'admin
        self.assertEqual(user_record[1], 'admin')
        self.assertEqual(user_record[4], 'admin')
        self.assertEqual(user_record[5], 'Jean Administrateur')
        self.assertIsNone(user_record[6])  # Pas d'unité de condo pour l'admin
        
        conn.close()
        logger.info("Authentification admin réussie avec succès")
    
    def test_scenario_resident_authentication_success(self):
        """
        Scénario: Un résident s'authentifie avec succès
        
        GIVEN: Le système a un utilisateur résident dans la base de données
        WHEN: Le résident fournit ses identifiants corrects
        THEN: L'authentification réussit et retourne les informations du résident
        """
        logger.info("Scénario: Authentification réussie d'un résident")
        
        # GIVEN - Le résident existe dans la base
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'jdupont' AND role = 'resident'")
        resident_exists = cursor.fetchone()[0]
        self.assertEqual(resident_exists, 1, "Le résident jdupont doit exister dans la base")
        
        # WHEN - Le résident fournit ses identifiants
        username = 'jdupont'
        password = 'monpassword'
        
        cursor.execute("""
            SELECT id, username, email, password_hash, role, full_name, condo_unit, is_active 
            FROM users WHERE username = ? AND is_active = 1
        """, (username,))
        
        user_record = cursor.fetchone()
        
        # THEN - L'authentification doit réussir
        self.assertIsNotNone(user_record, "L'utilisateur résident doit être trouvé")
        
        stored_hash = user_record[3]
        is_authenticated = User.verify_password(password, stored_hash)
        self.assertTrue(is_authenticated, "Le mot de passe résident doit être valide")
        
        # Vérifier les informations du résident
        self.assertEqual(user_record[1], 'jdupont')
        self.assertEqual(user_record[4], 'resident')
        self.assertEqual(user_record[5], 'Jean Dupont')
        self.assertEqual(user_record[6], 'A-101')  # Unité de condo assignée
        
        conn.close()
        logger.info("Authentification résident réussie avec succès")
    
    def test_scenario_authentication_failure_wrong_password(self):
        """
        Scénario: Un utilisateur échoue à s'authentifier avec un mauvais mot de passe
        
        GIVEN: Le système a un utilisateur dans la base de données
        WHEN: L'utilisateur fournit un mot de passe incorrect
        THEN: L'authentification échoue
        """
        logger.info("Scénario: Échec d'authentification avec mauvais mot de passe")
        
        # GIVEN - L'utilisateur existe
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        username = 'admin'
        wrong_password = 'mauvaismdp123'
        
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        user_record = cursor.fetchone()
        self.assertIsNotNone(user_record, "L'utilisateur doit exister pour le test")
        
        # WHEN - Mauvais mot de passe fourni
        stored_hash = user_record[0]
        
        # THEN - L'authentification doit échouer
        is_authenticated = User.verify_password(wrong_password, stored_hash)
        self.assertFalse(is_authenticated, "L'authentification doit échouer avec un mauvais mot de passe")
        
        conn.close()
        logger.info("Échec d'authentification correctement géré")
    
    def test_scenario_authentication_failure_unknown_user(self):
        """
        Scénario: Un utilisateur inexistant ne peut pas s'authentifier
        
        GIVEN: Le système ne contient pas un utilisateur spécifique
        WHEN: Cet utilisateur tente de s'authentifier
        THEN: L'authentification échoue car l'utilisateur n'existe pas
        """
        logger.info("Scénario: Échec d'authentification pour utilisateur inexistant")
        
        # GIVEN - L'utilisateur n'existe pas
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        unknown_username = 'utilisateur_inexistant'
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (unknown_username,))
        user_count = cursor.fetchone()[0]
        self.assertEqual(user_count, 0, "L'utilisateur ne doit pas exister pour ce test")
        
        # WHEN - Tentative d'authentification
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", (unknown_username,))
        user_record = cursor.fetchone()
        
        # THEN - Aucun utilisateur trouvé
        self.assertIsNone(user_record, "Aucun utilisateur ne doit être trouvé")
        
        conn.close()
        logger.info("Utilisateur inexistant correctement rejeté")
    
    def test_scenario_passwords_are_encrypted_in_database(self):
        """
        Scénario: Les mots de passe sont sécurisés dans la base de données
        
        GIVEN: Le système stocke des utilisateurs avec mots de passe
        WHEN: On examine les mots de passe dans la base de données
        THEN: Les mots de passe sont chiffrés et non en clair
        """
        logger.info("Scénario: Vérification du chiffrement des mots de passe")
        
        # GIVEN - Des utilisateurs avec mots de passe dans la base
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT username, password_hash FROM users")
        all_users = cursor.fetchall()
        
        # THEN - Tous les mots de passe doivent être chiffrés
        original_passwords = [user['password'] for user in self.users_data]
        
        for username, stored_hash in all_users:
            # Le hash ne doit pas être identique au mot de passe original
            for original_pwd in original_passwords:
                self.assertNotEqual(stored_hash, original_pwd, 
                    f"Le mot de passe de {username} ne doit pas être stocké en clair")
            
            # Le hash doit avoir une longueur appropriée
            self.assertGreater(len(stored_hash), 20, 
                f"Le hash du mot de passe de {username} doit être suffisamment long")
            
            # Le hash doit contenir le séparateur pour le salt
            self.assertIn(':', stored_hash, 
                f"Le hash de {username} doit contenir un salt séparé par ':'")
        
        conn.close()
        logger.info("Chiffrement des mots de passe vérifié avec succès")
    
    def test_scenario_all_three_default_users_can_authenticate(self):
        """
        Scénario: Les trois utilisateurs par défaut peuvent s'authentifier
        
        GIVEN: Le système a été initialisé avec 3 utilisateurs par défaut
        WHEN: Chaque utilisateur tente de s'authentifier avec ses identifiants
        THEN: Tous les trois peuvent s'authentifier avec succès
        """
        logger.info("Scénario: Authentification des 3 utilisateurs par défaut")
        
        # GIVEN - Les 3 utilisateurs par défaut existent
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        self.assertEqual(total_users, 3, "Il doit y avoir exactement 3 utilisateurs par défaut")
        
        # WHEN & THEN - Chaque utilisateur peut s'authentifier
        successful_authentications = 0
        
        for user_data in self.users_data:
            username = user_data['username']
            password = user_data['password']
            
            cursor.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,))
            user_record = cursor.fetchone()
            
            self.assertIsNotNone(user_record, f"L'utilisateur {username} doit exister")
            
            stored_hash, role = user_record
            is_authenticated = User.verify_password(password, stored_hash)
            
            if is_authenticated:
                successful_authentications += 1
                logger.info(f"Authentification réussie pour {username} (rôle: {role})")
            else:
                self.fail(f"Échec d'authentification pour {username}")
        
        # Tous les 3 utilisateurs doivent pouvoir s'authentifier
        self.assertEqual(successful_authentications, 3, 
            "Les 3 utilisateurs par défaut doivent pouvoir s'authentifier")
        
        conn.close()
        logger.info("Authentification des 3 utilisateurs par défaut réussie")
    
    def test_scenario_database_integrity_after_authentication(self):
        """
        Scénario: L'intégrité de la base de données est maintenue après authentification
        
        GIVEN: Le système a des utilisateurs dans la base de données
        WHEN: Plusieurs authentifications ont lieu
        THEN: La base de données maintient son intégrité et ses contraintes
        """
        logger.info("Scénario: Vérification de l'intégrité de la base après authentifications")
        
        # GIVEN - Base de données avec utilisateurs
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # WHEN - Plusieurs authentifications (simulation)
        for _ in range(5):  # Simuler 5 cycles d'authentification
            for user_data in self.users_data:
                username = user_data['username']
                password = user_data['password']
                
                cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
                user_record = cursor.fetchone()
                
                if user_record:
                    User.verify_password(password, user_record[0])
        
        # THEN - Vérifier l'intégrité
        # Vérifier que tous les utilisateurs existent toujours
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        self.assertEqual(user_count, 3, "Le nombre d'utilisateurs doit rester à 3")
        
        # Vérifier l'unicité des usernames
        cursor.execute("SELECT username, COUNT(*) FROM users GROUP BY username HAVING COUNT(*) > 1")
        duplicates = cursor.fetchall()
        self.assertEqual(len(duplicates), 0, "Aucun username ne doit être dupliqué")
        
        # Vérifier l'unicité des emails
        cursor.execute("SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1")
        email_duplicates = cursor.fetchall()
        self.assertEqual(len(email_duplicates), 0, "Aucun email ne doit être dupliqué")
        
        # Vérifier que les contraintes de rôle sont respectées
        cursor.execute("SELECT role FROM users WHERE role NOT IN ('admin', 'resident', 'guest')")
        invalid_roles = cursor.fetchall()
        self.assertEqual(len(invalid_roles), 0, "Tous les rôles doivent être valides")
        
        conn.close()
        logger.info("Intégrité de la base de données maintenue")


if __name__ == '__main__':
    unittest.main()
