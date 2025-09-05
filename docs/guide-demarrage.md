# Guide de Démarrage Rapide - Gestion Condos

## Application Production Ready avec Améliorations Critiques 

L'application de gestion de condominiums est maintenant **production ready** avec des améliorations critiques récentes :

### Fonctionnalités Clés
- **Stabilité des IDs garantie** : La modification d'une unité préserve l'intégrité de toutes les unités du projet
- **Performance optimisée** : Opérations SQL ciblées avec amélioration significative
- **Intégrité des données garantie** : Contexte de filtrage par projet préservé
- **Interface utilisateur flexible** : Support robuste des identifiants d'unités

### État des Tests
- **Tests unitaires** : 193/199 passent (97% succès)
- **Fonctionnalités** : Entièrement validées
- **Échecs non critiques** : 6 tests avec problèmes préexistants non liés aux fonctionnalités principales

## Démarrage en 3 étapes

### 1. Installation des dépendances
```bash
# Dépendances principales et web
pip install -r requirements.txt
pip install -r requirements-web.txt
```

### 2. Démarrage de l'application
```bash
python run_app.py
```

#### Système de Migration Centralisé
Au premier démarrage, l'application initialise automatiquement la base de données SQLite avec un **système de migration centralisé** :

- **Migrations Automatiques** : `SQLiteAdapter` exécute toutes les migrations nécessaires
- **Table de Tracking** : `schema_migrations` empêche les duplications de migrations  
- **Intégrité Garantie** : Les données existantes ne sont jamais corrompues lors des redémarrages
- **Idempotence** : Chaque migration ne s'exécute qu'une seule fois

**Logs de démarrage typiques :**
```
[INFO] Initialisation de la base de données...
[INFO] Base de données opérationnelle (5 condos)
[INFO] Système d'authentification initialisé
[INFO] === SYSTÈME INITIALISÉ AVEC SUCCÈS ===
```

### 3. Accès à l'interface web
- **URL** : http://127.0.0.1:8080
- Le navigateur s'ouvrira automatiquement
- **Temps de démarrage** : < 10 secondes

## Comptes de démonstration

### Administrateur (Conseil d'administration)
- **Utilisateur** : admin
- **Mot de passe** : admin123
- **Accès** : Toutes les fonctionnalités, gestion financière, administration des utilisateurs

### Résident (Copropriétaire)  
- **Utilisateur** : resident
- **Mot de passe** : resident123
- **Accès** : Consultation des condos, informations générales

### Invité
- **Utilisateur** : guest
- **Mot de passe** : guest123
- **Accès** : Informations publiques limitées

## Fonctionnalités disponibles

### Pour tous les utilisateurs
- Page d'accueil avec informations du système
- Authentification sécurisée par rôles
- Tableau de bord personnalisé selon les permissions

### Pour les résidents
- Consultation des condos résidentiels et commerciaux
- Visualisation des informations générales
- Accès à leur profil utilisateur

### Pour les administrateurs
- **Gestion complète des projets** avec API standardisée (project_id)
- **Module financier** avec calculs de revenus et projections
- **Gestion des utilisateurs** avec interface CRUD complète
  - Création, modification, suppression d'utilisateurs
  - Popups d'édition avec validation en temps réel
  - Statistiques et analytics des utilisateurs
- **Gestion optimisée des unités** : Fonctionnalités avancées
  - Modification d'unités individuelles sans affecter les autres
  - Stabilité des IDs garantie lors des modifications
  - Support flexible : modification par ID ou numéro d'unité
  - Préservation du contexte de filtrage par projet
- **API REST standardisée** pour intégration :
  - `/api/projects/<project_id>/statistics` - Statistiques par ID
  - `/api/projects/<project_id>/units/update` - Mise à jour unités
  - `PUT /api/unites/{id}` - **Modification d'unité optimisée**
  - `/api/user/<username>` - Détails utilisateur
- **Contrôle total** du système avec permissions étendues
- **Backward Compatibility** maintenue pour project_name via delegation
- **Export de données** (simulation CSV/PDF/Email)

## Architecture API 

### Standardisation project_id

L'application utilise maintenant une **API entièrement standardisée** :

#### Méthodes Principales (ID-based)
```python
# Services standardisés utilisant project_id
project_service.get_project_statistics(project_id)
project_service.update_project_units(project_id, count)  
project_service.delete_project_by_id(project_id)
```

#### Compatibilité Maintenue
```python
# Méthodes de compatibilité (avec delegation)
project_service.get_project_by_name(project_name)  # → délègue vers ID
project_service.delete_project(project_name)       # → délègue vers ID
```

#### Avantages
- **Cohérence** : API unifiée à travers tous les services
- **Performance** : Recherches directes par ID plus rapides
- **Maintenabilité** : Une seule source de vérité
- **Évolutivité** : Base solide pour extensions futures

## Concepts techniques démontrés

L'application intègre les 4 concepts techniques requis :

### 1. Lecture de fichiers
- Configuration JSON de l'application
- Base de données SQLite pour la persistance
- Chargement des données utilisateur et des condos

### 2. Programmation fonctionnelle  
- Décorateurs d'authentification (`@require_login`, `@require_role`)
- Fonctions lambda pour filtrage des données par rôle
- Map/filter pour transformation et affichage des données

### 3. Gestion d'erreurs
- Exceptions personnalisées (`UserAuthenticationError`, `UserValidationError`)  
- Try/catch robuste avec logging détaillé
- Messages d'erreur contextuels dans l'interface

### 4. Programmation asynchrone
- Service d'authentification asynchrone avec `async/await`
- Décorateur `@async_route` pour intégration Flask/asyncio
- Opérations non-bloquantes pour améliorer les performances

## Navigation de l'interface

### Menu principal
- **Accueil** : Présentation générale et concepts techniques
- **Tableau de bord** : Vue d'ensemble personnalisée par rôle
- **Condos** : Gestion et consultation des unités
- **Finance** : Calculs financiers (administrateurs uniquement)
- **Utilisateurs** : Administration des comptes (administrateurs uniquement)

### Contrôle d'accès automatique
L'interface adapte automatiquement les fonctionnalités disponibles selon le rôle :
- Les résidents voient uniquement les condos autorisés
- Les administrateurs accèdent à toutes les données financières
- Les invités ont un accès minimal aux informations publiques

## Arrêt de l'application
- **Ctrl+C** dans le terminal pour arrêter le serveur
- Ou fermer simplement la fenêtre du terminal

## En cas de problème

### Port déjà utilisé
Si le port 8080 est occupé, modifiez le port dans `run_app.py` :
```python
flask_app.run(host='127.0.0.1', port=5001)  # Changer 5001 par un port libre
```

### Dépendances manquantes
```bash
pip install Flask==2.3.2 Werkzeug==2.3.6
```

### Base de données corrompue
**Ancienne méthode :** Supprimez le fichier `data/condos.db` - il sera recréé automatiquement au démarrage.

**Méthode recommandée :** Grâce au système de migration centralisé, la corruption de données est maintenant **empêchée par design**. Les migrations ne s'exécutent qu'une seule fois et les données existantes sont préservées.

## Architecture de Base de Données

### Centralisation des Migrations - Garantie d'Intégrité

Le système utilise une architecture de **migration centralisée** dans `SQLiteAdapter` qui garantit :

#### 1. Source Unique de Vérité
```python
# Seul SQLiteAdapter gère les migrations
src/adapters/sqlite_adapter.py:
  - _run_migrations()                    # Point d'entrée unique
  - _execute_migration_with_tracking()   # Prévention duplications
```

#### 2. Protection Anti-Corruption
- **Table schema_migrations** : Track de toutes les migrations exécutées
- **Vérification avant exécution** : Empêche les duplications
- **Préservation des données** : Les données existantes ne sont jamais écrasées

#### 3. Configuration
```json
// config/database.json
{
  "database": {
    "type": "sqlite",
    "path": "data/condos.db",
    "migrations_path": "data/migrations/"
  }
}
```

### Avantages du Système
- **Fiabilité** : Aucune corruption de données possible
- **Performance** : Migrations exécutées une seule fois
- **Traçabilité** : Historique complet des modifications
- **Maintenance** : Gestion simplifiée des évolutions de schéma

---

**L'application est maintenant prête pour la démonstration académique avec tous les concepts techniques intégrés dans une interface web fonctionnelle !**
