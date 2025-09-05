"""
Tests d'intégration pour SystemConfigService avec SystemConfigRepositorySQLite

Tests vérifiant l'intégration complète entre le service et le repository
avec mocking complet de la base de données SQLite.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from src.application.services.system_config_service import SystemConfigService
from src.adapters.system_config_repository_sqlite import SystemConfigRepositorySQLite

class TestSystemConfigServiceIntegration(unittest.TestCase):
    """Tests d'intégration pour le service et repository de configuration système."""

    def setUp(self):
        """Configuration avant chaque test."""
        # Mock de la configuration avec un fichier temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.mock_config = {
            'database': {
                'path': os.path.join(self.temp_dir, 'test_condos.db')
            }
        }

    def tearDown(self):
        """Nettoyage après chaque test."""
        # Nettoyer le répertoire temporaire
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('src.adapters.system_config_repository_sqlite.sqlite3.connect')
    def test_full_admin_password_workflow_with_mocked_database(self, mock_connect):
        """Test du workflow complet de gestion du mot de passe admin avec base mockée."""
        # ARRANGE - Mock de la connexion SQLite
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        
        # Simuler que la config n'existe pas initialement
        mock_cursor.fetchone.side_effect = [None, None, {'id': 1}]  # get_config, set_config check, final verification
        mock_cursor.rowcount = 1
        
        # Configuration mockée
        with patch.object(SystemConfigRepositorySQLite, '_load_database_config', return_value=self.mock_config):
            repository = SystemConfigRepositorySQLite()
            service = SystemConfigService(repository)
        
        # ACT & ASSERT - État initial : mot de passe non changé
        self.assertFalse(service.is_admin_password_changed())
        
        # ACT - Marquer comme changé
        result = service.mark_admin_password_changed()
        self.assertTrue(result)
        
        # Modifier le mock pour simuler que la valeur existe maintenant
        mock_cursor.fetchone.side_effect = [{'config_value': 'true'}]
        
        # ASSERT - Vérifier que le changement est persisté
        self.assertTrue(service.is_admin_password_changed())

    @patch('src.adapters.system_config_repository_sqlite.sqlite3.connect')
    def test_system_setup_status_integration_with_mocked_database(self, mock_connect):
        """Test d'intégration du statut de setup système avec base mockée."""
        # ARRANGE - Mock de la connexion SQLite
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        
        # Simuler que la config indique mot de passe changé
        mock_cursor.fetchone.return_value = {'config_value': 'true'}
        
        # Configuration mockée
        with patch.object(SystemConfigRepositorySQLite, '_load_database_config', return_value=self.mock_config):
            repository = SystemConfigRepositorySQLite()
            service = SystemConfigService(repository)
        
        # ACT
        setup_status = service.get_system_setup_status()
        
        # ASSERT
        expected_status = {
            'admin_password_changed': True,
            'setup_completed': True
        }
        self.assertEqual(setup_status, expected_status)

    @patch('src.adapters.system_config_repository_sqlite.sqlite3.connect')
    def test_security_validation_integration_with_mocked_database(self, mock_connect):
        """Test d'intégration de la validation de sécurité avec base mockée."""
        # ARRANGE - Mock de la connexion SQLite
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        
        # Simuler un système non sécurisé (mot de passe non changé)
        mock_cursor.fetchone.return_value = None  # Pas de config trouvée
        
        # Configuration mockée
        with patch.object(SystemConfigRepositorySQLite, '_load_database_config', return_value=self.mock_config):
            repository = SystemConfigRepositorySQLite()
            service = SystemConfigService(repository)
        
        # ACT
        security_report = service.validate_system_security()
        
        # ASSERT
        expected_report = {
            'admin_password_changed': False,
            'security_level': 'LOW',
            'recommendations': ['Changer le mot de passe administrateur par défaut immédiatement']
        }
        self.assertEqual(security_report, expected_report)

    @patch('src.adapters.system_config_repository_sqlite.sqlite3.connect')
    def test_configuration_management_integration_with_mocked_database(self, mock_connect):
        """Test d'intégration de la gestion des configurations avec base mockée."""
        # ARRANGE - Mock de la connexion SQLite
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        
        # Simuler le cycle CRUD complet
        # Ordre: set_config check, get_config, delete check
        mock_cursor.fetchone.side_effect = [
            None,  # set_config: vérification que config n'existe pas
            {'config_value': 'test_value'},  # get_config: retourne la valeur
            {'id': 1}  # delete_config: config existe pour delete
        ]
        mock_cursor.rowcount = 1
        
        # Configuration mockée
        with patch.object(SystemConfigRepositorySQLite, '_load_database_config', return_value=self.mock_config):
            repository = SystemConfigRepositorySQLite()
            service = SystemConfigService(repository)
        
        # ACT & ASSERT - CREATE
        result_set = service.set_config_value('test_key', 'test_value', 'string', 'Test description')
        self.assertTrue(result_set)
        
        # ACT & ASSERT - READ
        value = service.get_config_value('test_key')
        self.assertEqual(value, 'test_value')
        
        # ACT & ASSERT - DELETE
        result_delete = service.delete_config('test_key')
        self.assertTrue(result_delete)

    @patch('src.adapters.system_config_repository_sqlite.sqlite3.connect')
    def test_boolean_configuration_integration_with_mocked_database(self, mock_connect):
        """Test d'intégration des configurations booléennes avec base mockée."""
        # ARRANGE - Mock de la connexion SQLite
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        
        # Simuler les réponses pour différentes valeurs booléennes
        mock_cursor.fetchone.side_effect = [
            None,  # set_boolean_config check
            {'config_value': 'true'},  # get_boolean_config
            None,  # set_boolean_config check for false
            {'config_value': 'false'}  # get_boolean_config for false
        ]
        
        # Configuration mockée
        with patch.object(SystemConfigRepositorySQLite, '_load_database_config', return_value=self.mock_config):
            repository = SystemConfigRepositorySQLite()
            service = SystemConfigService(repository)
        
        # ACT & ASSERT - Set True
        result_set_true = service.set_boolean_config('bool_flag', True, 'Boolean test flag')
        self.assertTrue(result_set_true)
        
        # ACT & ASSERT - Get True
        value_true = service.get_boolean_config('bool_flag', False)
        self.assertTrue(value_true)
        
        # ACT & ASSERT - Set False
        result_set_false = service.set_boolean_config('bool_flag', False, 'Boolean test flag')
        self.assertTrue(result_set_false)
        
        # ACT & ASSERT - Get False
        value_false = service.get_boolean_config('bool_flag', True)
        self.assertFalse(value_false)

    @patch('src.adapters.system_config_repository_sqlite.sqlite3.connect')
    def test_reset_admin_password_status_integration_with_mocked_database(self, mock_connect):
        """Test d'intégration de la remise à zéro du statut admin avec base mockée."""
        # ARRANGE - Mock de la connexion SQLite
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        
        # Simuler d'abord un état "changé", puis "non changé" après reset
        mock_cursor.fetchone.side_effect = [
            {'config_value': 'true'},  # État initial
            None,  # Vérification avant reset
            {'config_value': 'false'}  # État après reset
        ]
        
        # Configuration mockée
        with patch.object(SystemConfigRepositorySQLite, '_load_database_config', return_value=self.mock_config):
            repository = SystemConfigRepositorySQLite()
            service = SystemConfigService(repository)
        
        # ACT & ASSERT - État initial changé
        self.assertTrue(service.is_admin_password_changed())
        
        # ACT - Reset
        reset_result = service.reset_admin_password_status()
        self.assertTrue(reset_result)
        
        # ACT & ASSERT - État après reset
        self.assertFalse(service.is_admin_password_changed())

    @patch('src.adapters.system_config_repository_sqlite.sqlite3.connect')
    def test_get_all_system_configs_integration_with_mocked_database(self, mock_connect):
        """Test d'intégration de récupération de toutes les configurations avec base mockée."""
        # ARRANGE - Mock de la connexion SQLite
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        
        # Simuler plusieurs configurations avec tous les champs requis
        mock_configs = [
            {
                'config_key': 'admin_password_changed', 
                'config_value': 'true', 
                'config_type': 'boolean',
                'description': 'Status of admin password change',
                'created_at': '2024-01-01 00:00:00',
                'updated_at': '2024-01-01 00:00:00'
            },
            {
                'config_key': 'app_version', 
                'config_value': '1.0.0', 
                'config_type': 'string',
                'description': 'Application version',
                'created_at': '2024-01-01 00:00:00',
                'updated_at': '2024-01-01 00:00:00'
            },
            {
                'config_key': 'debug_mode', 
                'config_value': 'false', 
                'config_type': 'boolean',
                'description': 'Debug mode status',
                'created_at': '2024-01-01 00:00:00',
                'updated_at': '2024-01-01 00:00:00'
            }
        ]
        mock_cursor.fetchall.return_value = mock_configs
        
        # Configuration mockée
        with patch.object(SystemConfigRepositorySQLite, '_load_database_config', return_value=self.mock_config):
            repository = SystemConfigRepositorySQLite()
            service = SystemConfigService(repository)
        
        # ACT
        all_configs = service.get_all_system_configs()
        
        # ASSERT
        self.assertEqual(len(all_configs), 3)
        self.assertIn('admin_password_changed', all_configs)
        self.assertIn('app_version', all_configs)
        self.assertIn('debug_mode', all_configs)
        
        # Vérifier la structure des données
        admin_config = all_configs['admin_password_changed']
        self.assertEqual(admin_config['config_value'], 'true')
        self.assertEqual(admin_config['config_type'], 'boolean')

    @patch('src.adapters.system_config_repository_sqlite.sqlite3.connect')
    def test_error_handling_integration_with_mocked_database(self, mock_connect):
        """Test d'intégration de la gestion d'erreurs avec base mockée."""
        # ARRANGE - Mock qui lève une exception
        mock_connect.side_effect = Exception("Database connection failed")
        
        # Configuration mockée
        with patch.object(SystemConfigRepositorySQLite, '_load_database_config', return_value=self.mock_config):
            repository = SystemConfigRepositorySQLite()
            service = SystemConfigService(repository)
        
        # ACT & ASSERT - Le service doit gérer les erreurs gracieusement
        self.assertFalse(service.is_admin_password_changed())  # Retourne False par défaut
        self.assertIsNone(service.get_config_value('any_key'))  # Retourne None
        self.assertFalse(service.set_config_value('key', 'value'))  # Retourne False
        self.assertEqual(service.get_all_system_configs(), {})  # Retourne dict vide

    def test_service_initialization_with_default_repository_integration(self):
        """Test d'initialisation du service avec repository par défaut."""
        # ACT & ASSERT - L'initialisation ne doit pas lever d'exception
        with patch('src.application.services.system_config_service.SystemConfigRepositorySQLite') as mock_repo_class:
            mock_repo_instance = Mock()
            mock_repo_class.return_value = mock_repo_instance
            
            service = SystemConfigService()
            
            # Vérifier que le repository par défaut a été créé
            mock_repo_class.assert_called_once()
            self.assertEqual(service.system_config_repository, mock_repo_instance)

if __name__ == '__main__':
    unittest.main()
