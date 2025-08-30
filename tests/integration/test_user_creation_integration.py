#!/usr/bin/env python3
"""
Tests d'intégration pour la création d'utilisateur.
Tests l'intégration entre le service et le repository.
"""

import pytest
import asyncio
import os
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, os.path.abspath('.'))

from src.domain.entities.user import User, UserRole
from src.domain.services.user_creation_service import UserCreationService
from src.adapters.user_file_adapter import UserFileAdapter
from src.domain.exceptions.business_exceptions import UserCreationError


class TestUserCreationIntegration:
    """Tests d'intégration pour la création d'utilisateur."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        # Créer un répertoire temporaire pour les tests
        self.temp_dir = tempfile.mkdtemp()
        self.users_file = os.path.join(self.temp_dir, "test_users.json")
        
        # Créer l'adapteur et le service
        self.user_repository = UserFileAdapter(self.users_file)
        self.user_creation_service = UserCreationService(self.user_repository)
    
    def teardown_method(self):
        """Nettoyage après chaque test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_create_user_full_integration(self):
        """Test intégration complète de création d'utilisateur."""
        # Arrange
        await self.user_repository.initialize_default_users()
        
        # Act - créer un nouvel utilisateur
        new_user = await self.user_creation_service.create_user(
            username="integration_test",
            email="integration@test.com",
            password="testpass123",
            full_name="Test Integration User",
            role=UserRole.RESIDENT,
            condo_unit="C-301"
        )
        
        # Assert - vérifier que l'utilisateur a été créé
        assert new_user is not None
        assert new_user.username == "integration_test"
        
        # Vérifier que l'utilisateur est persisté
        retrieved_user = await self.user_repository.get_user_by_username("integration_test")
        assert retrieved_user is not None
        assert retrieved_user.email == "integration@test.com"
        assert retrieved_user.full_name == "Test Integration User"
        assert retrieved_user.role == UserRole.RESIDENT
        assert retrieved_user.condo_unit == "C-301"
        assert retrieved_user.is_active is True
    
    @pytest.mark.asyncio
    async def test_create_multiple_users_integration(self):
        """Test création de plusieurs utilisateurs."""
        # Arrange
        await self.user_repository.initialize_default_users()
        
        # Act - créer plusieurs utilisateurs
        user1 = await self.user_creation_service.create_user(
            username="user1",
            email="user1@test.com",
            password="password1",
            full_name="Premier Utilisateur",
            role=UserRole.RESIDENT,
            condo_unit="A-101"
        )
        
        user2 = await self.user_creation_service.create_user(
            username="user2",
            email="user2@test.com",
            password="password2",
            full_name="Deuxième Utilisateur",
            role=UserRole.ADMIN
        )
        
        user3 = await self.user_creation_service.create_user(
            username="user3",
            email="user3@test.com",
            password="password3",
            full_name="Troisième Utilisateur",
            role=UserRole.GUEST
        )
        
        # Assert - vérifier que tous sont créés
        all_users = await self.user_repository.get_all_users()
        usernames = [u.username for u in all_users]
        
        assert "user1" in usernames
        assert "user2" in usernames
        assert "user3" in usernames
        
        # Vérifier les détails spécifiques
        retrieved_user1 = await self.user_repository.get_user_by_username("user1")
        assert retrieved_user1.condo_unit == "A-101"
        
        retrieved_user2 = await self.user_repository.get_user_by_username("user2")
        assert retrieved_user2.role == UserRole.ADMIN
        assert retrieved_user2.condo_unit is None
    
    @pytest.mark.asyncio
    async def test_create_user_with_existing_default_users(self):
        """Test création avec utilisateurs par défaut existants."""
        # Arrange - initialiser avec utilisateurs par défaut
        await self.user_repository.initialize_default_users()
        
        # Vérifier qu'admin existe déjà
        admin_user = await self.user_repository.get_user_by_username("admin")
        assert admin_user is not None
        
        # Act - créer un nouveau utilisateur
        new_user = await self.user_creation_service.create_user(
            username="nouveau_resident",
            email="nouveau@test.com",
            password="newpass123",
            full_name="Nouveau Résident",
            role=UserRole.RESIDENT,
            condo_unit="B-205"
        )
        
        # Assert - vérifier que les deux existent
        assert new_user is not None
        
        all_users = await self.user_repository.get_all_users()
        usernames = [u.username for u in all_users]
        
        assert "admin" in usernames
        assert "nouveau_resident" in usernames
    
    @pytest.mark.asyncio
    async def test_prevent_duplicate_creation_integration(self):
        """Test prévention des doublons en intégration."""
        # Arrange
        await self.user_repository.initialize_default_users()
        
        # Créer un premier utilisateur
        await self.user_creation_service.create_user(
            username="unique_user",
            email="unique@test.com",
            password="pass123",
            full_name="Utilisateur Unique",
            role=UserRole.RESIDENT,
            condo_unit="A-101"
        )
        
        # Act & Assert - essayer de créer avec même username
        with pytest.raises(UserCreationError, match="Nom d'utilisateur déjà utilisé"):
            await self.user_creation_service.create_user(
                username="unique_user",  # Même username
                email="autre@test.com",
                password="autrepass",
                full_name="Autre User",
                role=UserRole.GUEST
            )
        
        # Act & Assert - essayer de créer avec même email
        with pytest.raises(UserCreationError, match="Adresse email déjà utilisée"):
            await self.user_creation_service.create_user(
                username="autre_user",
                email="unique@test.com",  # Même email
                password="autrepass",
                full_name="Autre User",
                role=UserRole.GUEST
            )
    
    @pytest.mark.asyncio
    async def test_file_persistence_integration(self):
        """Test persistance dans le fichier."""
        # Arrange
        await self.user_repository.initialize_default_users()
        
        # Act - créer un utilisateur
        await self.user_creation_service.create_user(
            username="persist_test",
            email="persist@test.com",
            password="persistpass",
            full_name="Test Persistance",
            role=UserRole.RESIDENT,
            condo_unit="D-401"
        )
        
        # Vérifier que le fichier existe
        assert os.path.exists(self.users_file)
        
        # Créer un nouveau repository pointant vers le même fichier
        new_repository = UserFileAdapter(self.users_file)
        await new_repository.initialize_default_users()
        
        # Assert - vérifier que l'utilisateur est toujours là
        retrieved_user = await new_repository.get_user_by_username("persist_test")
        assert retrieved_user is not None
        assert retrieved_user.email == "persist@test.com"
        assert retrieved_user.full_name == "Test Persistance"


if __name__ == "__main__":
    # Exécuter les tests
    pytest.main([__file__, "-v"])
