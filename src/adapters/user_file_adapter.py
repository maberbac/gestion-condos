"""
User File Adapter - Implémentation concrète pour la persistance fichier JSON.

[ARCHITECTURE HEXAGONALE]
Cet adapter implémente le UserRepositoryPort pour la persistance
en fichiers JSON. Il respecte l'architecture hexagonale en isolant
les détails de stockage du domaine métier.

[CONCEPTS TECHNIQUES INTÉGRÉS]
- Lecture de fichiers : Persistance utilisateurs via JSON
- Programmation asynchrone : Opérations non-bloquantes
- Gestion des erreurs : Exceptions spécialisées
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

import asyncio
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.domain.entities.user import User, UserRole, UserAuthenticationError, UserValidationError
from src.ports.user_repository import UserRepositoryPort


class UserFileAdapter(UserRepositoryPort):
    """
    Adaptateur pour la persistance des utilisateurs en fichiers JSON.
    
    Cette implémentation respecte l'architecture hexagonale en isolant
    les détails de stockage (fichiers JSON) du domaine métier.
    """
    
    def __init__(self, users_file: str = "data/users.json"):
        """
        Initialise l'adaptateur avec le chemin du fichier.
        
        Args:
            users_file: Chemin vers le fichier des utilisateurs
        """
        self.users_file = Path(users_file)
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Cache en mémoire pour performances
        self._users_cache: Optional[List[User]] = None
        self._cache_dirty = True
    
    async def get_all_users(self) -> List[User]:
        """
        Récupère tous les utilisateurs depuis le fichier JSON.
        
        [CONCEPT: Lecture de fichiers + Programmation asynchrone]
        """
        try:
            if self._cache_dirty or self._users_cache is None:
                await self._load_users()
            
            return self._users_cache.copy() if self._users_cache else []
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des utilisateurs: {e}")
            raise UserAuthenticationError(f"Impossible de charger les utilisateurs: {e}")
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Récupère un utilisateur par son nom d'utilisateur.
        
        [CONCEPT: Programmation fonctionnelle]
        Utilise filter() pour la recherche.
        """
        try:
            users = await self.get_all_users()
            
            # Programmation fonctionnelle : filtrage
            matching_users = list(filter(lambda u: u.username == username, users))
            
            return matching_users[0] if matching_users else None
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de l'utilisateur {username}: {e}")
            raise UserAuthenticationError(f"Erreur de recherche utilisateur: {e}")
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Récupère un utilisateur par son email.
        """
        try:
            users = await self.get_all_users()
            
            # Programmation fonctionnelle : filtrage
            matching_users = list(filter(lambda u: u.email == email, users))
            
            return matching_users[0] if matching_users else None
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche par email {email}: {e}")
            raise UserAuthenticationError(f"Erreur de recherche par email: {e}")
    
    async def save_user(self, user: User) -> User:
        """
        Sauvegarde un utilisateur (création ou mise à jour).
        
        [CONCEPT: Gestion des erreurs]
        Validation et gestion d'erreurs robuste.
        """
        try:
            if not user.username or not user.email:
                raise UserValidationError("Nom d'utilisateur et email requis")
            
            users = await self.get_all_users()
            
            # Recherche de l'utilisateur existant
            existing_index = -1
            for i, existing_user in enumerate(users):
                if existing_user.username == user.username:
                    existing_index = i
                    break
            
            if existing_index >= 0:
                # Mise à jour
                users[existing_index] = user
                logger.info(f"Utilisateur {user.username} mis à jour")
            else:
                # Création
                users.append(user)
                logger.info(f"Nouvel utilisateur {user.username} créé")
            
            await self.save_users(users)
            return user
            
        except UserValidationError:
            raise
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'utilisateur {user.username}: {e}")
            raise UserAuthenticationError(f"Impossible de sauvegarder l'utilisateur: {e}")
    
    async def save_users(self, users: List[User]) -> List[User]:
        """
        Sauvegarde la liste complète des utilisateurs.
        
        [CONCEPT: Lecture de fichiers + Programmation asynchrone]
        """
        try:
            # Préparation des données pour JSON
            users_data = {
                "users": [user.to_dict() for user in users],
                "last_updated": datetime.now().isoformat(),
                "total_users": len(users)
            }
            
            # Écriture asynchrone
            content = json.dumps(users_data, indent=2, ensure_ascii=False)
            await asyncio.to_thread(self.users_file.write_text, content, encoding='utf-8')
            
            # Mise à jour du cache
            self._users_cache = users.copy()
            self._cache_dirty = False
            
            logger.info(f"{len(users)} utilisateurs sauvegardés dans {self.users_file}")
            return users
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des utilisateurs: {e}")
            raise UserAuthenticationError(f"Impossible de sauvegarder les utilisateurs: {e}")
    
    async def delete_user(self, username: str) -> bool:
        """
        Supprime un utilisateur.
        """
        try:
            users = await self.get_all_users()
            
            # Filtrage pour supprimer l'utilisateur
            new_users = list(filter(lambda u: u.username != username, users))
            
            if len(new_users) < len(users):
                await self.save_users(new_users)
                logger.info(f"Utilisateur {username} supprimé")
                return True
            else:
                logger.warning(f"Utilisateur {username} introuvable pour suppression")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de l'utilisateur {username}: {e}")
            raise UserAuthenticationError(f"Impossible de supprimer l'utilisateur: {e}")
    
    async def user_exists(self, username: str) -> bool:
        """
        Vérifie si un utilisateur existe.
        """
        try:
            user = await self.get_user_by_username(username)
            return user is not None
        except Exception as e:
            logger.error(f"Erreur lors de la vérification d'existence de {username}: {e}")
            return False
    
    async def get_users_by_role(self, role: UserRole) -> List[User]:
        """
        Récupère tous les utilisateurs d'un rôle donné.
        
        [CONCEPT: Programmation fonctionnelle]
        Utilise filter() pour le filtrage par rôle.
        """
        try:
            users = await self.get_all_users()
            
            # Programmation fonctionnelle : filtrage par rôle
            return list(filter(lambda u: u.role == role, users))
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche par rôle {role}: {e}")
            raise UserAuthenticationError(f"Erreur de recherche par rôle: {e}")
    
    async def update_user_password(self, username: str, new_password_hash: str) -> bool:
        """
        Met à jour le mot de passe d'un utilisateur.
        """
        try:
            user = await self.get_user_by_username(username)
            if not user:
                return False
            
            # Mise à jour du mot de passe
            updated_user = User(
                username=user.username,
                email=user.email,
                password_hash=new_password_hash,
                role=user.role,
                full_name=user.full_name,
                condo_unit=user.condo_unit,
                phone=user.phone,
                is_active=user.is_active,
                created_at=user.created_at,
                last_login=user.last_login
            )
            
            await self.save_user(updated_user)
            # Invalider le cache pour forcer le rechargement
            self._cache_dirty = True
            logger.info(f"Mot de passe mis à jour pour {username}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du mot de passe pour {username}: {e}")
            raise UserAuthenticationError(f"Impossible de mettre à jour le mot de passe: {e}")
    
    async def update_user_by_username(self, username: str, updates: Dict[str, Any]) -> bool:
        """
        Met à jour les informations d'un utilisateur.
        
        Args:
            username: Nom d'utilisateur à mettre à jour
            updates: Dictionnaire des champs à mettre à jour
            
        Returns:
            True si la mise à jour a réussi, False sinon
            
        Raises:
            UserAuthenticationError: En cas d'erreur lors de la mise à jour
        """
        try:
            user = await self.get_user_by_username(username)
            if not user:
                logger.warning(f"Tentative de mise à jour d'un utilisateur inexistant: {username}")
                return False
            
            # Créer un nouvel utilisateur avec les modifications
            user_data = {
                'username': updates.get('username', user.username),
                'email': updates.get('email', user.email),
                'password_hash': updates.get('password_hash', user.password_hash),
                'role': UserRole(updates.get('role', user.role.value)) if 'role' in updates else user.role,
                'full_name': updates.get('full_name', user.full_name),
                'condo_unit': updates.get('condo_unit', user.condo_unit),
                'phone': updates.get('phone', user.phone),
                'is_active': updates.get('is_active', user.is_active),
                'created_at': user.created_at,
                'last_login': user.last_login
            }
            
            updated_user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                role=user_data['role'],
                full_name=user_data['full_name'],
                condo_unit=user_data['condo_unit'],
                phone=user_data['phone'],
                is_active=user_data['is_active'],
                created_at=user_data['created_at'],
                last_login=user_data['last_login']
            )
            
            await self.save_user(updated_user)
            # Invalider le cache pour forcer le rechargement
            self._cache_dirty = True
            logger.info(f"Utilisateur mis à jour: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'utilisateur {username}: {e}")
            raise UserAuthenticationError(f"Impossible de mettre à jour l'utilisateur: {e}")
    
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
                user.last_login = datetime.now()
                await self.save_user(user)
                
                return user
            else:
                logger.warning(f"Tentative d'authentification - mot de passe incorrect: {username}")
                return None
                
        except Exception as e:
            logger.error(f"Erreur lors de l'authentification de {username}: {e}")
            raise UserAuthenticationError(f"Erreur d'authentification: {e}")
    
    async def initialize_default_users(self) -> None:
        """
        Initialise les utilisateurs par défaut si aucun n'existe.
        
        [CONCEPT: Gestion des erreurs + Lecture de fichiers]
        """
        try:
            if not self.users_file.exists() or not await self.get_all_users():
                # Créer les utilisateurs par défaut
                default_users = [
                    User(
                        username="admin",
                        email="admin@condos.com",
                        password_hash=User.hash_password("admin123"),
                        role=UserRole.ADMIN,
                        full_name="Administrateur Système"
                    ),
                    User(
                        username="resident",
                        email="resident@condos.com",
                        password_hash=User.hash_password("resident123"),
                        role=UserRole.RESIDENT,
                        full_name="Résident Test",
                        condo_unit="101"
                    ),
                    User(
                        username="guest",
                        email="guest@condos.com",
                        password_hash=User.hash_password("guest123"),
                        role=UserRole.GUEST,
                        full_name="Invité Test"
                    )
                ]
                
                await self.save_users(default_users)
                logger.info("Utilisateurs par défaut initialisés")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des utilisateurs par défaut: {e}")
            raise UserAuthenticationError(f"Impossible d'initialiser les utilisateurs par défaut: {e}")
    
    async def _load_users(self) -> None:
        """
        Charge les utilisateurs depuis le fichier JSON.
        
        [CONCEPT: Lecture de fichiers + Gestion des erreurs]
        Méthode privée pour charger les données.
        """
        try:
            if not self.users_file.exists():
                self._users_cache = []
                self._cache_dirty = False
                return
            
            # Lecture asynchrone du fichier
            def read_file():
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return f.read()
            
            content = await asyncio.to_thread(read_file)
            data = json.loads(content)
            
            # Conversion des données en objets User
            users = []
            for user_data in data.get('users', []):
                try:
                    user = User.from_dict(user_data)
                    users.append(user)
                except Exception as e:
                    logger.warning(f"Utilisateur invalide ignoré: {e}")
            
            self._users_cache = users
            self._cache_dirty = False
            logger.debug(f"{len(users)} utilisateurs chargés depuis {self.users_file}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Fichier JSON invalide {self.users_file}: {e}")
            raise UserAuthenticationError(f"Fichier utilisateurs corrompu: {e}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des utilisateurs: {e}")
            raise UserAuthenticationError(f"Impossible de charger les utilisateurs: {e}")
