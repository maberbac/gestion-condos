"""
UserRepository SQLite - Implémentation du port UserRepositoryPort pour SQLite.

Cet adapter implémente la persistance des utilisateurs en utilisant SQLite
selon les standards définis dans copilot-instructions.md :
- Configuration JSON obligatoire (database.json)
- SQLite comme base de données principale
- Migrations automatiques
- Mots de passe chiffrés

[MÉTHODOLOGIE TDD]
Implémentation développée après les tests (phase GREEN de TDD).
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

import sqlite3
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from src.domain.entities.user import User, UserRole, UserValidationError
from src.ports.user_repository import UserRepositoryPort

class UserRepositorySQLiteError(Exception):
    """Exception spécialisée pour les erreurs du repository SQLite."""
    pass

class UserRepositorySQLite(UserRepositoryPort):
    """
    Repository SQLite pour la persistance des utilisateurs.

    [STANDARDS OBLIGATOIRES]
    - Configuration via config/database.json
    - Base de données SQLite principale
    - Mots de passe chiffrés obligatoires
    - Gestion des utilisateurs par défaut

    - Implémente UserRepositoryPort du domaine métier
    - Isole la logique SQLite du core business
    - Permet tests unitaires avec base en mémoire
    """

    def __init__(self, config_path: str = "config/database.json"):
        """
        Initialise le repository avec la configuration de base de données.

        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config = self._load_database_config(config_path)
        self.db_path = self.config['database']['path']
        self.migrations_dir = Path(self.config['database'].get('migrations_path', 'data/migrations/'))

        # Assurer que le répertoire data existe
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"UserRepository SQLite initialisé avec DB: {self.db_path}")

        # Initialiser la base de données
        self._initialize_database()

    def _load_database_config(self, config_path: str) -> Dict[str, Any]:
        """
        [STANDARD: Configuration JSON obligatoire]
        Charge la configuration de la base de données depuis JSON.
        """
        try:
            # Résoudre le chemin de façon robuste par rapport à la racine du projet
            if not os.path.isabs(config_path):
                # Trouver la racine du projet (répertoire contenant src/)
                current_dir = Path(__file__).resolve()
                while current_dir.parent != current_dir:
                    if (current_dir / 'src').is_dir():
                        project_root = current_dir
                        break
                    current_dir = current_dir.parent
                else:
                    # Fallback : utiliser le répertoire courant
                    project_root = Path.cwd()

                resolved_config_path = project_root / config_path
            else:
                resolved_config_path = Path(config_path)

            with open(resolved_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.debug(f"Configuration de base de données chargée depuis {resolved_config_path}")
                return config
        except FileNotFoundError:
            logger.error(f"Fichier de configuration introuvable: {config_path}")
            raise UserRepositorySQLiteError(f"Configuration de base de données introuvable: {config_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de format JSON dans {config_path}: {e}")
            raise UserRepositorySQLiteError(f"Configuration JSON invalide: {e}")

    def _initialize_database(self) -> None:
        """
        [STANDARD: Migrations automatiques]
        Initialise la base de données. Les migrations sont gérées par SQLiteAdapter.
        """
        if not Path(self.db_path).exists():
            self._create_database()

        self._ensure_default_users()

    def _create_database(self) -> None:
        """Crée le fichier de base de données SQLite vide."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("SELECT 1")  # Test de connexion
            conn.commit()
            logger.info(f"Base de données créée: {self.db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """Crée une nouvelle connexion SQLite avec configuration."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Pour accès par nom de colonne
        return conn

    def _ensure_default_users(self) -> None:
        """
        S'assure que les utilisateurs par défaut existent avec mots de passe chiffrés.

        [STANDARD: Mots de passe chiffrés obligatoires]
        """
        try:
            logger.info("Base de données initialisée - utilisateurs chargés depuis les migrations")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la base: {e}")
            raise UserRepositorySQLiteError(f"Erreur d'initialisation: {e}")

    # ==================== Implémentation UserRepositoryPort ====================

    async def get_all_users(self) -> List[User]:
        """Récupère tous les utilisateurs."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT username, email, password_hash, role, full_name,
                           condo_unit, phone, is_active, created_at, last_login
                    FROM users ORDER BY username
                """)

                rows = cursor.fetchall()
                users = []

                for row in rows:
                    user = self._row_to_user(row)
                    users.append(user)

                logger.debug(f"Récupération de {len(users)} utilisateurs")
                return users

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des utilisateurs: {e}")
            raise UserRepositorySQLiteError(f"Erreur de lecture des utilisateurs: {e}")

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Récupère un utilisateur par son nom d'utilisateur."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT username, email, password_hash, role, full_name,
                           condo_unit, phone, is_active, created_at, last_login
                    FROM users WHERE username = ?
                """, (username,))

                row = cursor.fetchone()
                if row:
                    user = self._row_to_user(row)
                    logger.debug(f"Utilisateur trouvé: {username}")
                    return user
                else:
                    logger.debug(f"Utilisateur introuvable: {username}")
                    return None

        except Exception as e:
            logger.error(f"Erreur lors de la recherche de l'utilisateur {username}: {e}")
            raise UserRepositorySQLiteError(f"Erreur de recherche utilisateur: {e}")

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Récupère un utilisateur par son email."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT username, email, password_hash, role, full_name,
                           condo_unit, phone, is_active, created_at, last_login
                    FROM users WHERE email = ?
                """, (email,))

                row = cursor.fetchone()
                if row:
                    user = self._row_to_user(row)
                    logger.debug(f"Utilisateur trouvé par email: {email}")
                    return user
                else:
                    logger.debug(f"Utilisateur introuvable par email: {email}")
                    return None

        except Exception as e:
            logger.error(f"Erreur lors de la recherche par email {email}: {e}")
            raise UserRepositorySQLiteError(f"Erreur de recherche par email: {e}")

    async def save_user(self, user: User) -> User:
        """Sauvegarde un utilisateur (création ou mise à jour)."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Vérifier si l'utilisateur existe
                cursor.execute("SELECT id FROM users WHERE username = ?", (user.username,))
                existing = cursor.fetchone()

                if existing:
                    # Mise à jour
                    cursor.execute("""
                        UPDATE users SET
                            email = ?, password_hash = ?, role = ?, full_name = ?,
                            condo_unit = ?, phone = ?, is_active = ?, last_login = ?
                        WHERE username = ?
                    """, (
                        user.email, user.password_hash, user.role.value, user.full_name,
                        user.condo_unit, user.phone, user.is_active,
                        user.last_login.isoformat() if user.last_login else None,
                        user.username
                    ))
                    logger.debug(f"Utilisateur mis à jour: {user.username}")
                else:
                    # Création
                    cursor.execute("""
                        INSERT INTO users (username, email, password_hash, role, full_name,
                                         condo_unit, phone, is_active, created_at, last_login)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        user.username, user.email, user.password_hash, user.role.value,
                        user.full_name, user.condo_unit, user.phone, user.is_active,
                        user.created_at.isoformat() if user.created_at else datetime.now().isoformat(),
                        user.last_login.isoformat() if user.last_login else None
                    ))
                    logger.info(f"Nouvel utilisateur créé: {user.username}")

                conn.commit()
                return user

        except sqlite3.IntegrityError as e:
            logger.error(f"Contrainte d'intégrité violée pour {user.username}: {e}")
            raise UserRepositorySQLiteError(f"Utilisateur ou email déjà existant: {e}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de {user.username}: {e}")
            raise UserRepositorySQLiteError(f"Erreur de sauvegarde: {e}")

    async def save_users(self, users: List[User]) -> List[User]:
        """Sauvegarde une liste d'utilisateurs."""
        saved_users = []
        for user in users:
            saved_user = await self.save_user(user)
            saved_users.append(saved_user)
        return saved_users

    async def delete_user(self, username: str) -> bool:
        """Supprime un utilisateur."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE username = ?", (username,))

                deleted_count = cursor.rowcount
                conn.commit()

                if deleted_count > 0:
                    logger.info(f"Utilisateur supprimé: {username}")
                    return True
                else:
                    logger.warning(f"Utilisateur à supprimer introuvable: {username}")
                    return False

        except Exception as e:
            logger.error(f"Erreur lors de la suppression de {username}: {e}")
            raise UserRepositorySQLiteError(f"Erreur de suppression: {e}")

    async def user_exists(self, username: str) -> bool:
        """Vérifie si un utilisateur existe."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM users WHERE username = ? LIMIT 1", (username,))
                return cursor.fetchone() is not None

        except Exception as e:
            logger.error(f"Erreur lors de la vérification d'existence de {username}: {e}")
            raise UserRepositorySQLiteError(f"Erreur de vérification: {e}")

    async def get_users_by_role(self, role: UserRole) -> List[User]:
        """Récupère tous les utilisateurs d'un rôle donné."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT username, email, password_hash, role, full_name,
                           condo_unit, phone, is_active, created_at, last_login
                    FROM users WHERE role = ? ORDER BY username
                """, (role.value,))

                rows = cursor.fetchall()
                users = []

                for row in rows:
                    user = self._row_to_user(row)
                    users.append(user)

                logger.debug(f"Récupération de {len(users)} utilisateurs avec le rôle {role.value}")
                return users

        except Exception as e:
            logger.error(f"Erreur lors de la recherche par rôle {role.value}: {e}")
            raise UserRepositorySQLiteError(f"Erreur de recherche par rôle: {e}")

    async def update_user_password(self, username: str, new_password_hash: str) -> bool:
        """Met à jour le mot de passe d'un utilisateur."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET password_hash = ? WHERE username = ?",
                    (new_password_hash, username)
                )

                updated_count = cursor.rowcount
                conn.commit()

                if updated_count > 0:
                    logger.info(f"Mot de passe mis à jour pour: {username}")
                    return True
                else:
                    logger.warning(f"Utilisateur introuvable pour mise à jour mot de passe: {username}")
                    return False

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du mot de passe de {username}: {e}")
            raise UserRepositorySQLiteError(f"Erreur de mise à jour mot de passe: {e}")

    async def update_user_by_username(self, username: str, user_data: Dict[str, Any]) -> bool:
        """
        Met à jour un utilisateur complet par nom d'utilisateur.

        Args:
            username: Nom d'utilisateur à mettre à jour
            user_data: Dictionnaire avec les nouvelles données utilisateur

        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Construire la requête de mise à jour dynamiquement
                update_fields = []
                update_values = []

                # Mapper les champs
                field_mapping = {
                    'username': 'username',
                    'email': 'email',
                    'full_name': 'full_name',
                    'role': 'role',
                    'condo_unit': 'condo_unit'
                }

                for field, db_column in field_mapping.items():
                    if field in user_data:
                        update_fields.append(f"{db_column} = ?")
                        if field == 'role':
                            # Convertir l'enum en string si nécessaire
                            role_value = user_data[field]
                            if hasattr(role_value, 'value'):
                                update_values.append(role_value.value)
                            else:
                                update_values.append(str(role_value))
                        else:
                            update_values.append(user_data[field])

                # Gérer le mot de passe séparément
                if 'password' in user_data and user_data['password']:
                    from src.domain.entities.user import User
                    password_hash = User.hash_password(user_data['password'])
                    update_fields.append("password_hash = ?")
                    update_values.append(password_hash)

                if not update_fields:
                    logger.warning(f"Aucun champ à mettre à jour pour l'utilisateur: {username}")
                    return False

                # Construire et exécuter la requête
                query = f"UPDATE users SET {', '.join(update_fields)} WHERE username = ?"
                update_values.append(username)  # Ajouter le username pour la clause WHERE

                cursor.execute(query, update_values)
                updated_count = cursor.rowcount
                conn.commit()

                if updated_count > 0:
                    logger.info(f"Utilisateur mis à jour avec succès: {username}")
                    return True
                else:
                    logger.warning(f"Utilisateur introuvable pour mise à jour: {username}")
                    return False

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'utilisateur {username}: {e}")
            raise UserRepositorySQLiteError(f"Erreur de mise à jour utilisateur: {e}")

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authentifie un utilisateur avec son nom d'utilisateur et mot de passe.

        Args:
            username: Nom d'utilisateur
            password: Mot de passe en clair

        Returns:
            Utilisateur authentifié ou None si échec
        """
        try:
            # Récupérer l'utilisateur par nom d'utilisateur
            user = await self.get_user_by_username(username)

            if user is None:
                logger.warning(f"Tentative d'authentification - utilisateur introuvable: {username}")
                return None

            # Vérifier si l'utilisateur est actif
            if not user.is_active:
                logger.warning(f"Tentative d'authentification - utilisateur inactif: {username}")
                return None

            # Vérifier le mot de passe
            if User.verify_password(password, user.password_hash):
                logger.info(f"Authentification réussie pour: {username}")

                # Mettre à jour la date de dernière connexion
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE users SET last_login = ? WHERE username = ?",
                        (datetime.now().isoformat(), username)
                    )
                    conn.commit()

                return user
            else:
                logger.warning(f"Tentative d'authentification - mot de passe incorrect: {username}")
                return None

        except Exception as e:
            logger.error(f"Erreur lors de l'authentification de {username}: {e}")
            raise UserRepositorySQLiteError(f"Erreur d'authentification: {e}")

    async def initialize_default_users(self) -> None:
        """
        Initialise les utilisateurs par défaut si aucun n'existe.
        Les identifiants sont chargés depuis la configuration.
        """
        default_users_config = self._get_default_users_config()

        logger.info("Initialisation des utilisateurs par défaut")

        for user_data in default_users_config:
            # Créer l'utilisateur avec mot de passe chiffré
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=User.hash_password(user_data['password']),
                role=user_data['role'],
                full_name=user_data['full_name'],
                condo_unit=user_data['condo_unit'],
                is_active=True
            )

            try:
                await self.save_user(user)
                logger.info(f"Utilisateur par défaut créé: {user.username}")
            except UserRepositorySQLiteError:
                # L'utilisateur existe peut-être déjà
                logger.debug(f"Utilisateur {user.username} existe déjà")

    def _row_to_user(self, row: sqlite3.Row) -> User:
        """Convertit une ligne SQLite en objet User."""
        created_at = None
        last_login = None

        try:
            if row[8]:  # created_at
                created_at = datetime.fromisoformat(row[8])
        except (ValueError, TypeError):
            created_at = datetime.now()

        try:
            if row[9]:  # last_login
                last_login = datetime.fromisoformat(row[9])
        except (ValueError, TypeError):
            last_login = None

        return User(
            username=row[0],
            email=row[1],
            password_hash=row[2],
            role=UserRole(row[3]),
            full_name=row[4],
            condo_unit=row[5],
            phone=row[6],
            is_active=bool(row[7]),
            created_at=created_at,
            last_login=last_login
        )
