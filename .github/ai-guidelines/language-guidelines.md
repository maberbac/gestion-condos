# Directives Spécifiques aux Langages

## Directives Python

### Style de Code et Conventions
- Suivre les directives de style PEP 8
- Utiliser des noms de variables et fonctions significatifs
- Implémenter des type hints pour une meilleure clarté du code
- Utiliser des docstrings pour toutes les fonctions et classes publiques

### Patterns de Programmation Fonctionnelle
```python
# Préféré: Approche fonctionnelle
donnees_traitees = list(map(valider_locataire, filter(est_actif, locataires)))

# Documenter pourquoi l'approche fonctionnelle est utilisée
# PROGRAMMATION FONCTIONNELLE: Démontre la transformation de données immutables
```

### Meilleures Pratiques de Gestion d'Exceptions
```python
# Types d'exception spécifiques pour différentes conditions d'erreur
class ErreurValidationLocataire(Exception):
    """Levée quand les données de locataire échouent aux règles de validation."""
    pass

# Gestion d'exception appropriée avec contexte
try:
    resultat = traiter_fichier_locataire(chemin_fichier)
except FileNotFoundError:
    logger.error(f"Fichier locataire non trouvé: {chemin_fichier}")
    raise ErreurValidationLocataire("Le fichier locataire requis est manquant")
except json.JSONDecodeError as e:
    logger.error(f"Format JSON invalide dans {chemin_fichier}: {e}")
    raise ErreurValidationLocataire("Le fichier locataire contient un format de données invalide")
```

### Programmation Asynchrone
```python
import asyncio
import aiofiles

async def traiter_plusieurs_fichiers(chemins_fichiers: list[str]) -> list[dict]:
    """
    Traite plusieurs fichiers de locataires de manière concurrente.
    
    PROGRAMMATION ASYNCHRONE: Démontre les opérations I/O non-bloquantes
    """
    taches = [traiter_fichier_async(chemin) for chemin in chemins_fichiers]
    resultats = await asyncio.gather(*taches, return_exceptions=True)
    return resultats
```

### Exigences de Documentation
- Utiliser des docstrings de style Google
- Inclure des type hints dans les signatures de fonctions
- Documenter les exceptions qui peuvent être levées
- Fournir des exemples d'utilisation dans les docstrings

## Directives Java

### Style de Code et Conventions
- Suivre les conventions de nommage Java (camelCase, PascalCase)
- Utiliser une structure de packages significative
- Implémenter des modificateurs d'accès appropriés
- Utiliser Javadoc pour toutes les méthodes et classes publiques

### Patterns de Programmation Fonctionnelle
```java
// Préféré: Stream API pour l'approche fonctionnelle
List<LocataireTraite> locatairesTraites = locataires.stream()
    .filter(Locataire::estActif)
    .map(this::validerLocataire)
    .collect(Collectors.toList());

// Documenter pourquoi l'approche fonctionnelle est utilisée
// PROGRAMMATION FONCTIONNELLE: Démontre la transformation de données immutables
```

### Meilleures Pratiques de Gestion d'Exceptions
```java
// Hiérarchie d'exceptions personnalisées
public class ExceptionValidationLocataire extends Exception {
    public ExceptionValidationLocataire(String message, Throwable cause) {
        super(message, cause);
    }
}

// Gestion d'exception appropriée avec logging
try {
    LocataireTraite resultat = traiterFichierLocataire(cheminFichier);
    return resultat;
} catch (IOException e) {
    logger.error("Échec de lecture du fichier locataire: " + cheminFichier, e);
    throw new ExceptionValidationLocataire("Impossible d'accéder aux données de locataire", e);
} catch (JsonParseException e) {
    logger.error("JSON invalide dans le fichier locataire: " + cheminFichier, e);
    throw new ExceptionValidationLocataire("Le format du fichier locataire est invalide", e);
}
```

### Programmation Asynchrone
```java
// Utiliser CompletableFuture pour les opérations async
public CompletableFuture<List<LocataireTraite>> traiterPlusieursFichiers(List<String> cheminsFichiers) {
    // PROGRAMMATION ASYNCHRONE: Démontre les opérations non-bloquantes
    List<CompletableFuture<LocataireTraite>> futures = cheminsFichiers.stream()
        .map(this::traiterFichierAsync)
        .collect(Collectors.toList());
    
    return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
        .thenApply(v -> futures.stream()
            .map(CompletableFuture::join)
            .collect(Collectors.toList()));
}
```

### Exigences de Documentation
- Utiliser Javadoc avec les tags @param, @return, @throws
- Inclure @since pour le suivi de versions
- Fournir des sections @example pour les méthodes complexes
- Documenter les considérations de sécurité des threads

## Patterns Universels

### Traitement de Fichiers (Agnostique au Langage)
Toujours démontrer ces concepts lors du traitement de fichiers :

1. **Lecture de Fichiers**: Utiliser les bibliothèques appropriées pour le langage
2. **Programmation Fonctionnelle**: Transformer les données sans mutations
3. **Gestion d'Exceptions**: Gérer les erreurs I/O avec élégance
4. **Opérations Async**: Traiter plusieurs fichiers de manière concurrente quand possible

### Stratégie de Gestion d'Erreurs
Indépendamment du langage :
- Créer des types d'exception spécifiques pour différentes conditions d'erreur
- Enregistrer les erreurs avec un contexte suffisant pour le débogage
- Fournir des messages d'erreur significatifs pour les utilisateurs
- Gérer les erreurs au niveau d'abstraction approprié

### Cohérence de Documentation
- Toujours expliquer quels concepts techniques sont démontrés
- Inclure des exemples pratiques qui fonctionnent avec des données réelles
- Documenter les implications de performance des approches choisies
- Expliquer les points d'intégration avec d'autres composants du système

### Organisation du Code
- Séparer les préoccupations en modules ou packages logiques
- Grouper les fonctionnalités liées ensemble
- Utiliser des patterns de nommage cohérents à travers le projet
- Implémenter une injection ou gestion de dépendances appropriée

## Considérations de Tests

### Tests Python
```python
import pytest
from unittest.mock import patch, mock_open

def test_traiter_fichier_locataire_succes():
    """Teste le traitement réussi du fichier locataire."""
    # GESTION D'EXCEPTIONS: Vérifier le fonctionnement normal
    # LECTURE DE FICHIERS: Tester avec des données de fichier mock
    donnees_mock = '{"id_locataire": "123", "nom": "Jean Dupont"}'
    
    with patch('builtins.open', mock_open(read_data=donnees_mock)):
        resultat = traiter_fichier_locataire('test.json')
        
    assert resultat['id_locataire'] == '123'
    assert resultat['nom'] == 'Jean Dupont'

def test_traiter_fichier_locataire_non_trouve():
    """Teste la gestion d'exception fichier non trouvé."""
    # GESTION D'EXCEPTIONS: Vérifier la gestion d'erreur appropriée
    with pytest.raises(ErreurValidationLocataire):
        traiter_fichier_locataire('inexistant.json')
```

### Tests Java
```java
@Test
public void testTraiterFichierLocataireSucces() throws Exception {
    // GESTION D'EXCEPTIONS: Vérifier le fonctionnement normal
    // LECTURE DE FICHIERS: Tester avec des données de fichier mock
    String donneesMock = "{\"idLocataire\": \"123\", \"nom\": \"Jean Dupont\"}";
    
    when(lecteurFichier.lireFichier("test.json")).thenReturn(donneesMock);
    
    LocataireTraite resultat = processeurLocataire.traiterFichierLocataire("test.json");
    
    assertEquals("123", resultat.getIdLocataire());
    assertEquals("Jean Dupont", resultat.getNom());
}

@Test(expected = ExceptionValidationLocataire.class)
public void testTraiterFichierLocataireNonTrouve() throws Exception {
    // GESTION D'EXCEPTIONS: Vérifier la gestion d'erreur appropriée
    when(lecteurFichier.lireFichier("inexistant.json"))
        .thenThrow(new FileNotFoundException());
    
    processeurLocataire.traiterFichierLocataire("inexistant.json");
}
```

## Directives de Performance

### Principes Généraux
- Documenter les implications de performance des approches choisies
- Utiliser les structures de données appropriées pour le cas d'usage
- Implémenter la mise en cache quand bénéfique
- Surveiller et enregistrer les métriques de performance

### Optimisations Spécifiques au Langage
- **Python**: Utiliser des générateurs pour de grands ensembles de données, exploiter le multiprocessing pour les tâches liées au CPU
- **Java**: Utiliser les types de collections appropriés, implémenter une gestion mémoire appropriée
- **Les Deux**: Utiliser le pooling de connexions pour les opérations base de données/réseau, implémenter des mécanismes de retry appropriés
