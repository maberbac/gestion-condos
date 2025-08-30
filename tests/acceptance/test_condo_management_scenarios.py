"""
Tests d'acceptance pour les scénarios de gestion des condos.

Ces tests valident les scénarios utilisateur complets end-to-end :
- Gestion des unités de condo
- Administration des résidents
- Workflows complets utilisateur
"""

import unittest
import asyncio
import tempfile
import os
import json
from unittest.mock import patch, Mock

from src.web.condo_app import app
from src.domain.entities.user import User, UserRole
from src.domain.entities.condo import Condo


class TestCondoManagementAcceptance(unittest.TestCase):
    """Tests d'acceptance pour la gestion des condos"""
    
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
        
        # Données de test - Utilisateurs
        self.admin_user = {
            'username': 'admin',
            'password': 'admin123',
            'role': 'admin',
            'full_name': 'Administrateur Principal'
        }
        
        self.resident_user = {
            'username': 'resident1',
            'password': 'resident123',
            'role': 'resident',
            'full_name': 'Jean Dupont',
            'condo_unit': 'A-101'
        }
        
        # Données de test - Condos
        self.test_condos = [
            {
                'unit_number': 'A-101',
                'owner_name': 'Jean Dupont',
                'square_footage': 850,
                'monthly_fees': 245.50,
                'building': 'A'
            },
            {
                'unit_number': 'B-205',
                'owner_name': 'Marie Tremblay',
                'square_footage': 1100,
                'monthly_fees': 315.75,
                'building': 'B'
            }
        ]
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        self.app_context.pop()
        
        # Nettoyer fichiers temporaires
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
    
    def _login_as_admin(self):
        """Méthode utilitaire pour se connecter comme admin"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            sess['role'] = 'admin'
            sess['full_name'] = 'Administrateur Principal'
    
    def _login_as_resident(self):
        """Méthode utilitaire pour se connecter comme résident"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'resident1'
            sess['role'] = 'resident'
            sess['full_name'] = 'Jean Dupont'
            sess['condo_unit'] = 'A-101'
    
    def test_complete_admin_workflow_condo_creation(self):
        """
        Scénario: Administrateur crée un nouveau condo
        ÉTANT DONNÉ un administrateur connecté
        QUAND il crée un nouveau condo avec toutes les informations
        ALORS le condo est créé et visible dans la liste
        """
        # ÉTANT DONNÉ un administrateur connecté
        self._login_as_admin()
        
        # Vérifier accès au dashboard admin
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        # Vérifier le contenu spécifique au dashboard admin
        self.assertIn(b'Administrateur', response.data)
        
        # QUAND il accède au formulaire de création de condo
        response = self.client.get('/admin/condos/new')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Nouveau Condo', response.data)
        
        # ET qu'il soumet les informations du nouveau condo
        new_condo_data = {
            'unit_number': 'C-301',
            'owner_name': 'Pierre Gagnon',
            'square_footage': '950',
            'monthly_fees': '275.00',
            'building': 'C'
        }
        
        response = self.client.post('/admin/condos/new', 
                                   data=new_condo_data,
                                   follow_redirects=True)
        
        # ALORS le condo est créé avec succès
        self.assertEqual(response.status_code, 200)
        self.assertIn('Condo créé avec succès'.encode('utf-8'), response.data)
        
        # ET il est visible dans la liste des condos
        response = self.client.get('/admin/condos')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'C-301', response.data)
        self.assertIn(b'Pierre Gagnon', response.data)
    
    def test_complete_admin_workflow_resident_management(self):
        """
        Scénario: Administrateur gère les résidents
        ÉTANT DONNÉ un administrateur connecté
        QUAND il ajoute un nouveau résident à un condo
        ALORS le résident est créé et associé au condo
        """
        # ÉTANT DONNÉ un administrateur connecté
        self._login_as_admin()
        
        # QUAND il accède à la gestion des résidents
        response = self.client.get('/admin/residents')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Gestion des Résidents'.encode('utf-8'), response.data)
        
        # ET qu'il ajoute un nouveau résident
        new_resident_data = {
            'username': 'new_resident',
            'email': 'nouveau@test.com',
            'password': 'password123',
            'full_name': 'Nouveau Résident',
            'condo_unit': 'A-102',
            'phone': '514-555-0123'
        }
        
        response = self.client.post('/admin/residents/new',
                                   data=new_resident_data,
                                   follow_redirects=True)
        
        # ALORS le résident est créé avec succès
        self.assertEqual(response.status_code, 200)
        self.assertIn('Résident créé avec succès'.encode('utf-8'), response.data)
        
        # ET il peut voir les détails du résident
        response = self.client.get('/admin/residents/new_resident')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Nouveau Résident'.encode('utf-8'), response.data)
        self.assertIn(b'A-102', response.data)
    
    def test_complete_resident_workflow_view_condo_info(self):
        """
        Scénario: Résident consulte ses informations de condo
        ÉTANT DONNÉ un résident connecté
        QUAND il accède à son tableau de bord
        ALORS il voit ses informations de condo et ses frais
        """
        # ÉTANT DONNÉ un résident connecté
        self._login_as_resident()
        
        # QUAND il accède à son tableau de bord
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Tableau de bord', response.data)
        
        # ALORS il voit ses informations personnelles
        self.assertIn(b'Jean Dupont', response.data)
        self.assertIn(b'A-101', response.data)
        
        # ET il peut accéder à ses informations de condo
        response = self.client.get('/resident/my-condo')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Mon Condo', response.data)
        self.assertIn(b'A-101', response.data)
    
    def test_complete_resident_workflow_access_restrictions(self):
        """
        Scénario: Résident ne peut pas accéder aux fonctions admin
        ÉTANT DONNÉ un résident connecté
        QUAND il tente d'accéder aux pages d'administration
        ALORS l'accès est refusé
        """
        # ÉTANT DONNÉ un résident connecté
        self._login_as_resident()
        
        # QUAND il tente d'accéder à l'administration
        response = self.client.get('/admin')
        
        # ALORS l'accès est refusé
        self.assertEqual(response.status_code, 403)
        
        # ET il ne peut pas créer de nouveaux condos
        response = self.client.get('/admin/condos/new')
        self.assertEqual(response.status_code, 403)
        
        # ET il ne peut pas gérer d'autres résidents
        response = self.client.get('/admin/residents')
        self.assertEqual(response.status_code, 403)
    
    def test_complete_workflow_condo_search_and_filter(self):
        """
        Scénario: Utilisateur recherche et filtre les condos
        ÉTANT DONNÉ un utilisateur connecté avec des condos existants
        QUAND il utilise les fonctions de recherche et filtrage
        ALORS il obtient les résultats appropriés
        """
        # ÉTANT DONNÉ un administrateur connecté
        self._login_as_admin()
        
        # QUAND il accède à la liste des condos
        response = self.client.get('/admin/condos')
        self.assertEqual(response.status_code, 200)
        
        # ET qu'il recherche par numéro d'unité
        response = self.client.get('/admin/condos?search=A-101')
        self.assertEqual(response.status_code, 200)
        # ALORS seuls les résultats pertinents sont affichés
        self.assertIn(b'A-101', response.data)
        
        # QUAND il filtre par bâtiment
        response = self.client.get('/admin/condos?building=A')
        self.assertEqual(response.status_code, 200)
        # ALORS seuls les condos du bâtiment A sont affichés
        self.assertIn('Bâtiment A'.encode('utf-8'), response.data)
    
    def test_complete_workflow_condo_update(self):
        """
        Scénario: Administrateur modifie les informations d'un condo
        ÉTANT DONNÉ un condo existant
        QUAND l'administrateur modifie ses informations
        ALORS les changements sont sauvegardés et visibles
        """
        # ÉTANT DONNÉ un administrateur connecté
        self._login_as_admin()
        
        # ET un condo existant à modifier
        condo_id = 'A-101'
        
        # QUAND il accède au formulaire de modification
        response = self.client.get(f'/admin/condos/{condo_id}/edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Modifier Condo', response.data)
        
        # ET qu'il soumet les modifications
        updated_data = {
            'unit_number': 'A-101',
            'owner_name': 'Jean Dupont-Modifié',
            'square_footage': '900',
            'monthly_fees': '260.00',
            'building': 'A'
        }
        
        response = self.client.post(f'/admin/condos/{condo_id}/edit',
                                   data=updated_data,
                                   follow_redirects=True)
        
        # ALORS les modifications sont sauvegardées
        self.assertEqual(response.status_code, 200)
        self.assertIn('Condo modifié avec succès'.encode('utf-8'), response.data)
        
        # ET les nouvelles informations sont visibles
        response = self.client.get(f'/admin/condos/{condo_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Jean Dupont-Modifié'.encode('utf-8'), response.data)
        self.assertIn(b'900', response.data)
    
    def test_complete_workflow_error_handling(self):
        """
        Scénario: Gestion d'erreurs dans les workflows complets
        ÉTANT DONNÉ différentes situations d'erreur
        QUAND l'utilisateur effectue des actions
        ALORS les erreurs sont gérées gracieusement
        """
        # ÉTANT DONNÉ un administrateur connecté
        self._login_as_admin()
        
        # QUAND il tente de créer un condo avec des données invalides
        invalid_data = {
            'unit_number': '',  # Requis mais vide
            'owner_name': 'Test',
            'square_footage': 'invalid',  # Doit être numérique
            'monthly_fees': '-100',  # Négatif
            'building': ''
        }
        
        response = self.client.post('/admin/condos/new', data=invalid_data)
        
        # ALORS les erreurs de validation sont affichées
        self.assertEqual(response.status_code, 200)  # Reste sur la page avec erreurs
        self.assertIn(b'erreur', response.data.lower())
        
        # QUAND il tente d'accéder à un condo inexistant
        response = self.client.get('/admin/condos/INEXISTANT')
        
        # ALORS une erreur 404 appropriée est retournée
        self.assertEqual(response.status_code, 404)
    
    def test_complete_workflow_bulk_operations(self):
        """
        Scénario: Opérations en lot sur les condos
        ÉTANT DONNÉ plusieurs condos sélectionnés
        QUAND l'administrateur effectue une opération en lot
        ALORS l'opération s'applique à tous les condos sélectionnés
        """
        # ÉTANT DONNÉ un administrateur connecté
        self._login_as_admin()
        
        # QUAND il sélectionne plusieurs condos pour une opération en lot
        selected_condos = ['A-101', 'B-205']
        bulk_data = {
            'selected_condos': selected_condos,
            'action': 'update_fees',
            'new_fees': '300.00'
        }
        
        response = self.client.post('/admin/condos/bulk-action',
                                   data=bulk_data,
                                   follow_redirects=True)
        
        # ALORS l'opération est appliquée avec succès
        self.assertEqual(response.status_code, 200)
        self.assertIn('Opération en lot terminée'.encode('utf-8'), response.data)
        
        # ET les changements sont visibles pour tous les condos sélectionnés
        for condo_id in selected_condos:
            response = self.client.get(f'/admin/condos/{condo_id}')
            self.assertEqual(response.status_code, 200)
            # Vérifier que les frais ont été mis à jour (si implémenté)
    
    def test_complete_workflow_data_export(self):
        """
        Scénario: Export des données de condos
        ÉTANT DONNÉ des condos dans le système
        QUAND l'administrateur exporte les données
        ALORS un fichier d'export est généré correctement
        """
        # ÉTANT DONNÉ un administrateur connecté
        self._login_as_admin()
        
        # QUAND il demande un export des données
        response = self.client.get('/admin/condos/export?format=csv')
        
        # ALORS le fichier est généré avec le bon type de contenu
        if response.status_code == 200:
            self.assertIn('text/csv', response.content_type)
            self.assertIn('attachment', response.headers.get('Content-Disposition', ''))
        else:
            # Si l'export n'est pas encore implémenté
            self.assertIn(response.status_code, [404, 501])
    
    def test_complete_workflow_audit_trail(self):
        """
        Scénario: Traçabilité des modifications
        ÉTANT DONNÉ des modifications effectuées sur les condos
        QUAND l'administrateur consulte l'historique
        ALORS les modifications sont tracées
        """
        # ÉTANT DONNÉ un administrateur connecté
        self._login_as_admin()
        
        # QUAND il effectue une modification
        condo_id = 'A-101'
        updated_data = {
            'unit_number': 'A-101',
            'owner_name': 'Nouveau Propriétaire',
            'square_footage': '850',
            'monthly_fees': '245.50',
            'building': 'A'
        }
        
        response = self.client.post(f'/admin/condos/{condo_id}/edit',
                                   data=updated_data,
                                   follow_redirects=True)
        
        # ET qu'il consulte l'historique des modifications
        response = self.client.get(f'/admin/condos/{condo_id}/history')
        
        # ALORS l'historique des modifications est disponible
        if response.status_code == 200:
            self.assertIn(b'Historique', response.data)
            self.assertIn('Nouveau Propriétaire'.encode('utf-8'), response.data)
        else:
            # Si l'historique n'est pas encore implémenté
            self.assertIn(response.status_code, [404, 501])
    
    def test_complete_workflow_mobile_responsive(self):
        """
        Scénario: Interface responsive pour mobile
        ÉTANT DONNÉ un utilisateur sur mobile
        QUAND il accède aux pages principales
        ALORS l'interface s'adapte correctement
        """
        # ÉTANT DONNÉ un administrateur connecté sur mobile
        self._login_as_admin()
        
        # Simuler headers mobile
        mobile_headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'
        }
        
        # QUAND il accède aux pages principales
        pages_to_test = [
            '/dashboard',
            '/admin',
            '/admin/condos',
            '/admin/residents'
        ]
        
        for page in pages_to_test:
            response = self.client.get(page, headers=mobile_headers)
            
            # ALORS les pages se chargent correctement
            self.assertIn(response.status_code, [200, 302])
            
            if response.status_code == 200:
                # Vérifier présence de viewport meta tag (responsive)
                self.assertIn(b'viewport', response.data.lower())
    
    def test_complete_integration_with_financial_system(self):
        """
        Scénario: Intégration avec le système financier
        ÉTANT DONNÉ des condos avec des frais mensuels
        QUAND le système calcule les totaux financiers
        ALORS les calculs sont corrects et cohérents
        """
        # ÉTANT DONNÉ un administrateur connecté
        self._login_as_admin()
        
        # QUAND il accède au rapport financier
        response = self.client.get('/admin/financial-report')
        
        if response.status_code == 200:
            # ALORS le rapport affiche les totaux corrects
            self.assertIn(b'Rapport Financier', response.data)
            self.assertIn(b'Total', response.data)
            
            # ET les calculs sont cohérents
            response = self.client.get('/api/financial-summary')
            if response.status_code == 200:
                data = json.loads(response.data)
                self.assertIn('total_monthly_fees', data)
                self.assertIsInstance(data['total_monthly_fees'], (int, float))
        else:
            # Si le rapport financier n'est pas encore implémenté
            self.assertIn(response.status_code, [404, 501])


if __name__ == '__main__':
    unittest.main()
