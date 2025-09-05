# Documentation des Tests - Projet Gestion Condos

## Organisation des Tests

### Structure Hiérarchique
Le projet utilise une organisation en trois niveaux de tests pour assurer une couverture complète et une maintenance efficace.

## Types de Tests

### Tests Unitaires (`unit/`)
**Objectif** : Valider chaque fonction/classe de manière isolée

**Caractéristiques** :
- Exécution très rapide (< 1 seconde par test)
- Utilisation extensive de mocks
- Un test = une fonction/méthode
- Aucune dépendance externe (fichiers, réseau, etc.)

**Structure** :
```
unit/
├── test_file_reader.py     # Lecture fichiers
├── test_functional_ops.py  # Programmation fonctionnelle  
├── test_error_handler.py   # Gestion erreurs
└── test_async_ops.py       # Programmation asynchrone
```

### Tests d'Intégration (`integration/`)
**Objectif** : Valider l'interaction entre modules

**Caractéristiques** :
- Exécution modérée (1-5 secondes par test)
- Utilise les vraies implémentations (pas de mocks)
- Test du flux de données entre composants
- **Utilise des fichiers d'input réels** pour valider les interactions
- **Peut créer des fichiers temporaires** pour tester l'écriture/modification
- Validation des gestions d'erreurs avec de vraies dépendances

**Structure** :
```
integration/
├── test_data_flow.py       # Flux entre lecteur → traitement → sortie
├── test_api_endpoints.py   # Intégration API complète
└── test_file_processing.py # Traitement complet fichiers
```

### Tests d'Acceptance (`acceptance/`)
**Objectif** : Valider les scénarios métier complets

**Caractéristiques** :
- Exécution plus lente (5-30 secondes par test)
- Scénarios utilisateur de bout en bout
- Environnement proche de la production
- Validation des règles métier

**Structure** :
```
acceptance/
├── test_user_scenarios.py     # Parcours utilisateur complets
├── test_business_rules.py     # Règles métier appliquées
└── test_condo_management.py   # Gestion complète condos
```

## Runners de Tests

### Scripts de Lancement Automatique

#### `run_all_unit_tests.py`
- Découverte automatique des tests unitaires
- Exécution rapide pour développement TDD
- Rapport de couverture optionnel

#### `run_all_integration_tests.py`
- Exécution des tests d'intégration
- Setup/teardown des ressources partagées
- Validation des flux inter-modules

#### `run_all_acceptance_tests.py`
- Exécution des scénarios métier
- Setup d'environnement complet
- Validation des critères d'acceptance

#### `run_all_tests.py`
- Orchestration complète de tous les tests
- Exécution séquentielle de tous les types de tests
- Rapports consolidés avec statistiques détaillées
- Pipeline de validation complète
- Logique de détection robuste basée sur les codes de retour
- Support pour couverture de code et rapports JSON/HTML

## Conventions et Standards

### Nommage des Tests
```python
# Format des classes
class TestFileReader(unittest.TestCase):
    
    # Format des méthodes
    def test_[action]_[condition]_[resultat_attendu](self):
        pass
```

### Structure d'un Test
```python
import unittest
from unittest.mock import Mock, patch

class TestExample(unittest.TestCase):
    def setUp(self):
        """Préparation avant chaque test"""
        self.test_data = {...}
    
    def test_function_with_valid_input_returns_expected_result(self):
        """Description claire du test"""
        # ARRANGE
        input_data = self.test_data
        expected = "expected_result"
        
        # ACT
        result = function_under_test(input_data)
        
        # ASSERT
        self.assertEqual(result, expected)
        
    def tearDown(self):
        """Nettoyage après chaque test"""
        pass
```

### Gestion des Dépendances

#### Tests Unitaires - Mocking Systématique
```python
@patch('module.external_dependency')
def test_function_mocked(self, mock_dependency):
    mock_dependency.return_value = "mocked_result"
    # Test de la logique pure
```

#### Tests d'Intégration - Dépendances Réelles
```python
def test_integration_with_real_input_files(self):
    # Utilise des fichiers d'input réels (fixtures de test)
    input_file = "tests/fixtures/sample_condos.json"  # Fichier persistant
    
    # Test du flux complet avec vraies données
    donnees = lire_fichier_json(input_file)           # Module 1 - lecture réelle
    resultats = traiter_donnees(donnees)              # Module 2 - traitement
    self.assertEqual(len(resultats), 3)               # Validation intégration

def test_integration_with_output_creation(self):
    # Pour tester la création de fichiers : fichiers temporaires
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_output:
        output_path = temp_output.name
    
    try:
        # Test création/écriture de fichier
        donnees = {"condos": [{"id": 1, "nom": "Test"}]}
        ecrire_fichier_json(donnees, output_path)     # Module à tester
        
        # Validation que le fichier a été créé correctement
        with open(output_path, 'r') as f:
            resultat = json.load(f)
            self.assertEqual(resultat["condos"][0]["nom"], "Test")
    finally:
        os.unlink(output_path)  # Nettoyage fichier temporaire
```

#### Tests d'Acceptance - Environnement Complet
```python
def test_complete_user_scenario(self):
    # Setup complet de l'environnement
    # Scénario utilisateur de bout en bout
    # Validation des critères métier
```

#### Tests d'Acceptance - Interface Moderne
```python
def test_modern_ui_responsive_design(self):
    # Validation du responsive design
    response = self.client.get('/dashboard')
    content = response.data.decode('utf-8')
    
    # Vérifier les breakpoints responsives
    self.assertIn('768px', content)  # Tablet breakpoint
    self.assertIn('480px', content)  # Mobile breakpoint

def test_security_no_hardcoded_users(self):
    # Vérifier absence d'utilisateurs hardcodés
    app_file_path = 'src/web/condo_app.py'
    with open(app_file_path, 'r') as f:
        content = f.read()
    
    # Aucun utilisateur ne doit être hardcodé
    self.assertNotIn('admin', content.lower())
```

## Métriques et Rapports

### Objectifs de Couverture
- **Tests Unitaires** : > 95% du code métier
- **Tests d'Intégration** : > 80% des flux inter-modules
- **Tests d'Acceptance** : 100% des scénarios métier critiques

### Temps d'Exécution Cibles
- **Tests Unitaires** : < 10 secondes total
- **Tests d'Intégration** : < 60 secondes total
- **Tests d'Acceptance** : < 5 minutes total
- **Suite Complète** : < 7 minutes total

## Commandes Utiles

### Développement Quotidien
```bash
# Cycle TDD rapide
python tests/run_all_unit_tests.py

# Validation après implémentation
python tests/run_all_integration_tests.py

# Test spécifique
python -m unittest tests.unit.test_file_reader.TestFileReader.test_specific -v
```

### Validation Avant Commit
```bash
# Pipeline complet
python tests/run_all_tests.py --with-coverage

# Vérification qualité
python tests/run_all_tests.py --report --html
```

### Debug et Analyse
```bash
# Tests en mode verbose
python tests/run_all_unit_tests.py --verbose

# Couverture détaillée
coverage run tests/run_all_tests.py
coverage report -m --show-missing
coverage html
```

## Intégration Continue

### Pipeline de Tests
1. **Tests Unitaires** (obligatoire - échec = stop)
2. **Tests d'Intégration** (obligatoire - échec = stop)  
3. **Tests d'Acceptance** (obligatoire - échec = stop)
4. **Rapport Couverture** (informatif)
5. **Analyse Qualité** (informatif)

### Critères de Qualité
- Tous les tests passent
- Couverture globale > 90%
- Temps d'exécution < 7 minutes
- Aucune régression détectée

---

**Organisation** : Hiérarchique (Unit → Integration → Acceptance)  
**Découverte** : Automatique via runners dédiés  
**TDD** : Cycle Red-Green-Refactor avec tests unitaires  
**Pipeline** : Validation complète avant livraison
