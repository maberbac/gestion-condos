# Consignes de Développement - Application Web Gestion de Condos

## Objectifs Techniques à Intégrer (OBLIGATOIRES)

### 1. Lecture de Fichiers
- **Obligation** : Implémenter la lecture de fichiers dans l'application
- **Formats acceptés** : JSON, CSV ou fichiers de configuration
- **Exemples d'usage** : 
  - Données des unités de condo (JSON/CSV)
  - Configuration de l'application
  - Import/export de données financières
- **Gestion d'erreurs** : FileNotFoundError, erreurs de format

### 2. Programmation Fonctionnelle
- **Obligation** : Utiliser des concepts de programmation fonctionnelle
- **Éléments requis** :
  - Fonctions pures (sans effets de bord)
  - Utilisation de `map()`, `filter()`, `reduce()`
  - Fonctions lambda
  - Immuabilité des données quand possible
- **Exemples d'application** :
  - Filtrage des données de résidents
  - Transformation des données financières
  - Calculs de frais de copropriété

### 3. Gestion des Erreurs par Exceptions
- **Obligation** : Implémentation robuste de la gestion d'erreurs
- **Types d'erreurs à gérer** :
  - Erreurs de fichiers (lecture/écriture)
  - Erreurs de réseau (requêtes HTTP)
  - Erreurs de validation des données utilisateur
  - Erreurs de base de données
- **Structure** : try/except avec messages d'erreur informatifs

### 4. Programmation Asynchrone
- **Obligation** : Utiliser la programmation asynchrone
- **Technologies** : `asyncio`, `aiohttp` (Python) ou équivalent
- **Applications** :
  - Requêtes API externes
  - Traitement parallèle de données
  - Gestion des sessions utilisateur
  - Opérations de base de données non-bloquantes

## Technologies Imposées

### Backend Obligatoire
- **Python** avec **Flask** ou **FastAPI**
- **HTML/CSS/JavaScript** pour le frontend
- Intégration des 4 concepts techniques (voir ci-dessus)

### Structure de Fichiers Recommandée
```
gestion-condos/
├── app.py                 # Application principale
├── modules/
│   ├── lecteur_fichiers.py    # Lecture de fichiers
│   ├── gestionnaire_erreurs.py # Gestion d'exceptions
│   ├── utils_fonctionnel.py   # Fonctions pures
│   └── async_handler.py       # Code asynchrone
├── data/
│   ├── condos.json           # Données des unités
│   ├── residents.csv         # Données résidents
│   └── config.json           # Configuration
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── base.html
│   ├── index.html
│   └── [autres_pages].html
└── rapport/
    └── rapport-application-web.md
```

## Éléments Obligatoires - Échéance du projet

### 1. Code Source
- [ ] Application web fonctionnelle
- [ ] Archive ZIP contenant tout le code
- [ ] Fichiers de données d'exemple
- [ ] Instructions d'installation/exécution

### 2. Documentation (Rapport)
- [ ] **Résumé** : Description de l'application et technologies utilisées
- [ ] **Description de l'application** : Objectif, fonctionnalités, interface
- [ ] **Choix de l'application** : Justification du concept choisi
- [ ] **Lecture de fichiers** : Implémentation et exemples de code
- [ ] **Programmation fonctionnelle** : Utilisation et exemples
- [ ] **Gestion des erreurs** : Stratégies d'exception et exemples
- [ ] **Programmation asynchrone** : Implémentation et bénéfices
- [ ] **Code source principal** : Extraits commentés du code clé
- [ ] **Discussion et analyse** : Défis, forces, faiblesses

### 3. Présentation (Choisir UNE option)
- [ ] **Option A** : Vidéo de démonstration (MP4 dans l'archive)
- [ ] **Option B** : Rapport PDF détaillé

## Instructions de Développement

### Phase 1 : Planification (Priorité HAUTE)
1. **Définir le scope minimal** pour respecter la date du 7 septembre
2. **Identifier les fonctionnalités essentielles** qui démontrent les 4 concepts
3. **Préparer les fichiers de données** (JSON/CSV simples)

### Phase 2 : Développement Core
1. **Lecture de fichiers** : Commencer par cette fonctionnalité
2. **Structure de base** : Flask/FastAPI + templates HTML
3. **Intégration progressive** des 3 autres concepts

### Phase 3 : Finalisation
1. **Tests et débogage**
2. **Rédaction du rapport**
3. **Préparation de l'archive finale**

## Critères de Qualité Attendus

### Technique (Majoritaire)
- **Intégration des 4 concepts obligatoires**
- **Qualité et clarté du code**
- **Fonctionnalité de l'application**
- **Gestion appropriée des erreurs**

### Documentation
- **Complétude du rapport selon le gabarit**
- **Exemples de code pertinents**
- **Analyse critique de l'implémentation**

### Fonctionnel
- **Application fonctionnelle et utilisable**
- **Démonstration claire des concepts techniques**

## Contraintes de Temps
- **Date limite ferme** : Timeline définie du projet
- **Temps disponible limité** selon les ressources du projet
- **Priorité** : Concepts techniques > Fonctionnalités avancées
- **Stratégie** : Minimum viable product (MVP) qui démontre tous les concepts

---

**IMPORTANT** : Se concentrer sur la démonstration claire des 4 concepts obligatoires plutôt que sur la complexité des fonctionnalités. Un système simple mais bien documenté et intégrant tous les concepts sera plus efficace qu'un système complexe incomplet.
