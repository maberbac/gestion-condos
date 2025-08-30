"""
Logger Manager - Système de logging centralisé similaire à Log4j pour Java.

Ce module fournit un système de logging unifié et configurable pour toute l'application,
permettant de contrôler les niveaux de logging via configuration JSON.

FONCTIONNALITÉS :
- Configuration centralisée via JSON
- Niveaux de logging standards (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Formatage personnalisable des messages
- Rotation des fichiers de logs
- Loggers spécialisés par module
- Désactivation simple via configuration
"""

import logging
import logging.handlers
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import sys


class LoggerManager:
    """
    Gestionnaire centralisé des loggers pour l'application.
    
    Permet de créer et configurer des loggers de façon cohérente
    selon la configuration JSON définie.
    """
    
    _instance: Optional['LoggerManager'] = None
    _loggers: Dict[str, logging.Logger] = {}
    _config: Dict[str, Any] = {}
    _initialized = False
    
    def __new__(cls) -> 'LoggerManager':
        """Singleton pattern pour avoir une seule instance de LoggerManager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialise le gestionnaire de loggers."""
        if not self._initialized:
            self._load_config()
            self._setup_root_logger()
            self._initialized = True
    
    def _load_config(self) -> None:
        """Charge la configuration de logging depuis le fichier JSON."""
        config_path = Path(__file__).parent.parent.parent / "config" / "logging.json"
        
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                # Configuration par défaut si le fichier n'existe pas
                self._config = self._get_default_config()
                self._save_default_config(config_path)
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la config logging: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Retourne la configuration par défaut du système de logging."""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "global": {
                "enabled": True,
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "date_format": "%Y-%m-%d %H:%M:%S"
            },
            "handlers": {
                "console": {
                    "enabled": True,
                    "level": "INFO",
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                },
                "file": {
                    "enabled": True,
                    "level": "DEBUG",
                    "filename": "logs/application.log",
                    "max_bytes": 10485760,  # 10MB
                    "backup_count": 5,
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
                },
                "error_file": {
                    "enabled": True,
                    "level": "ERROR",
                    "filename": "logs/errors.log",
                    "max_bytes": 5242880,  # 5MB
                    "backup_count": 3,
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
                }
            },
            "loggers": {
                "app": {
                    "level": "INFO",
                    "handlers": ["console", "file"]
                },
                "authentication": {
                    "level": "DEBUG",
                    "handlers": ["console", "file"]
                },
                "database": {
                    "level": "WARNING",
                    "handlers": ["console", "file", "error_file"]
                },
                "web": {
                    "level": "INFO",
                    "handlers": ["console", "file"]
                },
                "tests": {
                    "level": "ERROR",
                    "handlers": ["console"]
                }
            }
        }
    
    def _save_default_config(self, config_path: Path) -> None:
        """Sauvegarde la configuration par défaut dans un fichier JSON."""
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.info(f"Impossible de sauvegarder la config logging par défaut: {e}")
    
    def _setup_root_logger(self) -> None:
        """Configure le logger racine selon la configuration."""
        if not self._config.get("global", {}).get("enabled", True):
            logging.disable(logging.CRITICAL)
            return
        
        # Configuration du logger racine
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
        level_str = self._config.get("global", {}).get("level", "INFO")
        root_logger.setLevel(getattr(logging, level_str))
        
        # Créer les handlers selon la configuration
        self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """Configure tous les handlers définis dans la configuration."""
        handlers_config = self._config.get("handlers", {})
        
        # Handler console
        if handlers_config.get("console", {}).get("enabled", True):
            self._setup_console_handler(handlers_config["console"])
        
        # Handler fichier principal
        if handlers_config.get("file", {}).get("enabled", True):
            self._setup_file_handler(handlers_config["file"])
        
        # Handler fichier d'erreurs
        if handlers_config.get("error_file", {}).get("enabled", True):
            self._setup_error_file_handler(handlers_config["error_file"])
    
    def _setup_console_handler(self, config: Dict[str, Any]) -> None:
        """Configure le handler pour la sortie console."""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, config.get("level", "INFO")))
        
        formatter = logging.Formatter(
            fmt=config.get("format", "%(asctime)s [%(levelname)s] %(name)s: %(message)s"),
            datefmt=self._config.get("global", {}).get("date_format", "%Y-%m-%d %H:%M:%S")
        )
        handler.setFormatter(formatter)
        
        logging.getLogger().addHandler(handler)
    
    def _setup_file_handler(self, config: Dict[str, Any]) -> None:
        """Configure le handler pour le fichier de logs principal."""
        log_file = Path(config.get("filename", "logs/application.log"))
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.handlers.RotatingFileHandler(
            filename=str(log_file),
            maxBytes=config.get("max_bytes", 10485760),
            backupCount=config.get("backup_count", 5),
            encoding='utf-8'
        )
        handler.setLevel(getattr(logging, config.get("level", "DEBUG")))
        
        formatter = logging.Formatter(
            fmt=config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            datefmt=self._config.get("global", {}).get("date_format", "%Y-%m-%d %H:%M:%S")
        )
        handler.setFormatter(formatter)
        
        logging.getLogger().addHandler(handler)
    
    def _setup_error_file_handler(self, config: Dict[str, Any]) -> None:
        """Configure le handler pour le fichier d'erreurs séparé."""
        log_file = Path(config.get("filename", "logs/errors.log"))
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.handlers.RotatingFileHandler(
            filename=str(log_file),
            maxBytes=config.get("max_bytes", 5242880),
            backupCount=config.get("backup_count", 3),
            encoding='utf-8'
        )
        handler.setLevel(getattr(logging, config.get("level", "ERROR")))
        
        formatter = logging.Formatter(
            fmt=config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"),
            datefmt=self._config.get("global", {}).get("date_format", "%Y-%m-%d %H:%M:%S")
        )
        handler.setFormatter(formatter)
        
        logging.getLogger().addHandler(handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Obtient un logger configuré pour un module spécifique.
        
        Args:
            name: Nom du logger (généralement le nom du module)
            
        Returns:
            Logger configuré selon la configuration JSON
        """
        if name in self._loggers:
            return self._loggers[name]
        
        logger = logging.getLogger(name)
        
        # Configuration spécifique du logger selon la config
        logger_config = self._config.get("loggers", {}).get(name, {})
        if logger_config:
            level_str = logger_config.get("level", "INFO")
            logger.setLevel(getattr(logging, level_str))
        
        self._loggers[name] = logger
        return logger
    
    def reload_config(self) -> None:
        """Recharge la configuration de logging depuis le fichier."""
        self._load_config()
        self._setup_root_logger()
        
        # Reconfigurer tous les loggers existants
        for name, logger in self._loggers.items():
            logger_config = self._config.get("loggers", {}).get(name, {})
            if logger_config:
                level_str = logger_config.get("level", "INFO")
                logger.setLevel(getattr(logging, level_str))
    
    def set_level(self, logger_name: str, level: str) -> None:
        """
        Change dynamiquement le niveau d'un logger.
        
        Args:
            logger_name: Nom du logger à modifier
            level: Nouveau niveau (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        if logger_name in self._loggers:
            self._loggers[logger_name].setLevel(getattr(logging, level.upper()))
    
    def disable_logging(self) -> None:
        """Désactive complètement le système de logging."""
        logging.disable(logging.CRITICAL)
    
    def enable_logging(self) -> None:
        """Réactive le système de logging."""
        logging.disable(logging.NOTSET)


# Instance globale du gestionnaire de loggers
logger_manager = LoggerManager()


def get_logger(name: str) -> logging.Logger:
    """
    Fonction utilitaire pour obtenir un logger configuré.
    
    Usage:
        from src.infrastructure.logger_manager import get_logger
        logger = get_logger(__name__)
        logger.info("Message d'information")
    
    Args:
        name: Nom du logger (utiliser __name__ pour le module courant)
        
    Returns:
        Logger configuré
    """
    return logger_manager.get_logger(name)
