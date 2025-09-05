import unittest
import tempfile
import json
import os
from unittest.mock import patch, mock_open
from src.infrastructure.config_manager import ConfigurationManager, DatabaseConfig, AppConfig, LoggingConfig, get_app_config


class TestConfigurationManager(unittest.TestCase):
    
    def setUp(self):
        """Configuration avant chaque test"""
        # Créer un répertoire temporaire pour les tests
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, 'config')
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Créer les schémas nécessaires
        self.schemas_dir = os.path.join(self.config_dir, 'schemas')
        os.makedirs(self.schemas_dir, exist_ok=True)
        
        # Créer TOUS les fichiers obligatoires
        
        # 1. app.json
        self.app_config = {
            "app": {
                "name": "test-app",
                "version": "1.0.0",
                "environment": "development",
                "debug": True,
                "secret_key": "test-key"
            }
        }
        with open(os.path.join(self.config_dir, 'app.json'), 'w') as f:
            json.dump(self.app_config, f)
        
        # 2. database.json  
        self.database_config = {
            "database": {
                "type": "sqlite",
                "path": "data/test.db",
                "migrations_path": "data/migrations"
            }
        }
        with open(os.path.join(self.config_dir, 'database.json'), 'w') as f:
            json.dump(self.database_config, f)
        
        # 3. logging.json
        self.logging_config = {
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "file_path": "logs/test.log"
            }
        }
        with open(os.path.join(self.config_dir, 'logging.json'), 'w') as f:
            json.dump(self.logging_config, f)
        
        # Créer des schémas de validation simples
        schemas = {
            'app_schema.json': {
                "type": "object",
                "properties": {
                    "app": {"type": "object"}
                }
            },
            'database_schema.json': {
                "type": "object", 
                "properties": {
                    "database": {"type": "object"}
                }
            },
            'logging_schema.json': {
                "type": "object",
                "properties": {
                    "logging": {"type": "object"}
                }
            }
        }
        
        for schema_name, schema_content in schemas.items():
            with open(os.path.join(self.schemas_dir, schema_name), 'w') as f:
                json.dump(schema_content, f)
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        # Supprimer les fichiers temporaires
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
    
    def test_configuration_manager_initialization(self):
        """Tester l'initialisation du gestionnaire de configuration"""
        manager = ConfigurationManager(config_dir=self.config_dir)
        self.assertIsNotNone(manager)
        # Comparer les chemins en chaîne pour éviter les problèmes Windows/Path
        self.assertEqual(str(manager.config_dir), self.config_dir)
    
    def test_load_app_config_success(self):
        """Tester le chargement réussi de la configuration d'application"""
        manager = ConfigurationManager(config_dir=self.config_dir)
        app_config = manager.get_app_config()
        
        self.assertIsInstance(app_config, AppConfig)
        self.assertEqual(app_config.name, 'test-app')
        self.assertEqual(app_config.version, '1.0.0')
        self.assertTrue(app_config.debug)
    
    def test_load_database_config(self):
        """Tester le chargement de la configuration de base de données"""
        manager = ConfigurationManager(config_dir=self.config_dir)
        db_config = manager.get_database_config()
        
        self.assertIsInstance(db_config, DatabaseConfig)
        self.assertEqual(db_config.type, 'sqlite')
        self.assertEqual(db_config.path, 'data/test.db')
        self.assertEqual(db_config.migrations_path, 'data/migrations')
    
    def test_config_file_not_found(self):
        """Tester le comportement avec fichier de configuration inexistant"""
        empty_dir = os.path.join(self.temp_dir, 'empty')
        os.makedirs(empty_dir, exist_ok=True)
        
        # Devrait lever une exception ou utiliser des valeurs par défaut
        with self.assertRaises(Exception):
            manager = ConfigurationManager(config_dir=empty_dir)
            manager.get_app_config()
    
    def test_invalid_json_handling(self):
        """Tester la gestion de JSON invalide"""
        invalid_config_file = os.path.join(self.config_dir, 'invalid.json')
        with open(invalid_config_file, 'w') as f:
            f.write('{ invalid json }')
        
        manager = ConfigurationManager(config_dir=self.config_dir)
        
        # Devrait gérer gracieusement le JSON invalide
        with self.assertRaises(Exception):
            manager._load_json_file(invalid_config_file)
    
    def test_config_reload(self):
        """Tester le rechargement de configuration"""
        manager = ConfigurationManager(config_dir=self.config_dir)
        
        # Charger la config initiale
        initial_config = manager.get_app_config()
        self.assertEqual(initial_config.name, 'test-app')
        
        # Modifier le fichier de configuration
        modified_config = self.app_config.copy()
        modified_config['app']['name'] = 'modified-app'
        
        with open(os.path.join(self.config_dir, 'app.json'), 'w') as f:
            json.dump(modified_config, f)
        
        # Forcer le rechargement
        reloaded_config = manager.get_app_config(force_reload=True)
        self.assertEqual(reloaded_config.name, 'modified-app')
    
    def test_config_validation(self):
        """Tester la validation de configuration avec schéma"""
        manager = ConfigurationManager(config_dir=self.config_dir)
        
        # La configuration valide devrait passer
        valid_result = manager.validate_all_configs()
        self.assertTrue(valid_result)
    
    def test_database_config_from_dict(self):
        """Tester la création de DatabaseConfig depuis un dictionnaire"""
        db_config = DatabaseConfig.from_dict(self.database_config)
        
        self.assertEqual(db_config.type, 'sqlite')
        self.assertEqual(db_config.path, 'data/test.db')
        self.assertEqual(db_config.migrations_path, 'data/migrations')
    
    def test_app_config_from_dict(self):
        """Tester la création d'AppConfig depuis un dictionnaire"""
        app_config = AppConfig.from_dict(self.app_config)
        
        self.assertIsInstance(app_config, AppConfig)
        self.assertEqual(app_config.name, 'test-app')
        self.assertEqual(app_config.version, '1.0.0')
        self.assertTrue(app_config.debug)
    
    def test_config_summary(self):
        """Tester la génération de résumé de configuration"""
        manager = ConfigurationManager(config_dir=self.config_dir)
        summary = manager.get_config_summary()
        
        self.assertIsInstance(summary, dict)
        self.assertIn('environment', summary)
        self.assertIn('app', summary)
        self.assertIn('database', summary)


class TestConfigUtilityFunctions(unittest.TestCase):
    """Tests pour les fonctions utilitaires de configuration"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, 'config')
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Configuration de test minimale
        self.test_config = {
            "app": {
                "name": "test-app",
                "version": "1.0.0"
            },
            "database": {
                "type": "sqlite",
                "path": "data/test.db",
                "migrations_path": "data/migrations"
            },
            "web": {
                "host": "localhost",
                "port": 8080,
                "ssl_enabled": False
            }
        }
        
        config_file = os.path.join(self.config_dir, 'app.json')
        with open(config_file, 'w') as f:
            json.dump(self.test_config, f)
    
    def tearDown(self):
        """Nettoyage après chaque test"""
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
    
    @patch('src.infrastructure.config_manager.get_config_manager')
    def test_get_app_config_utility(self, mock_get_manager):
        """Tester la fonction utilitaire get_app_config"""
        # Mocker le manager et sa méthode
        mock_manager = mock_get_manager.return_value
        mock_app_config = AppConfig.from_dict(self.test_config)
        mock_manager.get_app_config.return_value = mock_app_config
        
        # Tester la fonction utilitaire
        result = get_app_config()
        
        self.assertIsInstance(result, AppConfig)
        mock_get_manager.assert_called_once()
        mock_manager.get_app_config.assert_called_once()


if __name__ == '__main__':
    unittest.main()
