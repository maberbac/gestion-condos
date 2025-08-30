# Standards de Documentation pour Agents IA

## Directives de Documentation du Code

### Commentaires Intégrés
Suivre ces principes pour tous les langages de programmation :

#### Python
```python
def traiter_donnees_utilisateur(fichier_utilisateur: str) -> dict:
    """
    Traite les informations d'utilisateur à partir d'un fichier et valide les champs requis.
    
    Args:
        fichier_utilisateur: Chemin vers le fichier JSON/CSV contenant les données d'utilisateur
        
    Returns:
        dict: Données d'utilisateur traitées avec statut de validation
        
    Raises:
        FileNotFoundError: Quand le fichier d'utilisateur n'existe pas
        ValidationError: Quand les champs requis de l'utilisateur sont manquants
    """
    # Charger les données d'utilisateur en utilisant une approche fonctionnelle pour démontrer le concept
    donnees = charger_et_valider(fichier_utilisateur)
    
    # Appliquer les règles métier pour la validation d'utilisateur
    # Ceci démontre le concept de gestion d'exceptions
    try:
        donnees_validees = appliquer_regles_validation(donnees)
        logger.info(f"Utilisateur validé avec succès: {donnees['username']}")
        return donnees_validees
    except ValidationError as e:
        logger.error(f"Échec de validation pour l'utilisateur: {e}")
        raise
```

#### Architecture Documentation Standards
```python
class UserService:
    """
    Service d'orchestration pour la gestion des utilisateurs.
    
    [ARCHITECTURE HEXAGONALE]
    - Couche Application Service
    - Orchestration entre Domain et Infrastructure
    - Interface entre Web et Business Logic
    
    [CONCEPTS TECHNIQUES DÉMONTRÉS]
    - Programmation asynchrone avec async/await
    - Gestion d'erreurs avec exceptions personnalisées
    - Programmation fonctionnelle dans le traitement des données
    """
    
    def __init__(self, user_repository: UserRepositoryPort):
        """
        Initialise le service avec injection de dépendance.
        
        Args:
            user_repository: Port du repository d'utilisateurs (interface)
        """
        self.user_repository = user_repository
        logger.info("UserService initialisé avec repository injecté")
```

### Standards de Logging Obligatoires
```python
# OBLIGATOIRE : Import du logger centralisé
from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

# INTERDICTION ABSOLUE des print()
# logger.debug() : Variables, étapes d'exécution détaillées
# logger.info() : Opérations terminées, état du système
# logger.warning() : Situations suspectes, avertissements
# logger.error() : Erreurs récupérables, exceptions gérées
# logger.critical() : Erreurs fatales, arrêt du système

# Exemple d'utilisation correcte
def sauvegarder_utilisateur(user_data):
    """Sauvegarde un utilisateur avec logging approprié."""
    try:
        logger.debug(f"Début sauvegarde utilisateur: {user_data.get('username')}")
        resultat = repository.save(user_data)
        logger.info(f"Utilisateur sauvegardé avec succès: {user_data['username']}")
        return resultat
    except ValidationError as e:
        logger.error(f"Erreur de validation lors de la sauvegarde: {e}")
        raise
    except Exception as e:
        logger.critical(f"Erreur critique lors de la sauvegarde: {e}")
        raise
```

## Directives pour Gestion des Migrations

### Documentation des Migrations Centralisées
```python
class SQLiteAdapter(CondoRepositoryPort):
    """
    Adapter SQLite centralisé pour la persistance des données.
    
    [CENTRALISATION OBLIGATOIRE DES MIGRATIONS]
    - SOURCE UNIQUE DE VÉRITÉ pour toutes les migrations
    - Utilise la table schema_migrations pour le tracking
    - Empêche la corruption des données lors des redémarrages
    - Aucun autre adapter ne doit contenir de logique de migration
    
    [PROTECTION ANTI-CORRUPTION]
    - Vérification avant exécution de chaque migration
    - Idempotence garantie : chaque migration ne s'exécute qu'une fois
    - Préservation des données existantes
    """
    
    def _run_migrations(self) -> None:
        """
        Exécute TOUTES les migrations du système de façon centralisée.
        
        RÈGLE CARDINALE : Seul point d'entrée pour les migrations.
        Utilise schema_migrations pour éviter les duplications.
        """
        
    def _execute_migration_with_tracking(self, migration_file: Path, conn: sqlite3.Connection) -> None:
        """
        Exécute une migration avec tracking pour éviter les duplications.
        
        MÉCANISME DE PROTECTION :
        1. Vérifie si migration déjà exécutée via schema_migrations
        2. Exécute la migration si nécessaire
        3. Marque la migration comme exécutée
        """
```

## Documentation des Tests avec Standards TDD

### Documentation Tests Unitaires
```python
class TestUserService(unittest.TestCase):
    """
    Tests unitaires pour UserService.
    
    [MÉTHODOLOGIE TDD]
    - Tests écrits AVANT le code (Red-Green-Refactor)
    - Repository complètement mocké
    - Aucune interaction base de données réelle
    - Tests indépendants dans n'importe quel ordre
    """
    
    @patch('src.adapters.user_repository_sqlite.UserRepositorySQLite')
    def test_get_user_by_username_found(self, mock_repository):
        """
        Test récupération d'un utilisateur existant par nom d'utilisateur.
        
        [MOCKING OBLIGATOIRE]
        - Repository complètement mocké avec @patch
        - Aucune connexion SQLite réelle
        - Données contrôlées via Mock
        """
        # Given - Données de test contrôlées
        expected_user = User(username="testuser", email="test@example.com")
        mock_repository.get_by_username.return_value = expected_user
        
        # When - Exécution de la méthode testée
        service = UserService(mock_repository)
        result = service.get_user_by_username("testuser")
        
        # Then - Validation des résultats
        self.assertEqual(result.username, "testuser")
        mock_repository.get_by_username.assert_called_once_with("testuser")
```

### Documentation Tests d'Intégration
```python
class TestAuthenticationIntegration(unittest.TestCase):
    """
    Tests d'intégration pour l'authentification.
    
    [INTÉGRATION MOCKÉE]
    - Services mockés pour isolation complète
    - Validation des interactions entre composants
    - Aucune base de données réelle utilisée
    """
    
    @patch('src.adapters.user_repository_sqlite.UserRepositorySQLite')
    @patch('src.application.services.user_service.UserService')
    def test_authentication_workflow(self, mock_service, mock_repository):
        """
        Test du workflow complet d'authentification.
        
        [ISOLATION TOTALE]
        - Tous les composants mockés
        - Workflow testé sans effets de bord
        - Validation des appels entre composants
        """
```

## Standards Markdown et Interdictions

### Règles Strictes pour Markdown
- **INTERDICTION ABSOLUE** : Aucun emoji dans la documentation (sauf fichiers .html UI)
- **PRINCIPE** : Documentation professionnelle et intemporelle
- **FORMAT** : Utiliser du texte simple pour tous les indicateurs
- **EXEMPLES INTERDITS** : ✓ ⚠ 🎉 🧪 🎯 ✅ ⚠️ 📋 🔍 📊
- **REMPLACEMENTS** : "OK", "ERREUR", "SUCCES", "ECHEC", "INFO", "ATTENTION"

### Structure de Documentation
```markdown
# Titre Principal

## Section Importante
- Point important
- Autre point important

### Sous-section
**STANDARD** : Utiliser le texte pour l'emphase
**INTERDICTION** : Pas d'emojis pour décorer

#### Exemple de Code
\```python
# Code bien documenté
def fonction_exemple():
    """Documentation claire sans emojis."""
    logger.info("Message informatif sans emojis")
    return "SUCCES"  # Texte simple au lieu d'emoji
\```
```

## Documentation d'Architecture

### Standards pour Architecture Hexagonale
```markdown
## Architecture : Ports et Adapters

### Couche Domaine (Core Business)
- **Entités** : User, Condo (logique métier pure)
- **Services** : Business logic sans dépendances externes
- **Cas d'usage** : Orchestration de la logique métier

### Couche Application
- **Services** : Orchestration entre domaine et infrastructure
- **DTOs** : Objets de transfert de données
- **Mappers** : Conversion entre entités et DTOs

### Couche Infrastructure
- **Adapters** : Implémentations concrètes des ports
- **Repositories** : Accès aux données avec SQLiteAdapter centralisé
- **Configuration** : Gestion des fichiers JSON de configuration
```

### Documentation des Migrations
```markdown
## Système de Migration Centralisé

### Principe de Centralisation
**SOURCE UNIQUE** : SQLiteAdapter gère TOUTES les migrations
**TABLE DE TRACKING** : schema_migrations empêche les duplications
**INTÉGRITÉ GARANTIE** : Données existantes jamais corrompues

### Architecture
- **Point d'entrée unique** : SQLiteAdapter._run_migrations()
- **Mécanisme de protection** : _execute_migration_with_tracking()
- **Autres adapters** : AUCUNE logique de migration autorisée
```
