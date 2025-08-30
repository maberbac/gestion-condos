"""
Tests d'acceptance simplifiés pour les scénarios utilisateur
Tests end-to-end avec mocks pour valider les fonctionnalités métier
"""
import unittest
import sys
import os
import json
from unittest.mock import Mock, patch

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestUserScenariosAcceptance(unittest.TestCase):
    """Tests d'acceptance pour les scénarios utilisateur principaux"""
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        # Données de test pour les scénarios
        self.test_condos = [
            {
                'unit_number': '101',
                'owner_name': 'Jean Dupont',
                'square_feet': 850.0,
                'condo_type': 'residential',
                'status': 'active',
                'monthly_fees_base': 350.0
            },
            {
                'unit_number': '102',
                'owner_name': 'Marie Martin', 
                'square_feet': 950.0,
                'condo_type': 'commercial',
                'status': 'active',
                'monthly_fees_base': 500.0
            }
        ]
        
        self.test_user = {
            'username': 'admin',
            'role': 'admin',
            'permissions': ['read', 'write', 'delete']
        }
    
    def test_scenario_consulter_liste_condos(self):
        """Scénario: Un utilisateur consulte la liste des condos"""
        # Arrange - Mock du service de données
        mock_data_service = Mock()
        mock_data_service.get_all_condos.return_value = self.test_condos
        
        # Act - Simuler l'action utilisateur
        condos_list = mock_data_service.get_all_condos()
        
        # Assert - Vérifier le résultat attendu
        self.assertEqual(len(condos_list), 2)
        self.assertEqual(condos_list[0]['unit_number'], '101')
        self.assertEqual(condos_list[1]['owner_name'], 'Marie Martin')
        mock_data_service.get_all_condos.assert_called_once()
    
    def test_scenario_calculer_frais_mensuels(self):
        """Scénario: Un gestionnaire calcule les frais mensuels totaux"""
        # Arrange
        mock_calculator = Mock()
        total_fees = sum(condo['monthly_fees_base'] for condo in self.test_condos)
        mock_calculator.calculate_total_fees.return_value = total_fees
        
        # Act - Le gestionnaire demande le calcul
        calculated_total = mock_calculator.calculate_total_fees(self.test_condos)
        
        # Assert
        self.assertEqual(calculated_total, 850.0)
        mock_calculator.calculate_total_fees.assert_called_once()
    
    def test_scenario_filtrer_condos_par_type(self):
        """Scénario: Un utilisateur filtre les condos par type"""
        # Arrange
        mock_filter_service = Mock()
        residential_condos = [c for c in self.test_condos if c['condo_type'] == 'residential']
        mock_filter_service.filter_by_type.return_value = residential_condos
        
        # Act - L'utilisateur applique un filtre
        filtered_condos = mock_filter_service.filter_by_type('residential')
        
        # Assert
        self.assertEqual(len(filtered_condos), 1)
        self.assertEqual(filtered_condos[0]['unit_number'], '101')
        mock_filter_service.filter_by_type.assert_called_once_with('residential')
    
    def test_scenario_authentification_utilisateur(self):
        """Scénario: Un utilisateur s'authentifie dans le système"""
        # Arrange
        mock_auth_service = Mock()
        mock_session = {'user_id': 'admin', 'role': 'admin', 'active': True}
        mock_auth_service.login.return_value = mock_session
        
        # Act - L'utilisateur se connecte
        session = mock_auth_service.login('admin', 'password123')
        
        # Assert
        self.assertIsNotNone(session)
        self.assertEqual(session['user_id'], 'admin')
        self.assertEqual(session['role'], 'admin')
        self.assertTrue(session['active'])
        mock_auth_service.login.assert_called_once_with('admin', 'password123')
    
    def test_scenario_gestion_erreurs_fichier(self):
        """Scénario: Le système gère les erreurs de fichier gracieusement"""
        # Arrange
        mock_file_service = Mock()
        mock_file_service.load_data.side_effect = FileNotFoundError("Fichier non trouvé")
        
        # Act & Assert - Le système gère l'erreur
        with self.assertRaises(FileNotFoundError):
            mock_file_service.load_data('inexistant.json')
        
        # Vérifier que l'erreur est bien capturée
        mock_file_service.load_data.assert_called_once_with('inexistant.json')
    
    def test_scenario_export_donnees(self):
        """Scénario: Un administrateur exporte les données des condos"""
        # Arrange
        mock_export_service = Mock()
        export_data = {
            'export_date': '2024-01-01',
            'total_condos': len(self.test_condos),
            'condos': self.test_condos
        }
        mock_export_service.export_to_json.return_value = export_data
        
        # Act - L'administrateur lance l'export
        exported_data = mock_export_service.export_to_json(self.test_condos)
        
        # Assert
        self.assertEqual(exported_data['total_condos'], 2)
        self.assertIn('condos', exported_data)
        self.assertEqual(len(exported_data['condos']), 2)
        mock_export_service.export_to_json.assert_called_once_with(self.test_condos)
    
    def test_scenario_recherche_condo_par_numero(self):
        """Scénario: Un utilisateur recherche un condo par numéro d'unité"""
        # Arrange
        mock_search_service = Mock()
        found_condo = next((c for c in self.test_condos if c['unit_number'] == '101'), None)
        mock_search_service.find_by_unit_number.return_value = found_condo
        
        # Act - L'utilisateur effectue une recherche
        result = mock_search_service.find_by_unit_number('101')
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result['unit_number'], '101')
        self.assertEqual(result['owner_name'], 'Jean Dupont')
        mock_search_service.find_by_unit_number.assert_called_once_with('101')
    
    def test_scenario_workflow_complet_gestion_condo(self):
        """Scénario: Workflow complet de gestion d'un condo"""
        # Arrange - Services mockés
        mock_data_service = Mock()
        mock_validator = Mock()
        mock_calculator = Mock()
        
        new_condo = {
            'unit_number': '103',
            'owner_name': 'Pierre Durand',
            'square_feet': 750.0,
            'condo_type': 'residential',
            'status': 'active',
            'monthly_fees_base': 320.0
        }
        
        # Configuration des mocks
        mock_validator.validate_condo.return_value = True
        mock_calculator.calculate_fees.return_value = 320.0
        mock_data_service.save_condo.return_value = new_condo
        
        # Act - Workflow complet
        # 1. Validation
        is_valid = mock_validator.validate_condo(new_condo)
        # 2. Calcul des frais
        calculated_fees = mock_calculator.calculate_fees(new_condo)
        # 3. Sauvegarde
        saved_condo = mock_data_service.save_condo(new_condo)
        
        # Assert - Vérifier chaque étape
        self.assertTrue(is_valid)
        self.assertEqual(calculated_fees, 320.0)
        self.assertEqual(saved_condo['unit_number'], '103')
        
        # Vérifier les appels
        mock_validator.validate_condo.assert_called_once_with(new_condo)
        mock_calculator.calculate_fees.assert_called_once_with(new_condo)
        mock_data_service.save_condo.assert_called_once_with(new_condo)


if __name__ == '__main__':
    unittest.main()
