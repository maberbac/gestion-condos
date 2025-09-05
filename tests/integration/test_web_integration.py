"""
Tests d'intégration pour l'interface web Flask.

[TDD - RED-GREEN-REFACTOR]
Ces tests valident l'intégration entre :
- Application Flask (interface)
- Services de domaine
- Authentification et sessions
- Architecture hexagonale via web
"""

import unittest
import asyncio
import tempfile
import os
import json
from unittest.mock import patch, Mock

from src.web.condo_app import app, init_services, auth_service, repository
from src.domain.entities.user import User, UserRole
from src.adapters.user_file_adapter import UserFileAdapter


class TestWebIntegration(unittest.TestCase):
    """Tests d'intégration pour l'interface web Flask"""
    
    def setUp(self):
        """Configuration pour chaque test"""
        # Configuration Flask pour tests
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'test-secret-key'
        
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Créer répertoire temporaire pour tests
        self.temp_dir = tempfile.mkdtemp()
        self.test_users_file = os.path.join(self.temp_dir, 'test_users.json')
        
        # Données de test
        self.test_users = [
            User(
                username='admin',
                email='admin@test.com',
                password_hash=User.hash_password('admin123'),
                role=UserRole.ADMIN,
                full_name='Admin User'
            ),
            User(
                username='resident1',
                email='resident1@test.com',
                password_hash=User.hash_password('resident123'),
                role=UserRole.RESIDENT,
                full_name='Resident One',
                condo_unit='A-101'
            )
        ]
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        self.app_context.pop()
        
        # Nettoyer fichiers temporaires
        if os.path.exists(self.test_users_file):
            os.remove(self.test_users_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    @patch('src.adapters.project_repository_sqlite.ProjectRepositorySQLite.__init__')
    @patch('src.web.condo_app.SQLiteAdapter')
    @patch('src.web.condo_app.UserRepositorySQLite')  
    @patch('src.web.condo_app.AuthenticationService')
    def test_service_initialization_integration(self, mock_auth_service, mock_user_repository, mock_adapter, mock_project_init):
        """Test intégration initialisation des services avec mocking complet des constructeurs"""
        # Arrange
        mock_user_repository_instance = Mock()
        mock_auth_instance = Mock()
        mock_adapter_instance = Mock()
        
        # Mock le constructeur SQLiteAdapter pour éviter le chargement de fichier
        mock_adapter_instance.config = {
            "database_file": "data/condos.db",
            "tables": {
                "users": "users",
                "condos": "condos"
            }
        }
        
        # Mock le constructeur UserRepositorySQLite pour éviter le chargement de fichier config
        mock_user_repository_instance.config = {
            "database_file": "data/condos.db",
            "table_name": "users"
        }
        
        # Mock le constructeur ProjectRepositorySQLite pour éviter les migrations SQL
        mock_project_init.return_value = None
        
        mock_user_repository.return_value = mock_user_repository_instance
        mock_auth_service.return_value = mock_auth_instance
        mock_adapter.return_value = mock_adapter_instance
        
        # Act - Appeler init_services avec les mocks en place
        result = None
        try:
            init_services()
            result = "success"
        except Exception as e:
            result = f"error: {str(e)}"
        
        # Assert - Vérifier que l'initialisation s'est déroulée sans erreur critique
        self.assertEqual(result, "success")
    
    def test_home_page_access_without_auth(self):
        """Test accès page d'accueil sans authentification"""
        # Act
        response = self.client.get('/')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Gestion des Condos', response.data)
    
    def test_login_page_access(self):
        """Test accès page de connexion"""
        # Act
        response = self.client.get('/login')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.data.lower())
    
    @patch('src.web.condo_app.auth_service')
    def test_login_workflow_success(self, mock_auth_service):
        """Test workflow de connexion réussie"""
        # Arrange - Créer un mock user avec les bonnes propriétés
        mock_user = Mock()
        mock_user.user_id = 'admin'
        mock_user.username = 'admin'
        mock_user.role = Mock()
        mock_user.role.value = 'admin'
        mock_user.full_name = 'Admin User'
        mock_user.condo_unit = 'Admin'
        mock_user.last_login = None
        
        # Mock de la méthode authenticate comme coroutine
        async def mock_authenticate(username, password):
            if username == 'admin' and password == 'admin123':
                return mock_user
            return None
        
        mock_auth_service.authenticate = mock_authenticate
        mock_auth_service.create_session.return_value = 'mock-session-token'
        
        # Act
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        # Vérifier que la session a été créée
        with self.client.session_transaction() as sess:
            self.assertIn('user_id', sess)
    
    @patch('src.web.condo_app.auth_service')
    def test_login_workflow_failure(self, mock_auth_service):
        """Test workflow de connexion échouée"""
        # Arrange
        async def mock_authenticate(username, password):
            return None  # Authentification échouée
        
        mock_auth_service.authenticate = mock_authenticate
        
        # Act
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        # Assert
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Identifiants invalides', response.data)
    
    def test_logout_workflow(self):
        """Test workflow de déconnexion"""
        # Arrange - Simuler utilisateur connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['role'] = 'admin'
            sess['session_token'] = 'mock-token'
        
        # Act
        response = self.client.get('/logout', follow_redirects=True)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la session a été nettoyée
        with self.client.session_transaction() as sess:
            self.assertNotIn('user_id', sess)
    
    def test_protected_route_without_auth(self):
        """Test accès route protégée sans authentification"""
        # Act
        response = self.client.get('/dashboard')
        
        # Assert
        self.assertEqual(response.status_code, 302)  # Redirection vers login
        self.assertIn('/login', response.location)
    
    def test_protected_route_with_auth(self):
        """Test accès route protégée avec authentification"""
        # Arrange - Simuler utilisateur connecté
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['role'] = 'admin'
        
        # Act
        response = self.client.get('/dashboard')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Tableau de bord', response.data)
    
    def test_role_based_access_admin_only(self):
        """Test accès basé sur les rôles - admin seulement"""
        # Arrange - Utilisateur résident
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'resident1'
            sess['role'] = 'resident'
        
        # Act
        response = self.client.get('/admin')
        
        # Assert
        self.assertEqual(response.status_code, 403)  # Accès refusé
    
    def test_role_based_access_admin_allowed(self):
        """Test accès basé sur les rôles - admin autorisé"""
        # Arrange - Utilisateur admin
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['role'] = 'admin'
        
        # Act
        response = self.client.get('/admin')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        # Vérifier le contenu du dashboard admin
        self.assertIn(b'Tableau de Bord Administrateur', response.data)
    
    def test_error_handling_integration(self):
        """Test intégration gestion d'erreurs"""
        # Act - Route qui n'existe pas
        response = self.client.get('/nonexistent')
        
        # Assert
        self.assertEqual(response.status_code, 404)
    
    @patch('src.web.condo_app.auth_service')
    def test_async_operations_in_web_context(self, mock_auth_service):
        """Test opérations asynchrones dans contexte web"""
        # Arrange - Créer un mock user avec les bonnes propriétés  
        mock_user = Mock()
        mock_user.user_id = 'testuser'
        mock_user.username = 'testuser'
        mock_user.role = Mock()
        mock_user.role.value = 'resident'
        mock_user.full_name = 'Test User'
        mock_user.condo_unit = '101'
        mock_user.last_login = None
        
        # Mock de la méthode authenticate comme coroutine
        async def mock_authenticate(username, password):
            if username == 'testuser':
                return mock_user
            return None
        
        mock_auth_service.authenticate = mock_authenticate
        mock_auth_service.create_session.return_value = 'session-token'
        
        # Act
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        })
        
        # Assert
        # Vérifier que l'opération async a été gérée correctement
        self.assertIn(response.status_code, [200, 302])
    
    def test_session_persistence_across_requests(self):
        """Test persistance session entre requêtes"""
        # Arrange - Première requête pour établir session
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['role'] = 'admin'
            sess['test_data'] = 'persistent_value'
        
        # Act - Deuxième requête
        response = self.client.get('/dashboard')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que les données de session persistent
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('test_data'), 'persistent_value')
    
    def test_csrf_protection_integration(self):
        """Test intégration protection CSRF"""
        # Note: CSRF désactivé pour les tests, mais on teste la structure
        
        # Act
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': 'password'
        })
        
        # Assert
        # Doit accepter la requête même sans token CSRF (config test)
        self.assertNotEqual(response.status_code, 400)
    
    def test_template_rendering_integration(self):
        """Test intégration rendu templates"""
        # Act
        response = self.client.get('/')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)
        self.assertIn(b'Gestion des Condos', response.data)
    
    def test_static_files_serving(self):
        """Test service fichiers statiques"""
        # Act
        response = self.client.get('/static/css/style.css')
        
        # Assert
        # Peut retourner 404 si le fichier n'existe pas, mais ne doit pas crasher
        self.assertIn(response.status_code, [200, 404])
    
    @patch('src.web.condo_app.auth_service')
    def test_concurrent_user_sessions(self, mock_auth_service):
        """Test sessions utilisateur concurrentes"""
        # Arrange
        def create_mock_user(username, role):
            mock_user = Mock()
            mock_user.username = username
            mock_user.role = role
            return mock_user
        
        # Simuler deux clients différents
        client1 = app.test_client()
        client2 = app.test_client()
        
        # Act - Sessions séparées
        with client1.session_transaction() as sess:
            sess['user_id'] = 'user1'
            sess['role'] = 'admin'
        
        with client2.session_transaction() as sess:
            sess['user_id'] = 'user2'
            sess['role'] = 'resident'
        
        response1 = client1.get('/dashboard')
        response2 = client2.get('/dashboard')
        
        # Assert
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        
        # Vérifier isolation des sessions
        with client1.session_transaction() as sess:
            self.assertEqual(sess['user_id'], 'user1')
        
        with client2.session_transaction() as sess:
            self.assertEqual(sess['user_id'], 'user2')
    
    def test_configuration_integration_with_web(self):
        """Test intégration configuration avec application web"""
        # Act
        with app.app_context():
            secret_key = app.config.get('SECRET_KEY')
            testing_mode = app.config.get('TESTING')
        
        # Assert
        self.assertIsNotNone(secret_key)
        self.assertTrue(testing_mode)


if __name__ == '__main__':
    unittest.main()
