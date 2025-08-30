#!/usr/bin/env python3
"""
Tests d'acceptance pour la fonctionnalité de création d'utilisateur.
Tests end-to-end de la logique métier et de l'intégration.
"""

import pytest
import asyncio
import os
import tempfile
import shutil

import sys
sys.path.insert(0, os.path.abspath('.'))


class TestUserCreationAcceptanceSimple:
    """Tests d'acceptance simplifiés pour la création d'utilisateur."""
    
    def test_user_creation_service_acceptance(self):
        """Test d'acceptance du service de création d'utilisateur."""
        # Test que le service existe et est importable
        from src.domain.services.user_creation_service import UserCreationService
        from src.adapters.user_file_adapter import UserFileAdapter
        from src.domain.entities.user import UserRole
        
        # Test que les classes sont bien définies
        assert UserCreationService is not None
        assert UserFileAdapter is not None
        assert UserRole.ADMIN is not None
        assert UserRole.RESIDENT is not None
        assert UserRole.GUEST is not None
    
    def test_user_creation_integration_acceptance(self):
        """Test d'acceptance de l'intégration création d'utilisateur."""
        # Créer un répertoire temporaire
        temp_dir = tempfile.mkdtemp()
        users_file = os.path.join(temp_dir, "test_users.json")
        
        try:
            # Test intégration complète
            from src.domain.services.user_creation_service import UserCreationService
            from src.adapters.user_file_adapter import UserFileAdapter
            from src.domain.entities.user import UserRole
            
            # Créer les composants
            repository = UserFileAdapter(users_file)
            service = UserCreationService(repository)
            
            # Test création asynchrone
            async def test_creation():
                await repository.initialize_default_users()
                
                # Créer un nouvel utilisateur
                user = await service.create_user(
                    username="test_acceptance",
                    email="test@acceptance.com",
                    password="testpass123",
                    full_name="Test Acceptance User",
                    role=UserRole.RESIDENT,
                    condo_unit="T-100"
                )
                
                assert user is not None
                assert user.username == "test_acceptance"
                assert user.email == "test@acceptance.com"
                assert user.role == UserRole.RESIDENT
                assert user.condo_unit == "T-100"
                
                # Vérifier persistance
                retrieved = await repository.get_user_by_username("test_acceptance")
                assert retrieved is not None
                assert retrieved.username == "test_acceptance"
                
                return True
            
            # Exécuter le test asynchrone
            result = asyncio.run(test_creation())
            assert result is True
            
        finally:
            # Nettoyage
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    def test_user_validation_rules_acceptance(self):
        """Test d'acceptance des règles de validation utilisateur."""
        from src.domain.services.user_creation_service import UserCreationService
        from src.adapters.user_file_adapter import UserFileAdapter
        from src.domain.entities.user import UserRole
        from src.domain.exceptions.business_exceptions import UserCreationError
        
        temp_dir = tempfile.mkdtemp()
        users_file = os.path.join(temp_dir, "validation_test.json")
        
        try:
            repository = UserFileAdapter(users_file)
            service = UserCreationService(repository)
            
            async def test_validations():
                await repository.initialize_default_users()
                
                # Test 1: Username trop court
                with pytest.raises(UserCreationError, match="au moins 3 caractères"):
                    await service.create_user(
                        username="ab",
                        email="test@test.com",
                        password="password123",
                        full_name="Test User",
                        role=UserRole.GUEST
                    )
                
                # Test 2: Email invalide
                with pytest.raises(UserCreationError, match="Email invalide"):
                    await service.create_user(
                        username="testuser",
                        email="email_invalide",
                        password="password123",
                        full_name="Test User",
                        role=UserRole.GUEST
                    )
                
                # Test 3: Mot de passe trop court
                with pytest.raises(UserCreationError, match="trop court"):
                    await service.create_user(
                        username="testuser",
                        email="test@test.com",
                        password="123",
                        full_name="Test User",
                        role=UserRole.GUEST
                    )
                
                # Test 4: Résident sans unité
                with pytest.raises(UserCreationError, match="Numéro d'unité requis"):
                    await service.create_user(
                        username="resident_test",
                        email="resident@test.com",
                        password="password123",
                        full_name="Test Resident",
                        role=UserRole.RESIDENT
                        # Pas d'unité fournie
                    )
                
                return True
            
            result = asyncio.run(test_validations())
            assert result is True
            
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    def test_web_interface_template_presence(self):
        """Test d'acceptance de la présence des templates web."""
        import os
        
        # Vérifier que les templates existent
        template_dir = "src/web/templates"
        
        # Template de création d'utilisateur
        users_new_template = os.path.join(template_dir, "users_new.html")
        assert os.path.exists(users_new_template), "Template users_new.html doit exister"
        
        # Template de liste des utilisateurs
        users_template = os.path.join(template_dir, "users.html")
        assert os.path.exists(users_template), "Template users.html doit exister"
        
        # Template de succès
        success_template = os.path.join(template_dir, "success.html")
        assert os.path.exists(success_template), "Template success.html doit exister"
    
    def test_route_definition_acceptance(self):
        """Test d'acceptance de la définition des routes."""
        from src.web.condo_app import app
        
        # Vérifier que la route de création d'utilisateur existe
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        
        assert "/users/new" in routes, "Route /users/new doit être définie"
        assert "/users" in routes, "Route /users doit être définie"
        
        # Vérifier les méthodes supportées
        for rule in app.url_map.iter_rules():
            if rule.rule == "/users/new":
                assert "GET" in rule.methods, "Route /users/new doit supporter GET"
                assert "POST" in rule.methods, "Route /users/new doit supporter POST"
    
    def test_complete_user_creation_workflow_acceptance(self):
        """Test d'acceptance du workflow complet de création d'utilisateur."""
        from src.domain.services.user_creation_service import UserCreationService
        from src.adapters.user_file_adapter import UserFileAdapter
        from src.domain.entities.user import UserRole
        
        temp_dir = tempfile.mkdtemp()
        users_file = os.path.join(temp_dir, "workflow_test.json")
        
        try:
            async def full_workflow():
                # 1. Initialisation
                repository = UserFileAdapter(users_file)
                service = UserCreationService(repository)
                await repository.initialize_default_users()
                
                # 2. Création d'un admin
                admin = await service.create_user(
                    username="workflow_admin",
                    email="admin@workflow.com",
                    password="adminpass123",
                    full_name="Workflow Admin",
                    role=UserRole.ADMIN
                )
                
                # 3. Création d'un résident
                resident = await service.create_user(
                    username="workflow_resident",
                    email="resident@workflow.com",
                    password="residentpass123",
                    full_name="Workflow Resident",
                    role=UserRole.RESIDENT,
                    condo_unit="WF-101"
                )
                
                # 4. Création d'un invité
                guest = await service.create_user(
                    username="workflow_guest",
                    email="guest@workflow.com",
                    password="guestpass123",
                    full_name="Workflow Guest",
                    role=UserRole.GUEST
                )
                
                # 5. Vérifications
                all_users = await repository.get_all_users()
                usernames = [u.username for u in all_users]
                
                assert "workflow_admin" in usernames
                assert "workflow_resident" in usernames
                assert "workflow_guest" in usernames
                
                # Vérifier les rôles
                admin_user = await repository.get_user_by_username("workflow_admin")
                assert admin_user.role == UserRole.ADMIN
                assert admin_user.condo_unit is None
                
                resident_user = await repository.get_user_by_username("workflow_resident")
                assert resident_user.role == UserRole.RESIDENT
                assert resident_user.condo_unit == "WF-101"
                
                guest_user = await repository.get_user_by_username("workflow_guest")
                assert guest_user.role == UserRole.GUEST
                assert guest_user.condo_unit is None
                
                return True
            
            result = asyncio.run(full_workflow())
            assert result is True
            
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


if __name__ == "__main__":
    # Exécuter les tests
    pytest.main([__file__, "-v"])
