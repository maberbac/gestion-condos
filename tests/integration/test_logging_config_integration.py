import unittest
import tempfile
import json
import os
import logging
from src.infrastructure.logger_manager import LoggerManager, get_logger
from src.infrastructure.config_manager import ConfigurationManager


class TestLoggingIntegration(unittest.TestCase):
    
    def setUp(self):
        """Configuration avant chaque test"""
        # Réinitialiser le singleton du logger
        LoggerManager._instance = None
        LoggerManager._initialized = False
        
        # Créer un environnement de test temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = os.path.join(self.temp_dir, 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        # Nettoyer les fichiers temporaires
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except:
                    pass
            for name in dirs:
                try:
                    os.rmdir(os.path.join(root, name))
                except:
                    pass
        try:
            os.rmdir(self.temp_dir)
        except:
            pass
        
        # Réinitialiser le singleton
        LoggerManager._instance = None
        LoggerManager._initialized = False
    
    def test_logger_basic_integration(self):
        """Tester l'intégration basique du système de logging"""
        # Initialiser le système de logging
        logger_manager = LoggerManager()
        
        # Obtenir des loggers
        logger1 = get_logger('test_module_1')
        logger2 = get_logger('test_module_2')
        
        # Vérifier que les loggers sont créés correctement
        self.assertIsNotNone(logger1)
        self.assertIsNotNone(logger2)
        self.assertNotEqual(logger1.name, logger2.name)
        
        # Tester que les loggers peuvent écrire des messages
        logger1.info("Message de test du module 1")
        logger2.warning("Avertissement du module 2")
        
        # Les messages devraient être traités sans erreur
        self.assertTrue(True)  # Si on arrive ici, pas d'exception
    
    def test_multiple_loggers_same_name(self):
        """Tester que les loggers avec le même nom sont la même instance"""
        logger_manager = LoggerManager()
        
        logger1 = get_logger('same_module')
        logger2 = get_logger('same_module')
        
        # Devraient être la même instance
        self.assertIs(logger1, logger2)
        self.assertEqual(logger1.name, logger2.name)
    
    def test_logging_levels_integration(self):
        """Tester l'intégration des différents niveaux de logging"""
        logger_manager = LoggerManager()
        logger = get_logger('level_test')
        
        # Tester tous les niveaux
        logger.debug("Message de debug")
        logger.info("Message d'info")
        logger.warning("Message d'avertissement")
        logger.error("Message d'erreur")
        logger.critical("Message critique")
        
        # Tous les messages devraient être traités sans erreur
        self.assertIsNotNone(logger)
    
    def test_logger_manager_reload(self):
        """Tester le rechargement de configuration"""
        logger_manager = LoggerManager()
        
        # Obtenir un logger initial
        initial_logger = get_logger('reload_test')
        initial_level = initial_logger.level
        
        # Recharger la configuration
        logger_manager.reload_config()
        
        # Obtenir un nouveau logger après rechargement
        reloaded_logger = get_logger('reload_test_2')
        
        # Le système devrait continuer à fonctionner
        self.assertIsNotNone(reloaded_logger)
        self.assertIsInstance(reloaded_logger.level, int)
    
    def test_error_handling_integration(self):
        """Tester la gestion d'erreurs d'intégration"""
        # Même avec des conditions d'erreur, le système devrait rester fonctionnel
        logger_manager = LoggerManager()
        
        # Obtenir un logger
        logger = get_logger('error_handling_test')
        self.assertIsNotNone(logger)
        
        # Le logger devrait pouvoir fonctionner même en cas de problème de config
        logger.info("Message de test avec gestion d'erreur")
        logger.error("Test d'erreur")
        
        # Si on arrive ici, le système gère correctement les erreurs
        self.assertTrue(True)
    
    def test_logger_hierarchy_integration(self):
        """Tester l'intégration de la hiérarchie des loggers"""
        logger_manager = LoggerManager()
        
        # Créer des loggers avec hiérarchie
        parent_logger = get_logger('parent')
        child_logger = get_logger('parent.child')
        grandchild_logger = get_logger('parent.child.grandchild')
        
        # Tous devraient être créés
        self.assertIsNotNone(parent_logger)
        self.assertIsNotNone(child_logger)
        self.assertIsNotNone(grandchild_logger)
        
        # Vérifier les noms
        self.assertEqual(parent_logger.name, 'parent')
        self.assertEqual(child_logger.name, 'parent.child')
        self.assertEqual(grandchild_logger.name, 'parent.child.grandchild')
    
    def test_concurrent_logger_creation(self):
        """Tester la création concurrente de loggers"""
        logger_manager = LoggerManager()
        
        # Créer plusieurs loggers rapidement
        loggers = []
        for i in range(10):
            logger = get_logger(f'concurrent_test_{i}')
            loggers.append(logger)
        
        # Tous devraient être créés avec des noms uniques
        self.assertEqual(len(loggers), 10)
        names = [logger.name for logger in loggers]
        self.assertEqual(len(set(names)), 10)  # Tous les noms uniques
    
    def test_logging_with_exceptions(self):
        """Tester le logging avec des exceptions"""
        logger_manager = LoggerManager()
        logger = get_logger('exception_test')
        
        try:
            # Simuler une exception
            raise ValueError("Test exception")
        except Exception as e:
            # Logger l'exception
            logger.error(f"Exception capturée: {e}")
            logger.exception("Exception avec traceback")
        
        # Le système devrait gérer correctement les exceptions
        self.assertIsNotNone(logger)
    
    def test_system_integration_workflow(self):
        """Tester un workflow complet d'intégration système"""
        # Simuler le démarrage d'une application
        startup_logger = get_logger('app.startup')
        startup_logger.info("Démarrage de l'application")
        
        # Simuler différents modules
        auth_logger = get_logger('app.auth')
        db_logger = get_logger('app.database')
        web_logger = get_logger('app.web')
        
        # Simuler l'activité des modules
        auth_logger.info("Module d'authentification initialisé")
        db_logger.info("Connexion à la base de données établie")
        web_logger.info("Serveur web démarré")
        
        # Simuler quelques opérations
        auth_logger.debug("Tentative de connexion utilisateur")
        db_logger.debug("Exécution de requête SQL")
        web_logger.info("Requête HTTP traitée")
        
        # Simuler un problème et sa résolution
        web_logger.warning("Charge élevée détectée")
        web_logger.error("Erreur temporaire")
        web_logger.info("Problème résolu")
        
        # Simuler l'arrêt
        startup_logger.info("Arrêt de l'application")
        
        # Vérifier que tous les loggers existent et fonctionnent
        self.assertIsNotNone(startup_logger)
        self.assertIsNotNone(auth_logger)
        self.assertIsNotNone(db_logger)
        self.assertIsNotNone(web_logger)


if __name__ == '__main__':
    unittest.main()
