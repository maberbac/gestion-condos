"""
Tests unitaires pour la fonctionnalité de suppression d'utilisateurs dans UserService
Respecte les consignes strictes de mocking des appels base de données
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.application.services.user_service import UserService
from src.domain.entities.user import User, UserRole


class TestUserDeletionService:
    
    def setup_method(self):
        """Configuration avant chaque test"""
        self.mock_repository = Mock()
        self.user_service = UserService(self.mock_repository)
    
    @patch('src.application.services.user_service.UserService._get_repository')
    def test_delete_user_by_username_success(self, mock_get_repo):
        """Test de suppression réussie d'un utilisateur existant - TOUS LES APPELS DB MOCKÉS"""
        # Arrange
        mock_get_repo.return_value = self.mock_repository
        username = "test_user"
        mock_user = User(
            username="test_user", 
            email="test@example.com",
            password_hash="hashed_password",
            role=UserRole.RESIDENT,
            full_name="Test User",
            condo_unit="101"
        )
        
        # Mock COMPLET - Aucun appel réel à la base de données
        self.mock_repository.get_user_by_username = AsyncMock(return_value=mock_user)
        self.mock_repository.delete_user = AsyncMock(return_value=True)
        
        # Act - Méthode avec repository complètement mocké
        result = self.user_service.delete_user_by_username(username)
        
        # Assert - Validation sans interaction avec base réelle
        assert result is True
        self.mock_repository.get_user_by_username.assert_called_once_with(username)
        self.mock_repository.delete_user.assert_called_once_with(username)
    
    @patch('src.application.services.user_service.UserService._get_repository')
    def test_delete_user_by_username_not_found(self, mock_get_repo):
        """Test de suppression d'un utilisateur inexistant - AUCUNE INTERACTION DB RÉELLE"""
        # Arrange
        mock_get_repo.return_value = self.mock_repository
        username = "nonexistent_user"
        self.mock_repository.get_user_by_username = AsyncMock(return_value=None)
        
        # Act - Test isolé sans base de données
        result = self.user_service.delete_user_by_username(username)
        
        # Assert
        assert result is False
        self.mock_repository.get_user_by_username.assert_called_once_with(username)
        self.mock_repository.delete_user.assert_not_called()
    
    @patch('src.application.services.user_service.UserService._get_repository')
    def test_delete_user_handles_database_errors(self, mock_get_repo):
        """Test de gestion des erreurs de base de données - EXCEPTION MOCKÉE"""
        # Arrange
        mock_get_repo.return_value = self.mock_repository
        username = "test_user"
        
        # Mock d'une exception de base de données - AUCUNE DB RÉELLE TOUCHÉE
        self.mock_repository.get_user_by_username = AsyncMock(side_effect=Exception("DB Connection Error"))
        
        # Act - Exception gérée sans interaction DB réelle
        result = self.user_service.delete_user_by_username(username)
        
        # Assert - Validation de la gestion d'erreur
        assert result is False
        self.mock_repository.get_user_by_username.assert_called_once_with(username)
    
    @patch('src.application.services.user_service.UserService._get_repository')  
    def test_cannot_delete_self(self, mock_get_repo):
        """Test d'empêchement de l'auto-suppression - VALIDATION MÉTIER MOCKÉE"""
        # Arrange
        mock_get_repo.return_value = self.mock_repository
        username = "admin"
        current_user_id = "admin"
        
        # Act - Test de logique métier sans base de données
        result = self.user_service.can_delete_user(username, current_user_id)
        
        # Assert - Validation que l'auto-suppression est interdite
        assert result is False
        
    @patch('src.application.services.user_service.UserService._get_repository')
    def test_can_delete_other_user(self, mock_get_repo):
        """Test d'autorisation de suppression d'autres utilisateurs - LOGIQUE MOCKÉE"""
        # Arrange  
        mock_get_repo.return_value = self.mock_repository
        username = "target_user"
        current_user_id = "admin"
        
        # Act - Test de permissions sans interaction DB
        result = self.user_service.can_delete_user(username, current_user_id)
        
        # Assert - Validation que la suppression d'autres utilisateurs est autorisée
        assert result is True
        
        # Assert
        assert result is True
