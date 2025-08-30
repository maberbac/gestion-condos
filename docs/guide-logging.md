# Guide d'utilisation du système de logging

## Vue d'ensemble

Ce projet utilise un système de logging centralisé similaire à Log4j de Java, permettant de contrôler facilement tous les messages de debug et de diagnostic de l'application via configuration JSON.

## Configuration rapide

### Voir la configuration actuelle
```bash
python configure_logging.py
```

### Désactiver complètement le logging
```bash
python configure_logging.py --disable
```

### Réactiver le logging
```bash
python configure_logging.py --enable
```

### Changer le niveau global
```bash
python configure_logging.py --level DEBUG    # Très verbeux
python configure_logging.py --level INFO     # Normal (par défaut)
python configure_logging.py --level WARNING  # Seulement avertissements et erreurs
python configure_logging.py --level ERROR    # Seulement les erreurs
```

### Configurer un module spécifique
```bash
python configure_logging.py --level DEBUG --module src.domain.services.authentication_service
python configure_logging.py --level ERROR --module tests
```

### Lister les modules disponibles
```bash
python configure_logging.py --list-modules
```

## Utilisation dans le code

### Import et création du logger
```python
from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)
```

### Utilisation des différents niveaux
```python
# Messages de débogage (niveau DEBUG)
logger.debug("Détails techniques pour le développement")

# Messages informatifs (niveau INFO)
logger.info("Opération terminée avec succès")

# Avertissements (niveau WARNING)
logger.warning("Situation suspecte mais non critique")

# Erreurs (niveau ERROR)
logger.error("Erreur récupérable")

# Erreurs critiques (niveau CRITICAL)
logger.critical("Erreur fatale, arrêt du système")
```

## Niveaux de logging

### DEBUG
- Messages très détaillés pour le développement
- Affiche les valeurs des variables, les étapes d'exécution
- **À utiliser seulement en développement**

### INFO (par défaut)
- Messages informatifs normaux
- Opérations importantes terminées
- État du système

### WARNING
- Situations suspectes mais non critiques
- Utilisation de valeurs par défaut
- Configurations manquantes

### ERROR
- Erreurs récupérables
- Exceptions gérées
- Échecs d'opérations

### CRITICAL
- Erreurs fatales
- Arrêt du système
- Corruption de données

## Configuration par fichier

Le fichier `config/logging.json` permet une configuration avancée :

```json
{
  "global": {
    "enabled": true,
    "level": "INFO"
  },
  "handlers": {
    "console": {
      "enabled": true,
      "level": "INFO"
    },
    "file": {
      "enabled": true,
      "level": "DEBUG",
      "filename": "logs/application.log"
    },
    "error_file": {
      "enabled": true,
      "level": "ERROR",
      "filename": "logs/errors.log"
    }
  },
  "loggers": {
    "src.domain.services.authentication_service": {
      "level": "DEBUG"
    },
    "tests": {
      "level": "ERROR"
    }
  }
}
```

## Fichiers de logs

### `logs/application.log`
- Tous les messages (DEBUG et plus)
- Rotation automatique (10MB, 5 fichiers)
- Format détaillé avec fonction et ligne

### `logs/errors.log`
- Seulement les erreurs (ERROR et CRITICAL)
- Rotation automatique (5MB, 3 fichiers)
- Format détaillé pour le débogage

## Exemples pratiques

### Environnement de développement
```bash
# Activer tous les détails
python configure_logging.py --level DEBUG

# Voir seulement les erreurs des tests
python configure_logging.py --level ERROR --module tests
```

### Environnement de production
```bash
# Niveau normal avec logging actif
python configure_logging.py --level WARNING

# Désactiver complètement si performance critique
python configure_logging.py --disable
```

### Débogage d'un module spécifique
```bash
# Activer le débogage pour l'authentification
python configure_logging.py --level DEBUG --module src.domain.services.authentication_service

# Niveau normal pour le reste
python configure_logging.py --level INFO
```

## Remplacement des print()

Tous les `print()` du projet ont été remplacés par des appels logger appropriés :
- `print("info")` → `logger.info("info")`
- `print("Error:", error)` → `logger.error(f"Erreur: {error}")`
- `print("Warning:", msg)` → `logger.warning(f"Attention: {msg}")`

## Avantages

1. **Contrôle centralisé** : Un seul fichier pour configurer tout le logging
2. **Niveaux flexibles** : Activation/désactivation par module et niveau
3. **Rotation automatique** : Évite l'accumulation de gros fichiers de logs
4. **Performance** : Logging désactivable pour la production
5. **Débogage facilité** : Messages détaillés avec fonction et ligne
6. **Séparation des erreurs** : Fichier dédié pour les erreurs importantes
