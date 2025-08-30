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
- [ ] Les cas limites sont considérés et gérés
- [ ] Le logging est implémenté où approprié

### Intégration
- [ ] Le code s'intègre correctement avec les composants existants
- [ ] Aucun changement incompatible n'est introduit
- [ ] Les dépendances sont correctement gérées
- [ ] La configuration est externalisée quand approprié

### Préparation aux Tests
- [ ] Le code est structuré pour faciliter les tests
- [ ] Les scénarios de test sont identifiables
- [ ] Les points de mock sont clairs pour les tests unitaires
- [ ] Les considérations de tests d'intégration sont documentées

## Checklist Communication

### Lors de Demandes de Clarification
- [ ] Des questions spécifiques sont formulées
- [ ] Le contexte est fourni pour les questions
- [ ] Des approches alternatives sont suggérées quand possible
- [ ] L'impact des différents choix est expliqué

### Lors de Fourniture de Solutions
- [ ] La justification de la solution est expliquée
- [ ] Les compromis sont mentionnés quand pertinents
- [ ] Les approches alternatives sont notées si applicable
- [ ] Les prochaines étapes ou actions de suivi sont claires

### Lors de Documentation
- [ ] Le but et le contexte sont clairement énoncés
- [ ] Les exemples d'utilisation sont pratiques et complets
- [ ] Les prérequis et dépendances sont listés
- [ ] Les informations de dépannage sont incluses

## Critères de Qualité

### Avant de Soumettre du Code
- [ ] Le code compile/s'exécute sans erreurs
- [ ] La fonctionnalité de base est vérifiée
- [ ] La documentation est complète et précise
- [ ] Le code suit les patterns établis du projet

### Avant de Marquer Complet
- [ ] Tous les éléments de checklist sont vérifiés
- [ ] Toute hypothèse ou limitation est documentée
- [ ] Les points d'intégration sont testés ou vérifiés
- [ ] Les fonctionnalités orientées utilisateur incluent la documentation d'utilisation
- [ ] Aucun fichier CHANGELOG, VERSION, ou RELEASE n'a été créé
- [ ] La documentation se concentre sur la fonctionnalité, pas le versioning
- [ ] Les fichiers utilitaires ou temporaires sont correctement placés dans `tmp/`
