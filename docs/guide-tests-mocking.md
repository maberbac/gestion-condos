# Guide des Tests avec Mocking - Standards du Projet

## Vue d'Ensemble

Ce document établit les standards stricts de mocking pour garantir l'isolation complète des tests dans le projet gestion-condos.

## Philosophie de Test

### Principe Fondamental : Isolation Totale
- **Aucun test ne doit dépendre d'un autre**
- **Aucun accès à la base de données de production**
- **Tests reproductibles dans n'importe quel ordre**
- **Données de test contrôlées et prévisibles**

### Architecture de Test en 3 Niveaux

```
tests/
├── unit/                    # Tests unitaires - Logic métier isolée
├── integration/             # Tests d'intégration - Composants ensemble
├── acceptance/              # Tests d'acceptance - Workflows complets
└── fixtures/                # Données et utilitaires de test
```

## Standards par Type de Test

### Tests Unitaires - Mock Complet du Repository

#### Template Obligatoire
```python
from unittest.mock import Mock, AsyncMock
from src.application.services.user_service import UserService

class TestUserService:
    def setup_method(self):
        """Configuration avec repository complètement mocké"""
        # OBLIGATION : Mock complet - Aucune interaction DB réelle
        self.mock_repository = Mock()
        self.user_service = UserService(self.mock_repository)
    
    def test_operation_success(self):
        """Test avec données mockées contrôlées"""
        # Arrange - Mock des réponses
        self.mock_repository.get_data = AsyncMock(return_value=mock_data)
        self.mock_repository.save_data = AsyncMock(return_value=True)
        
        # Act - Opération avec repository mocké
        result = self.user_service.operation("param")
        
        # Assert - Validation sans DB réelle
        assert result is True
        self.mock_repository.save_data.assert_called_once()
```

#### Règles Strictes
- **TOUJOURS** passer le mock_repository dans le constructeur
- **JAMAIS** instancier UserService() sans mock
- **TOUJOURS** utiliser AsyncMock pour les méthodes async
- **VÉRIFIER** les appels avec assert_called_once()

### Tests d'Intégration - Mock des Services

#### Template Obligatoire
```python
from unittest.mock import patch
from src.web.condo_app import app

class TestAPIIntegration:
    def setup_method(self):
        """Configuration Flask pour tests"""
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    @patch('src.web.condo_app.user_service')
    def test_api_endpoint(self, mock_user_service):
        """Test API avec service mocké"""
        # Arrange - Mock du service
        mock_user_service.operation.return_value = expected_result
        
        # Act - Appel API avec service mocké
        response = self.client.post('/api/endpoint', json=data)
        
        # Assert - Validation sans interaction service réel
        assert response.status_code == 200
        mock_user_service.operation.assert_called_once()
```

#### Règles Strictes
- **TOUJOURS** utiliser @patch pour mocker les services
- **JAMAIS** laisser les services accéder à la vraie base
- **MOCKER** tous les services utilisés par l'endpoint
- **VÉRIFIER** les interactions avec les services

### Tests d'Acceptance - Données Isolées

#### Template Obligatoire
```python
from unittest.mock import patch
from src.domain.entities.user import User, UserRole

class TestAcceptanceWorkflow:
    def setup_method(self):
        """Configuration pour workflow complet"""
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    @patch('src.web.condo_app.user_service')
    def test_complete_workflow(self, mock_user_service):
        """Test workflow avec données contrôlées"""
        # Arrange - Données de test isolées
        mock_users = [
            User(username="admin", role=UserRole.ADMIN, ...),
            User(username="test_user", role=UserRole.RESIDENT, ...)
        ]
        mock_user_service.get_all_users.return_value = mock_users
        mock_user_service.operation.return_value = True
        
        # Act - Workflow complet avec données mockées
        response1 = self.client.get('/users')
        response2 = self.client.post('/api/operation')
        
        # Assert - Validation avec données prévisibles
        assert response1.status_code == 200
        assert response2.status_code == 200
```

#### Règles Strictes
- **CRÉER** des données de test spécifiques pour chaque test
- **JAMAIS** dépendre de données existantes en base
- **MOCKER** tous les services utilisés dans le workflow
- **RESTAURER** l'état avant chaque test

## Techniques de Mocking Avancées

### Mock des Exceptions
```python
def test_handle_database_error(self):
    """Test de gestion d'erreur avec exception mockée"""
    # Mock d'une exception - AUCUNE DB réelle touchée
    self.mock_repository.get_data = AsyncMock(
        side_effect=Exception("DB Connection Error")
    )
    
    # Test de la gestion d'erreur
    result = self.service.operation()
    assert result is False
```

### Mock des Réponses Conditionnelles
```python
def test_conditional_behavior(self):
    """Test avec comportement conditionnel mocké"""
    # Mock avec retours différents selon les appels
    self.mock_repository.check_exists = AsyncMock(
        side_effect=[True, False, True]  # 3 appels différents
    )
    
    # Tests avec comportements prévisibles
    assert self.service.operation("exists") is True
    assert self.service.operation("not_exists") is False
```

## Anti-Patterns à Éviter

### INTERDIT : Test avec base réelle
```python
# MAUVAIS : Utilise la vraie base de données
def test_bad_example():
    service = UserService()  # Repository réel
    result = service.delete_user("real_user")  # Suppression réelle !
    assert result is True  # Dépend des données existantes
```

### INTERDIT : Tests dépendants
```python
# MAUVAIS : Tests dans un ordre spécifique
def test_create_user():
    # Crée un utilisateur en base
    pass

def test_delete_user():
    # Dépend du test précédent - INTERDIT !
    pass
```

### INTERDIT : Mock partiel
```python
# MAUVAIS : Mock incomplet
def test_partial_mock():
    mock_repo = Mock()
    # Oublie de mocker certaines méthodes
    service = UserService(mock_repo)
    # Risque d'appel réel à la base
```

## Validation et Debugging

### Checklist de Validation
- [ ] **Aucun test n'instancie de repository réel**
- [ ] **Tous les services sont mockés dans les tests d'intégration**
- [ ] **Aucun accès réseau ou fichier dans les tests**
- [ ] **Tests passent dans n'importe quel ordre**
- [ ] **Pas d'effet de bord entre tests**
- [ ] **Données de test complètement isolées**

### Debug des Tests Mockés
```python
# Vérifier qu'un mock a été appelé
mock_service.method.assert_called_once_with(expected_arg)

# Vérifier qu'un mock N'a PAS été appelé
mock_service.method.assert_not_called()

# Voir tous les appels d'un mock
print(mock_service.method.call_args_list)

# Vérifier le nombre d'appels
assert mock_service.method.call_count == 2
```

## Runners de Tests

### Structure Obligatoire
```
tests/
├── run_all_unit_tests.py      # Tests unitaires uniquement
├── run_all_integration_tests.py  # Tests d'intégration uniquement
├── run_all_acceptance_tests.py   # Tests d'acceptance uniquement
└── run_all_tests.py           # Exécution complète
```

### Exécution des Tests
```bash
# Tests unitaires (les plus rapides)
python tests/run_all_unit_tests.py

# Tests d'intégration
python tests/run_all_integration_tests.py

# Tests d'acceptance (les plus lents)
python tests/run_all_acceptance_tests.py

# Suite complète
python tests/run_all_tests.py
```

## Métriques de Qualité

### Objectifs de Performance
- **Tests unitaires** : < 1 seconde total
- **Tests d'intégration** : < 5 secondes total
- **Tests d'acceptance** : < 10 secondes total
- **Aucun I/O externe** : Réseau, fichiers, base de données

### Couverture de Test
- **Tests unitaires** : 100% des méthodes de service
- **Tests d'intégration** : 100% des endpoints API
- **Tests d'acceptance** : 100% des workflows utilisateur

## Conclusion

Ces standards garantissent :
- **Fiabilité** : Tests reproductibles et prévisibles
- **Performance** : Exécution rapide sans I/O externe
- **Isolation** : Aucune dépendance entre tests
- **Maintenabilité** : Code de test clair et documenté

**Règle d'or** : Si un test touche la base de données, le fichier système ou le réseau, il est mal conçu et doit être refactorisé avec des mocks.
