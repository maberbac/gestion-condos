# Directives Spécifiques aux Langages

## Directives Python - Standards Projet

### Style de Code et Conventions
- Suivre les directives de style PEP 8
- Utiliser des noms de variables et fonctions significatifs en français quand approprié
- Implémenter des type hints pour une meilleure clarté du code
- Utiliser des docstrings pour toutes les fonctions et classes publiques

### Système de Logging Obligatoire
```python
# IMPORT OBLIGATOIRE dans chaque module
from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

# INTERDICTION ABSOLUE des print()
# Utiliser exclusivement le système de logging

# Exemples d'utilisation appropriée
def traiter_donnees_utilisateur(user_data):
    """Traite les données d'un utilisateur avec logging approprié."""
    logger.debug(f"Début traitement utilisateur: {user_data.get('username')}")
    
    try:
        # Logique métier
        resultat = valider_et_sauvegarder(user_data)
        logger.info(f"Utilisateur traité avec succès: {user_data['username']}")
        return resultat
    except ValidationError as e:
        logger.error(f"Erreur de validation: {e}")
        raise
    except Exception as e:
        logger.critical(f"Erreur critique: {e}")
        raise
```

### Architecture Hexagonale Python
```python
# Structure des Services Application
class UserService:
    """
    Service d'orchestration pour la gestion des utilisateurs.
    
    [ARCHITECTURE HEXAGONALE]
    - Couche Application Service
    - Orchestration entre Domain et Infrastructure
    - Interface entre Web et Business Logic
    """
    
    def __init__(self, user_repository: UserRepositoryPort):
        """Injection de dépendance via les ports."""
        self.user_repository = user_repository
        logger.info("UserService initialisé")

# Structure des Adapters
class UserRepositorySQLite(UserRepositoryPort):
    """
    Adapter SQLite pour la persistance des utilisateurs.
    
    [STANDARDS OBLIGATOIRES]
    - Configuration via config/database.json
    - AUCUNE migration (centralisée dans SQLiteAdapter)
    - Mots de passe chiffrés obligatoires
    """
    
    def __init__(self, config_path: str = "config/database.json"):
        """
        Initialise le repository SANS logique de migration.
        
        RÈGLE : Les migrations sont centralisées dans SQLiteAdapter.
        """
        self.config = self._load_database_config(config_path)
        logger.info(f"UserRepository SQLite initialisé avec DB: {self.db_path}")
```

### Patterns de Programmation Fonctionnelle
```python
# Préféré: Approche fonctionnelle avec documentation
def filtrer_utilisateurs_actifs(utilisateurs: list[dict]) -> list[dict]:
    """
    Filtre les utilisateurs actifs en utilisant la programmation fonctionnelle.
    
    [CONCEPT: Programmation Fonctionnelle]
    - Utilise filter() pour démontrer le concept
    - Fonction pure sans effets de bord
    - Transformation de données immutables
    """
    return list(filter(lambda u: u.get('statut') == 'actif', utilisateurs))

def calculer_statistiques_users(users: list[dict]) -> dict:
    """
    Calcule les statistiques des utilisateurs avec approche fonctionnelle.
    
    [CONCEPT: Programmation Fonctionnelle]
    - Utilise map/filter/reduce pour transformations
    - Pipeline de données immutables
    """
    from functools import reduce
    
    # Compter par rôle avec programmation fonctionnelle
    roles_count = reduce(
        lambda acc, user: {**acc, user['role']: acc.get(user['role'], 0) + 1},
        users,
        {}
    )
    
    return {
        'total': len(users),
        'roles': roles_count,
        'actifs': len(list(filter(lambda u: u.get('actif', True), users)))
    }
```

### Gestion d'Erreurs avec Exceptions Personnalisées
```python
# Hiérarchie d'exceptions pour le projet
class GestionCondosError(Exception):
    """Exception de base pour l'application gestion condos."""
    pass

class UserValidationError(GestionCondosError):
    """Levée quand les données utilisateur échouent aux règles de validation."""
    pass

class UserAuthenticationError(GestionCondosError):
    """Levée lors d'échecs d'authentification."""
    pass

class DatabaseMigrationError(GestionCondosError):
    """Levée lors de problèmes de migration de base de données."""
    pass

# Gestion d'exception appropriée avec logging
def authentifier_utilisateur(username: str, password: str) -> User:
    """
    Authentifie un utilisateur avec gestion d'erreurs complète.
    
    [CONCEPT: Gestion des Erreurs par Exceptions]
    - Exceptions spécifiques pour différentes conditions
    - Logging approprié pour chaque type d'erreur
    - Messages d'erreur contextuels
    """
    try:
        user = user_repository.get_by_username(username)
        if not user:
            logger.warning(f"Tentative d'authentification avec utilisateur inexistant: {username}")
            raise UserAuthenticationError("Identifiants invalides")
            
        if not user.verify_password(password):
            logger.warning(f"Mot de passe incorrect pour: {username}")
            raise UserAuthenticationError("Identifiants invalides")
            
        logger.info(f"Authentification réussie pour: {username}")
        return user
        
    except DatabaseError as e:
        logger.error(f"Erreur base de données lors de l'authentification: {e}")
        raise UserAuthenticationError("Erreur système lors de l'authentification")
    except Exception as e:
        logger.critical(f"Erreur inattendue lors de l'authentification: {e}")
        raise
```

### Programmation Asynchrone avec Flask
```python
import asyncio
from functools import wraps

def async_route(f):
    """
    Décorateur pour intégrer async/await dans Flask.
    
    [CONCEPT: Programmation Asynchrone]
    - Intégration asyncio avec Flask
    - Gestion de l'event loop
    - Opérations non-bloquantes
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Gestion appropriée de l'event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(f(*args, **kwargs))
    
    return decorated_function

# Service asynchrone avec gestion d'erreurs
class UserService:
    async def get_users_for_web_display(self) -> list[dict]:
        """
        Récupère les utilisateurs de façon asynchrone.
        
        [CONCEPT: Programmation Asynchrone]
        - Opérations database non-bloquantes
        - Gestion d'erreurs dans contexte async
        """
        try:
            # Gestion de l'event loop pour SQLite
            if asyncio.get_event_loop().is_running():
                # Délégation vers thread séparé pour SQLite
                with ThreadPoolExecutor() as executor:
                    users = await asyncio.get_event_loop().run_in_executor(
                        executor, self.user_repository.get_all
                    )
            else:
                users = self.user_repository.get_all()
                
            logger.info(f"Récupération asynchrone de {len(users)} utilisateurs")
            return users
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération asynchrone: {e}")
            raise
```

### Standards TDD avec Mocking Strict
```python
import unittest
from unittest.mock import Mock, patch, MagicMock

class TestUserService(unittest.TestCase):
    """
    Tests unitaires pour UserService avec mocking strict.
    
    [MÉTHODOLOGIE TDD OBLIGATOIRE]
    - Tests écrits AVANT le code (Red-Green-Refactor)
    - Repository complètement mocké - AUCUNE base réelle
    - Tests indépendants dans n'importe quel ordre
    """
    
    def setUp(self):
        """Configuration avant chaque test avec mocking complet."""
        self.mock_repository = Mock(spec=UserRepositoryPort)
        self.user_service = UserService(self.mock_repository)
    
    @patch('src.adapters.user_repository_sqlite.UserRepositorySQLite')
    def test_get_user_by_username_found(self, mock_repo_class):
        """
        Test récupération utilisateur existant.
        
        [MOCKING OBLIGATOIRE]
        - Repository complètement mocké avec @patch
        - AUCUNE connexion SQLite réelle
        - Données contrôlées via Mock
        """
        # Given - Données de test mockées
        expected_user = User(username="testuser", email="test@example.com")
        self.mock_repository.get_by_username.return_value = expected_user
        
        # When - Exécution de la méthode testée
        result = self.user_service.get_user_by_username("testuser")
        
        # Then - Validation avec assertions
        self.assertEqual(result.username, "testuser")
        self.mock_repository.get_by_username.assert_called_once_with("testuser")
    
    def test_get_user_statistics_empty_list(self):
        """
        Test calcul statistiques avec liste vide.
        
        [ISOLATION TOTALE]
        - Aucune dépendance externe
        - Test de cas limite
        - Validation logique métier pure
        """
        # Given
        empty_users = []
        
        # When
        stats = self.user_service.get_user_statistics(empty_users)
        
        # Then
        self.assertEqual(stats['total'], 0)
        self.assertEqual(stats['roles'], {})
```

### Configuration et Base de Données
```python
# Configuration JSON obligatoire
def load_database_config(config_path: str = "config/database.json") -> dict:
    """
    Charge la configuration de base de données depuis JSON.
    
    [STANDARD: Configuration JSON obligatoire]
    - Toutes les configurations en JSON
    - Validation avec schémas
    - Gestion d'erreurs appropriée
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info(f"Configuration database chargée depuis: {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Fichier de configuration non trouvé: {config_path}")
        raise GestionCondosError(f"Configuration database manquante: {config_path}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON invalide dans {config_path}: {e}")
        raise GestionCondosError(f"Configuration database invalide: {e}")

# Migrations centralisées - RÈGLE ABSOLUE
class SQLiteAdapter(CondoRepositoryPort):
    """
    SEUL adapter autorisé à contenir des migrations.
    
    [CENTRALISATION OBLIGATOIRE]
    - SOURCE UNIQUE DE VÉRITÉ pour migrations
    - Table schema_migrations pour tracking
    - Protection anti-corruption garantie
    """
    
    def _run_migrations(self) -> None:
        """
        Exécute TOUTES les migrations du système.
        
        RÈGLE CARDINALE : Seul point d'entrée pour migrations.
        """
        logger.info("Début des migrations centralisées")
        # Implémentation de migration avec tracking
        
    def _execute_migration_with_tracking(self, migration_file: Path, conn: sqlite3.Connection) -> None:
        """Protection anti-duplication des migrations."""
        # Vérification table schema_migrations
        # Exécution seulement si pas déjà fait
```

### Exigences de Documentation Python
- Utiliser des docstrings de style Google
- Inclure des type hints dans les signatures de fonctions
- Documenter les exceptions qui peuvent être levées
- Fournir des exemples d'utilisation dans les docstrings
- Mentionner explicitement les concepts techniques démontrés
- **INTERDICTION ABSOLUE** : Aucun emoji dans les commentaires
- **OBLIGATION** : Utiliser logger au lieu de print()

### Standards Flask Web
```python
from flask import Flask, render_template, request, session
from src.application.services.user_service import UserService

app = Flask(__name__)

@app.route('/users')
@require_login
@require_role('admin')
def users_page():
    """
    Page de gestion des utilisateurs (admin uniquement).
    
    [SÉPARATION HTML/PYTHON OBLIGATOIRE]
    - AUCUN HTML dans le code Python
    - Templates externes uniquement
    - Render_template avec fichiers .html
    """
    try:
        users = user_service.get_users_for_web_display()
        stats = user_service.get_user_statistics(users)
        
        logger.info(f"Affichage page utilisateurs: {len(users)} utilisateurs")
        
        # OBLIGATOIRE : render_template avec fichier externe
        return render_template('users.html', 
                             users=users, 
                             statistics=stats,
                             current_user=session.get('user'))
                             
    except Exception as e:
        logger.error(f"Erreur dans la page utilisateurs: {e}")
        return render_template('errors/500.html'), 500
```
