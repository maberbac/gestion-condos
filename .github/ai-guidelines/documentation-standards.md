# Standards de Documentation pour Agents IA

## Directives de Documentation du Code

### Commentaires Intégrés
Suivre ces principes pour tous les langages de programmation :

#### Python
```python
def traiter_donnees_locataire(fichier_locataire: str) -> dict:
    """
    Traite les informations de locataire à partir d'un fichier et valide les champs requis.
    
    Args:
        fichier_locataire: Chemin vers le fichier JSON/CSV contenant les données de locataire
        
    Returns:
        dict: Données de locataire traitées avec statut de validation
        
    Raises:
        FileNotFoundError: Quand le fichier de locataire n'existe pas
        ValidationError: Quand les champs requis du locataire sont manquants
    """
    # Charger les données de locataire en utilisant une approche fonctionnelle pour démontrer le concept
    donnees = charger_et_valider(fichier_locataire)
    
    # Appliquer les règles métier pour la validation de locataire
    # Ceci démontre le concept de gestion d'exceptions
    try:
        donnees_validees = appliquer_regles_validation(donnees)
    except ValidationError as e:
        # Enregistrer l'échec de validation spécifique pour le débogage
        logger.error(f"Validation du locataire échouée: {e}")
        raise
    
    return donnees_validees
```

#### Java
```java
/**
 * Traite les informations de locataire à partir d'un fichier et valide les champs requis.
 * 
 * @param fichierLocataire Chemin vers le fichier JSON/CSV contenant les données de locataire
 * @return Objet DonneesLocataireTraitees avec statut de validation
 * @throws FileNotFoundException quand le fichier de locataire n'existe pas
 * @throws ValidationException quand les champs requis du locataire sont manquants
 */
public DonneesLocataireTraitees traiterDonneesLocataire(String fichierLocataire) {
    // Charger les données de locataire en utilisant une approche fonctionnelle pour démontrer le concept
    DonneesLocataire donnees = chargerEtValider(fichierLocataire);
    
    // Appliquer les règles métier pour la validation de locataire
    // Ceci démontre le concept de gestion d'exceptions
    try {
        DonneesLocataireTraitees donneesValidees = appliquerReglesValidation(donnees);
        return donneesValidees;
    } catch (ValidationException e) {
        // Enregistrer l'échec de validation spécifique pour le débogage
        logger.error("Validation du locataire échouée: " + e.getMessage());
        throw e;
    }
}
```

### Types de Commentaires et Quand les Utiliser

#### Commentaires de But
Expliquer POURQUOI le code existe et son objectif métier :
```python
# Calculer les frais mensuels en utilisant une structure de taux progressifs
# Requis par les règlements de l'association de copropriété pour une répartition équitable des coûts
```

#### Commentaires d'Implémentation
Expliquer COMMENT la logique complexe fonctionne :
```python
# Utiliser une recherche binaire pour optimiser la recherche de locataire dans de grandes bases de données
# Critique pour les performances avec des propriétés de 1000+ unités
```

#### Commentaires de Démonstration de Concepts
Mettre en évidence les concepts techniques démontrés :
```python
# PROGRAMMATION FONCTIONNELLE: Utilisation de map/reduce pour la transformation de données
# PROGRAMMATION ASYNCHRONE: Opérations de fichiers non-bloquantes pour de meilleures performances
# GESTION D'EXCEPTIONS: Gestion d'erreurs structurée avec des exceptions spécifiques
```

## Standards de Documentation Technique

### Documentation de Module/Classe

#### Structure
Chaque module ou classe significatif devrait avoir :
1. Aperçu du but et des responsabilités
2. Concepts clés démontrés
3. Exemples d'utilisation
4. Exigences de configuration
5. Dépendances et points d'intégration

#### Template
```markdown
# [Nom du Module/Classe]

## But
Brève description de ce que fait ce composant et pourquoi il existe.

## Concepts Techniques Démontrés
- [Concept 1]: Comment c'est implémenté et pourquoi
- [Concept 2]: Patterns spécifiques utilisés
- [Concept 3]: Avantages et compromis

## Exemples d'Utilisation

### Utilisation de Base
```[langage]
// Exemple simple montrant l'utilisation typique
```

### Utilisation Avancée
```[langage]
// Exemple complexe montrant les cas limites ou fonctionnalités avancées
```

## Configuration
Liste des paramètres de configuration, variables d'environnement, ou réglages.

## Dépendances
- Dépendances internes et comment elles sont utilisées
- Dépendances externes et exigences de version
- Dépendances optionnelles et leur impact

## Points d'Intégration
Comment ce composant se connecte avec d'autres parties du système.

## Gestion d'Erreurs
Scénarios d'erreur courants et comment ils sont gérés.

## Considérations de Performance
Toute implication de performance ou notes d'optimisation.
```

### Documentation API

Pour toute interface publique ou API :

```markdown
## Référence API

### [Nom de Méthode/Fonction]

**But**: Brève description de ce que cela fait

**Paramètres**:
- `param1` (type): Description et contraintes
- `param2` (type, optionnel): Description et valeur par défaut

**Retourne**: Description de la valeur de retour et type

**Lève/Lance**:
- `TypeException`: Quand et pourquoi cette exception se produit

**Exemple**:
```[langage]
// Exemple pratique avec données réalistes
```

**Notes**:
- Tout détail d'implémentation important
- Caractéristiques de performance
- Considérations de sécurité des threads
```

## Standards de Documentation Utilisateur

### Documentation de Fonctionnalités

Lors de l'implémentation de fonctionnalités orientées utilisateur :

```markdown
# [Nom de la Fonctionnalité]

## Aperçu
Ce que cette fonctionnalité fait du point de vue de l'utilisateur.

## Comment Utiliser

### Pour Commencer
Instructions étape par étape pour l'utilisation de base.

### Instructions Détaillées
1. Première action à effectuer
2. Résultat attendu ou feedback
3. Action suivante à effectuer
4. Résultat final

### Exemples
Scénarios du monde réel montrant la fonctionnalité en action.

## Options de Configuration
Réglages configurables par l'utilisateur et leurs effets.

## Dépannage
Problèmes courants et leurs solutions.

## Utilisation Avancée
Scénarios complexes ou fonctionnalités pour utilisateurs expérimentés.
```

## Directives de Génération de Documentation

### Quand Générer de la Documentation
- Nouveaux modules ou classes significatives
- APIs publiques ou interfaces
- Implémentations de logique métier complexe
- Fonctionnalités ou outils orientés utilisateur
- Processus de configuration ou déploiement

### Fichiers de Documentation à Maintenir
- `README.md`: Aperçu du projet et démarrage rapide
- `docs/technique/`: Architecture technique et détails d'implémentation
- `docs/utilisateur/`: Guides utilisateur et documentation des fonctionnalités
- `docs/api/`: Documentation de référence API
- **INTERDICTION**: Aucun fichier CHANGELOG, VERSION, ou RELEASE

### Intégration de Documentation Automatisée
- Inclure la génération de documentation dans le workflow de développement
- Mettre à jour la documentation pertinente lors de l'implémentation de nouvelles fonctionnalités
- Maintenir la cohérence entre les commentaires de code et la documentation externe
- Utiliser des exemples qui fonctionnent réellement avec la base de code actuelle
- Se concentrer sur la documentation fonctionnelle et technique, jamais le versioning
