# Intégration de Contexte Projet

## Intégration Automatique des Instructions

### Fichiers d'Instructions Obligatoires
L'agent IA doit automatiquement lire et intégrer :

1. **Instructions Principales** :
   - `.github/copilot-instructions.md` - Directives universelles
   - `instructions/instructions-ai.md` - Instructions spécifiques au projet actuel

2. **Contexte Projet Complet** :
   - `instructions/regles-developpement.md` - Standards de développement
   - `instructions/consignes-projet.md` - Exigences et contraintes
   - Tous les fichiers `.md` dans `docs/` - Documentation technique
   - Tous les fichiers `.md` dans `prompts/` - Templates et directives

### Règles d'Intégration
- **Lecture automatique** : Tous ces fichiers sont consultés avant chaque réponse
- **Priorisation intelligente** : Instructions spécifiques > Directives universelles
- **Détection de conflits** : Signaler toute contradiction entre sources
- **Cohérence maintenue** : Assurer l'harmonie entre tous les documents

## Comment Utiliser Ces Directives

### Pour le Projet Actuel (Gestion Condos Python/Flask)
Le projet actuel démontre des concepts techniques spécifiques. Lors du travail sur ce projet :

1. **Référencer les Fichiers Spécifiques au Projet** :
   - `instructions/instructions-ai.md` - Contexte et contraintes du projet
   - `instructions/regles-developpement.md` - Standards de développement
   - `instructions/consignes-projet.md` - Exigences du projet

2. **Appliquer les Directives Universelles** :
   - Utiliser les checklists de `development-checklists.md`
   - Suivre les standards de documentation de `documentation-standards.md`
   - Appliquer les patterns spécifiques Python de `language-guidelines.md`

### Pour les Projets Futurs
Ces directives sont conçues pour être réutilisables :

1. **Copier le dossier `.github/ai-guidelines/`** vers de nouveaux projets
2. **Mettre à jour le contexte spécifique au projet** dans `copilot-instructions.md` principal
3. **Adapter les directives de langage** basées sur la stack technologique
4. **Personnaliser les checklists** pour les exigences spécifiques au projet

## Intégration avec les Instructions Existantes

### Ordre de Priorité
Quand il y a des conflits ou chevauchements, suivre cette priorité :

1. **Instructions spécifiques au projet** (`instructions/instructions-ai.md`, `consignes-projet.md`)
2. **Standards de développement projet** (`instructions/regles-developpement.md`)
3. **Directives universelles IA** (fichiers `.github/ai-guidelines/`)
4. **Conventions spécifiques au langage** (pratiques standard pour le langage de programmation)
5. **Standards d'équipe ou organisationnels** (si applicable)

### Règles Anti-Versioning
- **JAMAIS** créer de fichiers CHANGELOG, VERSION, RELEASE, ou similaires
- **JAMAIS** documenter l'historique des versions ou changements
- **TOUJOURS** se concentrer sur la documentation fonctionnelle actuelle
- **SIGNALER** si une demande semble requérir du versioning pour redirection

### Combinaison d'Instructions
L'agent IA devrait :
- Toujours lire automatiquement tous les fichiers .md pertinents
- Appliquer les checklists universelles
- Utiliser les directives spécifiques au langage appropriées à la stack technologique actuelle
- Respecter les contraintes et exigences spécifiques au projet
- Générer la documentation selon les standards définis ici
- Éviter absolument la création de fichiers de versioning

## Personnalisation pour Différents Types de Projets

### Applications Web
- Se concentrer sur la documentation API et les directives d'interface utilisateur
- Mettre l'accent sur les considérations de sécurité dans les commentaires de code
- Documenter les procédures de déploiement et configuration

### Applications Desktop
- Mettre l'accent sur la documentation d'expérience utilisateur
- Se concentrer sur les détails d'implémentation spécifiques à la plateforme
- Documenter l'installation et les exigences système

### Bibliothèques/Frameworks
- Prioriser la documentation API et les exemples
- Se concentrer sur les directives d'intégration
- Documenter les considérations de compatibilité descendante

### Traitement de Données/Analytique
- Mettre l'accent sur la documentation de flux de données
- Se concentrer sur les considérations de performance et scalabilité
- Documenter les formats de données et logique de transformation

## Maintenance et Évolution

### Mises à Jour Régulières
Ces directives devraient être révisées et mises à jour :
- Quand de nouvelles fonctionnalités de langage ou meilleures pratiques émergent
- Quand les exigences du projet changent significativement
- Quand de nouveaux outils ou frameworks sont adoptés
- Basé sur les retours d'expérience de développement

### Contrôle de Version
- Suivre les changements à ces directives dans le contrôle de version
- Documenter le raisonnement derrière les changements significatifs
- Maintenir la compatibilité descendante quand possible
- Communiquer les changements à tous les membres de l'équipe

### Amélioration Continue
Encourager les retours et suggestions pour :
- Des éléments de checklist plus efficaces
- De meilleurs templates de documentation
- Des directives spécifiques au langage améliorées
- Des opportunités d'automatisation renforcées

## Référence Rapide

### Avant de Commencer Toute Tâche
1. Vérifier les exigences et contraintes spécifiques au projet
2. Réviser la checklist de pré-implémentation
3. Identifier quels concepts techniques doivent être démontrés
4. Planifier l'approche de documentation et tests

### Pendant le Développement
1. Suivre les directives de codage spécifiques au langage
2. Appliquer les standards de documentation appropriés
3. Implémenter une gestion d'erreurs appropriée
4. Ajouter des commentaires significatifs expliquant la logique métier

### Après Avoir Complété Toute Tâche
1. Parcourir la checklist de post-implémentation
2. Vérifier que la documentation est complète et précise
3. S'assurer que le code suit les patterns établis
4. Mettre à jour toute documentation technique affectée

### En Cas de Doute
1. Poser des questions spécifiques sur les exigences
2. Proposer des approches alternatives avec les compromis
3. Référencer ces directives pour les pratiques standard
4. Préférer la communication claire et la documentation
