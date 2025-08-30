# Checklists pour Assistant de Développement

## Checklist Pré-Implémentation

Utiliser cette checklist avant de commencer toute tâche de développement :

### Intégration Contextuelle
- [ ] Lire automatiquement tous les fichiers .md du projet
- [ ] Identifier et intégrer les instructions spécifiques du projet
- [ ] Vérifier la cohérence entre différentes sources d'instructions
- [ ] Signaler tout conflit ou ambiguïté dans les directives

### Analyse des Exigences
- [ ] L'exigence est clairement comprise
- [ ] Le contexte et les contraintes sont identifiés
- [ ] Les concepts/patterns techniques à démontrer sont clairs
- [ ] Les critères de succès sont définis

### Planification Technique
- [ ] L'approche de solution est appropriée pour le langage/framework
- [ ] Les patterns de code existants et l'architecture sont considérés
- [ ] Les dépendances et points d'intégration sont identifiés
- [ ] La stratégie de gestion d'erreurs est planifiée

### Planification Documentation
- [ ] La stratégie de commentaires de code est définie
- [ ] Les besoins de documentation technique sont identifiés
- [ ] Les exigences de documentation utilisateur sont comprises
- [ ] Les exemples et scénarios d'utilisation sont planifiés
- [ ] La destination des fichiers temporaires est déterminée (`tmp/` si approprié)

## Checklist Post-Implémentation

Utiliser cette checklist après avoir complété toute tâche de développement :

### Qualité du Code
- [ ] Le code suit les conventions spécifiques au langage
- [ ] Les conventions de nommage sont cohérentes et significatives
- [ ] Les fonctions/méthodes ont des responsabilités uniques
- [ ] Le code est lisible et maintenable

### Complétude de la Documentation
- [ ] Les commentaires expliquent la logique métier et les décisions
- [ ] La documentation des fonctions/méthodes est complète
- [ ] Les algorithmes complexes sont bien documentés
- [ ] Les APIs publiques ont des exemples d'utilisation

### Gestion d'Erreurs
- [ ] Une gestion d'erreurs appropriée est implémentée
- [ ] Les messages d'erreur sont clairs et actionnables
- [ ] Les exceptions appropriées sont utilisées pour différentes conditions d'erreur
- [ ] Le logging des erreurs est approprié et informatif

### Tests et Validation
- [ ] **TESTS ÉCRITS EN PREMIER** : Méthodologie TDD strictement appliquée
- [ ] **MOCKING COMPLET** : Tous les appels base de données mockés dans tests unitaires
- [ ] **ISOLATION TOTALE** : Tests d'intégration avec base de test isolée
- [ ] **DONNÉES CONTRÔLÉES** : Tests d'acceptance avec données mockées
- [ ] **INDÉPENDANCE** : Tests peuvent s'exécuter dans n'importe quel ordre
- [ ] La couverture de tests est appropriée pour la fonctionnalité
- [ ] Les tests incluent les cas limites et conditions d'erreur
- [ ] Les tests documentent clairement leur objectif et attentes

### Centralisation des Migrations
- [ ] **VÉRIFIER** que toutes les migrations sont dans SQLiteAdapter uniquement
- [ ] **CONFIRMER** qu'aucun autre repository ne contient de logique de migration
- [ ] **S'ASSURER** que le tracking utilise la table schema_migrations
- [ ] **VALIDER** l'idempotence des migrations (ne s'exécutent jamais deux fois)

### Performance et Intégration
- [ ] La performance est acceptable pour l'usage prévu
- [ ] L'intégration avec les composants existants fonctionne correctement
- [ ] Les ressources système sont utilisées de manière appropriée
- [ ] Les dépendances externes sont gérées correctement

### Documentation de Finalisation
- [ ] La documentation technique est mise à jour
- [ ] Les guides d'utilisation sont créés ou mis à jour quand nécessaire
- [ ] Les exemples de code sont fournis quand approprié
- [ ] Les changements breaking sont documentés
- [ ] **AUCUN EMOJI** utilisé dans la documentation ou le code (sauf fichiers .html UI)
- [ ] **AUCUN PRINT()** utilisé - Tous les messages passent par le logger
- [ ] **VALIDATION FINALE** : Scanner tous les fichiers modifiés pour emojis ET prints interdits

## Checklist de Révision Post-Développement

### Révision Architecturale
- [ ] La solution respecte l'architecture hexagonale du projet
- [ ] Les patterns de séparation des responsabilités sont respectés
- [ ] L'extensibilité future est considérée dans la conception
- [ ] Les interfaces et abstractions sont appropriées

### Révision Sécurité
- [ ] Les validations d'entrée appropriées sont en place
- [ ] Les données sensibles sont gérées de manière sécurisée
- [ ] Les permissions et contrôles d'accès sont corrects
- [ ] Aucune information sensible n'est exposée dans les logs

### Révision Maintenance
- [ ] Le code sera facile à maintenir et étendre
- [ ] Les dépendances sont appropriées et minimales
- [ ] La configuration est externalisée quand approprié
- [ ] Les métriques et monitoring sont en place si nécessaire
