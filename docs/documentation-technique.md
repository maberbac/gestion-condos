# Documentation Technique - Projet Gestion Condos

## Table des Matières
1. [Vue d'ensemble du projet](#vue-densemble-du-projet)
2. [Architecture du système](#architecture-du-système)
3. [Technologies utilisées](#technologies-utilisées)
4. [Concepts techniques implémentés](#concepts-techniques-implémentés)
5. [Structure du projet](#structure-du-projet)
6. [Installation et configuration](#installation-et-configuration)
7. [Composants principaux](#composants-principaux)
8. [Base de données et stockage](#base-de-données-et-stockage)
9. [API et interfaces](#api-et-interfaces)
10. [Sécurité](#sécurité)
11. [Performance et optimisation](#performance-et-optimisation)
12. [Tests](#tests)
13. [Déploiement](#déploiement)
14. [Maintenance et monitoring](#maintenance-et-monitoring)
15. [Dépannage](#dépannage)
16. [Développement futur](#développement-futur)

---

## Vue d'ensemble du projet

### Objectif
Le système de gestion de condominiums est une application web développée pour faciliter la gestion administrative et financière des copropriétés. L'application permet de gérer les informations des résidents, les unités, les finances et les communications.

### Portée fonctionnelle
- Gestion des résidents et des unités de condo
- Suivi des paiements et des frais de copropriété
- Génération de rapports financiers
- Communication avec les résidents
- Maintenance et gestion des installations communes

### Public cible
- Gestionnaires de copropriété
- Syndics
- Conseils d'administration de copropriétés
- Résidents (consultation limitée)

---

## Architecture du système

### Architecture Hexagonale (Ports et Adapters)
L'application suit une architecture hexagonale moderne garantissant l'isolation du domaine métier :

```
┌─────────────────────────────────────────────────────────────┐
│                     COUCHE WEB (Interface)                  │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   Templates     │    │   Flask Routes  │                │
│  │   HTML/CSS      │◄──►│   Controllers   │                │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                  COUCHE APPLICATION (Services)              │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   UserService   │    │ FinancialService│                │
│  │   (Orchestration│◄──►│  (Calculs)      │                │
│  │    & Logique)   │    │                 │                │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                 COUCHE DOMAINE (Métier)                     │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   Entités       │    │    Ports        │                │
│  │ (User, Condo)   │    │  (Interfaces)   │                │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│               COUCHE INFRASTRUCTURE (Adapters)              │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │  SQLite Adapter │    │  File Adapter   │                │
│  │  (Base données) │    │  (JSON/CSV)     │                │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### Patterns architecturaux
- **Architecture Hexagonale** : Isolation du domaine métier avec ports et adapters
- **Service Layer** : Orchestration de la logique métier pour l'interface web
- **Repository Pattern** : Abstraction de l'accès aux données
- **RESTful API** : Interface standardisée pour les communications
- **Dependency Injection** : Inversion des dépendances via interfaces

### Flux de données
1. **Interface web** → Requêtes HTTP vers Flask routes
2. **Controllers** → Délégation vers la couche Application Services
3. **Services** → Orchestration de la logique métier et appel aux Ports
4. **Adapters** → Implémentation concrète des Ports (SQLite, Files)
5. **Domaine** → Entités métier avec logique business encapsulée

---

## Technologies utilisées

### Backend
- **Langage** : Python 3.9+
- **Framework web** : Flask ou FastAPI
- **Gestion des dépendances** : pip + requirements.txt
- **Serveur de développement** : Intégré au framework

### Frontend
- **Langages** : HTML5, CSS3, JavaScript ES6+
- **Styles** : CSS natif (pas de framework)
- **Interface** : Responsive design
- **Communication** : Fetch API pour les requêtes AJAX

### Stockage des données
- **Format principal** : JSON pour les données structurées
- **Format secondaire** : CSV pour l'import/export
- **Configuration** : Fichiers de configuration JSON/YAML

### Outils de développement
- **Éditeur** : Visual Studio Code
- **Contrôle de version** : Git
- **Assistant IA** : GitHub Copilot
- **Debug** : Outils intégrés du navigateur + logs Python

---

## Concepts techniques implémentés

### 1. Lecture de fichiers
**Implémentation** : Module de gestion des fichiers JSON/CSV
- Lecture de données de résidents depuis fichiers JSON
- Import/export de données financières en CSV
- Chargement de configuration depuis fichiers

**Technologies** :
```python
import json
import csv
import os
```

**Gestion d'erreurs** :
- FileNotFoundError pour fichiers manquants
- json.JSONDecodeError pour format invalide
- UnicodeDecodeError pour problèmes d'encodage

### 2. Programmation fonctionnelle
**Implémentation** : Utilisation systématique des concepts fonctionnels
- Fonctions pures pour les calculs
- map(), filter(), reduce() pour les transformations
- Lambda functions pour les opérations simples
- Immuabilité des données quand possible

**Exemples d'usage** :
```python
# Filtrage des résidents actifs
residents_actifs = list(filter(lambda r: r['statut'] == 'actif', residents))

# Calcul des frais totaux
frais_totaux = reduce(lambda acc, frais: acc + frais['montant'], frais_list, 0)
```

### 3. Gestion des erreurs par exceptions
**Implémentation** : Hiérarchie d'exceptions personnalisées
- Classes d'exception spécialisées
- Try/except avec gestion spécifique
- Logging détaillé des erreurs
- Messages d'erreur utilisateur appropriés

**Structure** :
```python
class GestionCondosError(Exception):
    """Exception de base pour l'application"""
    pass

class ResidentError(GestionCondosError):
    """Erreurs liées aux résidents"""
    pass

class FinanceError(GestionCondosError):
    """Erreurs liées aux finances"""
    pass
```

### 4. Programmation asynchrone
**Implémentation** : Opérations non-bloquantes avec asyncio intégrées dans l'architecture hexagonale

**Réalisations actuelles** :
- **UserService** : Gestion asynchrone des opérations base de données utilisateur
- **UserRepositorySQLite** : Requêtes SQLite asynchrones avec gestion event loop
- **FileAdapter** : Opérations fichiers non-bloquantes avec aiofiles
- **Flask Integration** : Intégration async/await dans les routes web

**Architecture async** :
```python
# Service Layer avec async
class UserService:
    async def get_users_for_web_display(self):
        return await self.user_repository.get_all()

# Repository async avec event loop management
class UserRepositorySQLite:
    async def get_all(self):
        # Gestion automatique de l'event loop
        if asyncio.get_event_loop().is_running():
            # Délégation vers thread séparé
        else:
            # Exécution directe
```

**Concepts techniques démontrés** :
- **Event loop management** : Gestion appropriée des boucles d'événements
- **Thread integration** : Intégration async/sync dans Flask
- **Database async** : Opérations SQLite non-bloquantes
- **Error handling async** : Gestion d'exceptions dans le contexte asynchrone

**Technologies** :
```python
import asyncio
import aiofiles
import threading
import concurrent.futures
```

---

## Structure du projet

```
gestion-condos/
├── README.md                    # Documentation principale
├── requirements.txt             # Dépendances Python de base
├── requirements-web.txt         # Dépendances web Flask
├── run_app.py                   # Point d'entrée application web
├── configure_logging.py         # Configuration du système de logging
├── .gitignore                   # Fichiers exclus du versioning
│
├── .github/                     # Configuration GitHub
│   ├── copilot-instructions.md # Instructions GitHub Copilot  
│   └── ai-guidelines/           # Guidelines additionnelles IA
│
├── ai-guidelines/               # Instructions et contexte pour l'IA
│   ├── README.md               # Index des instructions IA
│   ├── checklist-concepts.md   # Checklist concepts techniques
│   ├── consignes-projet.md     # Exigences et contraintes projet
│   ├── debut-session.md        # Guide début de session IA
│   ├── guidelines-code.md      # Standards de code
│   ├── instructions-ai.md      # Instructions spécifiques projet
│   └── regles-developpement.md # Règles TDD et mocking
│
├── config/                      # Configuration système
│   ├── app.json                # Configuration application principale
│   ├── database.json           # Configuration base de données
│   ├── logging.json            # Configuration système de logs
│   └── schemas/                # Schémas de validation JSON
│
├── data/                        # Données et base de données
│   ├── condos.db               # Base de données SQLite principale
│   ├── projects.json           # Données projets (transition)
│   ├── users.json              # Données utilisateurs (transition)
│   └── migrations/             # Scripts d'initialisation base de données
│
├── docs/                        # Documentation du projet
│   ├── README.md               # Index de la documentation
│   ├── architecture.md         # Architecture hexagonale
│   ├── documentation-technique.md   # Documentation technique
│   ├── guide-demarrage.md      # Guide de démarrage
│   ├── guide-logging.md        # Documentation logging
│   ├── guide-tests-mocking.md  # Guide tests avec mocking
│   └── methodologie.md         # Méthodologie TDD
│
├── logs/                        # Fichiers de logs
│   ├── application.log         # Logs application principale
│   └── errors.log              # Logs d'erreurs
│
├── src/                         # Code source principal
│   ├── adapters/               # Adapters (couche infrastructure)
│   ├── application/            # Services applicatifs
│   ├── domain/                 # Domaine métier (core business)
│   │   ├── entities/           # Entités métier
│   │   ├── exceptions/         # Exceptions métier
│   │   ├── services/           # Services domaine
│   │   └── use_cases/          # Cas d'usage métier
│   ├── infrastructure/         # Infrastructure système
│   ├── ports/                  # Ports (interfaces hexagonales)
│   └── web/                    # Interface web Flask
│       ├── static/             # Ressources statiques CSS/JS
│       └── templates/          # Templates HTML Jinja2
│
├── tests/                       # Suite de tests complète (393 tests)
│   ├── run_all_unit_tests.py   # Runner tests unitaires (184 tests)
│   ├── run_all_integration_tests.py # Runner tests intégration (108 tests)
│   ├── run_all_acceptance_tests.py  # Runner tests acceptance (101 tests)
│   ├── run_all_tests.py        # Runner complet tous tests
│   ├── fixtures/               # Données et utilitaires de test
│   ├── unit/                   # Tests unitaires (logique métier)
│   ├── integration/            # Tests d'intégration (composants)
│   └── acceptance/             # Tests d'acceptance (scénarios)
│
└── tmp/                         # Fichiers temporaires et utilitaires
```

---

## Installation et configuration

### Prérequis système
- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)
- Navigateur web moderne (Chrome, Firefox, Safari, Edge)
- 500 MB d'espace disque libre

### Installation
1. **Cloner le repository** :
   ```bash
   git clone [url_du_repository]
   cd gestion-condos
   ```

2. **Créer un environnement virtuel** :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer l'application** :
   - Copier `config/app_config.example.json` vers `config/app_config.json`
   - Modifier les paramètres selon l'environnement

5. **Initialiser les données** :
   ```bash
   python src/app/init_data.py
   ```

### Configuration
Fichier `config/app_config.json` :
```json
{
  "debug": true,
  "host": "127.0.0.1",
  "port": 5000,
  "secret_key": "your-secret-key",
  "data_path": "./data/",
  "log_level": "INFO"
}
```

---

## Composants principaux

### Couche Application - Services

#### UserService (Service d'Orchestration Utilisateur)
**Responsabilité** : Orchestration des opérations utilisateur pour l'interface web

**Fichier** : `src/application/services/user_service.py`

**Fonctionnalités principales** :
- `get_users_for_web_display()` : Récupère et formate les utilisateurs pour affichage web
- `get_user_statistics()` : Calcule les statistiques d'utilisateurs (total, par rôle)
- `get_user_details_by_username()` : **NOUVEAU** - Récupère les détails complets d'un utilisateur
- `get_user_details_for_api()` : **NOUVEAU** - Formate les détails utilisateur pour l'API REST
- Gestion asynchrone avec intégration event loop
- Interface entre la couche web et la couche domaine

**Nouvelles méthodes implémentées** :

```python
async def get_user_details_by_username(self, username: str) -> Optional[User]:
    """
    Récupère les détails complets d'un utilisateur par nom d'utilisateur
    
    Args:
        username: Nom d'utilisateur à rechercher
        
    Returns:
        User: Objet utilisateur complet ou None si non trouvé
        
    Raises:
        Exception: En cas d'erreur de base de données
    """

def get_user_details_for_api(self, user: User) -> dict:
    """
    Formate les détails utilisateur pour l'API REST
    
    Args:
        user: Objet User à formater
        
    Returns:
        dict: Données utilisateur formatées pour JSON avec :
        - Informations personnelles
        - Rôle et permissions
        - Historique de connexion
        - Unité de condo assignée
    """
```

**Architecture** :
```python
class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository
    
    async def get_users_for_web_display(self):
        """Récupère les utilisateurs formatés pour l'affichage web"""
        
    def get_user_statistics(self, users):
        """Calcule les statistiques à partir d'une liste d'utilisateurs"""
        
    async def get_user_details_by_username(self, username: str):
        """NOUVEAU : Récupère les détails complets d'un utilisateur"""
        
    def get_user_details_for_api(self, user):
        """NOUVEAU : Formate les détails pour l'API REST"""
```

**Concepts techniques démontrés** :
- **Programmation asynchrone** : Méthodes async/await pour opérations non-bloquantes
- **Gestion d'erreurs** : Exception handling pour opérations database
- **Architecture ports/adapters** : Service utilisant les ports du domaine
- **Formatage de données** : Transformation entités domaine → DTO pour API
- **Contrôle d'accès** : Validation des permissions utilisateur

#### FinancialService (Service Financier)
**Responsabilité** : Calculs financiers avec programmation fonctionnelle

**Fonctionnalités** :
- Calculs de revenus et projections
- Utilisation systématique de map(), filter(), reduce()
- Fonctions pures pour garantir la reproductibilité
- Pipeline de transformation de données

### Couche Domaine - Entités et Ports

#### Entités Métier
**User** : Entité utilisateur avec rôles et validation
**Condo** : Entité condo avec types et calculs métier

#### Ports (Interfaces)
**UserRepository** : Interface pour l'accès aux données utilisateur
**CondoRepository** : Interface pour l'accès aux données condo

### Couche Infrastructure - Adapters

#### UserRepositorySQLite
**Responsabilité** : Implémentation concrète de l'accès aux données utilisateur via SQLite
- Opérations CRUD asynchrones
- Requêtes SQL optimisées
- Gestion des connexions database

#### FileAdapter  
**Responsabilité** : Lecture/écriture de fichiers JSON/CSV
- Opérations asynchrones avec aiofiles
- Validation des formats
- Gestion d'erreurs I/O

### Interface utilisateur
**Responsabilité** : Présentation et interaction
- Pages HTML responsives avec thème moderne (gradients, animations)
- Interface JavaScript interactive
- Validation côté client
- Communication avec l'API Flask

### Gestionnaire de résidents
**Responsabilité** : Gestion CRUD des informations des résidents (legacy - remplacé par UserService)
- Création, lecture, mise à jour, suppression
- Validation des données
- Recherche et filtrage

**Fichiers principaux** :
- `src/application/services/user_service.py` (nouveau)
- `src/domain/entities/user.py`
- `src/adapters/sqlite/user_repository_sqlite.py`

---

## Base de données et stockage

### Architecture de Base de Données SQLite

Le système utilise SQLite comme base de données principale avec une architecture centralisée pour les migrations.

#### Configuration de Base de Données
```json
// config/database.json
{
  "database": {
    "type": "sqlite",
    "path": "data/condos.db",
    "migrations_path": "data/migrations/",
    "wal_mode": true,
    "cache_size": 2000
  }
}
```

### Centralisation des Migrations - Architecture Critique

#### Principe de Centralisation
**TOUTES les migrations de base de données sont centralisées dans `SQLiteAdapter`** pour garantir l'intégrité des données et éviter les corruptions lors des redémarrages multiples.

#### Problème Résolu
Avant la centralisation, trois adaptateurs exécutaient leurs propres migrations de façon indépendante :
- `SQLiteAdapter._run_migrations()`
- `ProjectRepositorySQLite._run_migrations()` ❌ SUPPRIMÉ
- `UserRepositorySQLite._run_migrations()` ❌ SUPPRIMÉ

Cela causait des **corruptions de données** où les projets/unités étaient recréés avec des timestamps actuels au lieu de préserver les données originales.

#### Solution Implémentée

##### 1. Source Unique de Vérité
```python
# src/adapters/sqlite_adapter.py - SEUL POINT D'ENTRÉE MIGRATIONS
class SQLiteAdapter(CondoRepositoryPort):
    def _run_migrations(self) -> None:
        """Exécute TOUTES les migrations du système de façon centralisée"""
        # Utilise la table schema_migrations pour le tracking
        
    def _execute_migration_with_tracking(self, migration_file: Path, conn: sqlite3.Connection) -> None:
        """Exécute une migration avec tracking pour éviter les duplications"""
        # Vérifie schema_migrations avant exécution
        # Marque la migration comme exécutée
```

##### 2. Table de Tracking
```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    migration_name TEXT UNIQUE NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

##### 3. Autres Adapters Simplifiés
```python
# src/adapters/project_repository_sqlite.py
class ProjectRepositorySQLite:
    def __init__(self, db_path: str = None):
        # PLUS de _run_migrations() - Dépend de SQLiteAdapter
        
# src/adapters/user_repository_sqlite.py  
class UserRepositorySQLite(UserRepositoryPort):
    def __init__(self, config_path: str = "config/database.json"):
        # PLUS de _run_migrations() - Dépend de SQLiteAdapter
```

#### Avantages de la Centralisation
- **Idempotence** : Les migrations ne s'exécutent jamais deux fois
- **Intégrité** : Les données existantes ne sont jamais corrompues
- **Cohérence** : Un seul point de contrôle pour l'évolution du schéma
- **Traçabilité** : Historique complet des migrations via schema_migrations
- **Performance** : Évite les opérations redondantes au démarrage

### Modèle de données
Bien qu'utilisant des fichiers, l'application maintient un modèle de données structuré :

#### Résident
```json
{
  "id": "string",
  "nom": "string",
  "prenom": "string",
  "email": "string",
  "telephone": "string",
  "unite_id": "string",
  "date_entree": "date",
  "statut": "actif|inactif",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Unité
```json
{
  "id": "string",
  "numero": "string",
  "etage": "number",
  "superficie": "number",
  "charges_base": "number",
  "type": "appartement|commercial|parking",
  "statut": "occupee|libre|maintenance"
}
```

#### Transaction financière
```json
{
  "id": "string",
  "unite_id": "string",
  "resident_id": "string",
  "type": "charge|paiement|penalite",
  "montant": "number",
  "description": "string",
  "date_transaction": "date",
  "statut": "en_attente|paye|en_retard"
}
```

### Gestion des fichiers
- **Format principal** : JSON pour la structure et les relations
- **Format d'échange** : CSV pour l'import/export
- **Persistance** : Sauvegarde immédiate des modifications en base SQLite
- **Validation** : Schémas JSON pour la validation des données

---

## API et interfaces

### Endpoints principaux

#### Authentification et Session
- `POST /login` - Connexion utilisateur
- `POST /logout` - Déconnexion utilisateur
- `GET /profile` - Profil utilisateur connecté

#### Gestion des Utilisateurs
- `GET /users` - Interface de gestion des utilisateurs (admin)
- `GET /api/user/<username>` - Détails d'un utilisateur via API
- `GET /users/<username>/details` - Page complète de détails utilisateur
- `POST /users/new` - Créer un nouvel utilisateur

#### Résidents
- `GET /api/residents` - Liste des résidents
- `GET /api/residents/{id}` - Détails d'un résident
- `POST /api/residents` - Créer un résident
- `PUT /api/residents/{id}` - Modifier un résident
- `DELETE /api/residents/{id}` - Supprimer un résident

#### Unités
- `GET /api/unites` - Liste des unités
- `GET /api/unites/{id}` - Détails d'une unité
- `POST /api/unites` - Créer une unité
- `PUT /api/unites/{id}` - Modifier une unité

#### Finances
- `GET /api/finances/charges` - Charges par période
- `GET /api/finances/paiements` - Paiements reçus
- `POST /api/finances/calculer-charges` - Calculer les charges
- `GET /api/finances/rapport/{periode}` - Rapport financier

### Nouvelles Fonctionnalités - Détails Utilisateur

#### API de Consultation Utilisateur
```http
GET /api/user/<username>
Authorization: Session basée
```

**Réponse succès :**
```json
{
  "found": true,
  "username": "admin",
  "details": {
    "user_id": "admin",
    "username": "admin",
    "full_name": "Administrateur Principal",
    "email": "admin@condos.local",
    "role": "admin",
    "role_display": "Administrateur",
    "condo_unit": null,
    "last_login": "2025-08-30T10:00:00Z",
    "permissions": ["read", "write", "admin"],
    "can_manage_users": true,
    "can_access_finances": true
  }
}
```

#### Page de Détails Utilisateur
```http
GET /users/<username>/details
Authorization: Session basée avec contrôle d'accès
```

**Contrôle d'accès :**
- **Administrateurs** : Peuvent voir tous les utilisateurs
- **Résidents** : Peuvent voir leurs propres détails uniquement
- **Invités** : Accès limité selon configuration

**Fonctionnalités de la page :**
- Informations personnelles complètes
- Historique de connexions
- Permissions et autorisations
- Unité de condo assignée
- Actions administratives (si autorisé)

### Format des réponses
```json
{
  "success": true,
  "data": {},
  "message": "Operation réussie",
  "timestamp": "2025-08-27T10:00:00Z"
}
```

### Gestion des erreurs API
```json
{
  "success": false,
  "error": {
    "code": "RESIDENT_NOT_FOUND",
    "message": "Résident introuvable",
    "details": "Aucun résident avec l'ID spécifié"
  },
  "timestamp": "2025-08-27T10:00:00Z"
}
```

---

## Sécurité

### Authentification
- Session-based authentication
- Mots de passe hashés (bcrypt)
- Expiration automatique des sessions

### Autorisation
- Rôles utilisateurs : admin, gestionnaire, résident
- Permissions granulaires par endpoint
- Validation des droits d'accès

### Protection des données
- Validation stricte des entrées
- Échappement des données pour prévenir les injections
- Logs d'audit pour les actions sensibles

### Sécurité des fichiers
- Validation des types de fichiers
- Limitation de la taille des uploads
- Stockage sécurisé hors du webroot

---

## Performance et optimisation

### Optimisations côté serveur
- Cache en mémoire pour les données fréquemment accédées
- Pagination des résultats pour les grandes listes
- Compression des réponses HTTP
- Traitement asynchrone pour les opérations longues

### Optimisations côté client
- Minification des ressources CSS/JS
- Lazy loading des images
- Cache navigateur pour les ressources statiques
- Requêtes AJAX optimisées

### Gestion de la mémoire
- Chargement partiel des gros fichiers
- Nettoyage automatique des caches
- Gestion des ressources dans les opérations async

---

## Tests

### Méthodologie TDD (Test-Driven Development)
Le projet suit une méthodologie de développement TDD stricte avec le cycle Red-Green-Refactor :

1. **RED** : Écrire un test qui échoue avant d'écrire le code
2. **GREEN** : Écrire le minimum de code pour faire passer le test  
3. **REFACTOR** : Améliorer le code sans changer les fonctionnalités

### Suite de Tests Complète (393 tests - 100% succès)

**Structure organisée par niveaux** :
```
tests/
├── unit/                    # 184 tests unitaires (logique métier isolée)
├── integration/             # 108 tests d'intégration (composants ensemble)
├── acceptance/              # 101 tests d'acceptance (scénarios end-to-end)
├── fixtures/                # Données et utilitaires de test
├── run_all_unit_tests.py    # Runner tests unitaires
├── run_all_integration_tests.py  # Runner tests d'intégration
├── run_all_acceptance_tests.py   # Runner tests d'acceptance
└── run_all_tests.py         # Runner complet (393 tests)
```

#### Tests Unitaires (184 tests)
**Objectif** : Valider la logique métier de chaque composant de manière isolée
**Répertoire** : `tests/unit/`
**Couverture** : Entités, services domaine, adapters, configuration

**Standards de mocking stricts** :
- **Mocking obligatoire** : Tous les repositories et services externes mockés
- **Isolation totale** : Aucune interaction avec base de données ou fichiers
- **Performance** : Exécution ultra-rapide (pas d'I/O)

**Exemples principaux** :
- `test_condo_entity.py` - Validation logique métier entité Condo
- `test_condo_service.py` - Service métier condos avec mocking
- `test_config_manager.py` - Gestionnaire configuration
- `test_financial_service.py` - Calculs financiers isolés
- `test_logger_manager.py` - Système de logging
- `test_password_change_service.py` - Service changement mot de passe
- `test_project_entity.py` - Entité projet avec validations
- `test_project_service.py` - Service métier projets
- `test_user_creation_service.py` - Service création utilisateur
- `test_user_entity.py` - Entité utilisateur
- `test_user_file_adapter.py` - Adapter fichiers utilisateur

#### Tests d'Intégration (108 tests)
**Objectif** : Valider l'interaction entre composants du système
**Répertoire** : `tests/integration/`
**Couverture** : Services + Adapters, Database + Web, Configuration + Logging

**Mocking sélectif** :
- Services externes mockés, composants internes réels
- Base de test isolée pour environnement contrôlé
- Validation des flux de données entre couches

**Exemples principaux** :
- `test_authentication_database_integration.py` - Authentification avec base isolée
- `test_condo_routes_integration.py` - Routes web condos
- `test_logging_config_integration.py` - Configuration système de logging
- `test_password_change_integration.py` - Changement mot de passe end-to-end
- `test_project_integration.py` - Gestion projets complète
- `test_user_creation_integration.py` - Création utilisateurs avec validation
- `test_user_deletion_integration.py` - Suppression utilisateurs
- `test_web_integration.py` - Interface web complète

#### Tests d'Acceptance (101 tests)
**Objectif** : Valider les scénarios utilisateur complets
**Répertoire** : `tests/acceptance/`
**Couverture** : Workflows métier, Interface utilisateur, Sécurité

**Environnement réaliste** :
- Simulation conditions de production
- Données contrôlées mais représentatives
- Scénarios métier complets des utilisateurs finaux

**Exemples principaux** :
- `test_authentication_database_acceptance.py` - Scénarios authentification
- `test_condo_management_acceptance.py` - Gestion condos end-to-end
- `test_financial_scenarios.py` - Scénarios financiers complets
- `test_logging_system_acceptance.py` - Système de logging en action
- `test_modern_ui_acceptance.py` - Interface utilisateur moderne
- `test_password_change_acceptance.py` - Changement mot de passe utilisateur
- `test_project_acceptance.py` - Gestion projets complète
- `test_security_acceptance.py` - Sécurité et permissions
- `test_user_creation_acceptance.py` - Création utilisateurs
- `test_user_deletion_acceptance.py` - Suppression utilisateurs
- `test_web_interface.py` - Interface web complète

### Runners de Tests Spécialisés

**Exécution par catégorie** :
```bash
# Tests unitaires uniquement (184 tests - logique métier)
python tests/run_all_unit_tests.py

# Tests d'intégration uniquement (108 tests - composants)
python tests/run_all_integration_tests.py

# Tests d'acceptance uniquement (101 tests - scénarios)
python tests/run_all_acceptance_tests.py

# Suite complète avec rapport consolidé (393 tests)
python tests/run_all_tests.py
```
- `test_user_details_integration.py` : **NOUVEAU** - Tests intégration détails utilisateur (4 tests)
- `test_api_endpoints.py` : Tests des routes Flask
- `test_database_operations.py` : Tests des opérations SQLite

**Nouveaux tests d'intégration** :
```python
# test_user_details_integration.py - Tests intégration complète
def test_user_details_api_endpoint_success()  # Test endpoint API /api/user/<username>
def test_user_details_page_endpoint_success()  # Test page /users/<username>/details  
def test_user_details_authentication_required()  # Test authentification requise
def test_user_details_role_based_access()  # Test contrôle d'accès par rôle
```

#### Tests d'Acceptance (78 tests)
**Objectif** : Valider les fonctionnalités end-to-end
**Répertoire** : `tests/acceptance/`
**Couverture** : Scénarios utilisateur complets

**Exemples** :
- `test_user_creation_acceptance.py` : Création d'utilisateur bout en bout
- `test_user_details_acceptance.py` : **NOUVEAU** - Consultation détails utilisateur (5 tests)
- `test_condo_management_acceptance.py` : Gestion des condos
- `test_authentication_flow.py` : Flux d'authentification

**Nouveaux tests d'acceptance** :
```python
# test_user_details_acceptance.py - Scénarios utilisateur complets
def test_admin_can_view_any_user_details()  # Admin consulte détails tous utilisateurs
def test_resident_can_view_only_own_details()  # Résident consulte ses détails
def test_guest_cannot_view_user_details()  # Invité restrictions d'accès
def test_user_details_page_shows_comprehensive_information()  # Page détails complète
def test_user_details_modal_displays_real_data()  # Interface moderne fonctionnelle
```

### Scripts d'Exécution des Tests

```bash
# Tests unitaires uniquement
python tests/run_all_unit_tests.py

# Tests d'intégration uniquement  
python tests/run_all_integration_tests.py

# Tests d'acceptance uniquement
python tests/run_all_acceptance_tests.py

# Tous les tests (291 total)
python tests/run_all_tests.py
```

### Couverture et Qualité
- **291 tests total** avec 100% de succès
- **Temps d'exécution** : ~4.5 secondes total
- **Couverture fonctionnelle** : Toutes les fonctionnalités utilisateur
- **Mocking approprié** : Mock au niveau service plutôt que repository

### Exemples de Tests TDD Récents

#### UserService - Tests Unitaires
```python
def test_get_users_for_web_display_returns_formatted_data():
    """Test que le service formate correctement les données pour l'affichage web"""
    
def test_get_user_statistics_calculates_correct_totals():
    """Test que les statistiques d'utilisateurs sont calculées correctement"""
```

#### Intégration Web/Database
```python  
def test_users_page_displays_real_database_data():
    """Test que la page /users affiche les vraies données de la base"""
    
def test_users_page_handles_empty_database():
    """Test que la page gère gracieusement une base de données vide"""
```

### Validation Continue
- Tests exécutés avant chaque commit
- Validation automatique de l'architecture hexagonale
- Détection des régressions en temps réel
    └── test_load.py
```

### Outils de test
- **pytest** : Framework de test principal
- **coverage** : Couverture de code
- **mock** : Simulation d'objets
- **requests** : Tests d'API

### Données de test
- Jeux de données de test isolés
- Factory pattern pour la création d'objets de test
- Cleanup automatique après chaque test

---

## Déploiement

### Environnements
- **Développement** : Local avec debug activé
- **Test** : Serveur de test avec données simulées
- **Production** : Serveur de production avec données réelles

### Processus de déploiement
1. Tests automatisés passés
2. Build et packaging
3. Déploiement sur serveur de test
4. Tests d'acceptation
5. Déploiement en production
6. Monitoring post-déploiement

### Configuration serveur
- **Serveur web** : Nginx (reverse proxy)
- **Serveur d'application** : Gunicorn (WSGI)
- **Monitoring** : Logs centralisés
- **Stockage** : Base de données SQLite pour la persistance

---

## Maintenance et monitoring

### Logs et monitoring
- **Niveaux de log** : DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Rotation des logs** : Archivage automatique
- **Alertes** : Notifications en cas d'erreur critique
- **Métriques** : Performance et utilisation

### Maintenance préventive
- Vérification de l'intégrité de la base de données SQLite
- Nettoyage des fichiers temporaires
- Mise à jour des dépendances
- Optimisation des performances

### Monitoring applicatif
- Temps de réponse des endpoints
- Utilisation mémoire et CPU
- Taille et croissance des fichiers de données
- Erreurs et exceptions

---

## Dépannage

### Problèmes courants

#### Application ne démarre pas
1. Vérifier l'installation des dépendances
2. Contrôler les permissions des fichiers
3. Valider la configuration
4. Examiner les logs de démarrage

#### Erreurs de lecture de fichiers
1. Vérifier l'existence des fichiers de données
2. Contrôler les permissions de lecture
3. Valider le format JSON/CSV
4. Vérifier l'encodage des fichiers

#### Performances dégradées
1. Analyser la taille des fichiers de données
2. Vérifier l'utilisation mémoire
3. Optimiser les requêtes de données
4. Implémenter du cache si nécessaire

### Outils de diagnostic
- **Logs applicatifs** : Informations détaillées sur le fonctionnement
- **Profiling** : Analyse des performances
- **Monitoring système** : Utilisation des ressources
- **Tests de connectivité** : Validation des communications

---

## Développement futur

### Améliorations prévues
- Migration vers une base de données relationnelle
- API mobile pour application smartphone
- Système de notifications en temps réel
- Intégration avec systèmes comptables externes

### Architecture évolutive
- Microservices pour les modules principaux
- Container Docker pour le déploiement
- API GraphQL pour les requêtes complexes
- Event-driven architecture pour la communication

### Technologies émergentes
- Intelligence artificielle pour l'analyse prédictive
- Blockchain pour la traçabilité des transactions
- Progressive Web App pour l'expérience mobile
- Real-time analytics pour le monitoring

---

## Informations de maintenance

**Version actuelle** : 1.0.0  
**Dernière mise à jour** : Août 2025  
**Responsable technique** : [À définir]  
**Contact support** : [À définir]

Cette documentation doit être mise à jour à chaque modification significative de l'architecture ou des fonctionnalités du système.
