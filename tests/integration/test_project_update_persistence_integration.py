"""
Test d'intégration pour vérifier la correction de la persistance des modifications de projet
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from application.services.project_service import ProjectService
from domain.entities.project import Project, ProjectStatus


class TestProjectUpdatePersistenceIntegration(unittest.TestCase):
    """Test d'intégration pour la persistance des modifications de projet"""
    
    def setUp(self):
        """Configuration avec mocking complet pour éviter la base de données"""
        # Mock complet du repository
        self.mock_repository = Mock()
        self.mock_repository.get_all_projects.return_value = []
        self.mock_repository.save_project = Mock(return_value="test-id")
        
        # Service avec repository mocké
        self.project_service = ProjectService(project_repository=self.mock_repository)
    
    def test_update_project_calls_repository_save(self):
        """Vérifier que update_project appelle bien save_project pour la persistance"""
        # ÉTANT DONNÉ: Un projet existant
        existing_project = Project(
            name="Projet Test",
            address="123 Test Street",
            building_area=2000.0,
            construction_year=2023,
            unit_count=10,
            constructor="Test Builder"
        )
        existing_project.project_id = "test-persistence-id"
        
        # Ajouter le projet à la liste interne
        self.project_service._projects = [existing_project]
        
        # QUAND: On modifie le projet
        existing_project.name = "Projet Modifié"
        existing_project.address = "456 Nouvelle Adresse"
        existing_project.status = ProjectStatus.ACTIVE
        
        # QUAND: On appelle update_project
        result = self.project_service.update_project(existing_project)
        
        # ALORS: La méthode réussit
        self.assertTrue(result['success'], f"Erreur: {result.get('error', 'N/A')}")
        self.assertIn('mis à jour avec succès', result['message'])
        
        # ET: Le repository.save_project est appelé pour la persistance
        self.mock_repository.save_project.assert_called_once_with(existing_project)
        
        print("✅ Test réussi: update_project appelle bien save_project pour la persistance")
        
    def test_update_project_validates_and_persists_all_fields(self):
        """Vérifier que tous les champs modifiables sont persistés"""
        # ÉTANT DONNÉ: Un projet avec toutes les données
        project = Project(
            name="Projet Original",
            address="Adresse Originale",
            building_area=1500.0,
            construction_year=2022,
            unit_count=8,
            constructor="Constructeur Original"
        )
        project.project_id = "test-all-fields"
        project.status = ProjectStatus.PLANNING
        
        self.project_service._projects = [project]
        
        # QUAND: On modifie tous les champs autorisés
        project.name = "Nouveau Nom"
        project.address = "Nouvelle Adresse Complète"
        project.constructor = "Nouveau Constructeur"
        project.construction_year = 2025
        project.building_area = 2500.0
        project.status = ProjectStatus.COMPLETED
        # unit_count reste inchangé (non modifiable)
        
        # ALORS: La mise à jour réussit
        result = self.project_service.update_project(project)
        
        self.assertTrue(result['success'])
        self.mock_repository.save_project.assert_called_once()
        
        # Vérifier que le projet passé au repository a les bonnes valeurs
        saved_project = self.mock_repository.save_project.call_args[0][0]
        self.assertEqual(saved_project.name, "Nouveau Nom")
        self.assertEqual(saved_project.address, "Nouvelle Adresse Complète")
        self.assertEqual(saved_project.constructor, "Nouveau Constructeur")
        self.assertEqual(saved_project.construction_year, 2025)
        self.assertEqual(saved_project.building_area, 2500.0)
        self.assertEqual(saved_project.status, ProjectStatus.COMPLETED)
        self.assertEqual(saved_project.unit_count, 8)  # Inchangé
        
        print("✅ Test réussi: Tous les champs modifiables sont correctement persistés")


if __name__ == '__main__':
    unittest.main(verbosity=2)
