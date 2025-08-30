"""
Tests unitaires pour la consultation des détails d'utilisateur avec mocking complet.
Méthodologie: Tests isolés avec tous les appels base de données mockés.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.application.services.user_service import UserService
from src.domain.entities.user import User, UserRole
from src.infrastructure.logger_manager import get_logger

logger = get_logger(__name__)


class TestUserDetailsConsultationServiceMocked:
    """Tests de la consultation des détails utilisateur avec services mockés."""
    
    def setup_method(self):
        """Configuration des mocks pour chaque test."""
        self.mock_repository = Mock()
        self.mock_repository.get_user_by_username = AsyncMock()
        self.user_service = UserService(user_repository=self.mock_repository)
    
    def test_get_user_details_by_username_user_exists(self):
        """Test de récupération des détails d'un utilisateur existant."""
        # Arrange
        username = "resident1"
        mock_user = User(
            username=username,
            email="resident1@condos.com",
            password_hash="hash123",
            full_name="Jean Dupont",
            role=UserRole.RESIDENT,
            condo_unit="A-101"
        )
        self.mock_repository.get_user_by_username.return_value = mock_user
        
        # Act
        result = self.user_service.get_user_details_by_username(username)
        
        # Assert
        assert result is not None
        assert result['username'] == username
        assert result['full_name'] == "Jean Dupont"
        assert result['email'] == "resident1@condos.com"
        assert result['role'] == "resident"
        assert result['condo_unit'] == "A-101"
        assert result['has_condo_unit'] is True
        logger.debug(f"Test réussi: détails récupérés pour utilisateur existant {username}")
    
    def test_get_user_details_by_username_user_not_found(self):
        """Test de récupération des détails d'un utilisateur inexistant."""
        # Arrange
        username = "inexistant"
        self.mock_repository.get_user_by_username.return_value = None
        
        # Act
        result = self.user_service.get_user_details_by_username(username)
        
        # Assert
        assert result is None
        logger.debug(f"Test réussi: utilisateur inexistant {username} retourne None")
    
    def test_get_user_details_by_username_no_condo_unit(self):
        """Test de récupération des détails d'un utilisateur sans unité de condo."""
        # Arrange
        username = "admin1"
        mock_user = User(
            username=username,
            email="admin1@condos.com",
            password_hash="hash123",
            full_name="Marie Admin",
            role=UserRole.ADMIN,
            condo_unit=None
        )
        self.mock_repository.get_user_by_username.return_value = mock_user
        
        # Act
        result = self.user_service.get_user_details_by_username(username)
        
        # Assert
        assert result is not None
        assert result['username'] == username
        assert result['condo_unit'] == "Non assigné"
        assert result['has_condo_unit'] is False
        logger.debug(f"Test réussi: utilisateur sans unité de condo {username}")
    
    def test_get_user_details_for_api_user_exists(self):
        """Test de récupération des détails API d'un utilisateur existant."""
        # Arrange
        username = "resident1"
        mock_user = User(
            username=username,
            email="resident1@condos.com",
            password_hash="hash123",
            full_name="Jean Dupont",
            role=UserRole.RESIDENT,
            condo_unit="A-101"
        )
        self.mock_repository.get_user_by_username.return_value = mock_user
        
        # Act
        result = self.user_service.get_user_details_for_api(username)
        
        # Assert
        assert result['found'] is True
        assert result['username'] == username
        assert result['full_name'] == "Jean Dupont"
        assert 'details' in result
        logger.debug(f"Test réussi: détails API récupérés pour {username}")
    
    def test_repository_called_with_correct_username(self):
        """Test que le repository est appelé avec le bon nom d'utilisateur."""
        # Arrange
        username = "test_user"
        self.mock_repository.get_user_by_username.return_value = None
        
        # Act
        self.user_service.get_user_details_by_username(username)
        
        # Assert
        self.mock_repository.get_user_by_username.assert_called_once_with(username)
        logger.debug("Test réussi: repository appelé avec le bon paramètre")
