# Guide d'Utilisation - Feature Flags

## Système de Feature Flags pour Modules Optionnels

Le système de feature flags permet de désactiver certains modules optionnels de l'application via la base de données SQLite, sans nécessiter de modification du code ou de redémarrage de l'application.

### Modules Contrôlés par Feature Flags

| Module | Flag Name | Description |
|--------|-----------|-------------|
| Module Finance | `finance_module` | Active ou désactive le module finance complet |
| Calculs Financiers | `finance_calculations` | Active ou désactive les calculs financiers avancés |
| Rapports Financiers | `finance_reports` | Active ou désactive les rapports financiers détaillés |
| Module Analytics | `analytics_module` | Active ou désactive le module d'analytics et statistiques |

### Consultation de l'État des Feature Flags

Pour voir l'état actuel des feature flags :

```sql
SELECT flag_name, is_enabled, description 
FROM feature_flags;
```

### Désactivation d'un Module

Pour désactiver le module finance :

```sql
UPDATE feature_flags 
SET is_enabled = 0 
WHERE flag_name = 'finance_module';
```

### Réactivation d'un Module

Pour réactiver le module finance :

```sql
UPDATE feature_flags 
SET is_enabled = 1 
WHERE flag_name = 'finance_module';
```

### Comportement Technique

- **Contrôle d'accès** : Les routes protégées retournent une erreur HTML simple si le module est désactivé
- **Lecture en temps réel** : L'état des feature flags est vérifié à chaque requête
- **Aucun cache** : Aucune mise en cache des valeurs de feature flags
- **Gestion d'erreurs** : Si la base de données est inaccessible, les modules sont considérés comme activés par défaut

### Modules Non Contrôlés

Les modules suivants ne sont **PAS** contrôlés par des feature flags et restent toujours disponibles :
- Gestion des projets et unités
- Authentification et gestion des utilisateurs
- Configuration système
- Modules de base essentiels au fonctionnement

### Sécurité

**Important** : Le contrôle des feature flags nécessite un accès direct à la base de données SQLite. Aucune interface web n'est fournie volontairement pour éviter les modifications accidentelles depuis l'application.

### Exemple d'Utilisation

```bash
# Se connecter à la base de données
sqlite3 data/condos.db

# Vérifier l'état actuel
SELECT flag_name, is_enabled FROM feature_flags WHERE flag_name = 'finance_module';

# Désactiver le module finance
UPDATE feature_flags SET is_enabled = 0 WHERE flag_name = 'finance_module';

# Vérifier la modification
SELECT flag_name, is_enabled FROM feature_flags WHERE flag_name = 'finance_module';

# Quitter SQLite
.exit
```

L'effet est immédiat : les utilisateurs ne pourront plus accéder aux fonctionnalités du module finance dès leur prochaine action.
