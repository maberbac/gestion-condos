"""
Tests d'acceptance simplifiés pour l'interface moderne et la sécurité.

Ces tests valident les éléments essentiels sans dépendances complexes :
- Présence du design moderne dans les templates
- Absence d'utilisateurs hardcodés dans le code
- Structure et cohérence des pages
"""

import unittest
import sys
import os
import re
from pathlib import Path

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.infrastructure.logger_manager import get_logger

logger = get_logger(__name__)


class TestModernDesignSystemAcceptance(unittest.TestCase):
    """Tests d'acceptance pour vérifier le système de design moderne"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        self.templates_dir = Path(__file__).parent.parent.parent / 'src' / 'web' / 'templates'
        self.app_dir = Path(__file__).parent.parent.parent / 'src' / 'web'
        
    def test_modern_gradients_in_templates(self):
        """Vérifier la présence des gradients modernes dans les templates"""
        expected_gradients = [
            'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',  # Bleu-violet principal
            'linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)',  # Vert success
        ]
        
        templates_with_gradients = []
        
        for template_file in self.templates_dir.glob('*.html'):
            if template_file.name in ['base.html', 'login.html', 'profile.html', 'dashboard.html', 'success.html']:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for gradient in expected_gradients:
                    if gradient in content:
                        templates_with_gradients.append(template_file.name)
                        break
        
        # Au moins 3 templates devraient utiliser les gradients modernes
        self.assertGreaterEqual(len(templates_with_gradients), 3,
                               f"Au moins 3 templates devraient utiliser les gradients modernes. Trouvé: {templates_with_gradients}")
        
        logger.info(f"Gradients modernes trouvés dans: {templates_with_gradients}")

    def test_responsive_design_breakpoints(self):
        """Vérifier la présence des breakpoints responsive"""
        breakpoints = ['768px', '480px']
        templates_with_responsive = []
        
        for template_file in self.templates_dir.glob('*.html'):
            if template_file.name in ['profile.html', 'dashboard.html', 'success.html', 'error.html']:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Vérifier la présence des breakpoints
                has_breakpoints = all(bp in content for bp in breakpoints)
                if has_breakpoints:
                    templates_with_responsive.append(template_file.name)
        
        self.assertGreaterEqual(len(templates_with_responsive), 2,
                               f"Au moins 2 templates devraient avoir du responsive design. Trouvé: {templates_with_responsive}")
        
        logger.info(f"Design responsive trouvé dans: {templates_with_responsive}")

    def test_modern_animations_present(self):
        """Vérifier la présence d'animations modernes"""
        animation_keywords = ['@keyframes', 'animation:', 'transform:', 'transition:']
        templates_with_animations = []
        
        for template_file in self.templates_dir.glob('*.html'):
            if template_file.name in ['success.html', 'error.html', 'login.html']:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Vérifier la présence d'au moins 2 types d'animations
                animation_count = sum(1 for keyword in animation_keywords if keyword in content)
                if animation_count >= 2:
                    templates_with_animations.append(template_file.name)
        
        self.assertGreaterEqual(len(templates_with_animations), 2,
                               f"Au moins 2 templates devraient avoir des animations. Trouvé: {templates_with_animations}")
        
        logger.info(f"Animations modernes trouvées dans: {templates_with_animations}")

    def test_border_radius_standards(self):
        """Vérifier l'utilisation des standards de border-radius"""
        standard_radiuses = ['15px', '25px', '12px']  # Standards du design system
        templates_with_standards = []
        
        for template_file in self.templates_dir.glob('*.html'):
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Vérifier la présence des border-radius standards
                if any(radius in content for radius in standard_radiuses):
                    templates_with_standards.append(template_file.name)
        
        self.assertGreaterEqual(len(templates_with_standards), 4,
                               f"Au moins 4 templates devraient utiliser les border-radius standards. Trouvé: {templates_with_standards}")
        
        logger.info(f"Standards border-radius trouvés dans: {templates_with_standards}")

    def test_box_shadow_consistency(self):
        """Vérifier l'utilisation cohérente des box-shadow"""
        shadow_patterns = [
            r'box-shadow:\s*0\s+\d+px\s+\d+px\s+rgba',  # Pattern général
            'box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1)',  # Shadow standardisée
        ]
        
        templates_with_shadows = []
        
        for template_file in self.templates_dir.glob('*.html'):
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Vérifier la présence de box-shadow
                for pattern in shadow_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        templates_with_shadows.append(template_file.name)
                        break
        
        self.assertGreaterEqual(len(templates_with_shadows), 3,
                               f"Au moins 3 templates devraient utiliser des box-shadow. Trouvé: {templates_with_shadows}")
        
        logger.info(f"Box-shadow trouvées dans: {templates_with_shadows}")


class TestSecurityHardeningAcceptance(unittest.TestCase):
    """Tests d'acceptance pour vérifier le durcissement de la sécurité"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        self.app_dir = Path(__file__).parent.parent.parent / 'src' / 'web'
        self.main_app_file = self.app_dir / 'condo_app.py'
        
    def test_no_hardcoded_users_in_main_app(self):
        """Vérifier qu'aucun utilisateur n'est hardcodé dans l'application principale"""
        with open(self.main_app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns dangereux à détecter
        dangerous_patterns = [
            r'username\s*=\s*["\']admin["\']',
            r'password\s*=\s*["\'][^"\']+["\']',
            r'users\s*=\s*\{',
            r'default_users',
            r'ADMIN_USER',
            r'DEFAULT_PASSWORD',
            r'hardcoded.*user',
            r'admin.*password'
        ]
        
        violations = []
        for pattern in dangerous_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                violations.extend(matches)
        
        self.assertEqual(len(violations), 0,
                        f"Utilisateurs potentiellement hardcodés détectés: {violations}")
        
        logger.info("Vérification réussie: aucun utilisateur hardcodé dans l'application principale")

    def test_database_migration_references(self):
        """Vérifier que la création d'utilisateurs fait référence aux migrations de base de données"""
        with open(self.main_app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Rechercher des références aux migrations ou à la base de données
        db_references = [
            'migration',
            'database',
            'create_admin_user',
            'sql',
            'INSERT INTO users'
        ]
        
        found_references = []
        for ref in db_references:
            if ref.lower() in content.lower():
                found_references.append(ref)
        
        # Au moins une référence à la base de données devrait exister
        self.assertGreaterEqual(len(found_references), 1,
                               f"Au moins une référence à la base de données attendue. Trouvé: {found_references}")
        
        logger.info(f"Références de base de données trouvées: {found_references}")

    def test_password_security_patterns(self):
        """Vérifier l'absence de mots de passe en clair dans le code"""
        with open(self.main_app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns de mots de passe en clair à éviter (avec exclusions pour les migrations)
        password_patterns = [
            r'password\s*=\s*["\'](?!.*hash)(?!.*bcrypt)[^"\']{4,}["\']',  # Password = "something" long
            r'["\']password123["\']',  # Mots de passe évidents
            r'["\']admin123["\']',  # Mots de passe évidents
            r'["\']123456["\']',  # Mots de passe numériques simples
        ]
        
        password_violations = []
        for pattern in password_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            password_violations.extend(matches)
        
        # Filtrer les faux positifs (commentaires, migrations SQL, tests)
        real_violations = []
        for v in password_violations:
            # Ignorer si c'est dans un commentaire SQL
            if not any(keyword in v.lower() for keyword in ['migration', 'sql', 'create', 'insert', 'hash']):
                real_violations.append(v)
        
        self.assertEqual(len(real_violations), 0,
                        f"Mots de passe potentiellement en clair détectés: {real_violations}")
        
        logger.info("Vérification réussie: aucun mot de passe en clair détecté")

    def test_environment_variable_usage(self):
        """Vérifier qu'aucune variable d'environnement ne contient d'utilisateurs hardcodés"""
        with open(self.main_app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Rechercher l'utilisation de variables d'environnement pour les utilisateurs
        env_patterns = [
            r'os\.environ\[.*[uU]ser',
            r'os\.environ\[.*[aA]dmin',
            r'os\.environ\[.*[pP]assword',
            r'os\.getenv\(.*[uU]ser',
            r'os\.getenv\(.*[aA]dmin',
        ]
        
        env_violations = []
        for pattern in env_patterns:
            matches = re.findall(pattern, content)
            env_violations.extend(matches)
        
        # Selon les instructions, même les variables d'environnement sont interdites
        self.assertEqual(len(env_violations), 0,
                        f"Variables d'environnement pour utilisateurs détectées: {env_violations}")
        
        logger.info("Vérification réussie: aucune variable d'environnement pour utilisateurs")

    def test_authentication_flow_security(self):
        """Vérifier que l'authentification suit un flux sécurisé"""
        with open(self.main_app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Rechercher des patterns de sécurité dans l'authentification
        security_patterns = [
            'authenticate_user',
            'password_hash',
            'bcrypt',
            'pbkdf2',
            'sha256',
            'session',
            'login_required',
            'user_id',
            'role',
            'authentication',
            'login',
            'logout'
        ]
        
        found_security = []
        for pattern in security_patterns:
            if pattern in content:
                found_security.append(pattern)
        
        # Au moins 3 éléments de sécurité devraient être présents
        self.assertGreaterEqual(len(found_security), 3,
                               f"Au moins 3 éléments de sécurité attendus dans l'authentification. Trouvé: {found_security}")
        
        logger.info(f"Éléments de sécurité trouvés: {found_security}")


class TestTemplateConsistencyAcceptance(unittest.TestCase):
    """Tests d'acceptance pour vérifier la cohérence des templates"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        self.templates_dir = Path(__file__).parent.parent.parent / 'src' / 'web' / 'templates'
        
    def test_template_inheritance_structure(self):
        """Vérifier que les templates héritent correctement de base.html"""
        templates_with_inheritance = []
        
        for template_file in self.templates_dir.glob('*.html'):
            if template_file.name != 'base.html':
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Vérifier l'héritage de base.html
                if 'extends "base.html"' in content or 'extends \'base.html\'' in content:
                    templates_with_inheritance.append(template_file.name)
        
        # Au moins 5 templates devraient hériter de base.html
        self.assertGreaterEqual(len(templates_with_inheritance), 5,
                               f"Au moins 5 templates devraient hériter de base.html. Trouvé: {templates_with_inheritance}")
        
        logger.info(f"Templates avec héritage: {templates_with_inheritance}")

    def test_modern_ui_consistency(self):
        """Vérifier la cohérence du design moderne à travers les templates"""
        modern_templates = ['profile.html', 'dashboard.html', 'success.html', 'error.html']
        consistency_elements = [
            'border-radius',
            'linear-gradient',
            'box-shadow',
            'transform',
            'transition'
        ]
        
        consistent_templates = []
        
        for template_name in modern_templates:
            template_path = self.templates_dir / template_name
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Vérifier la présence d'au moins 3 éléments de design moderne
                elements_found = sum(1 for element in consistency_elements if element in content)
                if elements_found >= 3:
                    consistent_templates.append(template_name)
        
        # Au moins 3 templates modernes devraient être cohérents
        self.assertGreaterEqual(len(consistent_templates), 3,
                               f"Au moins 3 templates devraient être cohérents avec le design moderne. Trouvé: {consistent_templates}")
        
        logger.info(f"Templates cohérents avec le design moderne: {consistent_templates}")

    def test_html_structure_validity(self):
        """Vérifier la validité de base de la structure HTML"""
        templates_with_valid_structure = []
        
        for template_file in self.templates_dir.glob('*.html'):
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Vérifications de base de la structure HTML
            has_doctype = '<!DOCTYPE html>' in content or '{% extends' in content
            has_title = '<title>' in content or '{% block title %}' in content
            has_body = '<body>' in content or '{% block content %}' in content
            
            if has_doctype and (has_title or '{% extends' in content) and (has_body or '{% extends' in content):
                templates_with_valid_structure.append(template_file.name)
        
        # Tous les templates devraient avoir une structure valide
        total_templates = len(list(self.templates_dir.glob('*.html')))
        self.assertGreaterEqual(len(templates_with_valid_structure), total_templates * 0.8,
                               f"Au moins 80% des templates devraient avoir une structure HTML valide")
        
        logger.info(f"Templates avec structure HTML valide: {len(templates_with_valid_structure)}/{total_templates}")


if __name__ == '__main__':
    unittest.main()
