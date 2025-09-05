# Documentation du Projet

## Vue d'ensemble

Ce répertoire contient toute la documentation technique et utilisateur du projet de gestion de condominiums.

### Concepts Techniques Implémentés

- **Architecture Hexagonale** - Séparation claire des couches avec ports et adapteurs
- **Inversion de Contrôle** - Configuration flexible et testabilité maximale  
- **Repository Pattern** - Abstraction complète de la couche de persistance
- **Configuration Management** - Gestion centralisée JSON avec validation
- **Factory Pattern** - Création d'objets avec configuration flexible
- **Testing Strategy** - Tests unitaires, intégration et acceptance avec mocking complet
- **Logging Infrastructure** - Système de logs centralisé et configurable
- **Feature Flags** - Activation/désactivation dynamique des fonctionnalités
- **API Standardization** - Utilisation cohérente des project_id dans toutes les API

## Structure de la Documentation

```
docs/
├── README.md                                  # Ce fichier - Index de la documentation
├── architecture.md                           # Architecture technique hexagonale
├── ameliorations-critiques-unites.md         # Fonctionnalités critiques gestion des unités
├── conception-extensibilite.md               # Conception pour extensions futures
├── documentation-technique.md                # Documentation technique complète
├── fonctionnalites-details-utilisateur.md    # Guide détaillé consultation utilisateur
├── guide-demarrage.md                        # Guide de démarrage rapide
├── guide-gestion-erreurs.md                  # Guide complet de la gestion des erreurs HTTP
├── guide-logging.md                          # Documentation du système de logging
├── guide-tests-mocking.md                    # Guide complet des tests avec mocking
├── journal-developpement.md                  # Journal de développement et roadmap
└── methodologie.md                           # Méthodologie TDD et développement
```

## Documentation par Catégorie

### Migration et Base de Données
- **[Scripts de Migration](../data/migrations/README.md)** - Scripts automatisés de migration SQLite avec documentation complète

### Fonctionnalités Critiques
- **[Fonctionnalités Critiques Unités](ameliorations-critiques-unites.md)** - Fonctionnalités stabilité IDs et optimisations

### Architecture et Conception
- **[Architecture](architecture.md)** - Architecture hexagonale avec API standardisée project_id
- **[Conception Extensibilité](conception-extensibilite.md)** - Préparation aux extensions futures

### Méthodologie et Tests
- **[Méthodologie TDD](methodologie.md)** - Cycle TDD avec consignes de mocking strictes
- **[Guide Tests avec Mocking](guide-tests-mocking.md)** - Standards complets de test isolé

### Structure de Fichiers

Arborescence du projet après optimisation September 2025 :
```
gestion-condos/
├── src/                        # Code source principal
│   ├── core/                   # Logique métier et domaine
│   ├── infrastructure/         # Couche infrastructure (adapters, repositories)
│   ├── services/              # Services applicatifs
│   └── web/                   # Interface web Flask
├── tests/                     # Tests complets (413 tests, 100% succès)
│   ├── unit/                  # Tests unitaires (217)
│   ├── integration/           # Tests d'intégration (124) 
│   ├── acceptance/            # Tests d'acceptance (72)
│   └── fixtures/              # Données et utilitaires de test
├── config/                    # Configuration JSON centralisée
│   ├── app.json              # Configuration application
│   ├── database.json         # Configuration base de données
│   ├── logging.json          # Configuration logs
│   └── schemas/              # Schémas de validation
├── data/                      # Stockage SQLite
│   └── condos.db             # Base de données principale
├── docs/                      # Documentation projet
└── ai-guidelines/             # Instructions pour l'IA
```

### Fonctionnalités et Guides
- **[Guide de Démarrage](guide-demarrage.md)** - Installation et API standardisée project_id
- **[Guide Gestion des Erreurs](guide-gestion-erreurs.md)** - Système complet de gestion des erreurs HTTP
- **[Guide Logging](guide-logging.md)** - Configuration et utilisation du système de logs
- **[Fonctionnalités Détails Utilisateur](fonctionnalites-details-utilisateur.md)** - Guide complet de la consultation des détails utilisateur

### Documentation Technique
- **[Documentation Technique](documentation-technique.md)** - Spécifications complètes avec API standardisée

### Suivi de Projet
- **[Journal de Développement](journal-developpement.md)** - Historique et roadmap avec dernières implémentations

## Règles de Documentation

1. **Séparation claire** : Documentation projet ici, instructions IA dans `ai-guidelines/`
2. **Documentation synchronisée** : Maintenir la documentation synchrone avec le code
3. **Accessibilité** : Documentation claire pour utilisateurs et développeurs
4. **Cohérence** : Style et format uniformes

## Liens Utiles

- **Instructions IA** : Voir le répertoire `ai-guidelines/`
- **Code Source** : Voir le répertoire `src/`
- **Tests** : Voir le répertoire `tests/`
