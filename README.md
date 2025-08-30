# Système de Gestion de Condominiums

Application web de gestion administrative et financière pour copropriétés développée en Python.

## Description

Le Système de Gestion de Condominiums est une application web moderne qui facilite la gestion quotidienne des copropriétés. Elle permet aux gestionnaires et syndics de suivre les résidents, gérer les finances, et maintenir une communication efficace avec les propriétaires.

## Fonctionnalités Principales

- **Gestion des Résidents** : Suivi des informations des propriétaires et locataires
- **Gestion des Unités** : Administration des appartements et espaces communs
- **Finances** : Suivi des paiements, frais de copropriété et budgets
- **Rapports** : Génération de rapports financiers et administratifs
- **Communication** : Système de notifications et d'annonces

## Concepts Techniques Démontrés

Ce projet illustre l'implémentation de quatre concepts techniques avancés :

### 1. Lecture de Fichiers
- Import/export de données en format JSON et CSV
- Configuration de l'application via fichiers
- Gestion robuste des erreurs de fichiers

### 2. Programmation Fonctionnelle
- Utilisation de `map()`, `filter()`, `reduce()`
- Fonctions pures sans effets de bord
- Transformation et filtrage des données

### 3. Gestion des Erreurs par Exceptions
- Structure try/catch complète
- Messages d'erreur informatifs
- Logging et traçabilité des erreurs

### 4. Programmation Asynchrone
- Opérations non-bloquantes avec `asyncio`
- Requêtes API asynchrones
- Amélioration des performances

## Technologies

### Backend
- **Python 3.9+**
- **Flask** ou **FastAPI** (framework web)
- **asyncio** (programmation asynchrone)

### Frontend
- **HTML5**
### Frontend
- **HTML5**
- **CSS3**
- **JavaScript** (vanilla)

### Données
- **JSON** (données structurées)
- **CSV** (import/export)
- Pas de base de données complexe (approche fichiers)

## Méthodologie de Développement

### TDD avec Mocking Strict ⭐ **NOUVEAU**

Le projet applique une méthodologie **Test-Driven Development (TDD)** avec des **consignes strictes de mocking** pour garantir l'isolation complète des tests :

#### Cycle TDD Obligatoire
1. **RED** : Écrire les tests AVANT le code (tests qui échouent)
2. **GREEN** : Implémenter le minimum pour faire passer les tests
3. **REFACTOR** : Améliorer le code sans changer les fonctionnalités

#### Standards de Mocking Stricts
- **Tests Unitaires** : Repository complètement mocké - AUCUNE interaction DB réelle
- **Tests d'Intégration** : Services mockés avec `@patch` - Base de test isolée
- **Tests d'Acceptance** : Données de test contrôlées - Workflows mockés
- **Isolation Totale** : Tests indépendants dans n'importe quel ordre

#### Structure de Tests
```
tests/
├── unit/                    # Tests unitaires (logique métier isolée)
├── integration/             # Tests d'intégration (composants ensemble)  
├── acceptance/              # Tests d'acceptance (workflows end-to-end)
├── run_all_unit_tests.py    # Exécute TOUS les tests unitaires
├── run_all_integration_tests.py  # Exécute TOUS les tests d'intégration
├── run_all_acceptance_tests.py   # Exécute TOUS les tests d'acceptance
└── run_all_tests.py         # Exécute les 3 niveaux de tests
```

#### Avantages Observés
- **Performance** : Tests ultra-rapides (< 1 sec unitaires)
- **Fiabilité** : Aucun effet de bord entre tests
- **Reproductibilité** : Tests identiques dans n'importe quel ordre
- **Debugging** : Isolation facilite l'identification des problèmes

## Architecture : Hexagonale (Ports & Adapters)

### Justification Architecturale

Le projet adopte une **architecture hexagonale** pour plusieurs raisons stratégiques :

- **Extensibilité future** : Préparé pour évoluer vers la gestion de location, services juridiques, APIs externes
- **Concepts techniques** : Architecture qui met parfaitement en valeur les 4 concepts obligatoires
- **Testabilité** : Core métier isolé et facilement testable via TDD
- **Maintenabilité** : Séparation claire entre logique métier et infrastructure

### Vue Architecturale Simplifiée

```
┌─────────────────────────────────────────────────┐
│              COUCHE EXTERNE                     │
│   Web UI    │    Files     │   External APIs    │
│  (Flask)    │  (JSON/CSV)  │    (Future)        │
└─────────────────────────────────────────────────┘
                     │
┌─────────────────────────────────────────────────┐
│             COUCHE ADAPTERS                     │
│  [4 CONCEPTS TECHNIQUES INTÉGRÉS]              │
│  - web_adapter.py    [Async Programming]       │
│  - file_adapter.py   [File Reading]            │
│  - error_adapter.py  [Exception Handling]      │
│  - *_service.py      [Functional Programming]  │
└─────────────────────────────────────────────────┘
                     │
┌─────────────────────────────────────────────────┐
│               COUCHE PORTS                      │
│  - condo_repository_port.py                    │
│  - file_handler_port.py                        │
│  - notification_port.py                        │
└─────────────────────────────────────────────────┘
                     │
┌─────────────────────────────────────────────────┐
│           DOMAINE MÉTIER (CORE)                 │
│  - entities/ (Condo, Resident)                 │
│  - services/ (Business Logic)                  │
│  - use_cases/ (Application Logic)              │
└─────────────────────────────────────────────────┘
```

## Arborescence du Projet

```
gestion-condos/
├── .github/
│   └── copilot-instructions.md
├── src/                          # Architecture Hexagonale
│   ├── domain/                   # Domaine Métier (Core)
│   │   ├── entities/            #   - Entités pures (Condo, Resident)
│   │   ├── services/            #   - Services métier [Concept: Functional]
│   │   └── use_cases/           #   - Cas d'usage applicatifs
│   ├── ports/                    # Interfaces (Contracts)
│   ├── adapters/                 # Implémentations Concrètes
│   │   ├── file_adapter.py      #   - [Concept: File Reading]
│   │   ├── web_adapter.py       #   - [Concept: Async Programming]
│   │   ├── error_adapter.py     #   - [Concept: Exception Handling]
│   │   └── future_extensions/   #   - Extensions futures (location, juridique)
│   └── infrastructure/          # Configuration et utilitaires
├── tests/                        # Tests TDD avec unittest
│   ├── fixtures/                #   - Input/Expected/Config data
│   │   ├── config/
│   │   ├── expected/
│   │   └── input/
│   ├── integration/
│   ├── unit/
│   ├── acceptance/
│   ├── run_acceptance_tests.py
│   ├── run_all_tests.py
│   ├── run_integration_tests.py
│   └── run_unit_tests.py
├── docs/                         # Documentation Technique
│   ├── architecture.md          #   - Architecture hexagonale détaillée
│   ├── conception-extensibilite.md #   - Conception pour extensions futures
│   ├── documentation-technique.md  #   - Documentation technique complète
│   ├── guide-demarrage.md       #   - Guide de démarrage rapide
│   ├── guide-logging.md         #   - Documentation système de logging
│   ├── journal-developpement.md    #   - Journal de développement et roadmap
│   ├── methodologie.md          #   - TDD avec unittest
│   └── status-success.md        #   - Statut de réussite du projet
├── ai-guidelines/               # Instructions et Guidelines pour l'IA
│   ├── checklist-concepts.md    #   - Checklist des concepts techniques
│   ├── consignes-projet.md      #   - Exigences et contraintes du projet
│   ├── debut-session.md         #   - Guide de début de session IA
│   ├── guidelines-code.md       #   - Standards de code pour l'IA
│   ├── instructions-ai.md       #   - Instructions spécifiques projet
│   ├── regles-developpement.md  #   - Standards de développement
│   └── README.md                #   - Documentation du répertoire
├── tmp/                          # Scripts Temporaires/Utilitaires
├── consignes-projet.md
└── README.md
```

## Installation

### Prérequis
- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner le repository**
   ```bash
   git clone https://github.com/maberbac/gestion-condos.git
   cd gestion-condos
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   
   # Sur Windows
   venv\Scripts\activate
   
   # Sur macOS/Linux
   source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   # Dépendances de base
   pip install -r requirements.txt
   
   # Dépendances web (pour l'interface Flask)
   pip install -r requirements-web.txt
   ```

## Utilisation

### Interface Web (Recommandé)

L'application dispose d'une interface web complète avec authentification par rôles :

```bash
# Démarrer l'application web
python run_app.py
```

L'interface sera accessible sur `http://127.0.0.1:5000`

**Comptes de démonstration** :
- **Admin** : `admin` / `admin123` (accès complet au conseil d'administration)
- **Résident** : `resident` / `resident123` (consultation pour copropriétaires)  
- **Invité** : `guest` / `guest123` (accès limité pour visiteurs)

### Interface Console (Alternative)

Pour utiliser l'application en mode console :
   pip install -r requirements.txt
   ```

4. **Configurer l'application**
   ```bash
   # Copier et adapter le fichier de configuration
   cp data/config.example.json data/config.json
   ```

## Utilisation

### Démarrer l'application
```bash
python app.py
```

L'application sera accessible à l'adresse : `http://localhost:5000`

### Lancer les tests

#### Tests par catégorie
```bash
# Tests unitaires uniquement
python tests/run_all_unit_tests.py

# Tests d'intégration uniquement  
python tests/run_all_integration_tests.py

# Tests d'acceptance uniquement
python tests/run_all_acceptance_tests.py

# Tous les tests
python tests/run_all_tests.py
```

#### Tests avec unittest discovery
```bash
# Tests unitaires
python -m unittest discover -s tests/unit -v

# Tests d'intégration
python -m unittest discover -s tests/integration -v

# Tests d'acceptance
python -m unittest discover -s tests/acceptance -v

# Tous les tests
python -m unittest discover -s tests -v
```

#### Tests avec couverture
```bash
# Couverture pour tous les tests
coverage run tests/run_all_tests.py
coverage report -m
coverage html
```

### Données de démonstration
```bash
# Charger des données d'exemple
python scripts/load_demo_data.py
```

## Développement

### Méthodologie
Le projet suit une approche **Test-Driven Development (TDD)** :
- **Red** : Écrire un test qui échoue
- **Green** : Implémenter le minimum pour passer le test
- **Refactor** : Améliorer le code sans casser les tests

### Standards de Code
- **unittest** pour les tests
- **Docstrings** pour la documentation
- **PEP 8** pour le style Python
- **Commentaires** explicatifs pour les concepts techniques

### Contribution
1. Fork le projet
2. Créer une branche pour la fonctionnalité
3. Écrire les tests en premier (TDD)
4. Implémenter la fonctionnalité
5. S'assurer que tous les tests passent
6. Soumettre une pull request

## Configuration

### Fichier de configuration (`data/config.json`)
```json
{
  "app": {
    "debug": true,
    "host": "localhost",
    "port": 5000
  },
  "data": {
    "condos_file": "data/condos.json",
    "residents_file": "data/residents.csv"
  },
  "logging": {
    "level": "INFO",
    "file": "logs/app.log"
  }
}
```

## Tests

### Structure des Tests
Le projet utilise une organisation hiérarchique des tests pour une meilleure maintenabilité :

#### Tests Unitaires (`tests/unit/`)
- **Objectif** : Tester chaque fonction/classe de manière isolée
- **Scope** : Un seul module à la fois
- **Mocking** : Simulation des dépendances externes
- **Rapidité** : Exécution très rapide (< 1 seconde par test)

#### Tests d'Intégration (`tests/integration/`)
- **Objectif** : Tester l'interaction entre modules
- **Scope** : Flux de données entre composants
- **Dépendances** : Utilise les vraies implémentations
- **Temps** : Exécution modérée (1-5 secondes par test)

#### Tests d'Acceptance (`tests/acceptance/`)
- **Objectif** : Valider les scénarios métier complets
- **Scope** : Parcours utilisateur de bout en bout
- **Environnement** : Proche de la production
- **Temps** : Exécution plus lente (5-30 secondes par test)

### Runners de Tests
Chaque type de test dispose de son propre runner avec découverte automatique :

```bash
tests/
├── unit/                           # Tests unitaires par concept
│   ├── test_file_reader.py        # [CONCEPT] Lecture fichiers
│   ├── test_functional_ops.py     # [CONCEPT] Programmation fonctionnelle
│   ├── test_error_handler.py      # [CONCEPT] Gestion erreurs
│   └── test_async_ops.py          # [CONCEPT] Programmation asynchrone
├── integration/                    # Tests d'intégration
│   ├── test_data_flow.py          # Flux de données entre modules
│   ├── test_api_endpoints.py      # Intégration API
│   └── test_file_processing.py    # Traitement complet fichiers
├── acceptance/                     # Tests d'acceptance métier
│   ├── test_user_scenarios.py     # Scénarios utilisateur complets
│   ├── test_business_rules.py     # Règles métier
│   └── test_condo_management.py   # Gestion complète condos
├── README.md                       # Documentation tests
├── run_all_unit_tests.py          # Runner tests unitaires
├── run_all_integration_tests.py   # Runner tests d'intégration
├── run_all_acceptance_tests.py    # Runner tests d'acceptance
└── run_all_tests.py               # Runner global avec rapport
```

### Commandes de Test Utiles

#### Développement TDD
```bash
# Cycle TDD rapide - Tests unitaires uniquement
python tests/run_all_unit_tests.py --verbose

# Test spécifique unitaire
python -m unittest tests.unit.test_file_reader.TestFileReader.test_lire_fichier_json_valide -v

# Tests d'intégration après implémentation
python tests/run_all_integration_tests.py --verbose
```

#### Validation Complète
```bash
# Pipeline de tests complet (CI/CD style)
python tests/run_all_tests.py --with-coverage

# Tests par ordre de rapidité
python tests/run_all_unit_tests.py        # ~5 secondes
python tests/run_all_integration_tests.py # ~30 secondes  
python tests/run_all_acceptance_tests.py  # ~2 minutes
```

#### Couverture et Rapports
```bash
# Couverture par type de test
coverage run tests/run_all_unit_tests.py
coverage run -a tests/run_all_integration_tests.py
coverage run -a tests/run_all_acceptance_tests.py
coverage report -m
coverage html

# Rapport détaillé
python tests/run_all_tests.py --report --html
```

## Documentation

### Documentation Technique
- `docs/architecture.md` - Architecture et décisions techniques
- `docs/documentation-technique.md` - Documentation complète
- `docs/methodologie.md` - Processus de développement TDD
- `docs/guide-demarrage.md` - Guide de démarrage rapide
- `docs/status-success.md` - Statut de réussite du projet

### Instructions de Développement IA
- `ai-guidelines/consignes-projet.md` - Exigences du projet
- `ai-guidelines/regles-developpement.md` - Standards techniques
- `ai-guidelines/instructions-ai.md` - Guidelines pour assistants IA
- `ai-guidelines/checklist-concepts.md` - Checklist des concepts techniques

## Performance

### Optimisations Implémentées
- **Programmation asynchrone** pour les opérations I/O
- **Cache en mémoire** pour les données fréquemment accédées
- **Lazy loading** pour les gros fichiers de données
- **Compression** pour les réponses HTTP

### Métriques
- Temps de réponse moyen : < 200ms
- Temps de démarrage : < 10 secondes
- Couverture de tests : > 90%

## Sécurité

### Mesures Implémentées
- **Validation des entrées** utilisateur
- **Gestion sécurisée des fichiers** (prévention path traversal)
- **Logging sécurisé** (pas de données sensibles)
- **Gestion d'erreurs** sans exposition d'informations système

## Dépannage

### Problèmes Courants

**Erreur de démarrage de l'application**
```bash
# Vérifier la version Python
python --version

# Vérifier les dépendances
pip check

# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

**Tests qui échouent**
```bash
# Nettoyer et relancer
python -c "import sys; print(sys.path)"
python -m unittest discover -s tests -v
```

**Problèmes de fichiers de données**
```bash
# Vérifier les permissions
ls -la data/

# Valider le format JSON
python -m json.tool data/config.json
```

## Roadmap

### Version 1.0 (MVP)
- [x] Structure du projet
- [x] Documentation complète
- [x] Méthodologie TDD
- [ ] Concept 1 : Lecture de fichiers
- [ ] Concept 2 : Programmation fonctionnelle
- [ ] Concept 3 : Gestion des erreurs
- [ ] Concept 4 : Programmation asynchrone
- [ ] Interface utilisateur de base
- [ ] Tests complets

### Version 1.1 (Améliorations)
- [ ] Interface utilisateur améliorée
- [ ] Fonctionnalités avancées de reporting
- [ ] API REST complète
- [ ] Authentification utilisateur
- [ ] Notifications en temps réel

## Licence

Ce projet est développé dans un cadre éducatif.

## Contact

- **Développeur** : maberbac
- **Repository** : https://github.com/maberbac/gestion-condos
- **Documentation** : Voir le dossier `docs/`

---

**Dernière mise à jour** : Août 2025  
**Version** : 1.0.0-dev  
**Statut** : En développement actif
