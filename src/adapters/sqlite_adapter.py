"""
SQLite Adapter - Implémentation concrète pour la persistance SQLite.

[ARCHITECTURE HEXAGONALE + STANDARDS DE CONFIGURATION]
Cet adapter implémente la persistance des données en utilisant SQLite
selon les standards définis dans copilot-instructions.md :
- Configuration JSON obligatoire (database.json)
- SQLite comme base de données principale
- Migrations avec scripts SQL
- Persistance et gestion des données

NOTE: Version synchrone pour compatibilité initiale.
Version asynchrone disponible après installation d'aiosqlite.
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)


import sqlite3
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import threading


class SQLiteAdapter:
    """
    Adapter SQLite pour la persistance des données de condos.
    
    [STANDARDS OBLIGATOIRES]
    - Configuration via config/database.json
    - Base de données SQLite principale
    - Migrations automatiques
    - Gestion des données persistantes
    
    Architecture Hexagonale:
    - Implémente CondoRepositoryPort du domaine métier
    - Isole la logique SQLite du core business
    - Permet tests unitaires avec base en mémoire
    """
    
    def __init__(self, config_path: str = "config/database.json"):
        """
        Initialise l'adapter avec configuration JSON obligatoire.
        
        Args:
            config_path: Chemin vers fichier de configuration JSON
        """
        # Initialiser le logger en premier
        self.logger = logging.getLogger(__name__)
        
        # Charger la configuration
        self.config = self._load_database_config(config_path)
        self.db_path = Path(self.config['database']['path'])
        self.migrations_dir = Path(self.config['database']['migrations_path'])
        
        # Créer les répertoires s'ils n'existent pas
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
        
        # Thread lock pour opérations concurrentes
        self._db_lock = threading.Lock()
        
        # Initialiser la base de données
        self._initialize_database()
    
    def _load_database_config(self, config_path: str) -> Dict[str, Any]:
        """
        [STANDARD: Configuration JSON obligatoire]
        Charge la configuration depuis fichier JSON avec validation.
        """
        try:
            # Résoudre le chemin de façon robuste par rapport à la racine du projet
            if not os.path.isabs(config_path):
                # Trouver la racine du projet (répertoire contenant src/)
                current_dir = Path(__file__).resolve()
                while current_dir.parent != current_dir:
                    if (current_dir / 'src').is_dir():
                        project_root = current_dir
                        break
                    current_dir = current_dir.parent
                else:
                    # Fallback : utiliser le répertoire courant
                    project_root = Path.cwd()
                
                resolved_config_path = project_root / config_path
            else:
                resolved_config_path = Path(config_path)
            
            with open(resolved_config_path, 'r', encoding='utf-8') as file:
                config = json.load(file)
            
            # Validation basique de la configuration
            required_keys = ['database']
            for key in required_keys:
                if key not in config:
                    raise ValueError(f"Clé manquante dans la configuration: {key}")
            
            # Validation spécifique SQLite
            db_config = config['database']
            if db_config.get('type') != 'sqlite':
                raise ValueError("Type de base de données doit être 'sqlite'")
            
            self.logger.info(f"Configuration base de données chargée: {config_path}")
            return config
            
        except FileNotFoundError:
            raise ValueError(f"Fichier de configuration introuvable: {config_path}")
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            # Si erreur d'encodage, retourner config par défaut
            self.logger.warning(f"Erreur de lecture de config {config_path}: {e}, utilisation config par défaut")
            return {
                "database": {
                    "type": "sqlite",
                    "name": "condos.db",
                    "path": "data/condos.db",
                    "migrations_path": "data/migrations/"
                },
                "connection": {
                    "pool_size": 5,
                    "timeout_seconds": 30,
                    "retry_attempts": 3
                },
                "migrations": {
                    "auto_migrate": False,
                    "validate_schema": True
                },
                "performance": {
                    "enable_wal_mode": True,
                    "cache_size_kb": 2048,
                    "synchronous": "NORMAL"
                }
            }
    
    def _initialize_database(self) -> None:
        """
        [STANDARD: SQLite + Migrations]
        Initialise la base de données et exécute les migrations.
        """
        try:
            # Créer la base de données si elle n'existe pas
            if not self.db_path.exists():
                self.logger.info("Création de la base de données SQLite")
                self._create_database()
            
            # Exécuter les migrations
            self._run_migrations()
            
            # Configurer SQLite selon les standards
            self._configure_sqlite()
            
            self.logger.info("Base de données SQLite initialisée avec succès")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation SQLite: {e}")
            raise RuntimeError(f"Impossible d'initialiser la base: {e}")
    
    def _create_database(self) -> None:
        """Crée le fichier de base de données SQLite vide."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("SELECT 1")  # Test de connexion
            conn.commit()
    
    def _run_migrations(self) -> None:
        """
        [STANDARD: Migrations SQL]
        Exécute les scripts de migration dans l'ordre en utilisant schema_migrations.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Créer la table de suivi des migrations
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        version TEXT PRIMARY KEY,
                        applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Vérifier quelles migrations ont été appliquées
                cursor = conn.execute("SELECT version FROM schema_migrations")
                applied_migrations = {row[0] for row in cursor.fetchall()}
                
                # Obtenir tous les fichiers de migration
                migration_files = sorted(self.migrations_dir.glob("*.sql"))
                
                # Appliquer les nouvelles migrations
                for migration_file in migration_files:
                    migration_name = migration_file.name
                    if migration_name not in applied_migrations:
                        self._execute_migration_with_tracking(migration_file, conn)
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erreur lors des migrations: {e}")
            raise RuntimeError(f"Migrations échouées: {e}")
    
    def _execute_migration_with_tracking(self, migration_file: Path, conn: sqlite3.Connection) -> None:
        """Exécute une migration et l'enregistre dans schema_migrations."""
        try:
            # Lire et exécuter le script SQL
            with open(migration_file, 'r', encoding='utf-8') as file:
                migration_sql = file.read()
            
            # Exécuter la migration
            conn.executescript(migration_sql)
            
            # Marquer comme appliquée
            conn.execute(
                "INSERT INTO schema_migrations (version) VALUES (?)",
                (migration_file.name,)
            )
            
            self.logger.info(f"Migration exécutée: {migration_file.name}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la migration {migration_file.name}: {e}")
            raise RuntimeError(f"Migration échouée: {e}")
    
    def _configure_sqlite(self) -> None:
        """
        [STANDARD: Performance SQLite]
        Configure SQLite selon les bonnes pratiques.
        """
        perf_config = self.config.get('performance', {})
        
        with sqlite3.connect(self.db_path) as conn:
            # Mode WAL pour meilleures performances
            if perf_config.get('enable_wal_mode', True):
                conn.execute("PRAGMA journal_mode = WAL")
            
            # Taille du cache
            cache_size = perf_config.get('cache_size_kb', 2048)
            conn.execute(f"PRAGMA cache_size = -{cache_size}")
            
            # Mode synchrone
            sync_mode = perf_config.get('synchronous', 'NORMAL')
            conn.execute(f"PRAGMA synchronous = {sync_mode}")
            
            # Activer les clés étrangères
            conn.execute("PRAGMA foreign_keys = ON")
            
            conn.commit()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Crée une nouvelle connexion SQLite avec configuration."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Pour accès par nom de colonne
        return conn
