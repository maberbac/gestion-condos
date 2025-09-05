"""
Tests d'acceptance pour le système de setup administrateur

Tests end-to-end vérifiant le workflow complet de configuration
du mot de passe administrateur initial avec mocking complet.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json

from src.application.services.system_config_service import SystemConfigService
from src.application.services.user_service import UserService
from src.domain.services.authentication_service import AuthenticationService
from src.domain.services.password_change_service import PasswordChangeService

class TestAdminSetupAcceptance(unittest.TestCase):
    """Tests d'acceptance pour le setup administrateur."""

    def setUp(self):
        """Configuration avant chaque test."""
        # Mock des repositories
        self.mock_system_config_repo = Mock()
        self.mock_user_repo = Mock()
        
        # Mock des services
        self.mock_auth_service = Mock(spec=AuthenticationService)
        
        # Configuration du système (services)
        self.system_config_service = SystemConfigService(self.mock_system_config_repo)
        self.password_service = PasswordChangeService(self.mock_user_repo, self.mock_auth_service)

    def test_admin_first_login_workflow_requires_password_change(self):
        """
        SCÉNARIO D'ACCEPTANCE : Premier login administrateur
        
        ÉTANT DONNÉ un système fraîchement installé
        QUAND l'administrateur se connecte pour la première fois
        ALORS il doit être forcé de changer son mot de passe
        ET aucune fonction admin ne doit être accessible avant le changement
        """
        # ARRANGE - Système non configuré
        self.mock_system_config_repo.get_boolean_config.return_value = False
        
        # ACT & ASSERT - Vérifier l'état initial
        setup_completed = self.system_config_service.is_system_setup_completed()
        self.assertFalse(setup_completed)
        
        admin_password_changed = self.system_config_service.is_admin_password_changed()
        self.assertFalse(admin_password_changed)
        
        # ACT & ASSERT - Valider le niveau de sécurité
        security_report = self.system_config_service.validate_system_security()
        expected_security = {
            'admin_password_changed': False,
            'security_level': 'LOW',
            'recommendations': ['Changer le mot de passe administrateur par défaut immédiatement']
        }
        self.assertEqual(security_report, expected_security)

    async def test_admin_password_change_workflow_success(self):
        """
        SCÉNARIO D'ACCEPTANCE : Changement de mot de passe administrateur réussi
        
        ÉTANT DONNÉ un administrateur connecté avec mot de passe par défaut
        QUAND il change son mot de passe vers un mot de passe sécurisé
        ALORS le système doit marquer le setup comme terminé
        ET l'administrateur doit avoir accès à toutes les fonctions
        """
        # ARRANGE - Mot de passe par défaut non changé
        self.mock_system_config_repo.get_boolean_config.return_value = False
        self.mock_system_config_repo.set_boolean_config.return_value = True
        
        # Mock de l'authentification et du changement de mot de passe
        mock_admin_user = Mock()
        mock_admin_user.username = "admin"
        mock_admin_user.role.value = "admin"
        
        self.mock_auth_service.authenticate.return_value = mock_admin_user
        self.mock_user_repo.update_user_password.return_value = True
        
        # ACT - Changement de mot de passe
        password_change_result = await self.password_service.change_password(
            "admin", "default_password", "new_secure_password123"
        )
        
        # ASSERT - Changement réussi
        self.assertTrue(password_change_result)
        
        # ACT - Marquer le setup comme terminé
        mark_result = self.system_config_service.mark_admin_password_changed()
        
        # ASSERT - Setup marqué comme terminé
        self.assertTrue(mark_result)
        self.mock_system_config_repo.set_boolean_config.assert_called_with(
            'admin_password_changed', 
            True, 
            'Indique si l\'administrateur a changé son mot de passe par défaut'
        )

    def test_admin_setup_status_after_password_change(self):
        """
        SCÉNARIO D'ACCEPTANCE : Statut du système après changement de mot de passe
        
        ÉTANT DONNÉ un administrateur qui a changé son mot de passe
        QUAND on vérifie le statut du système
        ALORS le setup doit être marqué comme terminé
        ET le niveau de sécurité doit être ÉLEVÉ
        """
        # ARRANGE - Mot de passe changé
        self.mock_system_config_repo.get_boolean_config.return_value = True
        
        # ACT - Vérifier le statut de setup
        setup_status = self.system_config_service.get_system_setup_status()
        
        # ASSERT - Setup terminé
        expected_status = {
            'admin_password_changed': True,
            'setup_completed': True
        }
        self.assertEqual(setup_status, expected_status)
        
        # ACT - Vérifier la sécurité
        security_report = self.system_config_service.validate_system_security()
        
        # ASSERT - Sécurité élevée
        expected_security = {
            'admin_password_changed': True,
            'security_level': 'HIGH',
            'recommendations': []
        }
        self.assertEqual(security_report, expected_security)

    async def test_admin_password_change_validation_errors(self):
        """
        SCÉNARIO D'ACCEPTANCE : Validation des erreurs lors du changement de mot de passe
        
        ÉTANT DONNÉ un administrateur tentant de changer son mot de passe
        QUAND il fournit des données invalides
        ALORS le système doit rejeter le changement et fournir des messages d'erreur appropriés
        """
        # ARRANGE
        from src.domain.services.password_change_service import PasswordChangeError
        
        # ACT & ASSERT - Mot de passe actuel incorrect
        self.mock_auth_service.authenticate.return_value = None
        
        with self.assertRaises(PasswordChangeError) as context:
            await self.password_service.change_password("admin", "wrong_password", "new_password")
        
        self.assertIn("incorrect", str(context.exception))
        
        # ACT & ASSERT - Nouveau mot de passe trop court
        with self.assertRaises(PasswordChangeError) as context:
            await self.password_service.change_password("admin", "current", "123")
        
        self.assertIn("6 caractères", str(context.exception))
        
        # ACT & ASSERT - Nouveau mot de passe identique à l'actuel
        mock_user = Mock()
        self.mock_auth_service.authenticate.return_value = mock_user
        
        with self.assertRaises(PasswordChangeError) as context:
            await self.password_service.change_password("admin", "same_password", "same_password")
        
        self.assertIn("différent", str(context.exception))

    def test_system_configuration_persistence(self):
        """
        SCÉNARIO D'ACCEPTANCE : Persistance de la configuration système
        
        ÉTANT DONNÉ un système configuré
        QUAND on redémarre l'application
        ALORS la configuration doit être persistée
        ET l'administrateur ne doit pas avoir à reconfigurer
        """
        # ARRANGE - Configuration initiale
        config_data = [
            {'config_key': 'admin_password_changed', 'config_value': 'true', 'config_type': 'boolean'},
            {'config_key': 'system_version', 'config_value': '1.0.0', 'config_type': 'string'}
        ]
        self.mock_system_config_repo.get_all_configs.return_value = config_data
        
        # ACT - Récupérer toutes les configurations
        all_configs = self.system_config_service.get_all_system_configs()
        
        # ASSERT - Configuration persistée
        self.assertIn('admin_password_changed', all_configs)
        self.assertEqual(all_configs['admin_password_changed']['config_value'], 'true')
        self.assertEqual(all_configs['admin_password_changed']['config_type'], 'boolean')
        
        # ACT & ASSERT - Vérifier que le setup est considéré comme terminé
        self.mock_system_config_repo.get_boolean_config.return_value = True
        setup_completed = self.system_config_service.is_system_setup_completed()
        self.assertTrue(setup_completed)

    def test_admin_setup_reset_capability(self):
        """
        SCÉNARIO D'ACCEPTANCE : Capacité de remise à zéro du setup admin
        
        ÉTANT DONNÉ un système configuré
        QUAND un administrateur remet à zéro le statut de setup
        ALORS le prochain administrateur doit être forcé de changer son mot de passe
        """
        # ARRANGE - Système initialement configuré
        self.mock_system_config_repo.get_boolean_config.return_value = True
        self.mock_system_config_repo.set_boolean_config.return_value = True
        
        # ACT & ASSERT - État initial configuré
        self.assertTrue(self.system_config_service.is_admin_password_changed())
        
        # ACT - Remise à zéro
        reset_result = self.system_config_service.reset_admin_password_status()
        
        # ASSERT - Remise à zéro réussie
        self.assertTrue(reset_result)
        self.mock_system_config_repo.set_boolean_config.assert_called_with(
            'admin_password_changed', 
            False, 
            'Indique si l\'administrateur a changé son mot de passe par défaut'
        )
        
        # ACT & ASSERT - Vérifier que le setup n'est plus terminé
        self.mock_system_config_repo.get_boolean_config.return_value = False
        self.assertFalse(self.system_config_service.is_system_setup_completed())

    def test_multiple_configuration_management(self):
        """
        SCÉNARIO D'ACCEPTANCE : Gestion de multiples configurations système
        
        ÉTANT DONNÉ un système avec plusieurs paramètres de configuration
        QUAND on gère ces configurations
        ALORS chaque type de configuration doit être géré correctement
        """
        # ARRANGE - Mock des réponses pour différents types de config
        def mock_get_config_value(key):
            config_map = {
                'admin_password_changed': 'true',
                'debug_mode': 'false',
                'app_version': '1.0.0',
                'max_users': '100'
            }
            return config_map.get(key)
        
        def mock_get_boolean_config(key, default):
            bool_map = {
                'admin_password_changed': True,
                'debug_mode': False
            }
            return bool_map.get(key, default)
        
        self.mock_system_config_repo.get_config_value.side_effect = mock_get_config_value
        self.mock_system_config_repo.get_boolean_config.side_effect = mock_get_boolean_config
        self.mock_system_config_repo.set_config_value.return_value = True
        self.mock_system_config_repo.set_boolean_config.return_value = True
        
        # ACT & ASSERT - Gestion des configurations string
        app_version = self.system_config_service.get_config_value('app_version')
        self.assertEqual(app_version, '1.0.0')
        
        set_result = self.system_config_service.set_config_value('new_config', 'new_value', 'string', 'Test config')
        self.assertTrue(set_result)
        
        # ACT & ASSERT - Gestion des configurations booléennes
        debug_mode = self.system_config_service.get_boolean_config('debug_mode', True)
        self.assertFalse(debug_mode)
        
        bool_set_result = self.system_config_service.set_boolean_config('maintenance_mode', True, 'Maintenance flag')
        self.assertTrue(bool_set_result)
        
        # ACT & ASSERT - Configuration critique admin
        admin_password_status = self.system_config_service.is_admin_password_changed()
        self.assertTrue(admin_password_status)

    def test_error_recovery_and_fallback_behavior(self):
        """
        SCÉNARIO D'ACCEPTANCE : Récupération d'erreurs et comportement de fallback
        
        ÉTANT DONNÉ un système avec des erreurs de base de données
        QUAND les opérations de configuration échouent
        ALORS le système doit avoir un comportement de fallback sécurisé
        """
        # ARRANGE - Mock d'erreurs de base de données
        self.mock_system_config_repo.get_boolean_config.side_effect = Exception("Database error")
        self.mock_system_config_repo.get_config_value.side_effect = Exception("Database error")
        self.mock_system_config_repo.set_config_value.side_effect = Exception("Database error")
        
        # ACT & ASSERT - Comportement de fallback sécurisé
        # Pour la sécurité, on assume que le mot de passe n'a PAS été changé en cas d'erreur
        admin_password_changed = self.system_config_service.is_admin_password_changed()
        self.assertFalse(admin_password_changed)  # Fallback sécurisé
        
        setup_completed = self.system_config_service.is_system_setup_completed()
        self.assertFalse(setup_completed)  # Fallback sécurisé
        
        # Les opérations de lecture retournent des valeurs par défaut sécurisées
        config_value = self.system_config_service.get_config_value('any_key')
        self.assertIsNone(config_value)
        
        # Les opérations d'écriture échouent gracieusement
        set_result = self.system_config_service.set_config_value('key', 'value')
        self.assertFalse(set_result)

if __name__ == '__main__':
    unittest.main()
