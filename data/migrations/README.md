# Scripts d'Initialisation de Base de Données

## Vue d'ensemble

Le répertoire `data/migrations/` contient les scripts d'initialisation pour configurer une nouvelle instance de la base de données du système de gestion de condos. Ces scripts sont conçus pour créer un environnement de démonstration complet avec des données de base.

## Scripts d'Initialisation

### 001_initial_schema.sql
**Rôle** : Création du schéma de base de données
- Tables fondamentales (condos, residents, financial_records, system_config)
- Contraintes et validations
- Index pour les performances
- Triggers de mise à jour automatique

### 002_users_authentication.sql
**Rôle** : Système d'authentification
- Table des utilisateurs avec mots de passe chiffrés
- Rôles et permissions (admin, resident, guest)
- Utilisateur administrateur par défaut

### 003_projects_units_tables.sql
**Rôle** : Tables pour les projets et unités
- Table des projets immobiliers
- Table des unités (condos, parking, commercial)
- Relations et contraintes entre projets et unités

### 004_populate_projects.sql
**Rôle** : Initialisation des projets de démonstration
- **Centre-Ville Plaza** : 8 unités de stationnement (Montréal)
- **Complexe Rivière** : 15 unités mixtes résidentiel/commercial (Québec)
- **Résidence Les Érables** : 12 unités résidentielles (Sherbrooke)
- **Tour Horizon** : 20 unités mixtes résidentiel/commercial (Gatineau)

### 005_populate_units.sql
**Rôle** : Initialisation des unités de démonstration
- **55 unités au total** réparties sur les 4 projets
- Types variés : résidentiel, commercial, stationnement
- Prix et superficies réalistes
- Statut "available" pour démonstrations

## Utilisation pour Nouvelles Instances

Ces scripts sont optimisés pour :

### Démonstrations
- Données réalistes et variées
- Projets dans différentes villes du Québec
- Mix de types d'unités (résidentiel, commercial, stationnement)
- Prix et superficies représentatifs du marché

### Environnements de Développement
- Base de données propre et cohérente
- Données suffisantes pour tester toutes les fonctionnalités
- Aucune dépendance sur des données externes

### Formation et Tests
- Scénarios complets pour la formation
- Données stables pour les tests d'acceptance
- Environnement reproductible

## Exécution des Scripts

Les scripts doivent être exécutés dans l'ordre numérique :

```bash
# Exécution manuelle (pour référence)
sqlite3 data/condos.db < data/migrations/001_initial_schema.sql
sqlite3 data/condos.db < data/migrations/002_users_authentication.sql
sqlite3 data/condos.db < data/migrations/003_projects_units_tables.sql
sqlite3 data/condos.db < data/migrations/004_populate_projects.sql
sqlite3 data/condos.db < data/migrations/005_populate_units.sql
```

Le système de migrations automatique du projet se charge normalement de cette exécution.

## Validation

Après l'exécution complète :
- **4 projets** doivent être créés
- **55 unités** doivent être créées
- **1 utilisateur admin** par défaut disponible
- Tables et contraintes fonctionnelles

## Notes Importantes

- Ces scripts **nettoient** les données existantes (DELETE FROM tables)
- Ils sont conçus pour des **nouvelles instances**, pas pour la mise à jour
- Les données sont **fictives** et optimisées pour la démonstration
- L'utilisateur admin par défaut doit être reconfiguré en production
