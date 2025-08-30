# Instructions pour l'Assistant IA - Projet Gestion Condos

## Contexte Projet
- **Projet** : Système de gestion de condominiums
- **Date limite** : Timeline définie du projet
- **Contraintes** : Temps limité et ressources spécifiées
- **Objectif** : MVP fonctionnel démontrant les 4 concepts techniques obligatoires

## Règles Absolues à Respecter

### 1. Priorité des Concepts Obligatoires
**TOUJOURS** vérifier que chaque fonctionnalité développée intègre au moins un des 4 concepts :
- Lecture de fichiers
- Programmation fonctionnelle  
- Gestion des erreurs par exceptions
- Programmation asynchrone

### 2. Technologies Imposées
- **Backend** : Python + Flask ou FastAPI (PAS d'autre framework)
- **Frontend** : HTML/CSS/JavaScript uniquement
- **Données** : Fichiers JSON/CSV (PAS de base de données complexe)
- **Structure** : Respecter l'arborescence définie dans consignes-projet.md

### 3. Approche MVP (Minimum Viable Product)
- **Simplicité d'abord** : Fonctionnalité de base fonctionnelle > fonctionnalité complexe incomplète
- **Démonstration claire** : Chaque concept doit être évident dans le code
- **Documentation intégrée** : Commenter le code pour le rapport

### 4. Formatage Markdown
- **Interdiction** : NE PAS ajouter d'astérisques (*) dans les fichiers .md sauf si strictement nécessaire
- **Principe** : Privilégier la lisibilité simple plutôt que la sur-formatage
- **Exception** : Utiliser le gras/italique uniquement pour les éléments vraiment importants

### 5. Maintenance Documentation Automatique
- **Mise à jour obligatoire** : TOUJOURS mettre à jour les fichiers .md concernés lors d'ajout de nouvelles instructions
- **Cohérence** : Vérifier que tous les documents restent synchronisés avec les changements
- **Traçabilité** : Documenter les nouvelles règles dans les fichiers appropriés

### 6. Arborescence README en Temps Réel
- **Obligation** : Les README.md doivent TOUJOURS refléter l'arborescence actuelle du répertoire
- **Automatique** : Lors de création/suppression de fichiers ou dossiers, mettre à jour immédiatement l'arborescence dans le README correspondant
- **Précision** : L'arborescence doit être exacte, complète et à jour
- **Scope** : Appliquer cette règle à tous les README.md du projet (racine, sous-dossiers, etc.)

## Instructions de Développement

**CONSULTER OBLIGATOIREMENT** : `instructions/regles-developpement.md`

Ce fichier contient tous les standards techniques, templates de validation, et signaux d'alerte à suivre durant le développement.

## Fichiers de Référence Importants

### À Consulter Régulièrement
- `instructions/regles-developpement.md` - Standards techniques et validation (OBLIGATOIRE)
- `instructions/consignes-projet.md` - Exigences du projet (OBLIGATOIRE)
- `instructions/gabarit-rapport-application-web.txt` - Structure du rapport
- `docs/fonctionnalites.md` - Scope défini du projet (OBLIGATOIRE)

### À Mettre à Jour
- `docs/architecture.md` - Décisions techniques prises
- Code avec commentaires pour le rapport

## Signaux d'Alerte

### M'arrêter si :
- Je propose une fonctionnalité sans lien avec les 4 concepts
- Je suggère une technologie non autorisée
- Le scope devient trop complexe pour la deadline
- On s'éloigne de l'objectif MVP

### Me rappeler de :
- Garder le code simple et commenté
- Prioriser les concepts obligatoires
- Respecter la deadline du 7 septembre
- **Mettre à jour les .md** lors d'ajout de nouvelles instructions
- **Synchroniser les arborescences** dans tous les README.md

## Templates de Validation

### Checklist Avant Implémentation
- [ ] Concept(s) obligatoire(s) identifié(s)
- [ ] Technologie autorisée
- [ ] Temps compatible avec deadline
- [ ] Contribue au MVP
- [ ] Commentaires pour rapport prévus

### Checklist Après Implémentation  
- [ ] Fonctionne correctement
- [ ] Gestion d'erreurs appropriée
- [ ] Code commenté pour rapport
- [ ] Concept clairement démontré
- [ ] Peut être expliqué simplement
- [ ] **Documentation .md mise à jour** si applicable
- [ ] **Arborescence README synchronisée** si nouveaux fichiers/dossiers

---

**OBJECTIF FINAL** : Application simple, fonctionnelle, bien documentée qui démontre clairement les 4 concepts obligatoires et respecte la timeline définie du projet.
