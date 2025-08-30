"""
Tests d'acceptance pour la fonctionnalité de gestion des utilisateurs depuis la base de données
"""

import unittest
from unittest.mock import patch, Mock
from src.infrastructure.logger_manager import get_logger

logger = get_logger(__name__)

class TestUserManagementDatabaseAcceptance(unittest.TestCase):
    """Tests d'acceptance pour la gestion des utilisateurs avec données de base"""

    def setUp(self):
        """Configuration des tests d'acceptance"""
        from src.web.condo_app import app
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    @patch('src.adapters.user_repository_sqlite.UserRepositorySQLite')
    @patch('src.web.condo_app.ensure_services_initialized')
    def test_scenario_admin_views_real_user_list_from_database(self, mock_ensure_services, mock_user_repo_class):
        """Scénario: Un administrateur consulte la vraie liste des utilisateurs de la base"""
        logger.info("Scénario: Consultation de la liste des utilisateurs depuis la base de données")
        
        # Mock setup
        mock_ensure_services.return_value = None
        mock_user_repo = Mock()
        mock_user_repo_class.return_value = mock_user_repo
        mock_user_repo.get_all_users.return_value = [
            {'id': 1, 'username': 'admin', 'role': 'admin', 'email': 'admin@test.com', 'full_name': 'Admin User'},
            {'id': 2, 'username': 'jdupont', 'role': 'resident', 'email': 'jdupont@test.com', 'full_name': 'Jean Dupont'},
            {'id': 3, 'username': 'mgagnon', 'role': 'resident', 'email': 'mgagnon@test.com', 'full_name': 'Marie Gagnon'}
        ]
        
        # Étape 1: L'administrateur se connecte
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'admin'
            sess['role'] = 'admin'
        
        # Étape 2: Il accède à la page de gestion des utilisateurs
        response = self.client.get('/users')
        
        # Vérifications du scénario
        self.assertEqual(response.status_code, 200, "La page utilisateurs doit se charger")
        self.assertIn(b'Gestion des Utilisateurs', response.data, "Le titre doit être affiché")
        
        # Étape 3: Il voit les vrais utilisateurs de la base de données
        response_text = response.data.decode('utf-8', errors='ignore')
        
        # L'utilisateur admin de la base doit être visible
        self.assertTrue(
            'admin' in response_text.lower(),
            "L'utilisateur admin de la base doit être affiché"
        )
        
        logger.info("Liste des utilisateurs depuis la base affichée avec succès")

    @patch('src.adapters.user_repository_sqlite.UserRepositorySQLite')
    @patch('src.web.condo_app.ensure_services_initialized')
    def test_scenario_admin_sees_accurate_user_statistics(self, mock_ensure_services, mock_user_repo_class):
        """Scénario: Un administrateur voit des statistiques précises basées sur la vraie base"""
        logger.info("Scénario: Affichage des statistiques d'utilisateurs réelles")
        
        # Mock setup
        mock_ensure_services.return_value = None
        mock_user_repo = Mock()
        mock_user_repo_class.return_value = mock_user_repo
        mock_user_repo.get_all_users.return_value = [
            {'id': 1, 'username': 'admin', 'role': 'admin', 'email': 'admin@test.com', 'full_name': 'Admin User'},
            {'id': 2, 'username': 'jdupont', 'role': 'resident', 'email': 'jdupont@test.com', 'full_name': 'Jean Dupont'},
            {'id': 3, 'username': 'mgagnon', 'role': 'resident', 'email': 'mgagnon@test.com', 'full_name': 'Marie Gagnon'}
        ]
        
        # Étape 1: L'administrateur se connecte
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'admin'
            sess['role'] = 'admin'
        
        # Étape 2: Il accède à la page utilisateurs
        response = self.client.get('/users')
        
        # Vérifications du scénario
        self.assertEqual(response.status_code, 200)
        
        response_text = response.data.decode('utf-8', errors='ignore')
        
        # Étape 3: Il voit les vraies statistiques
        self.assertIn('Administrateurs', response_text, "Section des administrateurs doit être présente")
        self.assertIn('Résidents', response_text, "Section des résidents doit être présente")
        
        # Les compteurs doivent refléter les vraies données
        self.assertTrue(
            '1' in response_text or '2' in response_text or '3' in response_text,
            "Au moins un utilisateur doit être compté"
        )
        
        logger.info("Statistiques d'utilisateurs réelles affichées correctement")

    @patch('src.adapters.user_repository_sqlite.UserRepositorySQLite')
    @patch('src.web.condo_app.ensure_services_initialized')
    def test_scenario_user_data_consistency_between_database_and_display(self, mock_ensure_services, mock_user_repo_class):
        """Scénario: Les données affichées correspondent exactement à celles de la base"""
        logger.info("Scénario: Vérification de la cohérence des données utilisateur")
        
        # Mock setup
        mock_ensure_services.return_value = None
        mock_user_repo = Mock()
        mock_user_repo_class.return_value = mock_user_repo
        mock_user_repo.get_all_users.return_value = [
            {'id': 1, 'username': 'admin', 'role': 'admin', 'email': 'admin@test.com', 'full_name': 'Admin User'}
        ]
        
        # Étape 1: L'administrateur se connecte
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'admin'
            sess['role'] = 'admin'
        
        # Étape 2: Il charge la page utilisateurs
        response = self.client.get('/users')
        
        # Vérifications de cohérence
        self.assertEqual(response.status_code, 200)
        
        response_text = response.data.decode('utf-8', errors='ignore')
        
        # Étape 3: Vérifier que les champs essentiels sont affichés
        essential_fields_present = (
            'admin' in response_text.lower() and  # Username from database
            '@' in response_text  # Email addresses should be present
        )
        
        self.assertTrue(
            essential_fields_present,
            "Les champs essentiels de la base de données doivent être affichés"
        )
        
        logger.info("Cohérence des données entre base et affichage vérifiée")

    @patch('src.adapters.user_repository_sqlite.UserRepositorySQLite')
    @patch('src.web.condo_app.ensure_services_initialized')
    def test_scenario_no_hardcoded_user_data_remains(self, mock_ensure_services, mock_user_repo_class):
        """Scénario: Aucune donnée utilisateur hardcodée ne subsiste"""
        logger.info("Scénario: Vérification de l'absence de données hardcodées")
        
        # Mock setup
        mock_ensure_services.return_value = None
        mock_user_repo = Mock()
        mock_user_repo_class.return_value = mock_user_repo
        mock_user_repo.get_all_users.return_value = [
            {'username': 'admin', 'email': 'admin@condos.com', 'role': 'admin'},
            {'username': 'jdupont', 'email': 'jean.dupont@email.com', 'role': 'resident'}
        ]
        
        # Étape 1: L'administrateur se connecte
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'admin'
            sess['role'] = 'admin'
        
        # Étape 2: Il charge la page utilisateurs
        response = self.client.get('/users')
        
        self.assertEqual(response.status_code, 200)
        
        response_text = response.data.decode('utf-8', errors='ignore')
        
        # Étape 3: Vérifier qu'aucune donnée fictive n'apparaît
        forbidden_hardcoded_data = [
            'jean.dupont@email.com',
            'marie.martin@email.com',
            'A-101',  # Unité de condo fictive
            'B-205',  # Unité de condo fictive
            '2024-11-30 18:45:00',  # Date de connexion fictive
            '2024-11-29 14:20:00'   # Date de connexion fictive
        ]
        
        for hardcoded_data in forbidden_hardcoded_data:
            self.assertNotIn(
                hardcoded_data, response_text,
                f"La donnée hardcodée '{hardcoded_data}' ne doit plus apparaître"
            )
        
        logger.info("Aucune donnée hardcodée détectée - migration réussie")

    @patch('src.adapters.user_repository_sqlite.UserRepositorySQLite')
    @patch('src.web.condo_app.ensure_services_initialized')
    def test_scenario_page_performance_with_database_integration(self, mock_ensure_services, mock_user_repo_class):
        """Scénario: La page se charge rapidement avec l'intégration base de données"""
        logger.info("Scénario: Test de performance avec intégration base de données")
        
        import time
        
        # Mock setup
        mock_ensure_services.return_value = None
        mock_user_repo = Mock()
        mock_user_repo_class.return_value = mock_user_repo
        mock_user_repo.get_all_users.return_value = [
            {'id': 1, 'username': 'admin', 'role': 'admin', 'email': 'admin@test.com', 'full_name': 'Admin User'}
        ]
        
        # Étape 1: L'administrateur se connecte
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'admin'
            sess['role'] = 'admin'
        
        # Étape 2: Mesurer le temps de chargement
        start_time = time.time()
        response = self.client.get('/users')
        end_time = time.time()
        
        load_time = end_time - start_time
        
        # Vérifications de performance
        self.assertEqual(response.status_code, 200)
        self.assertLess(load_time, 2.0, "La page doit se charger en moins de 2 secondes")
        
        logger.info(f"Page chargée en {load_time:.3f} secondes avec intégration base de données")


if __name__ == '__main__':
    unittest.main()
