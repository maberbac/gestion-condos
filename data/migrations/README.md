# Scripts de Migration Base de Données

Ce répertoire contient les scripts automatisés pour la migration complète de la base de données condos1.db.

## Architecture de Migration

### 1. Migration des Schémas (`scripts/recreate_schemas.py`)
Recréation automatique de toute la structure de la base de données :
- Tables avec types de colonnes
- Index et contraintes
- Clés étrangères
- Déclencheurs SQLite

### 2. Migration des Données (`scripts/recreate_inserts.py`)
Recréation automatique de toutes les données existantes :
- Extraction de toutes les lignes des tables
- Génération d'INSERT statements optimisés
- Ordre d'insertion respectant les dépendances
- Gestion des types de données et échappement

## Utilisation

### Migration Complète
```bash
# 1. Créer la structure de base de données
python scripts/recreate_schemas.py --output-dir data/migrations/ --backup

# 2. Insérer toutes les données
python scripts/recreate_inserts.py --output-dir data/migrations/ --with-report

# 3. Exécuter les migrations (optionnel)
python scripts/recreate_schemas.py --execute --target-db data/condos_new.db
python scripts/recreate_inserts.py --execute --target-db data/condos_new.db
```

### Options Avancées

#### Schémas
```bash
python scripts/recreate_schemas.py [options]
```
- `--source-db PATH` : Base source (défaut: data/condos1.db)
- `--output-dir PATH` : Répertoire de sortie (défaut: data/migrations/)
- `--target-db PATH` : Base cible pour exécution directe
- `--backup` : Créer une sauvegarde avant migration
- `--execute` : Exécuter directement les migrations générées
- `--with-indexes` : Inclure la recréation des index
- `--with-triggers` : Inclure la recréation des déclencheurs

#### Données
```bash
python scripts/recreate_inserts.py [options]
```
- `--source-db PATH` : Base source (défaut: data/condos1.db)
- `--output-dir PATH` : Répertoire de sortie (défaut: data/migrations/)
- `--target-db PATH` : Base cible pour exécution directe
- `--exclude-tables` : Tables à exclure (séparées par virgules)
- `--backup` : Créer une sauvegarde avant migration
- `--execute` : Exécuter directement les migrations générées
- `--with-report` : Générer un rapport de résumé des données

## Structure des Fichiers Générés

### Scripts de Migration
```
data/migrations/
├── 001_recreate_schemas_condos1db.sql        # Migration des schémas de condos1.db
├── 002_recreate_inserts_condos1db.sql        # Migration des données de condos1.db
├── data_summary_condos1db.json               # Rapport des données extraites
└── README.md                                 # Cette documentation
```

### Contenu des Rapports JSON

#### Schema Summary
```json
{
  "analysis_info": {
    "source_database": "data/condos1.db",
    "analyzed_at": "2025-09-05T15:48:21.123456",
    "total_tables": 8,
    "total_indexes": 4,
    "total_triggers": 0
  },
  "tables_summary": {
    "table_name": {
      "column_count": 6,
      "columns": ["col1", "col2", ...],
      "indexes": ["index_name", ...],
      "foreign_keys": [...]
    }
  }
}
```

#### Data Summary
```json
{
  "extraction_info": {
    "source_database": "data/condos1.db",
    "extracted_at": "2025-09-05T15:50:38.627083",
    "total_tables": 6,
    "total_rows": 28,
    "excluded_tables": ["sqlite_sequence", "schema_migrations"]
  },
  "tables_summary": {
    "table_name": {
      "column_count": 6,
      "columns": ["col1", "col2", ...],
      "row_count": 5
    }
  }
}
```

## Ordre de Migration

### Dépendances des Tables
1. **system_config** : Configuration système (indépendante)
2. **feature_flags** : Flags de fonctionnalités (indépendante)
3. **users** : Utilisateurs (indépendante)
4. **projects** : Projets de condos (référencé par units)
5. **units** : Unités de condos (dépend de projects)
6. **financial_records** : Enregistrements financiers (dépend d'autres tables)

### Sécurité des Migrations
- Désactivation temporaire des clés étrangères pendant les INSERT
- Transactions complètes pour assurer la cohérence
- Validation de l'existence des bases cibles
- Gestion des erreurs avec rollback automatique
- Échappement SQL approprié pour tous les types de données

## Caractéristiques Techniques

### Base de Données Source
- **Type** : SQLite 3
- **Tables** : 8 tables (6 avec données, 2 système)
- **Données** : 28 lignes au total (5 users, 2 projects, 16 units, 5 feature_flags)
- **Contraintes** : Clés étrangères, index, contraintes de validation

### Scripts Générés
- **SQL Standard** : Compatible SQLite 3
- **Sécurité** : Échappement approprié des guillemets et caractères spéciaux
- **Performance** : INSERT optimisés avec gestion des transactions
- **Maintenance** : Commentaires détaillés et progression visible

### Logging et Monitoring
- **Logging centralisé** : Utilisation du système de logs du projet
- **Progression en temps réel** : Affichage détaillé des étapes
- **Validation des données** : Vérification des types et formats
- **Rapports automatiques** : Génération de résumés JSON détaillés

## Cas d'Usage

### 1. Migration Complète de Base
Migration d'une base de données existante vers un nouveau serveur :
```bash
python scripts/recreate_schemas.py --source-db data/condos1.db --execute --target-db data/condos_new.db
python scripts/recreate_inserts.py --source-db data/condos1.db --execute --target-db data/condos_new.db
```

### 2. Sauvegarde avec Scripts
Génération de scripts de sauvegarde pour archivage :
```bash
python scripts/recreate_schemas.py --backup --with-indexes --with-triggers
python scripts/recreate_inserts.py --with-report
```

### 3. Migration Partielle
Migration excluant certaines tables sensibles :
```bash
python scripts/recreate_inserts.py --exclude-tables "financial_records,users" --with-report
```

### 4. Validation de Structure
Analyse de la structure existante sans migration :
```bash
python scripts/recreate_schemas.py --output-dir tmp/
python scripts/recreate_inserts.py --output-dir tmp/ --with-report
```

## Dépannage

### Problèmes Courants

1. **Base de données verrouillée**
   - Fermer toutes les connexions actives
   - Redémarrer l'application si nécessaire

2. **Permissions insuffisantes**
   - Vérifier les droits d'écriture sur les répertoires de sortie
   - Exécuter avec les privilèges appropriés

3. **Tables manquantes**
   - Vérifier que la base source existe et est accessible
   - Valider la structure avec les rapports JSON

4. **Erreurs de clés étrangères**
   - Les scripts désactivent automatiquement les FK pendant migration
   - Vérifier l'ordre d'insertion si problème persiste

### Validation des Migrations

Après migration, valider avec :
```bash
sqlite3 data/condos_new.db ".schema"
sqlite3 data/condos_new.db "SELECT name, COUNT(*) FROM sqlite_master WHERE type='table' GROUP BY name;"
```

## Maintenance

### Mise à Jour des Scripts
- Les scripts s'adaptent automatiquement aux changements de structure
- Régénérer les migrations après modifications majeures du schéma
- Tester sur une copie avant production

### Archivage
- Conserver les scripts générés pour traçabilité
- Archiver les rapports JSON pour analyse historique
- Documenter les changements dans le journal de développement

## Support

Pour toute question ou problème :
1. Consulter les logs détaillés des scripts
2. Vérifier les rapports JSON générés
3. Valider la structure source avec les outils d'analyse
4. Documenter les cas d'usage spécifiques pour amélioration continue

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
