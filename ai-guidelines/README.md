# Instructions et Guidelines pour l'IA

Ce répertoire contient toutes les instructions, directives et contextes spécifiques pour les assistants IA travaillant sur ce projet.

## Structure

```
ai-guidelines/
├── README.md                    # Ce fichier - Vue d'ensemble du répertoire
├── api-standardization.md       # Documentation standardisation API project_id
├── checklist-concepts.md        # Checklist des 4 concepts techniques obligatoires
├── consignes-projet.md          # Exigences et contraintes du projet
├── debut-session.md             # Guide de début de session pour l'IA
├── guidelines-code.md           # Standards de code et bonnes pratiques
├── instructions-ai.md           # Instructions spécifiques au projet
├── regles-developpement.md      # Règles TDD et standards de développement
├── development-checklists.md    # Checklists pré/post développement
├── documentation-standards.md   # Standards documentation et logging
├── language-guidelines.md       # Directives Python spécifiques au projet
└── project-integration.md       # Guide d'intégration contextuelle
```

## Principe

Ce répertoire contient toutes les instructions et directives spécifiques pour les assistants IA travaillant sur ce projet de gestion de condominiums.

### Standards Appliqués
- **API project_id standardisée** : Tous les services utilisent project_id comme paramètre principal
- **Architecture de delegation** : Méthodes de compatibilité qui délèguent vers les méthodes ID-based
- **Services centralisés** : Routes web refactorisées pour utiliser les services centralisés
- **Tests complets** : Validation complète sans régression

### Guidelines IA Consolidées
- **Structure unifiée** : Tous les fichiers d'instructions IA centralisés ici
- **Standards appliqués** : Respect des directives `.github/copilot-instructions.md`

### Standards de Centralisation
- **Migrations de base de données** : Centralisées dans `SQLiteAdapter` uniquement
- **Système de logging** : Import obligatoire, interdiction des `print()`
- **Tests TDD stricts** : Mocking complet, isolation totale des tests
- **Séparation HTML/Python** : Templates externes obligatoires

### Guidelines Intégrées
- **Development Checklists** : Validation pré/post développement
- **Documentation Standards** : Normes de documentation et logging
- **Language Guidelines** : Directives Python spécifiques au projet
- **Project Integration** : Guide d'intégration contextuelle automatique

## Principe

**Séparation claire** : 
- **Ce répertoire** : Instructions pour l'IA, comportement, méthodologies
- **`docs/`** : Documentation du projet, guides utilisateur, spécifications techniques

## Standards Appliqués

### TDD avec Mocking Obligatoire
- **Cycle Red-Green-Refactor** avec tests écrits en premier
- **Repository mockés** dans tous les tests unitaires
- **Services mockés** dans tests d'intégration
- **Données isolées** dans tests d'acceptance

### Validation Automatique
- **Aucun accès base de données** dans les tests
- **Tests indépendants** dans n'importe quel ordre
- **Performance sans I/O externe**

## Règles d'utilisation

1. **Tous les fichiers d'instructions IA** doivent être placés ici
2. **Aucune documentation utilisateur** ne doit être dans ce répertoire
3. **Références croisées** avec `docs/` autorisées mais séparation maintenue
4. **Synchronisation automatique** des liens lors de déplacements de fichiers

## Fichiers actuels

Fichiers organisés selon les instructions :
- `.github/copilot-instructions.md` - Instructions principales GitHub Copilot
- `ai-guidelines/` - Toutes les instructions et guidelines IA (ce répertoire)

## Organisation

Tous les fichiers d'instructions IA sont organisés dans ce répertoire selon les règles d'organisation établies.
