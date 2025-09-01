"""
Tests unitaires pour le service de gestion des projets
Tests pour valider la logique d'orchestration des projets avec créati            self.assertGreaterEqual(unit.area, expected_avg * 0.55)  # 55% minimum
            self.assertLessEqual(unit.area, expected_avg * 1.5)   # 150% maximum d'unités
"""
import unittest
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
from datetime import datetime

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from application.services.project_service import ProjectService
from domain.entities.project import Project
from domain.entities.condo import Condo, CondoType, CondoStatus


class TestProjectService(unittest.TestCase):
    """Tests unitaires pour le service de gestion des projets"""
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        # Mock du repository
        self.mock_project_repository = Mock()
        self.mock_condo_repository = Mock()
        
        # Service à tester
        self.project_service = ProjectService(
            project_repository=self.mock_project_repository,
            condo_repository=self.mock_condo_repository
        )
        
        # Données de test
        self.valid_project_data = {
            'name': 'Résidence du Parc',
            'address': '123 Rue de la Paix, Montréal, QC H1A 1A1',
            'total_area': 5000.0,
            'construction_year': 2020,
            'unit_count': 15,
            'constructor': 'Construction ABC Inc.'
        }
    
    @patch('application.services.project_service.asyncio.run')
    def test_create_project_success(self, mock_asyncio_run):
        """Test de création réussie d'un projet avec unités"""
        # Arrange
        mock_asyncio_run.return_value = True  # Simulation succès save
        self.mock_project_repository.save_project.return_value = AsyncMock(return_value=True)
        self.mock_condo_repository.save_condo.return_value = AsyncMock(return_value=True)
        
        # Act
        result = self.project_service.create_project_with_units(self.valid_project_data)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertIn('project', result)
        self.assertIn('units', result)
        self.assertEqual(len(result['units']), 15)
        
        # Vérifier que le projet a été créé
        project = result['project']
        self.assertEqual(project.name, 'Résidence du Parc')
        self.assertEqual(project.unit_count, 15)
        self.assertEqual(len(project.units), 15)
    
    def test_create_project_validation_error(self):
        """Test de gestion d'erreur de validation lors de création"""
        # Arrange
        invalid_data = self.valid_project_data.copy()
        invalid_data['name'] = ''  # Nom vide invalide
        
        # Act
        result = self.project_service.create_project_with_units(invalid_data)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('nom du projet', result['error'])
    
    def test_create_project_repository_error(self):
        """Test de gestion d'erreur du repository"""
        # Arrange
        # Mock le repository pour lever une exception lors de la sauvegarde
        with patch.object(self.project_service.project_repository, 'save_project') as mock_save:
            mock_save.side_effect = Exception("Erreur de base de données")
            
            # Act
            result = self.project_service.create_project_with_units(self.valid_project_data)
            
            # Assert
            self.assertFalse(result['success'])
            self.assertIn('error', result)
            self.assertIn('Erreur système', result['error'])
    
    def test_generate_unit_numbers_logic(self):
        """Test de la logique de génération de numéros d'unités"""
        # Arrange
        project = Project(**self.valid_project_data)
        
        # Act
        units = project.generate_units()
        
        # Assert
        # Vérifier la logique de numérotation (étages + unités par étage)
        expected_numbers = []
        # Utiliser le format réel généré par le code : A-101, A-102, etc.
        for i in range(15):
            floor = (i // 4) + 1  # 4 unités par étage
            unit_on_floor = (i % 4) + 1
            expected_numbers.append(f"A-{floor:01d}{unit_on_floor:02d}")
        
        actual_numbers = [unit.unit_number for unit in units]
        self.assertEqual(actual_numbers, expected_numbers)
    
    def test_calculate_unit_areas_distribution(self):
        """Test de la distribution des superficies d'unités"""
        # Arrange
        project = Project(**self.valid_project_data)
        
        # Act
        units = project.generate_units()
        
        # Assert
        # Vérifier que les superficies sont dans une plage raisonnable
        expected_avg = project.total_area / project.unit_count  # 5000/15 ≈ 333.33
        
        for unit in units:
            # Chaque unité doit être dans une plage raisonnable (tenant compte des types différents et variations)
            # Commercial peut être 1.2x + 15% = 1.38x, Storage peut être 0.7x * 0.85 = 0.595x
            self.assertGreaterEqual(unit.area, expected_avg * 0.55)  # 55% minimum
            self.assertLessEqual(unit.area, expected_avg * 1.45)     # 145% maximum
        
        # La somme totale doit être raisonnablement proche de la superficie totale
        total_calculated = sum(unit.area for unit in units)
        # Tolérance de ±15% due à la variation aléatoire
        self.assertGreaterEqual(total_calculated, project.total_area * 0.85)
        self.assertLessEqual(total_calculated, project.total_area * 1.15)
    
    def test_get_project_statistics(self):
        """Test de calcul des statistiques d'un projet"""
        # Arrange
        project = Project(**self.valid_project_data)
        project.generate_units()
        
        # Simuler quelques ventes
        project.units[0].transfer_ownership("Jean Dupont")
        project.units[1].transfer_ownership("Marie Tremblay")
        
        # Ajouter le projet à la liste en mémoire du service
        self.project_service._projects = [project]
        
        # Act
        result = self.project_service.get_project_statistics('Résidence du Parc')
        
        # Assert
        self.assertTrue(result['success'])
        stats = result['statistics']
        
        self.assertEqual(stats['total_units'], 15)
        self.assertEqual(stats['sold_units'], 2)
        self.assertEqual(stats['available_units'], 13)
        self.assertAlmostEqual(stats['occupancy_rate'], (2/15)*100, places=1)
    
    def test_programming_functional_concepts(self):
        """Test des concepts de programmation fonctionnelle dans le service"""
        # Arrange
        project = Project(**self.valid_project_data)
        project.generate_units()
        
        # Simuler des ventes pour certaines unités
        sold_units = project.units[:5]  # 5 premières unités vendues
        for i, unit in enumerate(sold_units):
            unit.transfer_ownership(f"Propriétaire {i+1}")
        
        # Act - Utilisation de filter et map (programmation fonctionnelle)
        available_units = list(filter(lambda u: u.owner_name is None or u.owner_name == "Disponible", project.units))
        sold_units_list = list(filter(lambda u: u.owner_name is not None and u.owner_name != "Disponible", project.units))
        unit_areas = list(map(lambda u: u.area, project.units))
        
        # Assert
        self.assertEqual(len(available_units), 10)  # 15 - 5 = 10
        self.assertEqual(len(sold_units_list), 5)
        self.assertEqual(len(unit_areas), 15)
        
        # Vérifier que toutes les superficies sont positives
        self.assertTrue(all(area > 0 for area in unit_areas))
    
    def test_async_operations_simulation(self):
        """Test de simulation des opérations asynchrones"""
        # Arrange
        project = Project(**self.valid_project_data)
        
        # Act & Assert - Vérifier que les opérations peuvent être appelées
        # (dans un vrai contexte async, ceci utiliserait await)
        try:
            units = project.generate_units()
            stats = project.get_project_statistics()
            
            # Simulation de sauvegarde asynchrone réussie
            self.assertIsNotNone(units)
            self.assertIsNotNone(stats)
            self.assertTrue(True)  # Succès si aucune exception
            
        except Exception as e:
            self.fail(f"Les opérations asynchrones simulées ont échoué: {e}")
    
    def test_error_handling_comprehensive(self):
        """Test de gestion d'erreurs complète"""
        # Test 1: Données invalides
        invalid_data_cases = [
            {'name': '', 'error_contains': 'nom'},
            {'address': '', 'error_contains': 'adresse'},
            {'total_area': -100, 'error_contains': 'superficie'},
            {'construction_year': 1800, 'error_contains': 'année'},
            {'unit_count': 0, 'error_contains': 'unités'},
            {'constructor': '', 'error_contains': 'constructeur'}
        ]
        
        for invalid_case in invalid_data_cases:
            with self.subTest(invalid_case=invalid_case):
                test_data = self.valid_project_data.copy()
                test_data.update({k: v for k, v in invalid_case.items() if k != 'error_contains'})
                
                result = self.project_service.create_project_with_units(test_data)
                
                self.assertFalse(result['success'])
                self.assertIn('error', result)
                self.assertIn(invalid_case['error_contains'], result['error'].lower())

    def test_delete_project_success(self):
        """Test de suppression réussie d'un projet"""
        # Arrange
        project_name = "Test Project"
        project_id = "test-project-123"
        
        # Mock d'un projet existant
        mock_project = Mock()
        mock_project.name = project_name
        mock_project.project_id = project_id
        mock_project.units = [Mock(), Mock()]  # 2 unités
        
        # Configuration des mocks pour éviter l'erreur de chargement
        self.mock_project_repository.get_all_projects.return_value = [mock_project]
        self.mock_project_repository.delete_project.return_value = True
        
        # Recharger manuellement pour que les projets soient dans la liste
        self.project_service._load_projects()
        
        # Act
        result = self.project_service.delete_project(project_name)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['project_name'], project_name)
        self.assertEqual(result['total_units_deleted'], 2)
        self.assertIn('supprimé avec succès', result['message'])
        
        # Vérifier que le repository a été appelé avec le bon ID
        self.mock_project_repository.delete_project.assert_called_once_with(project_id)

    def test_delete_project_not_found(self):
        """Test de suppression d'un projet inexistant"""
        # Arrange
        project_name = "Projet Inexistant"
        self.mock_project_repository.get_all_projects.return_value = []  # Aucun projet
        self.project_service._load_projects()  # Recharger avec liste vide
        
        # Act
        result = self.project_service.delete_project(project_name)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertIn('non trouvé', result['error'])
        self.assertIn(project_name, result['error'])
        
        # Vérifier que le repository n'a pas été appelé
        self.mock_project_repository.delete_project.assert_not_called()

    def test_delete_project_repository_error(self):
        """Test de suppression avec erreur dans le repository"""
        # Arrange
        project_name = "Test Project"
        project_id = "test-project-123"
        
        mock_project = Mock()
        mock_project.name = project_name
        mock_project.project_id = project_id
        mock_project.units = []
        
        self.mock_project_repository.get_all_projects.return_value = [mock_project]
        self.mock_project_repository.delete_project.return_value = False  # Échec
        self.project_service._load_projects()  # Charger le projet
        
        # Act
        result = self.project_service.delete_project(project_name)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertIn('base de données', result['error'])


if __name__ == '__main__':
    unittest.main()
