# Intégration de Contexte Projet

## Intégration Automatique des Instructions

### Fichiers d'Instructions Obligatoires
L'agent IA doit automatiquement lire et intégrer le contenu de tous ces fichiers :

1. **Instructions Principales** :
   - `.github/copilot-instructions.md` - Directives universelles GitHub Copilot
   - `ai-guidelines/instructions-ai.md` - Instructions spécifiques au projet actuel

2. **Contexte Projet Complet** :
   - `ai-guidelines/regles-developpement.md` - Standards de développement TDD
   - `ai-guidelines/consignes-projet.md` - Exigences et contraintes du projet
   - `ai-guidelines/checklist-concepts.md` - Validation des 4 concepts techniques
   - Tous les fichiers `.md` dans `docs/` - Documentation technique du projet
   - Tous les fichiers `.md` dans `ai-guidelines/` - Instructions et contexte IA

### Règles d'Intégration
- **Lecture automatique** : Tous ces fichiers sont consultés avant chaque réponse
- **Priorisation intelligente** : Instructions spécifiques du projet > Directives universelles
- **Détection de conflits** : Signaler toute contradiction entre sources d'instructions
- **Cohérence maintenue** : Assurer l'harmonie entre tous les documents de contexte

## Architecture du Projet - Contexte Obligatoire

### Standards Techniques Appliqués
Le projet suit une **architecture hexagonale** avec des standards stricts :

#### Base de Données
- **SQLite principal** : `data/condos.db` comme base unique
- **Migrations centralisées** : TOUTES dans `SQLiteAdapter` uniquement
- **Configuration JSON** : `config/database.json` pour tous les paramètres
- **Protection anti-corruption** : Table `schema_migrations` pour tracking

#### Système de Logging
- **Import obligatoire** : `from src.infrastructure.logger_manager import get_logger`
- **Interdiction absolue** : Aucun `print()` autorisé dans le code
- **Niveaux appropriés** : debug/info/warning/error/critical selon le contexte
- **Configuration** : `config/logging.json` avec contrôle par module

#### Tests avec TDD Strict
- **Méthodologie obligatoire** : Tests écrits AVANT le code (Red-Green-Refactor)
- **Mocking complet** : AUCUNE base de données réelle dans les tests
- **Isolation totale** : Tests indépendants dans n'importe quel ordre
- **3 niveaux** : unit/ (184 tests), integration/ (108 tests), acceptance/ (101 tests)

### Concepts Techniques Obligatoires
Chaque développement doit intégrer au moins un de ces 4 concepts :

1. **Lecture de fichiers** : JSON/CSV avec gestion d'erreurs appropriée
2. **Programmation fonctionnelle** : map/filter/reduce, fonctions pures
3. **Gestion d'erreurs** : Exceptions personnalisées avec logging
4. **Programmation asynchrone** : async/await avec intégration Flask

## Comment Utiliser Ces Directives

### Pour le Projet Actuel (Gestion Condos Python/Flask)
Lors du travail sur ce projet, **TOUJOURS** :

1. **Consulter le Contexte Complet** :
   - `ai-guidelines/instructions-ai.md` - Contraintes et objectifs du projet
   - `ai-guidelines/regles-developpement.md` - Standards TDD et mocking
   - `ai-guidelines/consignes-projet.md` - Exigences techniques spécifiques
   - `.github/copilot-instructions.md` - Standards universels GitHub Copilot

2. **Appliquer les Standards Obligatoires** :
   - **Migrations** : Centralisation dans SQLiteAdapter UNIQUEMENT
   - **Logging** : Système centralisé, aucun print() autorisé
   - **Tests** : TDD avec mocking strict, aucune base réelle
   - **HTML/Python** : Séparation stricte, templates externes seulement
   - **Documentation** : Aucun emoji, style professionnel intemporel

3. **Valider avec les Checklists** :
   - `ai-guidelines/development-checklists.md` - Validation pré/post développement
   - `ai-guidelines/checklist-concepts.md` - Vérification des 4 concepts
   - Checklist intégrée dans `.github/copilot-instructions.md`

### Standards de Répertoire
```
ai-guidelines/                    # SEUL répertoire pour instructions IA
├── README.md                    # Vue d'ensemble (ce fichier)
├── instructions-ai.md           # Instructions spécifiques projet
├── regles-developpement.md      # Standards TDD et développement
├── consignes-projet.md          # Exigences et contraintes
├── checklist-concepts.md        # Validation 4 concepts techniques
├── development-checklists.md    # Checklists pré/post développement
├── documentation-standards.md   # Standards documentation et logging
├── language-guidelines.md       # Directives Python spécifiques
└── project-integration.md       # Intégration contexte (ce fichier)
```

**RÈGLE IMPORTANTE** : Le répertoire `ai-guidelines/` doit être à la **racine du projet**, pas dans `.github/`, selon les standards définis dans `.github/copilot-instructions.md`.

### Ordre de Priorité des Instructions
En cas de conflits ou chevauchements, suivre cette priorité :

1. **Standards universels** : `.github/copilot-instructions.md` (interdictions absolues)
2. **Instructions projet** : `ai-guidelines/instructions-ai.md` (contexte spécifique)
3. **Règles développement** : `ai-guidelines/regles-developpement.md` (méthodologie)
4. **Contraintes projet** : `ai-guidelines/consignes-projet.md` (exigences techniques)
5. **Documentation générale** : `docs/*.md` (référence technique)

### Intégration avec Documentation Existante

#### Séparation Claire des Responsabilités
- **`ai-guidelines/`** : Instructions pour l'IA, comportement, méthodologies, standards
- **`docs/`** : Documentation du projet, guides utilisateur, spécifications techniques
- **`.github/`** : Configuration GitHub et instructions GitHub Copilot universelles

#### Synchronisation Automatique
- **Arborescences** : Maintenir cohérence entre README.md dans chaque répertoire
- **Références croisées** : Liens appropriés entre ai-guidelines et docs
- **Mise à jour** : Synchroniser lors d'ajouts d'instructions ou changements structure

## Validation et Contrôle Qualité

### Checklist d'Intégration Automatique
Avant toute réponse, l'IA doit avoir :
- [ ] Lu tous les fichiers .md dans `ai-guidelines/`
- [ ] Consulté `.github/copilot-instructions.md` pour les standards universels
- [ ] Vérifié la cohérence entre les différentes sources d'instructions
- [ ] Identifié les contraintes spécifiques au projet actuel
- [ ] Compris les concepts techniques à démontrer
- [ ] Intégré les standards de qualité et méthodologies obligatoires

### Gestion des Conflits
Si des instructions contradictoires sont détectées :
1. **Signaler** le conflit explicitement à l'utilisateur
2. **Prioriser** selon l'ordre de priorité défini ci-dessus
3. **Demander clarification** si le conflit impact significativement la solution
4. **Documenter** la décision prise dans la réponse

### Mise à Jour Continue
- **Évolution** : Ces directives évoluent avec le projet
- **Feedback** : Intégrer les retours d'expérience dans les instructions
- **Cohérence** : Maintenir la synchronisation entre tous les fichiers d'instructions
- **Validation** : Vérifier régulièrement l'application effective des standards
