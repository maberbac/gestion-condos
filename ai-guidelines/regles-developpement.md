# Règles de Développement - Standards Techniques

## Instructions de Développement

### Avant de Coder
1. Toujours demander si la fonctionnalité proposée est prioritaire
2. Vérifier quel(s) concept(s) obligatoire(s) elle démontre
3. Estimer le temps de développement vs. deadline

### Pendant le Développement
1. Structure du code : Séparer chaque concept dans des modules distincts
2. Commentaires : Expliquer POURQUOI (pas seulement quoi) pour le rapport
3. Gestion d'erreurs : Implémenter des try/except informatifs partout
4. Tests simples : Vérifier que ça fonctionne avant de continuer

### Standards de Code
- Noms explicites : Variables et fonctions auto-documentées
- Fonctions courtes : Max 20-30 lignes par fonction
- Séparation des responsabilités : Un module = un concept
- Documentation : Docstrings pour toutes les fonctions

### Communication
- Style professionnel : Maintenir un ton clair et professionnel
- Référence emojis : Voir .github/copilot-instructions.md pour interdiction stricte

## Réponses Types à Adopter

### Quand je propose une fonctionnalité
Toujours répondre avec :
1. "Cette fonctionnalité démontre : [concept(s)]"
2. "Temps estimé : [estimation]"
3. "Priorité : [Haute/Moyenne/Basse] car [raison]"
4. "Alternative plus simple : [si applicable]"

### Quand je demande du code
Structure de la réponse :
1. Rappel du concept démontré
2. Code avec commentaires explicatifs
3. Explication pour le rapport
4. Test/validation proposé

### Quand je suis bloqué
M'aider en :
1. Identifiant le problème spécifique
2. Proposant une solution simple d'abord
3. Gardant en tête la timeline du projet
4. Suggérant des alternatives si nécessaire

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

## Signaux d'Alerte

### M'arrêter si :
- Je propose une fonctionnalité sans lien avec les 4 concepts
- Je suggère une technologie non autorisée
- Le scope devient trop complexe pour la timeline du projet
- On s'éloigne de l'objectif MVP

### Me rappeler de :
- Garder le code simple et commenté
- Documenter les décisions pour le rapport
- Prioriser les concepts obligatoires
- Respecter la timeline définie du projet
