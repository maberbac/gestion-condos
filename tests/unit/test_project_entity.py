"""
Tests unitaires pour l'entité Project (Condominium)
Tests pour valider la logique métier de création de projets avec unités automatiques
"""
import unittest
import sys
import os
from datetime import datetime

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.domain.entities.project import Project
from src.domain.entities.unit import Unit, UnitType, UnitStatus


class TestProjectEntity(unittest.TestCase):
    """Tests unitaires pour la classe Project"""
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.valid_project_data = {
            'name': 'Résidence du Parc',
            'address': '123 Rue de la Paix, Montréal, QC H1A 1A1',
            'building_area': 5000.0,
            'construction_year': 2020,
            'unit_count': 15,
            'constructor': 'Construction ABC Inc.'
        }
    
    def test_creation_project_valide(self):
        """Création d'un projet avec données valides"""
        # Arrange & Act
        project = Project(**self.valid_project_data)
        
        # Assert
        self.assertEqual(project.name, 'Résidence du Parc')
        self.assertEqual(project.address, '123 Rue de la Paix, Montréal, QC H1A 1A1')
        self.assertEqual(project.building_area, 5000.0)
        self.assertEqual(project.construction_year, 2020)
        self.assertEqual(project.unit_count, 15)
        self.assertEqual(project.constructor, 'Construction ABC Inc.')
        self.assertIsNotNone(project.creation_date)
        self.assertEqual(len(project.units), 0)  # Unités créées séparément
    
    def test_nom_projet_obligatoire(self):
        """Le nom du projet est obligatoire"""
        # Arrange
        invalid_data = self.valid_project_data.copy()
        invalid_data['name'] = ''
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            Project(**invalid_data)
        self.assertIn("nom du projet", str(context.exception))
    
    def test_adresse_obligatoire(self):
        """L'adresse est obligatoire"""
        # Arrange
        invalid_data = self.valid_project_data.copy()
        invalid_data['address'] = ''
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            Project(**invalid_data)
        self.assertIn("adresse", str(context.exception))
    
    def test_superficie_positive(self):
        """La superficie totale doit être positive"""
        # Arrange
        invalid_data = self.valid_project_data.copy()
        invalid_data['building_area'] = -100.0
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            Project(**invalid_data)
        self.assertIn("superficie", str(context.exception))
    
    def test_annee_construction_valide(self):
        """L'année de construction doit être réaliste"""
        # Arrange
        invalid_data = self.valid_project_data.copy()
        invalid_data['construction_year'] = 1800  # Trop ancienne
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            Project(**invalid_data)
        self.assertIn("année", str(context.exception))
    
    def test_nombre_unites_positif(self):
        """Le nombre d'unités doit être positif"""
        # Arrange
        invalid_data = self.valid_project_data.copy()
        invalid_data['unit_count'] = 0
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            Project(**invalid_data)
        self.assertIn("nombre d'unités", str(context.exception))
    
    def test_constructeur_obligatoire(self):
        """Le constructeur est obligatoire"""
        # Arrange
        invalid_data = self.valid_project_data.copy()
        invalid_data['constructor'] = ''
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            Project(**invalid_data)
        self.assertIn("constructeur", str(context.exception))
    
    def test_creation_unites_automatiques(self):
        """Test de création automatique des unités"""
        # Arrange
        project = Project(**self.valid_project_data)
        expected_unit_count = 15
        
        # Act
        units = project.generate_units()
        
        # Assert
        self.assertEqual(len(units), expected_unit_count)
        self.assertEqual(len(project.units), expected_unit_count)
        
        # Vérifier les numéros d'unités générés
        unit_numbers = [unit.unit_number for unit in units]
        # Le format attendu est A-XXX (section A, numéros séquentiels)
        # 15 unités réparties sur 4 étages = A-101, A-102, A-103, A-104, A-201, A-202, etc.
        expected_numbers = ["A-101", "A-102", "A-103", "A-104", 
                           "A-201", "A-202", "A-203", "A-204",
                           "A-301", "A-302", "A-303", "A-304",
                           "A-401", "A-402", "A-403"]
        self.assertEqual(unit_numbers, expected_numbers)
    
    def test_creation_unites_avec_superficie_automatique(self):
        """Test de calcul automatique de la superficie par unité"""
        # Arrange
        project = Project(**self.valid_project_data)
        
        # Act
        units = project.generate_units()
        
        # Assert
        # Superficie totale divisée par nombre d'unités (avec variation)
        expected_avg_area = project.building_area / project.unit_count
        for unit in units:
            self.assertGreater(unit.area, 0)
            # La superficie doit être dans une plage raisonnable (±40% de la moyenne)
            self.assertGreater(unit.area, expected_avg_area * 0.6)
            self.assertLess(unit.area, expected_avg_area * 1.4)
    
    def test_serialization_projet(self):
        """Test de sérialisation/désérialisation du projet"""
        # Arrange
        project = Project(**self.valid_project_data)
        project.generate_units()
        
        # Act
        project_dict = project.to_dict()
        restored_project = Project.from_dict(project_dict)
        
        # Assert
        self.assertEqual(restored_project.name, project.name)
        self.assertEqual(restored_project.address, project.address)
        self.assertEqual(restored_project.unit_count, project.unit_count)
        self.assertEqual(len(restored_project.units), len(project.units))
    
    def test_ajout_unites_apres_creation(self):
        """Test d'ajout d'unités supplémentaires après création du projet"""
        # Arrange
        project = Project(**self.valid_project_data)
        project.generate_units()
        initial_count = len(project.units)
        
        # Act
        additional_units = 5
        new_units = project.add_units(additional_units)
        
        # Assert
        self.assertEqual(len(new_units), additional_units)
        self.assertEqual(len(project.units), initial_count + additional_units)
        self.assertEqual(project.unit_count, initial_count + additional_units)
    
    def test_calcul_superficie_moyenne(self):
        """Test du calcul de la superficie moyenne par unité"""
        # Arrange
        project = Project(**self.valid_project_data)
        project.generate_units()
        
        # Act
        average_area = project.average_unit_area()
        
        # Assert
        expected_average = project.building_area / project.unit_count
        self.assertAlmostEqual(average_area, expected_average, delta=50.0)  # Tolérance de 50 sq ft


if __name__ == '__main__':
    unittest.main()
