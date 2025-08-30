#!/usr/bin/env python3
"""
Configuration du système de logging.

Ce script permet de configurer facilement les niveaux de logging 
pour différents modules de l'application sans modifier le code.

Usage:
    python configure_logging.py [--level LEVEL] [--module MODULE] [--disable] [--enable]
"""

import json
import argparse
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Ajouter le répertoire racine au path pour imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)


def load_logging_config() -> Dict[str, Any]:
    """Charge la configuration de logging actuelle."""
    config_path = Path("config/logging.json")
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        logger.error("Fichier de configuration logging.json introuvable")
        return {}


def save_logging_config(config: Dict[str, Any]) -> None:
    """Sauvegarde la configuration de logging."""
    config_path = Path("config/logging.json")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Configuration sauvegardée dans {config_path}")


def show_current_config() -> None:
    """Affiche la configuration actuelle."""
    config = load_logging_config()
    
    logger.info("=== CONFIGURATION ACTUELLE DU LOGGING ===")
    logger.info("")
    
    # Configuration globale
    global_config = config.get("global", {})
    logger.info(f"Statut global: {'ACTIVÉ' if global_config.get('enabled', True) else 'DÉSACTIVÉ'}")
    logger.info(f"Niveau global: {global_config.get('level', 'INFO')}")
    logger.info("")
    
    # Handlers
    logger.info("Handlers:")
    handlers = config.get("handlers", {})
    for handler_name, handler_config in handlers.items():
        status = "ACTIVÉ" if handler_config.get("enabled", True) else "DÉSACTIVÉ"
        level = handler_config.get("level", "INFO")
        logger.info(f"  {handler_name}: {status} (niveau: {level})")
    logger.info("")
    
    # Loggers par module
    logger.info("Loggers par module:")
    loggers = config.get("loggers", {})
    for logger_name, logger_config in loggers.items():
        level = logger_config.get("level", "INFO")
        handlers_list = ", ".join(logger_config.get("handlers", []))
        logger.info(f"  {logger_name}: {level} -> [{handlers_list}]")


def set_global_level(level: str) -> None:
    """Définit le niveau de logging global."""
    config = load_logging_config()
    
    if "global" not in config:
        config["global"] = {}
    
    config["global"]["level"] = level.upper()
    save_logging_config(config)
    logger.info(f"Niveau global défini à: {level.upper()}")


def set_module_level(module: str, level: str) -> None:
    """Définit le niveau de logging pour un module spécifique."""
    config = load_logging_config()
    
    if "loggers" not in config:
        config["loggers"] = {}
    
    if module not in config["loggers"]:
        config["loggers"][module] = {
            "level": level.upper(),
            "handlers": ["console", "file"]
        }
    else:
        config["loggers"][module]["level"] = level.upper()
    
    save_logging_config(config)
    logger.info(f"Niveau pour le module '{module}' défini à: {level.upper()}")


def disable_logging() -> None:
    """Désactive complètement le logging."""
    config = load_logging_config()
    
    if "global" not in config:
        config["global"] = {}
    
    config["global"]["enabled"] = False
    save_logging_config(config)
    logger.info("Logging DÉSACTIVÉ globalement")


def enable_logging() -> None:
    """Active le logging."""
    config = load_logging_config()
    
    if "global" not in config:
        config["global"] = {}
    
    config["global"]["enabled"] = True
    save_logging_config(config)
    logger.info("Logging ACTIVÉ globalement")


def list_available_modules() -> None:
    """Liste les modules disponibles pour la configuration."""
    config = load_logging_config()
    
    logger.info("=== MODULES DISPONIBLES ===")
    logger.info("")
    logger.info("Modules déjà configurés:")
    loggers = config.get("loggers", {})
    for module_name in sorted(loggers.keys()):
        level = loggers[module_name].get("level", "INFO")
        logger.info(f"  {module_name} (niveau: {level})")
    
    logger.info("")
    logger.info("Modules suggérés pour la configuration:")
    suggested_modules = [
        "src.domain.services.authentication_service",
        "src.adapters.sqlite_adapter",
        "src.web.condo_app",
        "src.infrastructure.config_manager",
        "run_app",
        "tests"
    ]
    
    for module in suggested_modules:
        if module not in loggers:
            logger.info(f"  {module}")


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(description='Configuration du système de logging')
    parser.add_argument('--level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                       help='Définit le niveau de logging global')
    parser.add_argument('--module', type=str,
                       help='Module spécifique à configurer (utilisé avec --level)')
    parser.add_argument('--disable', action='store_true',
                       help='Désactive complètement le logging')
    parser.add_argument('--enable', action='store_true',
                       help='Active le logging')
    parser.add_argument('--show', action='store_true',
                       help='Affiche la configuration actuelle')
    parser.add_argument('--list-modules', action='store_true',
                       help='Liste les modules disponibles')
    
    args = parser.parse_args()
    
    # Si aucun argument, afficher la configuration actuelle
    if not any(vars(args).values()):
        show_current_config()
        return
    
    # Traitement des arguments
    if args.show:
        show_current_config()
    elif args.list_modules:
        list_available_modules()
    elif args.disable:
        disable_logging()
    elif args.enable:
        enable_logging()
    elif args.level:
        if args.module:
            set_module_level(args.module, args.level)
        else:
            set_global_level(args.level)
    else:
        logger.info("Utilisation: configure_logging.py --help pour voir les options")


if __name__ == '__main__':
    main()
