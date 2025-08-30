"""
Tests unitaires pour les détails d'utilisateur - TDD Phase RED
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.application.services.user_service import UserService
from src.domain.entities.user import User, UserRole


class TestUserDetailsService:
    """Tests unitaires pour le service de détails utilisateur"""
    
    def setup_method(self):
        """Configuration pour chaque test"""
        self.mock_repository = Mock()
        self.user_service = UserService(self.mock_repository)
    
    def test_get_user_details_by_username_returns_formatted_data(self):
        """Test que get_user_details_by_username retourne des données formatées"""
        # Arrange
        mock_user = User(
            username="admin",
            full_name="Admin User", 
            email="admin@condos.com",
            password_hash="hashed_password",
            role=UserRole.ADMIN,
            condo_unit="A-101"
        )
        mock_user.last_login = "2024-12-29 10:30:00"
        
        self.mock_repository.get_user_by_username = AsyncMock(return_value=mock_user)
        
        # Act
        result = self.user_service.get_user_details_by_username("admin")
        
        # Assert
        assert result is not None
        assert result['username'] == "admin"
        assert result['full_name'] == "Admin User"
        assert result['email'] == "admin@condos.com"
        assert result['role'] == "admin"
        assert result['role_display'] == "Administrateur"
        assert result['condo_unit'] == "A-101"
        assert result['last_login'] == "2024-12-29 10:30:00"
        assert result['has_condo_unit'] is True
    
    def test_get_user_details_for_api_returns_json_serializable_data(self):
        """Test que get_user_details_for_api retourne des données sérialisables JSON"""
        # Arrange
        mock_user = User(
            username="resident",
            full_name="Jane Resident",
            email="jane@condos.com",
            password_hash="hashed_password", 
            role=UserRole.RESIDENT,
            condo_unit="B-205"
        )
        
        self.mock_repository.get_user_by_username = AsyncMock(return_value=mock_user)
        
        # Act
        result = self.user_service.get_user_details_for_api("resident")
        
        # Assert
        assert result is not None
        assert result['username'] == "resident"
        assert result['full_name'] == "Jane Resident"
        assert result['email'] == "jane@condos.com"
        assert result['role'] == "resident"
        assert result['condo_unit'] == "B-205"
        assert result['found'] is True
        assert 'details' in result
        assert result['details']['role_display'] == "Résident"
    
    def test_get_user_details_handles_user_not_found(self):
        """Test que le service gère gracieusement les utilisateurs non trouvés"""
        # Arrange
        self.mock_repository.get_user_by_username = AsyncMock(return_value=None)
        
        # Act
        result = self.user_service.get_user_details_by_username("inexistant")
        
        # Assert
        assert result is None
    
    def test_get_user_details_handles_repository_errors(self):
        """Test que le service gère les erreurs du repository"""
        # Arrange
        self.mock_repository.get_user_by_username = AsyncMock(side_effect=Exception("Database error"))
        
        # Act
        result = self.user_service.get_user_details_by_username("admin")
        
        # Assert
        assert result is None  # Le service doit retourner None en cas d'erreur


if __name__ == "__main__":
    pytest.main([__file__])
