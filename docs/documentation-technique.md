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

### Architecture générale
L'application suit une architecture web classique à trois niveaux :

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Présentation  │    │    Logique      │    │    Données      │
│   (Frontend)    │◄──►│   Métier        │◄──►│   (Fichiers)    │
│   HTML/CSS/JS   │    │  (Backend)      │    │   JSON/CSV      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Patterns architecturaux
- **MVC (Model-View-Controller)** : Séparation claire des responsabilités
- **RESTful API** : Interface standardisée pour les communications
- **Layered Architecture** : Organisation en couches logiques

### Flux de données
1. **Interface utilisateur** → Requêtes HTTP
2. **Routeur** → Distribution des requêtes
3. **Contrôleurs** → Logique métier
4. **Services** → Traitement des données
5. **Gestionnaires de fichiers** → Persistance

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
**Implémentation** : Opérations non-bloquantes avec asyncio
- Traitement parallèle des fichiers multiples
- Requêtes API externes asynchrones
- Gestion des sessions utilisateur
- Opérations de persistance en arrière-plan

**Technologies** :
```python
import asyncio
import aiohttp
import aiofiles
```

---

## Structure du projet

```
gestion-condos/
├── .github/                    # Instructions pour GitHub Copilot
│   ├── copilot-instructions.md
│   └── ai-guidelines/
├── docs/                       # Documentation
│   └── documentation-technique.md
├── instructions/               # Instructions spécifiques au projet
│   ├── instructions-ai.md
│   ├── regles-developpement.md
│   └── consignes-projet.md
├── prompts/                   # Templates et directives
│   └── checklist-concepts.md
├── tmp/                       # Fichiers temporaires (ignorés par Git)
├── src/                       # Code source principal
│   ├── app/                   # Application principale
│   │   ├── __init__.py
│   │   ├── main.py           # Point d'entrée
│   │   ├── routes/           # Routeurs et contrôleurs
│   │   ├── services/         # Logique métier
│   │   ├── models/           # Modèles de données
│   │   └── utils/            # Utilitaires
│   ├── static/               # Ressources statiques
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/            # Templates HTML
├── data/                     # Données de l'application
│   ├── residents.json
│   ├── unites.json
│   └── finances.csv
├── config/                   # Fichiers de configuration
│   ├── app_config.json
│   └── database_config.json
├── tests/                    # Tests unitaires et d'intégration
├── requirements.txt          # Dépendances Python
├── .gitignore
└── README.md
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

### Gestionnaire de résidents
**Responsabilité** : Gestion CRUD des informations des résidents
- Création, lecture, mise à jour, suppression
- Validation des données
- Recherche et filtrage

**Fichiers principaux** :
- `src/app/services/resident_service.py`
- `src/app/models/resident.py`
- `data/residents.json`

### Gestionnaire d'unités
**Responsabilité** : Gestion des unités de copropriété
- Association résidents-unités
- Calcul des charges par unité
- Historique des occupations

### Gestionnaire financier
**Responsabilité** : Suivi financier de la copropriété
- Calcul des frais de copropriété
- Suivi des paiements
- Génération de rapports
- Export des données comptables

### Interface utilisateur
**Responsabilité** : Présentation et interaction
- Pages HTML responsives
- Interface JavaScript interactive
- Validation côté client
- Communication avec l'API

---

## Base de données et stockage

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

### Stratégie de test
- **Tests unitaires** : Fonctions individuelles
- **Tests d'intégration** : Interaction entre composants
- **Tests fonctionnels** : Scénarios utilisateur complets
- **Tests de performance** : Charge et stress

### Structure des tests
```
tests/
├── unit/
│   ├── test_resident_service.py
│   ├── test_finance_service.py
│   └── test_utils.py
├── integration/
│   ├── test_api_endpoints.py
│   └── test_file_operations.py
├── functional/
│   └── test_user_scenarios.py
└── performance/
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
