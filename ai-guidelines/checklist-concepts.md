# Checklist des 4 Concepts Obligatoires

## Avant d'implémenter une fonctionnalité

**Question systématique :** Cette fonctionnalité démontre-t-elle au moins un des concepts suivants ?

### 1. Lecture de Fichiers
- [ ] Lit des fichiers JSON/CSV/config
- [ ] Gère les erreurs de fichier (FileNotFoundError, format invalide)
- [ ] Exemple d'usage clair pour le rapport

### 2. Programmation Fonctionnelle  
- [ ] Utilise des fonctions pures (sans effets de bord)
- [ ] Emploie map(), filter(), reduce(), ou lambda
- [ ] Favorise l'immuabilité des données
- [ ] Transformations de données claires

### 3. Gestion des Erreurs par Exceptions
- [ ] Try/except appropriés
- [ ] Messages d'erreur informatifs
- [ ] Gestion robuste des cas d'échec
- [ ] Ne fait pas crasher l'application

### 4. Programmation Asynchrone
- [ ] Utilise async/await
- [ ] Emploie aiohttp ou asyncio
- [ ] Améliore les performances
- [ ] Gestion non-bloquante

## Validation Post-Implémentation

- [ ] Le concept est clairement visible dans le code
- [ ] Les commentaires expliquent le POURQUOI
- [ ] Un exemple peut être extrait pour le rapport
- [ ] La fonctionnalité est testable/démontrable

## Signal d'Alerte

**STOP** si aucun concept n'est démontré clairement
**STOP** si le code est trop complexe pour la deadline
**STOP** si ça n'ajoute pas de valeur au MVP

**CONTINUER** si au moins 1 concept est bien démontré
