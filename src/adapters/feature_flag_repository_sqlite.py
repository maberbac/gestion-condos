"""
FeatureFlagRepositorySQLite - Implémentation SQLite pour les feature flags.

Implémentation concrète du port FeatureFlagRepositoryPort utilisant SQLite.
Gère la persistance des feature flags en base de données.
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

import sqlite3
import os
from typing import List, Optional
from datetime import datetime
from src.ports.feature_flag_repository import FeatureFlagRepositoryPort
from src.domain.entities.feature_flag import FeatureFlag

class FeatureFlagRepositorySQLite(FeatureFlagRepositoryPort):
    """
    Implémentation SQLite du repository des feature flags.
    """

    def __init__(self, db_path: str = "data/condos.db"):
        """
        Initialise le repository avec la base de données SQLite.

        Args:
            db_path: Chemin vers la base SQLite
        """
        self.db_path = db_path
        # S'assurer que le répertoire existe
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        logger.info(f"FeatureFlagRepositorySQLite initialisé avec DB: {self.db_path}")

    def get_all(self) -> List[FeatureFlag]:
        """Récupère tous les feature flags."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT id, flag_name, is_enabled, description, created_at, updated_at
                    FROM feature_flags
                    ORDER BY flag_name
                """)

                flags = []
                for row in cursor.fetchall():
                    flag = FeatureFlag(
                        id=row['id'],
                        flag_name=row['flag_name'],
                        is_enabled=bool(row['is_enabled']),
                        description=row['description'],
                        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                        updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                    )
                    flags.append(flag)

                logger.debug(f"Récupération de {len(flags)} feature flags")
                return flags

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des feature flags: {e}")
            return []

    def get_by_name(self, flag_name: str) -> Optional[FeatureFlag]:
        """Récupère un feature flag par son nom."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT id, flag_name, is_enabled, description, created_at, updated_at
                    FROM feature_flags
                    WHERE flag_name = ?
                """, (flag_name,))

                row = cursor.fetchone()
                if row:
                    flag = FeatureFlag(
                        id=row['id'],
                        flag_name=row['flag_name'],
                        is_enabled=bool(row['is_enabled']),
                        description=row['description'],
                        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                        updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                    )
                    logger.debug(f"Feature flag trouvé: {flag}")
                    return flag

                logger.debug(f"Feature flag non trouvé: {flag_name}")
                return None

        except Exception as e:
            logger.error(f"Erreur lors de la récupération du feature flag {flag_name}: {e}")
            return None

    def is_enabled(self, flag_name: str) -> bool:
        """Vérifie si un feature flag est activé."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT is_enabled
                    FROM feature_flags
                    WHERE flag_name = ?
                """, (flag_name,))

                row = cursor.fetchone()
                if row:
                    is_enabled = bool(row[0])
                    logger.debug(f"Feature flag {flag_name}: {'ACTIVÉ' if is_enabled else 'DÉSACTIVÉ'}")
                    return is_enabled

                logger.warning(f"Feature flag non trouvé: {flag_name}, considéré comme désactivé")
                return False

        except Exception as e:
            logger.error(f"Erreur lors de la vérification du feature flag {flag_name}: {e}")
            return False

    def create(self, feature_flag: FeatureFlag) -> FeatureFlag:
        """Crée un nouveau feature flag."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    INSERT INTO feature_flags (flag_name, is_enabled, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    feature_flag.flag_name,
                    feature_flag.is_enabled,
                    feature_flag.description,
                    feature_flag.created_at.isoformat() if feature_flag.created_at else datetime.now().isoformat(),
                    feature_flag.updated_at.isoformat() if feature_flag.updated_at else datetime.now().isoformat()
                ))

                feature_flag.id = cursor.lastrowid
                conn.commit()

                logger.info(f"Feature flag créé: {feature_flag}")
                return feature_flag

        except Exception as e:
            logger.error(f"Erreur lors de la création du feature flag {feature_flag.flag_name}: {e}")
            raise

    def update(self, feature_flag: FeatureFlag) -> FeatureFlag:
        """Met à jour un feature flag existant."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                feature_flag.updated_at = datetime.now()

                conn.execute("""
                    UPDATE feature_flags
                    SET is_enabled = ?, description = ?, updated_at = ?
                    WHERE flag_name = ?
                """, (
                    feature_flag.is_enabled,
                    feature_flag.description,
                    feature_flag.updated_at.isoformat(),
                    feature_flag.flag_name
                ))

                conn.commit()

                logger.info(f"Feature flag mis à jour: {feature_flag}")
                return feature_flag

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du feature flag {feature_flag.flag_name}: {e}")
            raise

    def enable_flag(self, flag_name: str) -> bool:
        """Active un feature flag par son nom."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    UPDATE feature_flags
                    SET is_enabled = 1, updated_at = ?
                    WHERE flag_name = ?
                """, (datetime.now().isoformat(), flag_name))

                conn.commit()

                if cursor.rowcount > 0:
                    logger.info(f"Feature flag activé: {flag_name}")
                    return True
                else:
                    logger.warning(f"Feature flag non trouvé pour activation: {flag_name}")
                    return False

        except Exception as e:
            logger.error(f"Erreur lors de l'activation du feature flag {flag_name}: {e}")
            return False

    def disable_flag(self, flag_name: str) -> bool:
        """Désactive un feature flag par son nom."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    UPDATE feature_flags
                    SET is_enabled = 0, updated_at = ?
                    WHERE flag_name = ?
                """, (datetime.now().isoformat(), flag_name))

                conn.commit()

                if cursor.rowcount > 0:
                    logger.info(f"Feature flag désactivé: {flag_name}")
                    return True
                else:
                    logger.warning(f"Feature flag non trouvé pour désactivation: {flag_name}")
                    return False

        except Exception as e:
            logger.error(f"Erreur lors de la désactivation du feature flag {flag_name}: {e}")
            return False

    def toggle_flag(self, flag_name: str) -> bool:
        """Inverse l'état d'un feature flag par son nom."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Récupérer l'état actuel
                cursor = conn.execute("""
                    SELECT is_enabled FROM feature_flags WHERE flag_name = ?
                """, (flag_name,))

                row = cursor.fetchone()
                if not row:
                    logger.warning(f"Feature flag non trouvé pour inversion: {flag_name}")
                    return False

                # Inverser l'état
                new_state = not bool(row[0])
                cursor = conn.execute("""
                    UPDATE feature_flags
                    SET is_enabled = ?, updated_at = ?
                    WHERE flag_name = ?
                """, (new_state, datetime.now().isoformat(), flag_name))

                conn.commit()

                logger.info(f"Feature flag inversé: {flag_name} -> {'ACTIVÉ' if new_state else 'DÉSACTIVÉ'}")
                return True

        except Exception as e:
            logger.error(f"Erreur lors de l'inversion du feature flag {flag_name}: {e}")
            return False

    def delete(self, flag_name: str) -> bool:
        """Supprime un feature flag par son nom."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM feature_flags WHERE flag_name = ?
                """, (flag_name,))

                conn.commit()

                if cursor.rowcount > 0:
                    logger.info(f"Feature flag supprimé: {flag_name}")
                    return True
                else:
                    logger.warning(f"Feature flag non trouvé pour suppression: {flag_name}")
                    return False

        except Exception as e:
            logger.error(f"Erreur lors de la suppression du feature flag {flag_name}: {e}")
            return False
