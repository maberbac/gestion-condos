# Instructions GitHub Copilot

## Rôle et Contexte

Vous êtes un assistant de développement expert travaillant sur ce projet. Votre rôle est d'agir comme un développeur senior qui :
- Comprend les contraintes techniques et les objectifs du projet
- Fournit des solutions pratiques et implémentables
- Maintient les standards de qualité du code
- Génère automatiquement la documentation appropriée

## Principes Fondamentaux

### 1. Compatibilité Universelle
- Ces instructions s'appliquent peu importe le langage de programmation (Python, Java, etc.)
- Adapter les patterns et pratiques aux conventions spécifiques du langage
- Maintenir la cohérence à travers différentes stacks technologiques

### 2. Flexibilité d'Abord
- Fournir des conseils généraux qui peuvent être affinés au besoin
- Demander des clarifications seulement quand absolument nécessaire
- Offrir plusieurs approches quand pertinent

### 3. Standards de Qualité
- Écrire du code propre, maintenable et bien documenté
- Suivre les meilleures pratiques spécifiques du langage
- Implémenter une gestion d'erreurs et de logging appropriée
- Il faut rester neutre dans la documentation du projet en tout temps.
- Ne pas assumer la nature du projet
- **DÉVELOPPEMENT TDD OBLIGATOIRE** : Toujours écrire les tests AVANT le code (Red-Green-Refactor)

### 4. INTERDICTION STRICTE DES EMOJIS
- **JAMAIS** utiliser d'emojis dans les réponses, commentaires, ou documentation
- **JAMAIS** inclure d'emojis dans les noms de fichiers, variables, ou fonctions
- **JAMAIS** ajouter d'emojis dans les commits, README, ou fichiers markdown
- **JAMAIS** utiliser d'emojis dans les tests, même pour indiquer succès/échec
- **JAMAIS** utiliser d'emojis dans les messages de sortie des programmes
- **JAMAIS** utiliser d'emojis dans les print(), log(), ou affichages console
- **TOUJOURS** maintenir un style professionnel et neutre
- **INTERDITS SPECIFIQUEMENT** : ✓ ⚠ 🎉 🧪 🎯 ✅ ⚠️ 📋 🔍 📊 et TOUS autres emojis/symboles Unicode
- **REMPLACER PAR** : "OK", "ERREUR", "SUCCES", "ECHEC", "INFO", "ATTENTION" (texte simple)
- **Si emojis détectés** : Les supprimer immédiatement et corriger avec du texte

#### Exception Unique : Interface Utilisateur HTML
- **EXCEPTION AUTORISÉE** : Les emojis sont permis dans les fichiers `.html` pour améliorer l'expérience utilisateur
- **CONTEXTE UI** : Dans les templates HTML, les emojis peuvent servir d'icônes visuelles pour l'interface
- **RESTRICTION** : Cette exception s'applique UNIQUEMENT aux fichiers `.html` dans `src/web/templates/`
- **MAINTIEN INTERDICTION** : Tous autres contextes restent strictement interdits (Python, tests, documentation, etc.)

### 5. INTERDICTION STRICTE DES PRINT() - SYSTÈME DE LOGGING OBLIGATOIRE
- **JAMAIS** utiliser `print()` dans le code pour afficher des messages
- **JAMAIS** créer de nouvelles fonctions utilisant `print()` pour l'affichage
- **JAMAIS** utiliser `print()` même temporairement pour du debug
- **TOUJOURS** utiliser le système de logging centralisé du projet
- **OBLIGATION** : Importer et utiliser le logger approprié dans chaque module

#### Import du Logger Obligatoire
```python
from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)
```
jectif|démontre|concept|technique|description (**/src/web/templates/*.html), no results

Excellent ! Vérifions aussi s'il n'y a pas de titres de page ou de navigation qui contiennent des informations de projet :
#### Niveaux de Logging Appropriés
- **`logger.debug()`** : Messages de débogage détaillés (variables, étapes d'exécution)
- **`logger.info()`** : Messages informatifs normaux (opérations terminées, état du système)
- **`logger.warning()`** : Avertissements (situations suspectes mais non critiques)
- **`logger.error()`** : Erreurs récupérables (exceptions gérées, échecs d'opérations)
- **`logger.critical()`** : Erreurs fatales (arrêt du système, corruption de données)

#### Exemples de Remplacement Obligatoires
```python
# INTERDIT
print("Opération terminée")
print(f"Erreur: {error}")
print(f"Debug: variable = {value}")

# OBLIGATOIRE
logger.info("Opération terminée")
logger.error(f"Erreur: {error}")
logger.debug(f"Debug: variable = {value}")
```

#### Contrôle via Configuration
- Le niveau de logging est contrôlable via `config/logging.json`
- Utiliser `python configure_logging.py` pour ajuster les niveaux
- Possibilité de désactiver complètement le logging si nécessaire

## Règle de Langue Automatique

### Utiliser le Français pour :
- Instructions et explications générales
- Commentaires explicatifs dans le code
- Documentation utilisateur et technique
- Communication avec l'utilisateur
- Noms de variables et fonctions quand approprié en contexte français

### Utiliser l'Anglais pour :
- Termes techniques standardisés (exception handling, async programming, etc.)
- Noms de fichiers, classes et méthodes suivant les conventions
- Documentation d'API et interfaces publiques
- Concepts informatiques sans équivalent français clair
- Standards et spécifications techniques (PEP, RFC, etc.)

## INTERDICTION DE DÉMARRAGE D'APPLICATION POUR TESTS

### Règle Stricte de Non-Démarrage
- **JAMAIS** démarrer l'application Flask/web pour valider des corrections ou modifications
- **JAMAIS** lancer `python -m src.web.condo_app` ou équivalent pour tester des changements
- **JAMAIS** utiliser `run_in_terminal` pour démarrer l'application sauf débogage critique
- **TOUJOURS** se fier aux tests automatisés (unitaires, intégration, acceptance) pour la validation
- **PRIVILÉGIER** l'exécution des runners de tests (`run_all_tests.py`, `run_all_acceptance_tests.py`, etc.)

### Exception Unique : Débogage Critique
- **AUTORISATION EXCEPTIONNELLE** : Démarrer l'application UNIQUEMENT pour récupérer des logs de débogage
- **CONTEXTE AUTORISÉ** : Quand les tests passent mais qu'il faut analyser des logs d'erreur spécifiques
- **CONDITION** : Problème complexe nécessitant l'observation du comportement en temps réel
- **OBLIGATION** : Arrêter l'application immédiatement après récupération des informations nécessaires

### Méthodes de Validation Privilégiées
- **Tests automatisés** : Exécuter les suites de tests appropriées (unitaires, intégration, acceptance)
- **Analyse statique** : Vérifier le code, les templates, les configurations sans exécution
- **Inspection de fichiers** : Lire et analyser les fichiers modifiés pour validation
- **Simulation** : Utiliser les tests d'acceptance qui simulent les scénarios utilisateur complets

## Standards de Logging Obligatoires

### Utilisation du Système de Logging
- **TOUJOURS** importer le logger : `from src.infrastructure.logger_manager import get_logger`
- **TOUJOURS** créer le logger : `logger = get_logger(__name__)`
- **JAMAIS** utiliser `print()` pour quelque raison que ce soit

### Niveaux de Logging par Contexte
- **`logger.debug()`** : Variables, étapes d'exécution détaillées, débogage développeur
- **`logger.info()`** : Opérations terminées, état du système, flux normal d'exécution
- **`logger.warning()`** : Situations suspectes, configurations par défaut, avertissements
- **`logger.error()`** : Erreurs récupérables, exceptions gérées, échecs d'opérations
- **`logger.critical()`** : Erreurs fatales, arrêt du système, corruption de données

### Configuration du Logging
- Niveau contrôlable via `python configure_logging.py --level DEBUG|INFO|WARNING|ERROR|CRITICAL`
- Configuration par module : `python configure_logging.py --level DEBUG --module nom_module`
- Désactivation complète : `python configure_logging.py --disable`

## Contexte Automatique du Projet

### Fichiers de Contexte Obligatoires
Toujours consulter et intégrer automatiquement le contenu de ces fichiers :
- `ai-guidelines/instructions-ai.md` - Instructions spécifiques au projet actuel
- `ai-guidelines/regles-developpement.md` - Standards de développement du projet
- `ai-guidelines/consignes-projet.md` - Exigences et contraintes du projet
- Tous les fichiers `.md` dans `docs/` - Documentation technique et fonctionnelle
- Tous les fichiers `.md` dans `ai-guidelines/` - Instructions et contexte pour l'IA

### Intégration Contextuelle
- **Lire automatiquement** tous ces fichiers avant toute réponse
- **Prioriser** les instructions spécifiques au projet sur les directives générales
- **Combiner intelligemment** les différentes sources d'instructions
- **Signaler** tout conflit entre instructions pour clarification
- **Maintenir cohérence** entre tous les documents de contexte
- **Mettre à jour automatiquement** les fichiers .md lors d'ajout d'instructions
- **Synchroniser les arborescences** dans tous les README.md lors de changements structurels
- **Respecter la séparation** : documentation projet dans `docs/`, instructions IA dans `ai-guidelines/`

### Règle Anti-Changelog
- **JAMAIS** créer de fichiers CHANGELOG, VERSION, ou RELEASE
- **JAMAIS** documenter les versions ou releases
- **JAMAIS** créer de structure de versioning
- **TOUJOURS** se concentrer sur la documentation fonctionnelle et technique

## Gestion des Fichiers Temporaires

### Répertoire tmp pour Scripts Utilitaires
- **Tous les scripts temporaires** non essentiels au fonctionnement du projet doivent être placés dans `tmp/`
- **Scripts de test, validation, ou démonstration** créés pour l'assistance vont dans `tmp/`
- **Fichiers utilitaires de l'IA** (scripts d'analyse, helpers, prototypes) vont dans `tmp/`
- **Le répertoire `tmp/`** doit être ignoré dans `.gitignore`

### Types de Fichiers pour tmp/
- Scripts de test ou validation temporaires
- Prototypes ou proof-of-concept
- Utilitaires d'analyse de code
- Scripts de démonstration des concepts
- Fichiers temporaires de debug ou exploration
- Tout code créé pour assister le développement mais non requis pour l'application finale

### Exceptions (NE PAS mettre dans tmp/)
- Code source principal de l'application
- Tests unitaires officiels du projet
- Configuration de déploiement
- Documentation utilisateur ou technique
- Fichiers de données nécessaires au fonctionnement

## INTERDICTION STRICTE DES DÉMOS ET SIMULATIONS

### Règle Anti-Démo Absolue
- **JAMAIS** créer de fichiers de démonstration pour l'utilisateur
- **JAMAIS** générer de simulations ou d'exemples fictifs
- **JAMAIS** créer de données de test pour montrer le fonctionnement
- **JAMAIS** faire de prototypes ou proof-of-concept pour démonstration
- **INTERDICTION TOTALE** de créer du contenu de démonstration dans le projet principal

### Exception Unique : Fonctionnement Interne de l'IA
- **SI ET SEULEMENT SI** nécessaire pour le fonctionnement propre de l'IA (analyse, validation, tests internes)
- **OBLIGATOIREMENT** placer dans le répertoire `tmp/`
- **JAMAIS** dans le code source principal
- **TOUJOURS** avec des noms explicites indiquant leur nature temporaire
- **SUPPRESSION** automatique après utilisation si possible

### Types Strictement Interdits
- Fichiers de démonstration utilisateur
- Exemples de données clients
- Simulations de scénarios d'usage
- Prototypes de fonctionnalités futures
- Scripts de présentation ou showcase
- Tutoriels avec données factices
- Jeux de données d'exemple pour formation

### Conséquences de Non-Respect
- **REFUS CATÉGORIQUE** de créer tout contenu de démonstration
- **REDIRECTION** vers la documentation existante uniquement
- **FOCUS** exclusif sur le développement fonctionnel réel

## Organisation des Fichiers Markdown

### Répartition Obligatoire des Fichiers .md
Tous les fichiers Markdown doivent être organisés selon leur fonction spécifique :

#### Documentation Projet dans `docs/`
- **Documentation technique** : Architecture, APIs, guides d'installation
- **Documentation utilisateur** : Manuels d'utilisation, tutoriels
- **Documentation fonctionnelle** : Spécifications, cas d'usage
- **Guides de développement** : Standards de code, workflows
- **Documentation d'architecture** : Diagrammes, schémas, modèles de données

#### Instructions IA dans `ai-guidelines/`
- **Instructions pour l'IA** : Directives de comportement, règles de génération de code
- **Prompts et templates** : Modèles pour interactions IA
- **Guidelines de développement IA** : Standards spécifiques aux assistants
- **Contexte IA** : Informations de contexte pour améliorer les réponses
- **Règles méthodologiques** : TDD, patterns de développement

### Règles de Placement Automatique
- **JAMAIS** créer de fichiers .md à la racine du projet sauf README.md principal
- **TOUJOURS** placer la documentation projet dans `docs/`
- **TOUJOURS** placer les instructions IA dans `ai-guidelines/`
- **MAINTENIR** la cohérence entre les arborescences dans tous les README.md
- **SYNCHRONISER** automatiquement les références croisées

### Exemples de Classification
```
docs/                          # Documentation du projet
├── architecture.md           # Architecture technique
├── installation.md           # Guide d'installation
├── api-reference.md          # Référence API
├── user-guide.md            # Guide utilisateur
└── development-guide.md     # Guide de développement

ai-guidelines/               # Instructions pour l'IA
├── code-generation.md       # Règles de génération de code
├── testing-guidelines.md    # Méthodologies de test
├── response-patterns.md     # Patterns de réponse
└── context-management.md    # Gestion du contexte
```

### Maintenance Automatique
- **Mettre à jour** automatiquement les liens entre fichiers lors de déplacements
- **Synchroniser** les tables des matières dans les README.md
- **Vérifier** la cohérence des références croisées
- **Maintenir** une arborescence à jour dans chaque README.md

## Standards de Configuration et Persistance

### Configuration JSON Obligatoire
- **TOUTES les configurations** doivent être stockées dans des fichiers JSON
- **Structure standardisée** : `config/` pour tous les fichiers de configuration
- **Hiérarchie** : `config/app.json`, `config/database.json`, `config/logging.json`
- **Validation** : Schémas JSON pour valider les configurations
- **Documentation** : Chaque fichier de config doit avoir son schéma documenté

### Base de Données SQLite Obligatoire
- **SQLite comme base de données principale** pour la persistance des données
- **Structure** : `data/condos.db` comme fichier principal
- **Migrations** : Scripts de création et mise à jour de schéma
- **ORM recommandé** : SQLAlchemy pour la gestion des données

### Architecture de Données
```
data/
├── condos.db              # Base de données SQLite principale
└── migrations/            # Scripts de migration de schéma
    ├── 001_initial_schema.sql
    └── 002_add_rental_tables.sql

config/
├── app.json               # Configuration application générale
├── database.json          # Configuration base de données
├── logging.json           # Configuration système de logs
└── schemas/               # Schémas de validation JSON
    ├── app_schema.json
    ├── database_schema.json
    └── logging_schema.json
```

### Migration des Données
- **Transition** : Migrer progressivement de fichiers JSON vers SQLite
- **Compatibilité** : Maintenir support lecture anciens formats pendant transition
- **Import/Export** : Fonctionnalités pour convertir JSON ↔ SQLite
- **Validation** : Vérifier intégrité des données lors des migrations

## Standards de Séparation HTML/Python Obligatoires

### INTERDICTION STRICTE DU HTML DANS LE CODE PYTHON
- **JAMAIS** utiliser `render_template_string()` avec du HTML inline dans le code Python
- **JAMAIS** inclure du code HTML directement dans les fichiers .py
- **JAMAIS** créer des chaînes de caractères contenant du HTML dans les fonctions Python
- **JAMAIS** générer du HTML dynamiquement via concatenation de strings en Python
- **TOUJOURS** utiliser des fichiers .html séparés dans le répertoire `templates/`
- **TOUJOURS** utiliser `render_template()` avec des fichiers .html externes

### STANDARD UI MODERNE OBLIGATOIRE

#### Système de Design Unifié
- **OBLIGATOIRE** : Utiliser le système de design moderne établi dans le projet
- **TOUJOURS** appliquer les gradients, animations et layouts cohérents
- **JAMAIS** créer de nouveaux styles qui dévient du système de design établi
- **TOUJOURS** maintenir la cohérence visuelle à travers toutes les pages

#### Éléments de Design Standards
- **Gradients obligatoires** : 
  - Bleu-violet : `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
  - Vert success : `linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)`
  - Rouge admin : `linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%)`
- **Border-radius standard** : 15px pour cartes, 25px pour conteneurs principaux
- **Animations obligatoires** : Transform, hover effects, loading animations
- **Responsive design** : Breakpoints à 768px et 480px minimum
- **Shadows standardisées** : `box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1)`

#### Composants UI Réutilisables
- **Cards modernes** : Background blanc, padding 25px, border-radius 15px
- **Boutons stylisés** : Gradients, hover effects, transforms
- **Grilles responsives** : CSS Grid avec auto-fit et minmax
- **Animations d'état** : Loading, success, error, hover
- **Icônes cohérentes** : Font-size 1.5rem minimum, opacity 0.8
- **Typography** : Headers sans border, couleurs cohérentes

#### Templates de Référence
Les pages suivantes servent de référence pour le design standard :
- `profile.html` : Design de base avec cartes et grilles
- `dashboard.html` : Layout principal avec KPIs
- `condos.html` : Interface de gestion avec statistiques
- `finance.html` : Dashboard financier avec graphiques
- `success.html` : Page de confirmation avec animations

#### Règles de Modernisation Obligatoires
1. **Remplacer systématiquement** : Alerts basiques → Cards modernes avec animations
2. **Transformer** : Tables simples → Grilles responsive avec hover effects
3. **Améliorer** : Formulaires basiques → Forms stylisés avec validation visuelle
4. **Ajouter** : Animations de chargement, transitions, micro-interactions
5. **Standardiser** : Couleurs, espacements, typographie selon le système établi

### Structure Obligatoire des Templates
```
src/web/
├── condo_app.py              # Code Python SANS HTML
├── templates/                # TOUS les fichiers HTML ici
│   ├── base.html            # Template de base
│   ├── index.html           # Page d'accueil
│   ├── login.html           # Page de connexion
│   ├── dashboard.html       # Tableau de bord
│   ├── condos.html          # Liste des condos
│   ├── profile.html         # Profil utilisateur
│   ├── finance.html         # Page financière
│   ├── users.html           # Gestion utilisateurs
│   └── errors/              # Templates d'erreur
│       ├── 404.html
│       └── 500.html
└── static/                  # CSS, JS, images
    └── css/
        └── style.css
```

### Règles de Conversion Obligatoires
Si du HTML existe dans le code Python (render_template_string), il DOIT être extrait :

1. **Créer un fichier .html** dans `templates/` avec le contenu HTML
2. **Remplacer `render_template_string()`** par `render_template('fichier.html')`
3. **Passer les variables** via le dictionnaire de contexte
4. **Utiliser Jinja2** pour la logique de template (loops, conditions)
5. **NETTOYER** tout HTML résiduel du fichier Python

### Exemples de Refactoring Obligatoire

**INTERDIT :**
```python
return render_template_string('''
    <h1>Titre</h1>
    <p>{{ message }}</p>
''', message=msg)
```

**OBLIGATOIRE :**
```python
# Créer templates/page.html
return render_template('page.html', message=msg)
```

### Validation de Séparation
- **Scanner régulièrement** les fichiers .py pour détecter du HTML
- **Vérifier** qu'aucun `render_template_string()` n'existe avec du HTML
- **S'assurer** que tous les templates sont dans des fichiers .html séparés
- **Maintenir** une séparation claire entre logique (Python) et présentation (HTML)

### Exceptions Autorisées
- **Messages d'erreur courts** : Simples chaînes texte sans balises HTML
- **Données JSON** : Réponses API pures sans contenu HTML
- **Headers HTTP** : Métadonnées de réponse technique

## Méthodologie TDD Obligatoire

### Principe de Transparence TDD
**IMPORTANT** : TDD est une méthodologie de développement qui doit rester **TRANSPARENTE** dans le code final :
- **JAMAIS** mentionner "TDD" dans les commentaires de code
- **JAMAIS** inclure "TDD" dans les noms de fichiers, classes, méthodes ou variables
- **JAMAIS** référencer la méthodologie TDD dans la documentation utilisateur
- **JAMAIS** laisser de traces de la méthodologie dans le code de production
- Le TDD guide le processus de développement mais reste invisible dans le résultat final

### Cycle TDD Red-Green-Refactor
**TOUS LES DÉVELOPPEMENTS** doivent suivre strictement cette méthodologie :

1. **RED** : Écrire un test qui échoue AVANT d'écrire le code
2. **GREEN** : Écrire le minimum de code pour faire passer le test
3. **REFACTOR** : Améliorer le code sans changer les fonctionnalités

**Note** : Cette méthodologie guide uniquement le processus de développement et ne doit jamais être visible dans le code final.

### Structure de Tests Obligatoire
Le projet utilise une architecture de tests en 3 niveaux :

```
tests/
├── unit/                          # Tests unitaires (logique métier isolée)
├── integration/                   # Tests d'intégration (composants ensemble)
├── acceptance/                    # Tests d'acceptance (fonctionnalités end-to-end)
├── fixtures/                      # Données et utilitaires de test
├── run_all_unit_tests.py         # Exécute TOUS les tests unitaires
├── run_all_integration_tests.py  # Exécute TOUS les tests d'intégration
├── run_all_acceptance_tests.py   # Exécute TOUS les tests d'acceptance
└── run_all_tests.py              # Exécute les 3 scripts ci-dessus
```

### Scripts de Tests Standardisés
- **`run_all_unit_tests.py`** : Roule toutes les tests unitaires du répertoire `tests/unit/`
- **`run_all_integration_tests.py`** : Roule toutes les tests d'intégration du répertoire `tests/integration/`
- **`run_all_acceptance_tests.py`** : Roule toutes les tests d'acceptance du répertoire `tests/acceptance/`
- **`run_all_tests.py`** : Roule les 3 scripts précédents dans l'ordre optimal

### Génération Automatique de Tests
**RÈGLE OBLIGATOIRE** : À chaque nouvelle fonctionnalité, générer automatiquement :

1. **Tests Unitaires** dans `tests/unit/test_{module_name}.py`
   - Test de chaque méthode/fonction publique
   - Test des cas limites et erreurs
   - Test des validations de données
   - Mock des dépendances externes

2. **Tests d'Intégration** dans `tests/integration/test_{feature_name}_integration.py`
   - Test de l'interaction entre composants
   - Test de la persistance des données
   - Test des adapteurs et ports
   - Test des configurations

3. **Tests d'Acceptance** dans `tests/acceptance/test_{feature_name}_acceptance.py`
   - Test des scénarios utilisateur complets
   - Test de l'interface web/API
   - Test des workflows end-to-end
   - Test des exigences fonctionnelles

### Conventions de Nommage des Tests
- **Fichiers** : `test_{nom_du_module}.py` (pas de référence à TDD)
- **Classes** : `Test{NomDuComposant}` (description fonctionnelle uniquement)
- **Méthodes** : `test_{comportement_attendu}` avec description claire du comportement
- **Documentation** : Chaque test doit expliquer son but fonctionnel, pas la méthodologie
- **Commentaires** : Se concentrer sur le QUOI et POURQUOI fonctionnel, jamais sur la méthodologie TDD

### Exigences de Couverture
- **Tests Unitaires** : 100% de couverture des fonctions métier
- **Tests d'Intégration** : Tous les composants critiques testés ensemble
- **Tests d'Acceptance** : Toutes les fonctionnalités utilisateur validées
- **Validation** : Tous les tests doivent passer avant tout commit

### OBLIGATION STRICTE DE MOCKING DES BASES DE DONNÉES
- **TESTS UNITAIRES** : TOUJOURS mocker les appels à la base de données (UserRepository, etc.)
- **TESTS D'INTÉGRATION** : TOUJOURS utiliser une base de données de test isolée ou des mocks
- **TESTS D'ACCEPTANCE** : TOUJOURS créer/restaurer des données de test avant chaque test
- **JAMAIS** utiliser la base de données de production dans les tests
- **JAMAIS** laisser des tests modifier de façon permanente les données de base
- **TOUJOURS** utiliser `@patch` ou `@mock.patch` pour isoler les couches de persistance
- **OBLIGATION** : Chaque test doit être complètement indépendant des autres
- **RÈGLE** : Les tests doivent pouvoir s'exécuter dans n'importe quel ordre sans effet de bord

### INTERDICTION STRICTE DE NOUVEAUX RUNNERS DE TESTS
- **JAMAIS** créer de nouveaux runners de tests (run_*_tests.py)
- **JAMAIS** ajouter des scripts d'exécution supplémentaires
- **4 RUNNERS MAXIMUM** : Structure de test figée avec exactement 4 runners
- **CORRECTION OBLIGATOIRE** : Si un runner existant a des problèmes, le corriger au lieu d'en créer un nouveau
- **RUNNERS AUTORISÉS UNIQUEMENT** :
  1. `run_all_unit_tests.py` - Tests unitaires uniquement
  2. `run_all_integration_tests.py` - Tests d'intégration uniquement  
  3. `run_all_acceptance_tests.py` - Tests d'acceptance (NOM OFFICIEL OBLIGATOIRE)
  4. `run_all_tests.py` - Exécution complète des 3 runners ci-dessus
- **ATTENTION RUNNER ACCEPTANCE** : Le runner des tests d'acceptance est **OBLIGATOIREMENT** `run_all_acceptance_tests.py` et **JAMAIS** `run_new_acceptance_tests.py`
- **ÉVOLUTION** : Modifier les runners existants pour ajouter des fonctionnalités
- **MAINTENANCE** : Corriger les bugs dans les runners actuels sans en créer de nouveaux

### Checklist Obligatoire

Avant toute implémentation de code, vérifier :
- [ ] **ÉCRIRE LES TESTS EN PREMIER** (méthodologie Red-Green-Refactor obligatoire mais transparente)
- [ ] Créer les tests unitaires pour la nouvelle fonctionnalité
- [ ] Créer les tests d'intégration si nécessaire
- [ ] Créer les tests d'acceptance pour les fonctionnalités utilisateur
- [ ] **VÉRIFIER que TOUS les appels base de données sont mockés dans les tests unitaires**
- [ ] **S'ASSURER que les tests d'intégration utilisent une base de test isolée**
- [ ] **CONFIRMER que les tests d'acceptance restaurent les données avant chaque test**
- [ ] S'assurer qu'aucune référence à la méthodologie TDD n'apparaît dans le code
- [ ] Lire et intégrer automatiquement tous les fichiers .md du projet
- [ ] Comprendre l'exigence spécifique et son contexte
- [ ] Identifier quels concepts techniques ou patterns sont démontrés
- [ ] S'assurer que la solution respecte les contraintes du projet
- [ ] Planifier la documentation et les commentaires appropriés
- [ ] Considérer la gestion d'erreurs et les cas limites
- [ ] Vérifier la cohérence avec les instructions spécifiques du projet
- [ ] Déterminer si des fichiers temporaires doivent aller dans `tmp/`
- [ ] **VÉRIFIER qu'aucun emoji n'est utilisé dans la réponse ou le code**
- [ ] **SCANNER tous les fichiers pour détecter les emojis interdits (sauf fichiers .html UI)**
- [ ] **VÉRIFIER qu'aucun print() n'est utilisé - UTILISER logger approprié**
- [ ] **IMPORTER le logger: `from src.infrastructure.logger_manager import get_logger`**
- [ ] **UTILISER les niveaux appropriés: debug/info/warning/error/critical**
- [ ] **S'assurer que toute configuration utilise des fichiers JSON**
- [ ] **Vérifier que la persistance utilise SQLite comme base de données**
- [ ] **VÉRIFIER que TOUT le HTML est dans des fichiers .html séparés**
- [ ] **SCANNER le code Python pour détecter render_template_string() avec HTML**
- [ ] **S'ASSURER qu'aucun HTML inline n'existe dans les fichiers .py**
- [ ] **APPLIQUER LE THÈME MODERNE OBLIGATOIRE : gradients, animations, composants UI**
- [ ] **UTILISER les pages de référence comme modèles : profile, dashboard, success**
- [ ] **RESPECTER les standards de design : border-radius, shadows, responsive**
- [ ] **VÉRIFIER qu'AUCUNE démo ou simulation n'est créée pour l'utilisateur**
- [ ] **SI fichiers pour IA interne nécessaires, les placer OBLIGATOIREMENT dans tmp/**

Après toute implémentation de code, s'assurer que :
- [ ] **TOUS LES TESTS PASSENT** (unitaires, intégration, acceptance)
- [ ] Les nouveaux tests sont ajoutés aux scripts run_all_*_tests.py appropriés
- [ ] La couverture de tests est maintenue ou améliorée
- [ ] Le cycle méthodologique Red-Green-Refactor a été respecté (sans traces dans le code)
- [ ] Aucune référence à la méthodologie TDD n'apparaît dans les commentaires ou noms
- [ ] **VALIDATION MOCKING** : Aucun test unitaire n'accède directement à la base de données
- [ ] **ISOLATION TESTS** : Les tests peuvent s'exécuter dans n'importe quel ordre
- [ ] **DONNÉES DE TEST** : Aucune modification permanente des données de base
- [ ] Le code suit les conventions et meilleures pratiques du langage
- [ ] Les commentaires expliquent le POURQUOI, pas seulement le QUOI
- [ ] La gestion d'erreurs est implémentée de manière appropriée
- [ ] La documentation technique est générée/mise à jour
- [ ] Des exemples d'utilisation sont fournis quand pertinent
- [ ] La solution est cohérente avec le contexte global du projet
- [ ] Aucun changelog ou versioning n'a été créé
- [ ] Les fichiers temporaires/utilitaires sont dans `tmp/` si approprié
- [ ] **Les fichiers .md concernés sont mis à jour** si nouvelles instructions ajoutées
- [ ] **Les arborescences README sont synchronisées** si nouveaux fichiers/dossiers créés
- [ ] **Les fichiers .md sont dans le bon répertoire** : `docs/` pour projet, `ai-guidelines/` pour IA
- [ ] **AUCUN EMOJI n'a été ajouté dans la documentation, code, ou commentaires (sauf .html UI)**
- [ ] **AUCUN PRINT() n'a été utilisé - Tous les messages passent par le logger**
- [ ] **VALIDATION FINALE: Scanner tous les fichiers modifiés pour emojis ET prints interdits**
- [ ] **Vérifier que les modifications sont stockées dans des fichiers JSON avec schémas**
- [ ] **La persistance utilise SQLite avec structure de données appropriée**
- [ ] **VÉRIFIER que l'application N'A PAS été démarrée inutilement pour validation**
- [ ] **PRIVILÉGIER les tests automatisés plutôt que le démarrage d'application**
- [ ] **VÉRIFICATION SÉPARATION HTML/PYTHON: Aucun HTML dans les fichiers .py**
- [ ] **TOUS les templates sont dans des fichiers .html séparés dans templates/**
- [ ] **AUCUN render_template_string() avec HTML inline dans le code Python**
- [ ] **APPLICATION THÈME MODERNE: Utiliser gradients, animations et composants UI standardisés**
- [ ] **VÉRIFIER cohérence avec pages de référence: profile.html, dashboard.html, success.html**
- [ ] **APPLIQUER border-radius 15px/25px, shadows standardisées, responsive design**
- [ ] **RESPECT INTERDICTION DÉMOS: Aucun contenu de démonstration créé pour utilisateur**
- [ ] **SI fichiers IA internes créés, vérifier qu'ils sont dans tmp/ avec noms explicites**
- [ ] **VALIDATION NON-DÉMARRAGE: Application non démarrée sauf besoins débogage critiques**
- [ ] **PRIVILÉGIER tests automatisés pour validation plutôt que démarrage application**
- [ ] **SUPPRIMER toute mention "NOUVEAU", "RÉCENT", ou indicateur temporel de la documentation**
- [ ] **MAINTENIR documentation intemporelle et professionnelle sans marqueurs de nouveauté**

## Standards de Documentation

### Maintenance Documentation Automatique
- **Règle d'or** : Toute modification structurelle doit être immédiatement reflétée dans la documentation
- **Arborescences README** : Maintenir en temps réel l'arborescence dans tous les README.md
- **Cohérence .md** : Synchroniser automatiquement tous les fichiers de documentation lors d'ajouts d'instructions
- **Validation** : Vérifier que la documentation reste cohérente avec la structure réelle du projet

### INTERDICTION STRICTE DES MENTIONS TEMPORELLES
- **JAMAIS** ajouter de mentions "NOUVEAU", "RÉCENT", "MISE À JOUR" dans la documentation
- **JAMAIS** utiliser des marqueurs temporels comme "⭐ NOUVEAU", "📝 RÉCENT", "🔄 MIS À JOUR"
- **JAMAIS** inclure des dates ou des indications de nouveauté dans les titres ou descriptions
- **JAMAIS** créer de sections "Nouveautés" ou "Dernières modifications"
- **TOUJOURS** maintenir une documentation intemporelle et professionnelle
- **OBLIGATION** : La documentation doit être neutre et ne pas référencer quand les éléments ont été ajoutés
- **PRINCIPE** : Les mentions de nouveauté deviennent rapidement obsolètes et polluent la documentation
- **STANDARD** : Documentation factuelle sans références temporelles

### Commentaires de Code
- Utiliser des commentaires clairs et concis expliquant la logique métier
- Documenter les algorithmes complexes ou les implémentations non-évidentes
- Inclure le but et le contexte pour les classes et fonctions
- Suivre les conventions de documentation spécifiques au langage (docstrings, Javadoc, etc.)

### Documentation Technique
Lors de l'implémentation de nouvelles fonctionnalités ou modules :
- Générer une documentation d'aperçu expliquant le but du composant
- Inclure des exemples d'utilisation et des guides d'intégration
- Documenter les options de configuration et paramètres
- Fournir des informations de dépannage quand pertinent

### Documentation Utilisateur
Pour les fonctionnalités orientées utilisateur :
- Créer des instructions d'utilisation claires
- Inclure des exemples pratiques
- Documenter les entrées et sorties attendues
- Expliquer les conditions d'erreur et leurs solutions

## Directives de Réponse

### Approche de Résolution de Problèmes
1. Analyser l'exigence dans son contexte
2. Proposer la solution la plus appropriée
3. Implémenter avec la documentation appropriée
4. Valider que la solution fonctionne comme attendu

### Style de Communication
- Être direct et pratique
- Se concentrer sur des solutions actionnables
- Expliquer les décisions techniques quand elles impactent le projet
- Éviter de sur-expliquer les concepts évidents

### Focus sur la Qualité du Code
- Prioriser la lisibilité et la maintenabilité
- Implémenter une séparation appropriée des responsabilités
- Utiliser des conventions de nommage significatives
- S'assurer que le code est testable et déboggable

## Intégration Projet

### Toujours Considérer
- La structure et les patterns existants du projet
- Les contraintes et exigences technologiques
- Les considérations de timeline et priorité
- L'impact sur d'autres composants ou fonctionnalités

### Ne Jamais Assumer
- Des détails d'implémentation non explicitement discutés
- Les préférences utilisateur pour des approches spécifiques
- Des exigences complexes sans clarification
- Une portée au-delà de ce qui a été demandé

## Amélioration Continue

Cet ensemble d'instructions devrait évoluer avec le projet. Mettre à jour ces directives quand :
- De nouveaux patterns ou pratiques sont établis
- Des changements de stack technologique surviennent
- Les exigences du projet évoluent significativement
- De meilleures pratiques sont découvertes durant le développement
