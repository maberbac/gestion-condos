#!/usr/bin/env python3
"""
Tests unitaires pour le service de création d'utilisateur.
Tests les fonctionnalités de création d'utilisateur avec validation et gestion d'erreurs.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.domain.entities.user import User, UserRole, UserValidationError
from src.domain.services.user_creation_service import UserCreationService
from src.ports.user_repository import UserRepositoryPort
from src.domain.exceptions.business_exceptions import UserCreationError


class TestUserCreationService:
    """Tests pour le service de création d'utilisateur."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_user_repository = AsyncMock(spec=UserRepositoryPort)
        self.user_creation_service = UserCreationService(self.mock_user_repository)
    
    @pytest.mark.asyncio
    async def test_create_user_success_resident(self):
        """Test création réussie d'un utilisateur résident."""
        # Arrange
        username = "nouveau_resident"
        email = "resident@example.com"
        password = "password123"
        full_name = "Nouveau Résident"
        role = UserRole.RESIDENT
        condo_unit = "A-101"
        
        self.mock_user_repository.get_user_by_username.return_value = None
        self.mock_user_repository.get_user_by_email.return_value = None
        self.mock_user_repository.save_user.return_value = True
        
        # Act
        result = await self.user_creation_service.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role=role,
            condo_unit=condo_unit
        )
        
        # Assert
        assert result is not None
        assert result.username == username
        assert result.email == email
        assert result.full_name == full_name
        assert result.role == role
        assert result.condo_unit == condo_unit
        assert result.is_active is True
        assert result.created_at is not None
        assert User.verify_password(password, result.password_hash)
        
        # Vérifier que le repository a été appelé
        self.mock_user_repository.save_user.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_success_admin(self):
        """Test création réussie d'un administrateur."""
        # Arrange
        username = "nouvel_admin"
        email = "admin@example.com"
        password = "adminpass123"
        full_name = "Nouvel Admin"
        role = UserRole.ADMIN
        
        self.mock_user_repository.get_user_by_username.return_value = None
        self.mock_user_repository.get_user_by_email.return_value = None
        self.mock_user_repository.save_user.return_value = True
        
        # Act
        result = await self.user_creation_service.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role=role
        )
        
        # Assert
        assert result is not None
        assert result.username == username
        assert result.role == role
        assert result.condo_unit is None  # Admin n'a pas d'unité
    
    @pytest.mark.asyncio
    async def test_create_user_username_exists(self):
        """Test échec si nom d'utilisateur existe déjà."""
        # Arrange
        existing_user = User(
            username="existant",
            email="autre@example.com",
            password_hash="hash",
            role=UserRole.RESIDENT,
            full_name="Utilisateur Existant",
            condo_unit="A-101"  # Ajout unité pour résident
        )
        
        self.mock_user_repository.get_user_by_username.return_value = existing_user
        
        # Act & Assert
        with pytest.raises(UserCreationError, match="Nom d'utilisateur déjà utilisé"):
            await self.user_creation_service.create_user(
                username="existant",
                email="nouveau@example.com",
                password="password123",
                full_name="Nouveau User",
                role=UserRole.RESIDENT,
                condo_unit="B-202"
            )
    
    @pytest.mark.asyncio
    async def test_create_user_email_exists(self):
        """Test échec si email existe déjà."""
        # Arrange
        existing_user = User(
            username="autre_user",
            email="existant@example.com",
            password_hash="hash",
            role=UserRole.RESIDENT,
            full_name="Autre Utilisateur",
            condo_unit="B-202"  # Ajout unité pour résident
        )
        
        self.mock_user_repository.get_user_by_username.return_value = None
        self.mock_user_repository.get_user_by_email.return_value = existing_user
        
        # Act & Assert
        with pytest.raises(UserCreationError, match="Adresse email déjà utilisée"):
            await self.user_creation_service.create_user(
                username="nouveau_user",
                email="existant@example.com",
                password="password123",
                full_name="Nouveau User",
                role=UserRole.RESIDENT,
                condo_unit="B-202"
            )
    
    @pytest.mark.asyncio
    async def test_create_user_invalid_data(self):
        """Test échec avec données invalides."""
        # Test nom d'utilisateur vide
        with pytest.raises(UserCreationError, match="Nom d'utilisateur requis"):
            await self.user_creation_service.create_user(
                username="",
                email="test@example.com",
                password="password123",
                full_name="Test User",
                role=UserRole.RESIDENT
            )
        
        # Test email invalide
        with pytest.raises(UserCreationError, match="Email invalide"):
            await self.user_creation_service.create_user(
                username="testuser",
                email="email_invalide",
                password="password123",
                full_name="Test User",
                role=UserRole.RESIDENT
            )
        
        # Test mot de passe trop court
        with pytest.raises(UserCreationError, match="Mot de passe trop court"):
            await self.user_creation_service.create_user(
                username="testuser",
                email="test@example.com",
                password="123",
                full_name="Test User",
                role=UserRole.RESIDENT
            )
    
    @pytest.mark.asyncio
    async def test_create_user_resident_without_unit(self):
        """Test échec si résident sans unité."""
        with pytest.raises(UserCreationError, match="Numéro d'unité requis pour les résidents"):
            await self.user_creation_service.create_user(
                username="resident_sans_unite",
                email="resident@example.com",
                password="password123",
                full_name="Résident Sans Unité",
                role=UserRole.RESIDENT
                # condo_unit manquant
            )
    
    @pytest.mark.asyncio
    async def test_create_user_repository_failure(self):
        """Test échec si erreur du repository."""
        # Arrange
        self.mock_user_repository.get_user_by_username.return_value = None
        self.mock_user_repository.get_user_by_email.return_value = None
        self.mock_user_repository.save_user.return_value = False
        
        # Act & Assert
        with pytest.raises(UserCreationError, match="Échec de la sauvegarde de l'utilisateur"):
            await self.user_creation_service.create_user(
                username="nouveau_user",
                email="test@example.com",
                password="password123",
                full_name="Test User",
                role=UserRole.RESIDENT,
                condo_unit="A-101"
            )
    
    @pytest.mark.asyncio
    async def test_create_user_validation_error_handling(self):
        """Test gestion des erreurs de validation de l'entité User."""
        # Arrange - forcer une UserValidationError
        self.mock_user_repository.get_user_by_username.return_value = None
        self.mock_user_repository.get_user_by_email.return_value = None
        
        # Act & Assert - nom complet trop court (déclenchera validation error)
        with pytest.raises(UserCreationError, match="Nom complet requis"):
            await self.user_creation_service.create_user(
                username="testuser",
                email="test@example.com",
                password="password123",
                full_name="A",  # Trop court
                role=UserRole.RESIDENT,
                condo_unit="A-101"
            )
    
    @pytest.mark.asyncio
    async def test_create_user_repository_exception(self):
        """Test gestion des exceptions du repository."""
        # Arrange
        self.mock_user_repository.get_user_by_username.side_effect = Exception("Erreur base de données")
        
        # Act & Assert
        with pytest.raises(UserCreationError, match="Erreur lors de la création"):
            await self.user_creation_service.create_user(
                username="testuser",
                email="test@example.com",
                password="password123",
                full_name="Test User",
                role=UserRole.RESIDENT,
                condo_unit="A-101"
            )


if __name__ == "__main__":
    # Exécuter les tests
    pytest.main([__file__, "-v"])
