# Guide de Démarrage Rapide - Gestion Condos

## Application Complètement Fonctionnelle

L'application de gestion de condominiums est maintenant **complètement implémentée** avec tous les concepts techniques intégrés et une suite de tests TDD de 393 tests (100% succès).

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
- **URL** : http://127.0.0.1:5000
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
- **Gestion complète des condos** avec statistiques détaillées
- **Module financier** avec calculs de revenus et projections
- **Gestion des utilisateurs** avec interface CRUD complète
  - Création, modification, suppression d'utilisateurs
  - Popups d'édition avec validation en temps réel
  - Statistiques et analytics des utilisateurs
- **API REST** pour intégration (`/api/user/<username>`)
- **Contrôle total** du système avec permissions étendues
- **Gestion des utilisateurs** avec création/modification de comptes
- **API REST** pour intégration avec d'autres systèmes
- **Export de données** (simulation CSV/PDF/Email)

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
Si le port 5000 est occupé, modifiez le port dans `run_app.py` :
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
