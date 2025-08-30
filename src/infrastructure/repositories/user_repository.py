"""
Repository utilisateur pour l'infrastructure - Alias vers l'adapter SQLite

[ARCHITECTURE HEXAGONALE]
Ce module fait le lien entre l'infrastructure attendue par les tests
et l'adapter SQLite réel. Il simplifie l'importation pour la couche infrastructure.
"""

from src.adapters.user_repository_sqlite import UserRepositorySQLite

# Alias pour maintenir la compatibilité avec la structure attendue
UserRepository = UserRepositorySQLite
