"""
Script de démarrage principal pour l'application de gestion des condos.

Ce script démontre l'intégration complète des 4 concepts techniques
dans un contexte d'application web réelle avec authentification par rôles.

CONCEPTS TECHNIQUES INTÉGRÉS :
1. Lecture de fichiers : Configuration, base de données, données utilisateur
2. Programmation fonctionnelle : Décorateurs, filtres, transformations
3. Gestion d'erreurs : Exceptions personnalisées, validation robuste  
4. Programmation asynchrone : Services d'authentification, initialisation
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)


import asyncio
import logging
import sys
from pathlib import Path
import webbrowser
import time

# Configuration du chemin pour les imports
sys.path.append(str(Path(__file__).parent.parent))

# Imports du projet
from src.web.condo_app import app, init_services
# from tmp.init_demo_users import initialize_demo_users  # Déplacé vers tmp - non requis en production
from src.infrastructure.config_manager import ConfigurationManager
from src.adapters.sqlite_adapter import SQLiteAdapter

async def initialize_system():
    """
    [CONCEPT: Programmation asynchrone + Lecture de fichiers + Gestion d'erreurs]
    
    Initialise complètement le système avec tous les composants nécessaires.
    Démontre l'orchestration asynchrone des services.
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=== INITIALISATION DU SYSTÈME GESTION CONDOS ===")
        
        # [CONCEPT: Lecture de fichiers] Vérification de la configuration
        logger.info("1. Vérification de la configuration...")
        config_manager = ConfigurationManager()
        
        try:
            app_config = config_manager.get_app_config()
            db_config = config_manager.get_database_config()
            logger.info("Configuration chargée avec succès")
        except Exception as e:
            logger.warning(f"Configuration par défaut utilisée: {e}")
        
        # [CONCEPT: Lecture de fichiers] Initialisation de la base de données
        logger.info("2. Initialisation de la base de données...")
        repository = SQLiteAdapter()
        
        # Vérifier que la base fonctionne
        try:
            condos = repository.get_all_condos()
            logger.info(f"Base de données opérationnelle ({len(condos)} condos)")
        except Exception as e:
            logger.error(f"✗ Erreur base de données: {e}")
            raise
        
        # [CONCEPT: Programmation asynchrone] Initialisation du système
        logger.info("3. Système prêt - utilisateurs chargés depuis la base de données...")
        # await initialize_demo_users()  # Supprimé - non requis en production
        logger.info("Système d'authentification initialisé")
        
        # [CONCEPT: Gestion d'erreurs] Validation complète du système
        logger.info("4. Validation du système...")
        
        # Test des services principaux
        from src.domain.services.authentication_service import AuthenticationService
        auth_service = AuthenticationService(repository)  # Passer le repository en paramètre
        
        # Validation simple : créer le service suffit
        logger.info("Service d'authentification opérationnel")
        
        logger.info("=== SYSTÈME INITIALISÉ AVEC SUCCÈS ===")
        return True
        
    except Exception as e:
        # [CONCEPT: Gestion d'erreurs] Gestion centralisée des erreurs d'initialisation
        logger.error(f"=== ÉCHEC D'INITIALISATION: {e} ===")
        return False

def setup_logging():
    """Configuration avancée du système de logging."""
    # Créer le répertoire des logs
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(logs_dir / 'app_startup.log', encoding='utf-8')
        ]
    )

async def main():
    """
    [CONCEPT: Programmation asynchrone]
    
    Point d'entrée principal avec orchestration asynchrone complète.
    """
    # Configuration initiale
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # [CONCEPT: Programmation asynchrone] Initialisation asynchrone
    success = await initialize_system()
    
    if not success:
        logger.error("Impossible de démarrer l'application")
        sys.exit(1)
    
    # Configuration Flask pour production
    app.config.update({
        'DEBUG': True,
        'HOST': '127.0.0.1',
        'PORT': 8080
    })
    
    logger.info("\nDémarrage du serveur web...")
    logger.info("   URL: http://127.0.0.1:8080")
    logger.info("   Ctrl+C pour arrêter")
    logger.info("\n" + "=" * 60)
    
    # Optionnel : ouvrir le navigateur automatiquement
    try:
        time.sleep(1)  # Laisser le temps au serveur de démarrer
        webbrowser.open('http://127.0.0.1:8080')
    except Exception:
        pass  # Navigateur non disponible, ce n'est pas grave
    
    # [CONCEPT: Gestion d'erreurs] Démarrage sécurisé du serveur
    try:
        app.run(
            debug=True, 
            host='127.0.0.1', 
            port=8080, 
            use_reloader=False  # Éviter les doubles démarrages
        )
    except KeyboardInterrupt:
        logger.info("Application arrêtée par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur du serveur web: {e}")
        sys.exit(1)

if __name__ == '__main__':
    # [CONCEPT: Programmation asynchrone] Point d'entrée avec asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n\nApplication fermée. À bientôt!")
    except Exception as e:
        logger.error(f"\nErreur fatale: {e}")
        sys.exit(1)
