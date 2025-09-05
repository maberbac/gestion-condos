"""
Configuration Manager - Utilitaire pour charger et valider les configurations JSON.

[STANDARDS OBLIGATOIRES]
Ce module gère toutes les configurations selon les standards définis :
- Configuration JSON obligatoire avec validation de schémas
- Centralisation dans config/ avec hiérarchie structurée
- Validation automatique avec schémas JSON
- Support de configuration par environnement
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

import json
import jsonschema
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from dataclasses import dataclass
from enum import Enum

class ConfigurationError(Exception):
    """Exception levée pour les erreurs de configuration."""
    pass

class Environment(Enum):
    """Environnements supportés pour la configuration."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

@dataclass
class DatabaseConfig:
    """Configuration spécifique à la base de données."""
    type: str
    path: str
    migrations_path: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatabaseConfig':
        db_config = data.get('database', {})
        return cls(
            type=db_config.get('type', 'sqlite'),
            path=db_config.get('path', 'data/condos.db'),
            migrations_path=db_config.get('migrations_path', 'data/migrations')
        )

@dataclass
class AppConfig:
    """Configuration générale de l'application."""
    name: str
    version: str
    environment: Environment
    debug: bool
    secret_key: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        app_config = data.get('app', {})
        return cls(
            name=app_config.get('name', 'Gestion Condos'),
            version=app_config.get('version', '1.0.0'),
            environment=Environment(app_config.get('environment', 'development')),
            debug=app_config.get('debug', True),
            secret_key=app_config.get('secret_key', 'dev-key-change-in-production')
        )

@dataclass
class LoggingConfig:
    """Configuration du système de logs."""
    level: str
    format: str
    file_path: Optional[str]
    max_size_mb: int
    backup_count: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LoggingConfig':
        logging_config = data.get('logging', {})
        return cls(
            level=logging_config.get('level', 'INFO'),
            format=logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            file_path=logging_config.get('file_path'),
            max_size_mb=logging_config.get('max_size_mb', 10),
            backup_count=logging_config.get('backup_count', 5)
        )

class ConfigurationManager:
    """
    Gestionnaire central des configurations JSON.

    [STANDARDS DE CONFIGURATION]
    - Charge toutes les configurations depuis config/
    - Valide avec schémas JSON obligatoires
    - Support multi-environnement
    - Cache les configurations en mémoire
    - Rechargement à chaud en mode développement
    """

    def __init__(self, config_dir: str = "config", environment: str = None):
        """
        Initialise le gestionnaire de configuration.

        Args:
            config_dir: Répertoire contenant les fichiers de configuration
            environment: Environnement actuel (development/testing/production)
        """
        self.config_dir = Path(config_dir)
        self.schemas_dir = self.config_dir / "schemas"
        self.environment = Environment(environment or "development")

        # Cache des configurations
        self._app_config: Optional[AppConfig] = None
        self._database_config: Optional[DatabaseConfig] = None
        self._logging_config: Optional[LoggingConfig] = None
        self._raw_configs: Dict[str, Dict[str, Any]] = {}

        self.logger = logging.getLogger(__name__)

        # Vérifier que les répertoires existent
        self._validate_directory_structure()

    def _validate_directory_structure(self) -> None:
        """Valide que la structure de configuration est présente."""
        if not self.config_dir.exists():
            raise ConfigurationError(f"Répertoire de configuration introuvable: {self.config_dir}")

        if not self.schemas_dir.exists():
            raise ConfigurationError(f"Répertoire de schémas introuvable: {self.schemas_dir}")

        # Vérifier les fichiers obligatoires
        required_files = ['app.json', 'database.json', 'logging.json']
        for filename in required_files:
            config_file = self.config_dir / filename
            if not config_file.exists():
                raise ConfigurationError(f"Fichier de configuration obligatoire manquant: {filename}")

    def _load_json_file(self, filepath: Path) -> Dict[str, Any]:
        """Charge un fichier JSON avec gestion d'erreurs."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
            self.logger.debug(f"Configuration chargée: {filepath}")
            return data
        except FileNotFoundError:
            raise ConfigurationError(f"Fichier de configuration introuvable: {filepath}")
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"JSON invalide dans {filepath}: {e}")

    def _load_schema(self, schema_name: str) -> Dict[str, Any]:
        """Charge un schéma de validation JSON."""
        schema_path = self.schemas_dir / f"{schema_name}_schema.json"
        if not schema_path.exists():
            self.logger.warning(f"Schéma de validation introuvable: {schema_path}")
            return {}

        return self._load_json_file(schema_path)

    def _validate_config(self, config_data: Dict[str, Any], schema_name: str) -> None:
        """
        [STANDARD: Validation JSON obligatoire]
        Valide une configuration contre son schéma JSON.
        """
        schema = self._load_schema(schema_name)
        if not schema:
            self.logger.warning(f"Validation ignorée pour {schema_name} (schéma manquant)")
            return

        try:
            jsonschema.validate(config_data, schema)
            self.logger.debug(f"Configuration {schema_name} validée avec succès")
        except jsonschema.ValidationError as e:
            error_msg = f"Configuration {schema_name} invalide: {e.message}"
            self.logger.error(error_msg)
            raise ConfigurationError(error_msg)
        except jsonschema.SchemaError as e:
            error_msg = f"Schéma {schema_name} invalide: {e.message}"
            self.logger.error(error_msg)
            raise ConfigurationError(error_msg)

    def _load_and_validate_config(self, filename: str) -> Dict[str, Any]:
        """Charge et valide un fichier de configuration."""
        config_path = self.config_dir / filename
        config_data = self._load_json_file(config_path)

        # Extraire le nom du schéma (ex: app.json -> app)
        schema_name = filename.replace('.json', '')
        self._validate_config(config_data, schema_name)

        # Appliquer les overrides d'environnement si présents
        config_data = self._apply_environment_overrides(config_data, schema_name)

        return config_data

    def _apply_environment_overrides(self, config_data: Dict[str, Any], config_name: str) -> Dict[str, Any]:
        """
        Applique les overrides spécifiques à l'environnement.

        Cherche des fichiers comme app.development.json, app.testing.json, etc.
        """
        env_filename = f"{config_name}.{self.environment.value}.json"
        env_file_path = self.config_dir / env_filename

        if env_file_path.exists():
            env_overrides = self._load_json_file(env_file_path)
            # Fusion profonde des configurations
            config_data = self._deep_merge_configs(config_data, env_overrides)
            self.logger.info(f"Overrides d'environnement appliqués: {env_filename}")

        return config_data

    def _deep_merge_configs(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """Fusion profonde de deux dictionnaires de configuration."""
        result = base_config.copy()

        for key, value in override_config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    # ==================== API Publique ====================

    def get_app_config(self, force_reload: bool = False) -> AppConfig:
        """
        Récupère la configuration de l'application.

        Args:
            force_reload: Force le rechargement depuis le fichier
        """
        if self._app_config is None or force_reload:
            config_data = self._load_and_validate_config('app.json')
            self._app_config = AppConfig.from_dict(config_data)
            self._raw_configs['app'] = config_data

        return self._app_config

    def get_database_config(self, force_reload: bool = False) -> DatabaseConfig:
        """
        Récupère la configuration de la base de données.

        Args:
            force_reload: Force le rechargement depuis le fichier
        """
        if self._database_config is None or force_reload:
            config_data = self._load_and_validate_config('database.json')
            self._database_config = DatabaseConfig.from_dict(config_data)
            self._raw_configs['database'] = config_data

        return self._database_config

    def get_logging_config(self, force_reload: bool = False) -> LoggingConfig:
        """
        Récupère la configuration du système de logs.

        Args:
            force_reload: Force le rechargement depuis le fichier
        """
        if self._logging_config is None or force_reload:
            config_data = self._load_and_validate_config('logging.json')
            self._logging_config = LoggingConfig.from_dict(config_data)
            self._raw_configs['logging'] = config_data

        return self._logging_config

    def get_raw_config(self, config_name: str, force_reload: bool = False) -> Dict[str, Any]:
        """
        Récupère la configuration brute (Dict) pour accès direct.

        Args:
            config_name: Nom du fichier de config (sans .json)
            force_reload: Force le rechargement depuis le fichier
        """
        if config_name not in self._raw_configs or force_reload:
            config_data = self._load_and_validate_config(f'{config_name}.json')
            self._raw_configs[config_name] = config_data

        return self._raw_configs[config_name]

    def reload_all_configs(self) -> None:
        """Recharge toutes les configurations depuis les fichiers."""
        self.logger.info("Rechargement de toutes les configurations")

        self._app_config = None
        self._database_config = None
        self._logging_config = None
        self._raw_configs.clear()

        # Pré-charger les configurations principales
        self.get_app_config()
        self.get_database_config()
        self.get_logging_config()

    def validate_all_configs(self) -> bool:
        """
        Valide toutes les configurations contre leurs schémas.

        Returns:
            True si toutes les validations passent, False sinon
        """
        try:
            # Charger et valider toutes les configurations obligatoires
            self.get_app_config(force_reload=True)
            self.get_database_config(force_reload=True)
            self.get_logging_config(force_reload=True)

            self.logger.info("Toutes les configurations sont valides")
            return True

        except ConfigurationError as e:
            self.logger.error(f"Validation des configurations échouée: {e}")
            return False

    def get_config_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de toutes les configurations."""
        app_config = self.get_app_config()
        db_config = self.get_database_config()
        log_config = self.get_logging_config()

        return {
            'environment': self.environment.value,
            'app': {
                'name': app_config.name,
                'version': app_config.version,
                'debug': app_config.debug
            },
            'database': {
                'type': db_config.type,
                'path': db_config.path
            },
            'logging': {
                'level': log_config.level,
                'file_path': log_config.file_path
            }
        }

# Instance globale singleton
_config_manager: Optional[ConfigurationManager] = None

def get_config_manager(config_dir: str = "config", environment: str = None) -> ConfigurationManager:
    """
    Récupère l'instance globale du gestionnaire de configuration.

    Args:
        config_dir: Répertoire de configuration (utilisé seulement à la première création)
        environment: Environnement (utilisé seulement à la première création)
    """
    global _config_manager

    if _config_manager is None:
        _config_manager = ConfigurationManager(config_dir, environment)

    return _config_manager

# Fonctions utilitaires pour accès direct
def get_app_config() -> AppConfig:
    """Raccourci pour récupérer la configuration de l'application."""
    return get_config_manager().get_app_config()

def get_database_config() -> DatabaseConfig:
    """Raccourci pour récupérer la configuration de la base de données."""
    return get_config_manager().get_database_config()

def get_logging_config() -> LoggingConfig:
    """Raccourci pour récupérer la configuration du système de logs."""
    return get_config_manager().get_logging_config()

# Exemple d'utilisation
if __name__ == "__main__":
    import logging

    # Configuration basique du logging pour le test
    logging.basicConfig(level=logging.INFO)

    try:
        # Créer le gestionnaire de configuration
        config_manager = ConfigurationManager()

        # Valider toutes les configurations
        if config_manager.validate_all_configs():
            logger.info("Toutes les configurations sont valides")

            # Afficher le résumé
            summary = config_manager.get_config_summary()
            logger.info(f"Résumé de configuration: {json.dumps(summary, indent=2)}")

            # Exemples d'accès aux configurations
            app_config = config_manager.get_app_config()
            logger.info(f"Application: {app_config.name} v{app_config.version}")

            db_config = config_manager.get_database_config()
            logger.info(f"Base de données: {db_config.type} à {db_config.path}")

        else:
            logger.error("Erreurs de validation détectées")

    except ConfigurationError as e:
        logger.error(f"Erreur de configuration: {e}")
