"""
Package principal de l'application Gestion Condos.

Architecture Hexagonale (Ports & Adapters)
==========================================

Ce package contient une application construite selon l'architecture hexagonale,
parfaitement adaptée pour la démonstration des 4 concepts techniques obligatoires
et l'extensibilité future vers la gestion de location et services juridiques.

Structure:
    domain/     - Domaine métier (core business logic)
    ports/      - Interfaces (contracts)
    adapters/   - Implémentations concrètes
    infrastructure/ - Configuration et utilitaires
"""

__version__ = "1.0.0"
__author__ = "Équipe Gestion Condos"
