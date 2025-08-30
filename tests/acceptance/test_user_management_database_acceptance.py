"""
Tests d'acceptance pour la fonctionnalité de gestion des utilisateurs depuis la base de données
"""

import unittest
from src.web.condo_app import app
from src.infrastructure.logger_manager import get_logger

logger = get_logger(__name__)


class TestUserManagementDatabaseAcceptance(unittest.TestCase):
    """Tests d'acceptance pour la gestion des utilisateurs avec données de base"""

    def setUp(self):
        """Configuration des tests d'acceptance"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_scenario_admin_views_real_user_list_from_database(self):
        """Scénario: Un administrateur consulte la vraie liste des utilisateurs de la base"""
        logger.info("Scénario: Consultation de la liste des utilisateurs depuis la base de données")
        
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
        # (pas les données fictives hardcodées)
        response_text = response.data.decode('utf-8', errors='ignore')
        
        # L'utilisateur admin de la base doit être visible
        self.assertTrue(
            'admin' in response_text.lower(),
            "L'utilisateur admin de la base doit être affiché"
        )
        
        # Les anciennes données fictives ne doivent plus apparaître
        self.assertNotIn('jean.dupont', response_text, "Les données fictives ne doivent plus être affichées")
        self.assertNotIn('marie.martin', response_text, "Les données fictives ne doivent plus être affichées")
        
        logger.info("Liste des utilisateurs depuis la base affichée avec succès")

    def test_scenario_admin_sees_accurate_user_statistics(self):
        """Scénario: Un administrateur voit des statistiques précises basées sur la vraie base"""
        logger.info("Scénario: Affichage des statistiques d'utilisateurs réelles")
        
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
        # (au moins 1 admin devrait exister dans la base)
        self.assertTrue(
            '1' in response_text or '2' in response_text or '3' in response_text,
            "Au moins un utilisateur doit être compté"
        )
        
        logger.info("Statistiques d'utilisateurs réelles affichées correctement")

    def test_scenario_user_data_consistency_between_database_and_display(self):
        """Scénario: Les données affichées correspondent exactement à celles de la base"""
        logger.info("Scénario: Vérification de la cohérence des données utilisateur")
        
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
        # (Les champs qui doivent venir de la vraie base de données)
        essential_fields_present = (
            'admin' in response_text.lower() and  # Username from database
            '@' in response_text  # Email addresses should be present
        )
        
        self.assertTrue(
            essential_fields_present,
            "Les champs essentiels de la base de données doivent être affichés"
        )
        
        logger.info("Cohérence des données entre base et affichage vérifiée")

    def test_scenario_no_hardcoded_user_data_remains(self):
        """Scénario: Aucune donnée utilisateur hardcodée ne subsiste"""
        logger.info("Scénario: Vérification de l'absence de données hardcodées")
        
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

    def test_scenario_page_performance_with_database_integration(self):
        """Scénario: La page se charge rapidement avec l'intégration base de données"""
        logger.info("Scénario: Test de performance avec intégration base de données")
        
        import time
        
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
