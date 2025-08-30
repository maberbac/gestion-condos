# Instructions et Guidelines pour l'IA

Ce répertoire contient toutes les instructions, directives et contextes spécifiques pour les assistants IA travaillant sur ce projet.

## Structure

```
ai-guidelines/
├── README.md                # Ce fichier - Vue d'ensemble du répertoire
├── checklist-concepts.md    # Checklist des 4 concepts techniques obligatoires
├── consignes-projet.md      # Exigences et contraintes du projet
├── debut-session.md         # Guide de début de session pour l'IA
├── guidelines-code.md       # Standards de code et bonnes pratiques
├── instructions-ai.md       # Instructions spécifiques au projet
└── regles-developpement.md  # ⭐ MIS À JOUR - Règles avec standards TDD et mocking
```

## Mise à Jour Récente (30 août 2025)

### Nouvelles Consignes de Mocking
- **Standards TDD stricts** intégrés dans `regles-developpement.md`
- **Checklist de validation** pour mocking des tests
- **Templates obligatoires** pour tests unitaires, intégration, acceptance
- **Anti-patterns documentés** à éviter absolument

### Instructions GitHub Copilot Étendues
- **Obligations strictes de mocking** des bases de données
- **Checklist étendue** avec validation d'isolation des tests
- **Règles d'indépendance** des tests (ordre d'exécution libre)

## Principe

**Séparation claire** : 
- **Ce répertoire** : Instructions pour l'IA, comportement, méthodologies
- **`docs/`** : Documentation du projet, guides utilisateur, spécifications techniques

## Nouveaux Standards Appliqués

### TDD avec Mocking Obligatoire
- **Cycle Red-Green-Refactor** avec tests écrits en premier
- **Repository mockés** dans tous les tests unitaires
- **Services mockés** dans tests d'intégration
- **Données isolées** dans tests d'acceptance

### Validation Automatique
- **Aucun accès base de données** dans les tests
- **Tests indépendants** dans n'importe quel ordre
- **Performance optimisée** sans I/O externe

## Règles d'utilisation

1. **Tous les fichiers d'instructions IA** doivent être placés ici
2. **Aucune documentation utilisateur** ne doit être dans ce répertoire
3. **Références croisées** avec `docs/` autorisées mais séparation maintenue
4. **Mise à jour automatique** des liens lors de déplacements de fichiers

## Fichiers actuels

Fichiers déplacés et organisés selon les nouvelles instructions :
- `.github/copilot-instructions.md` - Instructions principales GitHub Copilot
- `ai-guidelines/` - Toutes les instructions et guidelines IA (ce répertoire)

## Migration

**Terminée** : Tous les fichiers d'instructions IA ont été migrés vers ce répertoire selon les nouvelles règles d'organisation.
