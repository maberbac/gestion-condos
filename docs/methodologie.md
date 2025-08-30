# Méthodologie TDD - Projet Gestion Condos

## Table des Matières
1. [Philosophie TDD](#philosophie-tdd)
2. [Cycle TDD adapté](#cycle-tdd-adapté)
3. [Processus par concept technique](#processus-par-concept-technique)
4. [Standards de test](#standards-de-test)
5. [Gestion des priorités](#gestion-des-priorités)
6. [Outils et environnement](#outils-et-environnement)
7. [Validation des concepts](#validation-des-concepts)

---

## Philosophie TDD

### Principe fondamental : Test First
- **Red** → **Green** → **Refactor** : Le cycle TDD classique
- Tests écris AVANT le code d'implémentation
- Validation continue et immédiate des concepts techniques
- Détection rapide des erreurs et régressions

### Approche TDD adaptée au projet
- **Validation de concept** : Chaque test valide un aspect du concept technique
- **Documentation vivante** : Les tests servent de spécification
- **Confiance** : Code fonctionnel garanti à chaque étape
- **Simplicité** : Only code what's needed to pass the tests

### Avantages pour notre contexte
- **Rapidité** : Détection immédiate des problèmes
- **Qualité** : Code testé par design
- **Concepts clairs** : Chaque concept technique validé par ses tests
- **Maintenance** : Refactoring sécurisé grâce aux tests

---

## Cycle TDD adapté

### Le cycle Red-Green-Refactor pour chaque concept

```
                    CYCLE TDD POUR CHAQUE CONCEPT
                              
    ┌─────────────────────────────────────────────┐
    │             NOUVEAU CONCEPT                 │
    │        (Ex: Lecture fichiers)               │
    └─────────────────┬───────────────────────────┘
                      │
                      ▼
              ┌───────────────┐
              │   RED         │ ── Écrire un test qui échoue
              │               │    Test spécifique au concept
              │ Write Test    │    Définir le comportement attendu
              │ (Failing)     │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │   GREEN       │ ── Écrire le minimum de code
              │               │    pour faire passer le test
              │ Make it Work  │    Focus sur la fonctionnalité
              │ (Passing)     │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │   REFACTOR    │ ── Améliorer le code
              │               │    Sans casser les tests
              │ Clean Code    │    Optimiser et documenter
              │ (Optimized)   │
              └───────┬───────┘
                      │
                      ▼
         ┌─────────────────────┐
         │    CONCEPT VALIDÉ   │ ── Tous les tests passent
         │  Passer au suivant  │    Concept bien démontré
         └─────────────────────┘
```

### Phases détaillées du cycle

#### Phase RED : Écrire le test qui échoue
1. **Définir le comportement** : Que doit faire ce concept ?
2. **Écrire le test** : Test spécifique et focalisé
3. **Vérifier l'échec** : Le test doit échouer (pas d'implémentation)
4. **Clarifier l'objectif** : Le test exprime clairement l'attente

#### Phase GREEN : Faire passer le test
1. **Code minimal** : Juste ce qu'il faut pour passer le test
2. **Pas d'optimisation** : Focus sur la fonctionnalité
3. **Validation** : Le test passe maintenant
4. **Concept démontré** : La fonctionnalité de base fonctionne

#### Phase REFACTOR : Améliorer le code
1. **Nettoyer le code** : Améliorer la lisibilité
2. **Optimiser** : Performance et structure
3. **Documenter** : Commentaires et explications
4. **Valider** : Tous les tests continuent de passer

---

## Processus par concept technique

### 1. Lecture de fichiers (TDD)

#### Tests à écrire en priorité :
```python
import unittest

class TestFileReader(unittest.TestCase):
    def test_lire_fichier_json_valide(self):
        # RED: Test pour lire un fichier JSON correct
        pass

    def test_gerer_fichier_inexistant(self):
        # RED: Test pour gérer l'erreur de fichier manquant
        pass

    def test_gerer_json_invalide(self):
        # RED: Test pour gérer un JSON mal formaté
        pass
```

#### Cycle d'implémentation :
1. **RED** : Écrire test_lire_fichier_json_valide() → échec
2. **GREEN** : Implémenter fonction basique de lecture
3. **REFACTOR** : Améliorer la structure et documenter
4. **RED** : Écrire test_gerer_fichier_inexistant() → échec
5. **GREEN** : Ajouter gestion d'erreur fichier
6. **REFACTOR** : Optimiser la gestion d'erreurs
7. **Continuer** : Jusqu'à tous les aspects couverts

### 2. Programmation fonctionnelle (TDD)

#### Tests à écrire en priorité :
```python
import unittest

class TestFunctionalOps(unittest.TestCase):
    def test_transformer_donnees_avec_map(self):
        # RED: Test pour transformation avec map()
        pass

    def test_filtrer_donnees_avec_filter(self):
        # RED: Test pour filtrage avec filter()
        pass

    def test_aggreger_donnees_avec_reduce(self):
        # RED: Test pour agrégation avec reduce()
        pass
```

### 3. Gestion des erreurs par exceptions (TDD)

#### Tests à écrire en priorité :
```python
import unittest

class TestErrorHandler(unittest.TestCase):
    def test_exception_donnees_invalides(self):
        # RED: Test pour lever exception sur données invalides
        pass

    def test_gestion_exception_avec_try_catch(self):
        # RED: Test pour gérer exception gracieusement
        pass

    def test_logging_erreurs(self):
        # RED: Test pour logger les erreurs appropriées
        pass
```

### 4. Programmation asynchrone (TDD)

#### Tests à écrire en priorité :
```python
import unittest
import asyncio

class TestAsyncOps(unittest.TestCase):
    def test_operation_asynchrone(self):
        # RED: Test pour opération async
        async def run_test():
            # Code de test async ici
            pass
        
        asyncio.run(run_test())

    def test_gestion_erreur_async(self):
        # RED: Test pour gestion d'erreur en async
        pass

    def test_performance_async_vs_sync(self):
        # RED: Test pour démontrer l'amélioration de performance
        pass
```

---

## Standards de test

### Types de tests par concept

#### Tests unitaires (Micro-validation)
- **Une fonction = Un test** minimum
- **Cas nominal** : Le comportement normal
- **Cas d'erreur** : Gestion des exceptions
- **Cas limites** : Valeurs extrêmes

#### Tests de concept (Macro-validation)
- **Démonstration claire** : Le concept est utilisé correctement
- **Intégration** : Le concept fonctionne dans le contexte
- **Documentation** : Le test explique pourquoi ce concept

### Conventions de nommage des tests
```python
import unittest

# Format des classes : Test[NomDuModule]
class TestFileReader(unittest.TestCase):
    # Format des méthodes : test_[action]_[condition]_[résultat_attendu]
    def test_lire_fichier_json_valide_retourne_dictionnaire(self):
        pass
    
    def test_lire_fichier_inexistant_leve_filenotfound(self):
        pass
    
    def test_transformer_liste_avec_map_applique_fonction(self):
        pass
```

### Structure d'un test unittest
```python
import unittest
from unittest.mock import patch, mock_open

class TestExample(unittest.TestCase):
    def setUp(self):
        # ARRANGE : Préparer les données de test (avant chaque test)
        self.fichier_test = "test_data.json"
        self.donnees_attendues = {"key": "value"}
    
    def test_exemple(self):
        # ACT : Exécuter l'action à tester
        resultat = lire_fichier_json(self.fichier_test)
        
        # ASSERT : Vérifier le résultat avec assertions unittest
        self.assertEqual(resultat, self.donnees_attendues)
        self.assertIsInstance(resultat, dict)
        
    def tearDown(self):
        # CLEANUP : Nettoyer après chaque test si nécessaire
        pass

if __name__ == '__main__':
    unittest.main()
```

---

## Gestion des priorités

### Ordre TDD par concept
1. **Concept 1** : Tests + Implémentation complète
2. **Concept 2** : Tests + Implémentation complète  
3. **Concept 3** : Tests + Implémentation complète
4. **Concept 4** : Tests + Implémentation complète
5. **Intégration** : Tests d'intégration entre concepts
6. **Interface** : Tests UI et expérience utilisateur

### Règles de priorité TDD
- **Test échoue** = Priorité absolue (phase RED)
- **Test passe** = Continuer au refactor ou test suivant
- **Tous les tests passent** = Concept validé, passer au suivant
- **Régression** = Arrêter tout, fixer immédiatement

### Indicateurs de progression
- **Pourcentage de tests** qui passent
- **Couverture de code** par les tests
- **Concepts validés** vs concepts restants
- **Vélocité** : Tests écrits et passés par jour

---

## Outils et environnement

### Stack TDD
- **Framework de test** : unittest (Python standard)
- **Coverage** : coverage.py pour mesurer la couverture
- **Assertions** : unittest.TestCase assertions
- **Mocking** : unittest.mock pour simuler dépendances

### Workflow TDD
```bash
# 1. Lancer tous les tests
python -m unittest discover -s tests -v

# 2. Lancer un test spécifique
python -m unittest tests.test_file_reader.TestFileReader.test_lire_fichier_json_valide -v

# 3. Écrire un test qui échoue
# 4. Voir le test échouer (RED)
# 5. Écrire le code pour passer (GREEN)
# 6. Refactorer si nécessaire (REFACTOR)
# 7. Répéter

# Vérifier la couverture
coverage run -m unittest discover -s tests
coverage report -m
coverage html
```

### Structure de projet TDD
```
gestion-condos/
├── src/                     # Code source
│   ├── file_reader.py      
│   ├── functional_ops.py    
│   ├── error_handler.py     
│   └── async_operations.py  
├── tests/                   # Tests
│   ├── test_file_reader.py     # Tests concept 1
│   ├── test_functional_ops.py  # Tests concept 2
│   ├── test_error_handler.py   # Tests concept 3
│   ├── test_async_ops.py       # Tests concept 4
│   └── test_integration.py     # Tests d'intégration
├── tmp/                     # Expérimentations
└── docs/                    # Documentation
```

---

## Validation des concepts

### Critères TDD pour chaque concept

#### Concept validé quand :
- **Tests complets** : Tous les aspects testés
- **Tests passent** : Aucun test en échec
- **Code propre** : Refactorisé et documenté
- **Démonstration claire** : Le concept est évident dans le code

#### Checklist par concept :

**Lecture de fichiers :**
- [ ] Test lecture fichier JSON valide
- [ ] Test gestion fichier inexistant
- [ ] Test gestion format invalide
- [ ] Code refactorisé et documenté

**Programmation fonctionnelle :**
- [ ] Test transformation avec map()
- [ ] Test filtrage avec filter()
- [ ] Test agrégation avec reduce()
- [ ] Démonstration avantages approche fonctionnelle

**Gestion erreurs par exceptions :**
- [ ] Test lever exceptions appropriées
- [ ] Test gestion avec try/catch
- [ ] Test logging erreurs
- [ ] Hiérarchie exceptions documentée

**Programmation asynchrone :**
- [ ] Test opérations async
- [ ] Test gestion erreurs async
- [ ] Test amélioration performance
- [ ] Bénéfices async documentés

### Métriques de succès TDD
- **Couverture de code** : > 90%
- **Temps d'exécution tests** : < 30 secondes
- **Tests par concept** : Minimum 5 tests significatifs par TestCase
- **Zéro régression** : Tous les tests passent toujours

### Commandes unittest essentielles
```bash
# Lancer tous les tests
python -m unittest discover -s tests -v

# Lancer une classe de tests spécifique
python -m unittest tests.test_file_reader.TestFileReader -v

# Lancer un test spécifique
python -m unittest tests.test_file_reader.TestFileReader.test_lire_fichier_json_valide -v

# Avec couverture
coverage run -m unittest discover -s tests
coverage report -m
coverage html  # Génère rapport HTML dans htmlcov/
```

---

## Avantages TDD pour notre projet

### Rapidité de développement
- Détection immédiate des problèmes
- Pas de debugging long après coup
- Confiance pour refactorer

### Validation des concepts
- Chaque concept clairement testé
- Démonstration évidente dans les tests
- Documentation vivante du comportement

### Qualité garantie
- Code testé par design
- Couverture élevée automatique
- Moins de bugs en production

### Documentation automatique
- Tests servent de spécification
- Exemples d'usage dans les tests
- Comportement attendu clairement défini

---

**Méthodologie** : Test-Driven Development (TDD)  
**Principe** : Red → Green → Refactor  
**Focus** : Validation rapide des concepts techniques  
**Dernière mise à jour** : Août 2025
