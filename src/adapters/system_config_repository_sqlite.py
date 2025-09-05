"""
SystemConfigRepositorySQLite - Repository pour la gestion de la configuration système.

Repository SQLite pour la gestion des paramètres de configuration système
selon les standards définis dans copilot-instructions.md :
- Configuration JSON obligatoire (database.json)
- SQLite comme base de données principale
- Gestion des paramètres de configuration système
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

import sqlite3
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

class SystemConfigRepositorySQLiteError(Exception):
    """Exception spécialisée pour les erreurs du repository SQLite."""
    pass

class SystemConfigRepositorySQLite:
    """
    Repository SQLite pour la persistance des configurations système.

    [STANDARDS OBLIGATOIRES]
    - Configuration via config/database.json
    - Base de données SQLite principale
    - Gestion des paramètres système
    - Isolation de la logique SQLite du domaine métier
    """

    def __init__(self, config_path: str = "config/database.json"):
        """
        Initialise le repository avec la configuration de base de données.

        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config = self._load_database_config(config_path)
        self.db_path = self.config['database']['path']

        # Assurer que le répertoire data existe
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"SystemConfigRepository SQLite initialisé avec DB: {self.db_path}")

    def _load_database_config(self, config_path: str) -> Dict[str, Any]:
        """
        [STANDARD: Configuration JSON obligatoire]
        Charge la configuration de la base de données depuis JSON.
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

            with open(resolved_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.debug(f"Configuration de base de données chargée depuis {resolved_config_path}")
                return config
        except FileNotFoundError:
            logger.error(f"Fichier de configuration introuvable: {config_path}")
            raise SystemConfigRepositorySQLiteError(f"Configuration de base de données introuvable: {config_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de format JSON dans {config_path}: {e}")
            raise SystemConfigRepositorySQLiteError(f"Configuration JSON invalide: {e}")

    def _get_connection(self) -> sqlite3.Connection:
        """Crée une nouvelle connexion SQLite avec configuration."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Pour accès par nom de colonne
        return conn

    def get_config_value(self, config_key: str) -> Optional[str]:
        """
        Récupère la valeur d'une clé de configuration.

        Args:
            config_key: Clé de configuration à récupérer

        Returns:
            Valeur de la configuration ou None si non trouvée
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT config_value FROM system_config WHERE config_key = ?",
                    (config_key,)
                )
                row = cursor.fetchone()
                if row:
                    logger.debug(f"Configuration récupérée: {config_key} = {row['config_value']}")
                    return row['config_value']
                
                logger.debug(f"Configuration non trouvée: {config_key}")
                return None

        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la configuration {config_key}: {e}")
            return None

    def set_config_value(self, config_key: str, config_value: str, config_type: str = 'string', description: str = None) -> bool:
        """
        Définit ou met à jour une valeur de configuration.

        Args:
            config_key: Clé de configuration
            config_value: Valeur de configuration
            config_type: Type de configuration (string, number, boolean, json)
            description: Description optionnelle

        Returns:
            True si la mise à jour réussit, False sinon
        """
        try:
            with self._get_connection() as conn:
                # Vérifier si la clé existe déjà
                cursor = conn.execute(
                    "SELECT id FROM system_config WHERE config_key = ?",
                    (config_key,)
                )
                exists = cursor.fetchone()

                current_time = datetime.now().isoformat()

                if exists:
                    # Mettre à jour
                    conn.execute("""
                        UPDATE system_config 
                        SET config_value = ?, config_type = ?, description = ?, updated_at = ?
                        WHERE config_key = ?
                    """, (config_value, config_type, description, current_time, config_key))
                    logger.info(f"Configuration mise à jour: {config_key} = {config_value}")
                else:
                    # Insérer
                    conn.execute("""
                        INSERT INTO system_config (config_key, config_value, config_type, description, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (config_key, config_value, config_type, description, current_time, current_time))
                    logger.info(f"Configuration créée: {config_key} = {config_value}")

                conn.commit()
                return True

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la configuration {config_key}: {e}")
            return False

    def get_boolean_config(self, config_key: str, default_value: bool = False) -> bool:
        """
        Récupère une configuration booléenne.

        Args:
            config_key: Clé de configuration
            default_value: Valeur par défaut si non trouvée

        Returns:
            Valeur booléenne de la configuration
        """
        value = self.get_config_value(config_key)
        if value is None:
            return default_value
        
        # Convertir string vers boolean
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        
        return bool(value)

    def set_boolean_config(self, config_key: str, config_value: bool, description: str = None) -> bool:
        """
        Définit une configuration booléenne.

        Args:
            config_key: Clé de configuration
            config_value: Valeur booléenne
            description: Description optionnelle

        Returns:
            True si la mise à jour réussit
        """
        return self.set_config_value(config_key, str(config_value).lower(), 'boolean', description)

    def delete_config(self, config_key: str) -> bool:
        """
        Supprime une configuration.

        Args:
            config_key: Clé de configuration à supprimer

        Returns:
            True si la suppression réussit
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("DELETE FROM system_config WHERE config_key = ?", (config_key,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Configuration supprimée: {config_key}")
                    return True
                else:
                    logger.warning(f"Configuration non trouvée pour suppression: {config_key}")
                    return False

        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la configuration {config_key}: {e}")
            return False

    def get_all_configs(self) -> List[Dict[str, Any]]:
        """
        Récupère toutes les configurations système.

        Returns:
            Liste des configurations système
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    SELECT config_key, config_value, config_type, description, created_at, updated_at
                    FROM system_config
                    ORDER BY config_key
                """)
                
                configs = []
                for row in cursor.fetchall():
                    configs.append({
                        'config_key': row['config_key'],
                        'config_value': row['config_value'],
                        'config_type': row['config_type'],
                        'description': row['description'],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    })
                
                logger.debug(f"Récupéré {len(configs)} configurations système")
                return configs

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des configurations: {e}")
            return []

    def config_exists(self, config_key: str) -> bool:
        """
        Vérifie si une configuration existe.

        Args:
            config_key: Clé de configuration à vérifier

        Returns:
            True si la configuration existe
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT 1 FROM system_config WHERE config_key = ?",
                    (config_key,)
                )
                exists = cursor.fetchone() is not None
                logger.debug(f"Configuration {config_key} existe: {exists}")
                return exists

        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'existence de {config_key}: {e}")
            return False
