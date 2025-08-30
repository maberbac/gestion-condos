# Guidelines de Code - Standards du Projet

## Structure de Code Obligatoire

### Séparation par Concept
```
modules/
├── lecteur_fichiers.py    # Lecture de fichiers + gestion erreurs
├── utils_fonctionnel.py   # Fonctions pures + map/filter/reduce  
├── gestionnaire_erreurs.py # Exceptions personnalisées
└── async_handler.py       # Code asynchrone
```

### Commentaires pour Rapport
**Format requis :**
```python
def fonction_exemple():
    """
    [CONCEPT: Programmation Fonctionnelle]
    Cette fonction démontre l'utilisation de map() pour transformer
    les données sans modifier l'original (principe d'immuabilité).
    
    Utilisé dans le rapport section "Programmation fonctionnelle".
    """
    # Code ici...
```

## Standards de Nommage

### Variables et Fonctions
- **Explicites** : `calculer_frais_mensuels()` pas `calc()`
- **Français accepté** : Pour correspondre au domaine métier
- **Snake_case** : Standard Python

### Fichiers et Modules
- **Préfixes clairs** : `lecteur_`, `gestionnaire_`, `utils_`
- **Un concept par fichier** : Facilite l'extraction pour le rapport

## Gestion d'Erreurs Systématique

### Pattern Obligatoire
```python
def operation_avec_fichier():
    """[CONCEPT: Gestion d'erreurs]"""
    try:
        # Opération principale
        pass
    except FileNotFoundError as e:
        logger.error(f"Fichier non trouvé: {e}")
        return {"erreur": "Fichier manquant", "details": str(e)}
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        return {"erreur": "Opération échouée", "details": str(e)}
```

### Messages d'Erreur
- **Informatifs** : Expliquer ce qui s'est passé
- **Actionables** : Suggérer une solution si possible
- **Loggés** : Pour débogage et démonstration

## Code Asynchrone

### Pattern Standard
```python
import asyncio
import aiohttp

async def operation_async():
    """[CONCEPT: Programmation Asynchrone]"""
    try:
        async with aiohttp.ClientSession() as session:
            # Opération asynchrone
            pass
    except aiohttp.ClientError as e:
        # Gestion d'erreur asynchrone
        pass
```

## Documentation Inline

### Fonctions Importantes
- **Docstring** : Objectif + concept démontré
- **Commentaires** : Explication des choix techniques
- **Exemples** : Dans les docstrings si pertinent

### Pour le Rapport
- Marquer clairement quel concept est démontré
- Expliquer les bénéfices de l'approche choisie
- Préparer les extraits de code à inclure

## Validation du Code

### Avant Commit
- [ ] Au moins 1 concept clairement démontré
- [ ] Gestion d'erreurs appropriée
- [ ] Commentaires pour le rapport présents
- [ ] Code testé manuellement
- [ ] Respecte les standards de nommage

### Tests Simples
- Pas de framework complexe (contrainte temps)
- Tests manuels documentés
- Cas d'erreur vérifiés
- Démonstration fonctionnelle prête

---

**RAPPEL** : Le code doit être simple, fonctionnel et facilement extractible pour le rapport final.
