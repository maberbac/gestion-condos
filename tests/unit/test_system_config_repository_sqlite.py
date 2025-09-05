"""
Tests unitaires pour SystemConfigRepositorySQLite

Tests utilisant TDD (Red-Green-Refactor) pour le repository de configuration système,
avec mocking complet de la base de données SQLite.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sqlite3
import json
from pathlib import Path

from src.adapters.system_config_repository_sqlite import SystemConfigRepositorySQLite, SystemConfigRepositorySQLiteError

class TestSystemConfigRepositorySQLite(unittest.TestCase):
    """Tests unitaires pour le repository de configuration système."""

    def setUp(self):
        """Configuration avant chaque test."""
        # Mock de la configuration
        self.mock_config = {
            'database': {
                'path': 'test_condos.db'
            }
        }
        
        # Patcher la méthode de chargement de configuration
        with patch.object(SystemConfigRepositorySQLite, '_load_database_config', return_value=self.mock_config):
            self.repository = SystemConfigRepositorySQLite()

    @patch('src.adapters.system_config_repository_sqlite.sqlite3.connect')
    def test_get_config_value_existing_key(self, mock_connect):
        """Test de récupération d'une clé de configuration existante."""
        # ARRANGE
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_row = {'config_value': 'test_value'}
        
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        mock_cursor.fetchone.return_value = mock_row
        
        # ACT
        result = self.repository.get_config_value('test_key')
        
        # ASSERT
        self.assertEqual(result, 'test_value')
        mock_conn.execute.assert_called_once_with(
            "SELECT config_value FROM system_config WHERE config_key = ?",
            ('test_key',)
        )

    @patch('src.adapters.system_config_repository_sqlite.sqlite3.connect')
    def test_get_config_value_non_existing_key(self, mock_connect):
        """Test de récupération d'une clé inexistante."""
        # ARRANGE
        mock_conn = Mock()
        mock_cursor = Mock()
        
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        # ACT
        result = self.repository.get_config_value('non_existing_key')
        
        # ASSERT
        self.assertIsNone(result)

    @patch('src.adapters.system_config_repository_sqlite.sqlite3.connect')
    def test_get_config_value_database_error(self, mock_connect):
        """Test de récupération avec erreur de base de données."""
        # ARRANGE
        mock_connect.side_effect = sqlite3.Error("Database error")
        
        # ACT
        result = self.repository.get_config_value('test_key')
        
        # ASSERT
        self.assertIsNone(result)

    @patch('src.adapters.system_config_repository_sqlite.sqlite3.connect')
    @patch('src.adapters.system_config_repository_sqlite.datetime')
    def test_set_config_value_new_key(self, mock_datetime, mock_connect):
        """Test de définition d'une nouvelle clé de configuration."""
        # ARRANGE
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_datetime.now.return_value.isoformat.return_value = '2025-01-01T00:00:00'
        
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # Clé n'existe pas
        
        # ACT
        result = self.repository.set_config_value('new_key', 'new_value', 'string', 'Description test')
        
        # ASSERT
        self.assertTrue(result)
        # Vérifier que l'INSERT a été appelé (2ème appel à execute)
        self.assertEqual(mock_conn.execute.call_count, 2)

    @patch('src.adapters.system_config_repository_sqlite.sqlite3.connect')
    @patch('src.adapters.system_config_repository_sqlite.datetime')
    def test_set_config_value_existing_key(self, mock_datetime, mock_connect):
        """Test de mise à jour d'une clé existante."""
        # ARRANGE
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_datetime.now.return_value.isoformat.return_value = '2025-01-01T00:00:00'
        
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'id': 1}  # Clé existe
        
        # ACT
        result = self.repository.set_config_value('existing_key', 'updated_value', 'string', 'Description mise à jour')
        
        # ASSERT
        self.assertTrue(result)
        # Vérifier que l'UPDATE a été appelé (2ème appel à execute)
        self.assertEqual(mock_conn.execute.call_count, 2)

    @patch('src.adapters.system_config_repository_sqlite.sqlite3.connect')
    def test_set_config_value_database_error(self, mock_connect):
        """Test de définition avec erreur de base de données."""
        # ARRANGE
        mock_connect.side_effect = sqlite3.Error("Database error")
        
        # ACT
        result = self.repository.set_config_value('test_key', 'test_value')
        
        # ASSERT
        self.assertFalse(result)

    def test_get_boolean_config_true_value(self):
        """Test de récupération d'une configuration booléenne vraie."""
        # ARRANGE
        with patch.object(self.repository, 'get_config_value', return_value='true'):
            # ACT
            result = self.repository.get_boolean_config('test_flag', False)
            
            # ASSERT
            self.assertTrue(result)

    def test_get_boolean_config_false_value(self):
        """Test de récupération d'une configuration booléenne fausse."""
        # ARRANGE
        with patch.object(self.repository, 'get_config_value', return_value='false'):
            # ACT
            result = self.repository.get_boolean_config('test_flag', True)
            
            # ASSERT
            self.assertFalse(result)

    def test_get_boolean_config_non_existing_key(self):
        """Test de récupération d'une configuration booléenne inexistante."""
        # ARRANGE
        with patch.object(self.repository, 'get_config_value', return_value=None):
            # ACT
            result = self.repository.get_boolean_config('non_existing_flag', True)
            
            # ASSERT
            self.assertTrue(result)  # Valeur par défaut

    def test_get_boolean_config_various_true_values(self):
        """Test des différentes valeurs considérées comme True."""
        true_values = ['true', '1', 'yes', 'on', 'True', 'TRUE']
        
        for value in true_values:
            with patch.object(self.repository, 'get_config_value', return_value=value):
                result = self.repository.get_boolean_config('test_flag', False)
                self.assertTrue(result, f"Value '{value}' should be True")

    def test_set_boolean_config_true(self):
        """Test de définition d'une configuration booléenne à True."""
        # ARRANGE
        with patch.object(self.repository, 'set_config_value', return_value=True) as mock_set:
            # ACT
            result = self.repository.set_boolean_config('test_flag', True, 'Description test')
            
            # ASSERT
            self.assertTrue(result)
            mock_set.assert_called_once_with('test_flag', 'true', 'boolean', 'Description test')

    def test_set_boolean_config_false(self):
        """Test de définition d'une configuration booléenne à False."""
        # ARRANGE
        with patch.object(self.repository, 'set_config_value', return_value=True) as mock_set:
            # ACT
            result = self.repository.set_boolean_config('test_flag', False, 'Description test')
            
            # ASSERT
            self.assertTrue(result)
            mock_set.assert_called_once_with('test_flag', 'false', 'boolean', 'Description test')

    @patch('src.adapters.system_config_repository_sqlite.sqlite3.connect')
    def test_delete_config_existing_key(self, mock_connect):
        """Test de suppression d'une configuration existante."""
        # ARRANGE
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        
        # ACT
        result = self.repository.delete_config('existing_key')
        
        # ASSERT
        self.assertTrue(result)
        mock_conn.execute.assert_called_once_with(
            "DELETE FROM system_config WHERE config_key = ?",
            ('existing_key',)
        )

    @patch('src.adapters.system_config_repository_sqlite.sqlite3.connect')
    def test_delete_config_non_existing_key(self, mock_connect):
        """Test de suppression d'une configuration inexistante."""
        # ARRANGE
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.rowcount = 0
        
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        
        # ACT
        result = self.repository.delete_config('non_existing_key')
        
        # ASSERT
        self.assertFalse(result)

    @patch('src.adapters.system_config_repository_sqlite.sqlite3.connect')
    def test_get_all_configs_success(self, mock_connect):
        """Test de récupération de toutes les configurations."""
        # ARRANGE
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_rows = [
            {
                'config_key': 'key1',
                'config_value': 'value1',
                'config_type': 'string',
                'description': 'Description 1',
                'created_at': '2025-01-01',
                'updated_at': '2025-01-01'
            },
            {
                'config_key': 'key2',
                'config_value': 'value2',
                'config_type': 'boolean',
                'description': 'Description 2',
                'created_at': '2025-01-01',
                'updated_at': '2025-01-01'
            }
        ]
        
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        mock_cursor.fetchall.return_value = mock_rows
        
        # ACT
        result = self.repository.get_all_configs()
        
        # ASSERT
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['config_key'], 'key1')
        self.assertEqual(result[1]['config_key'], 'key2')

    @patch('src.adapters.system_config_repository_sqlite.sqlite3.connect')
    def test_get_all_configs_database_error(self, mock_connect):
        """Test de récupération avec erreur de base de données."""
        # ARRANGE
        mock_connect.side_effect = sqlite3.Error("Database error")
        
        # ACT
        result = self.repository.get_all_configs()
        
        # ASSERT
        self.assertEqual(result, [])

    @patch('src.adapters.system_config_repository_sqlite.sqlite3.connect')
    def test_config_exists_true(self, mock_connect):
        """Test de vérification d'existence d'une configuration existante."""
        # ARRANGE
        mock_conn = Mock()
        mock_cursor = Mock()
        
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'id': 1}
        
        # ACT
        result = self.repository.config_exists('existing_key')
        
        # ASSERT
        self.assertTrue(result)

    @patch('src.adapters.system_config_repository_sqlite.sqlite3.connect')
    def test_config_exists_false(self, mock_connect):
        """Test de vérification d'existence d'une configuration inexistante."""
        # ARRANGE
        mock_conn = Mock()
        mock_cursor = Mock()
        
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        # ACT
        result = self.repository.config_exists('non_existing_key')
        
        # ASSERT
        self.assertFalse(result)

    @patch('src.adapters.system_config_repository_sqlite.sqlite3.connect')
    def test_config_exists_database_error(self, mock_connect):
        """Test de vérification d'existence avec erreur de base de données."""
        # ARRANGE
        mock_connect.side_effect = sqlite3.Error("Database error")
        
        # ACT
        result = self.repository.config_exists('test_key')
        
        # ASSERT
        self.assertFalse(result)

    @patch('builtins.open', side_effect=FileNotFoundError())
    def test_load_database_config_file_not_found(self, mock_open):
        """Test de chargement de configuration avec fichier inexistant."""
        # ACT & ASSERT
        with self.assertRaises(SystemConfigRepositorySQLiteError):
            SystemConfigRepositorySQLite("non_existing_config.json")

    @patch('builtins.open')
    @patch('json.load', side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
    def test_load_database_config_invalid_json(self, mock_json_load, mock_open):
        """Test de chargement de configuration avec JSON invalide."""
        # ACT & ASSERT
        with self.assertRaises(SystemConfigRepositorySQLiteError):
            SystemConfigRepositorySQLite("invalid_config.json")

    @patch('src.adapters.system_config_repository_sqlite.Path.mkdir')
    def test_repository_initialization_creates_directory(self, mock_mkdir):
        """Test que l'initialisation crée le répertoire de données."""
        # ARRANGE & ACT
        with patch.object(SystemConfigRepositorySQLite, '_load_database_config', return_value=self.mock_config):
            repository = SystemConfigRepositorySQLite()
        
        # ASSERT
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_get_connection_sets_row_factory(self):
        """Test que _get_connection configure le row_factory."""
        # ARRANGE
        with patch('src.adapters.system_config_repository_sqlite.sqlite3.connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value = mock_conn
            
            # ACT
            conn = self.repository._get_connection()
            
            # ASSERT
            self.assertEqual(mock_conn.row_factory, sqlite3.Row)

if __name__ == '__main__':
    unittest.main()
