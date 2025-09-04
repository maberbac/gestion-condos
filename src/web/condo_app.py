"""
Application web Flask pour la gestion des unités avec authentification.

CONCEPTS TECHNIQUES INTÃ‰GRÃ‰S :
1. Lecture de fichiers : Configuration JSON et données utilisateur  
2. Programmation fonctionnelle : Décorateurs et fonctions lambda pour l'authentification
3. Gestion d'erreurs : Try/catch avec exceptions personnalisées
4. Programmation asynchrone : Intégration avec le service d'authentification async

Architecture :
- Interface web Flask avec sessions utilisateur
- Authentification basée sur les rÃ´les (ADMIN/RESIDENT/GUEST)  
- Intégration avec les services de domaine existants
- Templates HTML pour l'interface utilisateur
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import asyncio
import functools
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import json

# Imports du domaine
from src.domain.entities.user import User, UserRole, UserAuthenticationError, UserValidationError
from src.domain.entities.unit import Unit, UnitType, UnitStatus
from src.domain.entities.project import Project, ProjectStatus
from src.domain.services.authentication_service import AuthenticationService

# Classe pour la compatibilité entre le backend et les templates
class UnitData:
    """Classe de données unifiée pour les templates."""
    def __init__(self, unit=None, project_name='', from_dict=None):
        if from_dict:
            # Création depuis un dictionnaire (compatibilité ancienne API)
            self.id = from_dict.get('id', '')  # Ajouter l'ID
            self.unit_number = from_dict.get('unit_number', '')
            self.owner_name = from_dict.get('owner_name', '')
            self.square_feet = from_dict.get('square_feet', 0)
            self.condo_type = from_dict.get('condo_type', 'residential')
            self.status = from_dict.get('status', 'available')
            self.monthly_fees = from_dict.get('monthly_fees', 0)
            self.building_name = from_dict.get('building_name', project_name)
            self.project_id = from_dict.get('project_id', '')  # Ajouter project_id
        elif unit:
            # Création depuis un objet Unit (nouvelle API)
            self.id = unit.id  # Ajouter l'ID depuis Unit
            self.unit_number = unit.unit_number
            self.owner_name = unit.owner_name
            self.square_feet = unit.area
            # Convertir les enums en strings pour compatibilité template
            self.condo_type = unit.unit_type.value if hasattr(unit.unit_type, 'value') else str(unit.unit_type)
            self.status = unit.status.value if hasattr(unit.status, 'value') else str(unit.status)
            
            # CORRECTION: Utiliser les frais stockés au lieu des frais calculés
            if unit.calculated_monthly_fees is not None:
                # Utiliser la valeur stockée en base (peut être string ou float)
                try:
                    self.monthly_fees = float(unit.calculated_monthly_fees)
                except (ValueError, TypeError):
                    # Si conversion échoue, utiliser le calcul comme fallback
                    self.monthly_fees = float(unit.calculate_monthly_fees())
            else:
                # Si pas de valeur stockée, utiliser le calcul
                self.monthly_fees = float(unit.calculate_monthly_fees())
            
            self.building_name = project_name
            self.project_id = unit.project_id  # Ajouter project_id depuis Unit
        else:
            # Initialisation vide
            self.id = ''  # Ajouter l'ID vide
            self.unit_number = ''
            self.owner_name = ''
            self.square_feet = 0
            self.condo_type = 'residential'
            self.status = 'available'
            self.monthly_fees = 0
            self.building_name = project_name
            self.project_id = ''  # Ajouter project_id vide
from src.adapters.user_repository_sqlite import UserRepositorySQLite
from src.adapters.sqlite_adapter import SQLiteAdapter
from src.infrastructure.config_manager import ConfigurationManager
from src.infrastructure.logger_manager import get_logger
from src.application.services.project_service import ProjectService

# Configuration de l'application
app = Flask(__name__, 
           static_folder='static',
           static_url_path='/static')

# Configuration globale
try:
    config_manager = ConfigurationManager()
    app_config = config_manager.get_app_config()
    app.secret_key = app_config.secret_key
except Exception as e:
    app.secret_key = 'fallback-dev-key'
    logging.error(f"Erreur chargement configuration: {e}")

# Services globaux - initialisation différée
auth_service = None
repository = None
user_repository = None
condo_service = None
project_service = None
user_service = None
feature_flag_service = None
logger = get_logger(__name__)

# Fonction helper pour les templates
def is_feature_enabled(flag_name: str) -> bool:
    """Vérifie si un feature flag est activé pour utilisation dans les templates."""
    global feature_flag_service
    try:
        if feature_flag_service is None:
            ensure_services_initialized()
        
        if feature_flag_service is None:
            return True  # Par défaut, autoriser si service non disponible
            
        return feature_flag_service.is_feature_enabled(flag_name)
    except Exception as e:
        logger.error(f"Erreur vérification feature flag '{flag_name}' dans template: {e}")
        return True  # Par défaut, autoriser en cas d'erreur

# Rendre la fonction disponible dans tous les templates
app.jinja_env.globals['is_feature_enabled'] = is_feature_enabled

# Service pour gérer les unités comme des condos dans l'interface
class SQLiteCondoService:
    def __init__(self, project_service=None):
        if project_service:
            self.project_service = project_service
        else:
            from src.application.services.project_service import ProjectService
            self.project_service = ProjectService()
    
    def get_all_condos(self, user_role='guest'):
        """récupÃ¨re tous les condos depuis SQLite."""
        try:
            # récupérer tous les projets
            projects_result = self.project_service.get_all_projects()
            if not projects_result['success']:
                logger.error(f"Erreur récupération projets: {projects_result['error']}")
                return []
            
            condos = []
            for project in projects_result['projects']:
                if project.units:
                    for idx, unit in enumerate(project.units):
                        # Utiliser l'ID de la base de données si disponible
                        unit_id = unit.id if unit.id is not None else f"temp_{idx}"
                        
                        # Formater pour l'affichage
                        condo = {
                            'id': unit_id,  # Utiliser le vrai ID de la base de données
                            'unit_number': unit.unit_number,
                            'owner_name': unit.owner_name,
                            'square_feet': unit.area,
                            'unit_type': {'name': unit.unit_type.value.upper()},
                            'status': unit.status.value.upper(),
                            'monthly_fees': float(unit.calculated_monthly_fees) if unit.calculated_monthly_fees else 0.0,
                            'is_available': unit.status == UnitStatus.AVAILABLE,
                            'type_icon': unit.type_icon,
                            'status_icon': unit.status_icon
                        }
                        condos.append(condo)
            
            logger.info(f"récupération de {len(condos)} condos depuis SQLite pour rÃ´le {user_role}")
            return condos
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des condos SQLite: {e}")
            return []
    
    def create_condo(self, condo_data):
        """Crée un nouveau condo (unité)."""
        try:
            from src.domain.entities.unit import Unit, UnitType, UnitStatus
            from src.domain.entities.project import Project, ProjectStatus
            
            # Trouver ou créer un projet pour cette unité
            projects_result = self.project_service.get_all_projects()
            project_id = None
            
            if projects_result['success'] and projects_result['projects']:
                # Utiliser le premier projet existant
                project = projects_result['projects'][0]
                project_id = project.project_id
            else:
                # Créer un nouveau projet d'abord
                project = Project(
                    name="Résidence par défaut",
                    address="Adresse par défaut",
                    building_area=1000.0,
                    construction_year=2023,
                    unit_count=1,
                    constructor="Default Constructor",
                    status=ProjectStatus.ACTIVE
                )
                save_result = self.project_service.create_project(project)
                if not save_result['success']:
                    logger.error(f"Erreur sauvegarde nouveau projet: {save_result['error']}")
                    return False
                project_id = project.project_id
            
            # Créer l'unité avec tous les paramètres requis
            unit_type = UnitType(condo_data.get('condo_type', 'residential'))
            status = UnitStatus(condo_data.get('status', 'available'))
            
            unit = Unit(
                unit_number=condo_data['unit_number'],
                project_id=project_id,
                area=float(condo_data['square_feet']),
                unit_type=unit_type,
                status=status,
                owner_name=condo_data.get('owner_name', ''),
                estimated_price=float(condo_data.get('estimated_price', 0)) if condo_data.get('estimated_price') else None
            )
            
            # Récupérer le projet cible et ajouter l'unité
            target_project_result = self.project_service.get_project_by_id(project_id)
            if not target_project_result['success']:
                logger.error(f"Impossible de récupérer le projet cible: {target_project_result['error']}")
                return False
            
            target_project = target_project_result['project']
            target_project.units.append(unit)
            
            # Sauvegarder le projet avec la nouvelle unité
            save_result = self.project_service.update_project(target_project)
            if not save_result['success']:
                logger.error(f"Erreur sauvegarde unité: {save_result['error']}")
                return False
            
            logger.info(f"Condo créé avec succès: {condo_data['unit_number']}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur création condo: {e}")
            return False
    
    def get_condo_by_unit_number(self, unit_number):
        """Récupère un condo par son numéro d'unité."""
        try:
            condos = self.get_all_condos()
            for condo in condos:
                if condo['unit_number'] == unit_number:
                    return UnitData(from_dict=condo)
            return None
        except Exception as e:
            logger.error(f"Erreur récupération condo {unit_number}: {e}")
            return None
    
    def get_condo_by_id(self, unit_id):
        """Récupère un condo par son ID unique (conforme aux nouvelles instructions API)."""
        try:
            condos = self.get_all_condos()
            for condo in condos:
                if condo['id'] == unit_id:
                    return UnitData(from_dict=condo)
            return None
        except Exception as e:
            logger.error(f"Erreur récupération condo par ID {unit_id}: {e}")
            return None
    
    def get_condo_by_identifier(self, identifier):
        """
        Récupère un condo par identifiant (ID ou unit_number).
        Méthode transitoire pour gérer la migration vers les ID.
        """
        try:
            # Vérifier si l'identifiant est un ID de base de données (entier)
            try:
                unit_db_id = int(identifier)
                # C'est un ID de base de données, utiliser la recherche directe
                result = self.project_service.get_unit_by_db_id(unit_db_id)
                if result['success']:
                    unit = result['unit']
                    project = result['project']
                    
                    # Créer un objet compatible avec le template
                    return UnitData(unit, project.name)
                    
            except ValueError:
                # Ce n'est pas un entier, continuer avec les méthodes normales
                pass
            
            # D'abord essayer par ID (nouvelle méthode recommandée)
            condo = self.get_condo_by_id(identifier)
            if condo:
                return condo
            
            # Fallback sur unit_number pour compatibilité
            return self.get_condo_by_unit_number(identifier)
        except Exception as e:
            logger.error(f"Erreur récupération condo par identifiant {identifier}: {e}")
            return None
    
    def update_condo(self, identifier, condo_data):
        """Met à jour un condo par son ID ou unit_number."""
        try:
            # D'abord, essayer de trouver l'unité par ID (méthode préférée)
            if identifier.isdigit():
                unit_id = int(identifier)
                # Utiliser la nouvelle méthode pour mettre à jour directement par ID
                result = self.project_service.update_unit_by_id(unit_id, condo_data)
                if result['success']:
                    logger.info(f"Unité ID {unit_id} mise à jour avec succès")
                    return True
                else:
                    logger.error(f"Échec mise à jour unité ID {unit_id}: {result['error']}")
                    return False
            
            # Fallback: recherche par unit_number (moins efficace)
            else:
                # Récupérer tous les projets
                projects_result = self.project_service.get_all_projects()
                if not projects_result['success']:
                    logger.error(f"Erreur récupération projets: {projects_result['error']}")
                    return False
                
                # Trouver le projet et l'unité correspondante
                unit_found = False
                for project in projects_result['projects']:
                    for unit in project.units:
                        if unit.unit_number == identifier:
                            # Utiliser la nouvelle méthode avec l'ID de l'unité trouvée
                            result = self.project_service.update_unit_by_id(unit.id, condo_data)
                            if result['success']:
                                logger.info(f"Unité {identifier} (ID {unit.id}) mise à jour avec succès")
                                return True
                            else:
                                logger.error(f"Échec mise à jour unité {identifier}: {result['error']}")
                                return False
                
                if not unit_found:
                    logger.error(f"Unité {identifier} introuvable")
                    return False
            
        except Exception as e:
            logger.error(f"Erreur lors de la modification du condo {identifier}: {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la modification du condo {identifier}: {e}")
            return False
    
    def get_statistics(self):
        """Génère les statistiques des condos."""
        try:
            condos = self.get_all_condos()
            stats = {
                'total_condos': len(condos),
                'occupied_condos': len([c for c in condos if not c['is_available']]),
                'available_condos': len([c for c in condos if c['is_available']]),
                'residential_condos': len([c for c in condos if c['unit_type']['name'] == 'RESIDENTIAL']),
                'commercial_condos': len([c for c in condos if c['unit_type']['name'] == 'COMMERCIAL']),
                'parking_condos': len([c for c in condos if c['unit_type']['name'] == 'PARKING']),
                'storage_condos': len([c for c in condos if c['unit_type']['name'] == 'STORAGE']),
                'total_revenue': sum(c['monthly_fees'] for c in condos),
                'average_fees': sum(c['monthly_fees'] for c in condos) / len(condos) if condos else 0
            }
            logger.debug(f"Statistiques générées: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Erreur génération statistiques: {e}")
            return {
                'total_condos': 0,
                'occupied_condos': 0,
                'available_condos': 0,
                'residential_condos': 0,
                'commercial_condos': 0,
                'parking_condos': 0,
                'storage_condos': 0,
                'total_revenue': 0,
                'average_fees': 0
            }

def calculate_relative_time(dt):
    """Calcule le temps relatif par rapport Ã  maintenant."""
    if not dt:
        return "Jamais"
    
    if isinstance(dt, str):
        try:
            # Essayer de parser différents formats de date
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S.%f']:
                try:
                    dt = datetime.strptime(dt, fmt)
                    break
                except ValueError:
                    continue
            else:
                return dt  # Retourner la chaÃ®ne originale si parsing échoue
        except:
            return dt
    
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"Il y a {years} an{'s' if years > 1 else ''}"
    elif diff.days > 30:
        months = diff.days // 30
        return f"Il y a {months} mois"
    elif diff.days > 0:
        return f"Il y a {diff.days} jour{'s' if diff.days > 1 else ''}"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"Il y a {hours}h"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"Il y a {minutes}min"
    else:
        return "Ã€ l'instant"

def init_services():
    """Initialise les services de domaine avec gestion d'erreurs."""
    global auth_service, repository, user_repository, condo_service, project_service, user_service, feature_flag_service
    try:
        repository = SQLiteAdapter('data/condos.db')
        user_repository = UserRepositorySQLite()
        auth_service = AuthenticationService(user_repository)
        
        # Utiliser le ProjectService qui gère les unités via SQLite
        from src.application.services.project_service import ProjectService
        project_service = ProjectService()
        
        # Utiliser notre service SQLiteCondoService avec le projet service partagé
        condo_service = SQLiteCondoService(project_service)
        
        # Initialiser le service utilisateur
        from src.application.services.user_service import UserService
        user_service = UserService()
        
        # Initialiser le service feature flags
        from src.adapters.feature_flag_repository_sqlite import FeatureFlagRepositorySQLite
        from src.application.services.feature_flag_service import FeatureFlagService
        feature_flag_repository = FeatureFlagRepositorySQLite()
        feature_flag_service = FeatureFlagService(feature_flag_repository)
        
        logger.info("Services initialisés avec succès (avec SQLite, authentification BD et feature flags)")
    except Exception as e:
        logger.error(f"Erreur initialisation services: {e}")
        raise

def ensure_services_initialized():
    """S'assure que les services sont initialisés, notamment pour les tests."""
    global condo_service, user_service, project_service, feature_flag_service
    if condo_service is None:
        try:
            init_services()
        except Exception as e:
            logger.warning(f"Échec d'initialisation complète des services, utilisation du service de base: {e}")
            # En cas d'échec, créer les services de base
            if project_service is None:
                from src.application.services.project_service import ProjectService
                project_service = ProjectService()
            
            # Utiliser notre wrapper SQLite avec le service projet partagé
            condo_service = SQLiteCondoService(project_service)
            
            # Initialiser user_service même en cas d'échec
            from src.application.services.user_service import UserService
            user_service = UserService()
            
            # Initialiser feature_flag_service même en cas d'échec
            if feature_flag_service is None:
                try:
                    from src.adapters.feature_flag_repository_sqlite import FeatureFlagRepositorySQLite
                    from src.application.services.feature_flag_service import FeatureFlagService
                    feature_flag_repository = FeatureFlagRepositorySQLite()
                    feature_flag_service = FeatureFlagService(feature_flag_repository)
                except Exception as fe:
                    logger.error(f"Impossible d'initialiser le service feature flags: {fe}")
                    feature_flag_service = None

def require_feature_flag(flag_name: str):
    """Décorateur pour vérifier qu'un feature flag est activé."""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            global feature_flag_service
            ensure_services_initialized()
            
            try:
                # Si le service n'est pas disponible, permettre l'accès par défaut
                if feature_flag_service is None:
                    logger.warning(f"Service feature flags non disponible, accès autorisé par défaut pour {f.__name__}")
                    return f(*args, **kwargs)
                
                # Vérifier si le feature flag est activé
                if not feature_flag_service.is_feature_enabled(flag_name):
                    logger.info(f"Accès refusé à {f.__name__}: feature flag '{flag_name}' désactivé")
                    
                    # Retourner erreur appropriée selon le type de requête
                    if request.path.startswith('/api/'):
                        return jsonify({
                            'success': False,
                            'error': f'Fonctionnalité désactivée: {flag_name}',
                            'feature_disabled': True
                        }), 503  # Service Unavailable
                    
                    # Pour les pages web, afficher la page feature_disabled.html
                    try:
                        return render_template('errors/feature_disabled.html', 
                                             feature_name=flag_name,
                                             feature_display_name=flag_name.replace('_', ' ').title()), 503
                    except Exception as template_error:
                        logger.error(f"Erreur rendu template feature_disabled: {template_error}")
                        # Fallback vers HTML simple si problème de template
                        return f"""
                        <!DOCTYPE html>
                        <html><head><title>Fonctionnalité désactivée</title></head>
                        <body style="text-align:center;padding:50px;">
                        <h1>Fonctionnalité désactivée</h1>
                        <p>Le module {flag_name} est actuellement désactivé.</p>
                        <a href="/">Retour à l'accueil</a>
                        </body></html>
                        """, 503
                
                logger.debug(f"Accès autorisé à {f.__name__}: feature flag '{flag_name}' activé")
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Erreur lors de la vérification du feature flag '{flag_name}': {e}")
                # En cas d'erreur, bloquer l'accès par sécurité
                if request.path.startswith('/api/'):
                    return jsonify({
                        'success': False,
                        'error': 'Erreur de vérification des fonctionnalités',
                        'feature_disabled': True
                    }), 503
                
                error_html = """
                <!DOCTYPE html>
                <html lang="fr">
                <head>
                    <meta charset="UTF-8">
                    <title>Erreur système</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .error { background: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px; max-width: 500px; margin: 0 auto; }
                    </style>
                </head>
                <body>
                    <div class="error">
                        <h1>Erreur système</h1>
                        <p>Impossible de vérifier l'état de la fonctionnalité.</p>
                        <a href="/">Retour à l'accueil</a>
                    </div>
                </body>
                </html>
                """
                return error_html, 503
                
        return decorated_function
    return decorator

def require_admin(f):
    """Décorateur pour vérifier que l'utilisateur est un administrateur."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        logger.debug(f"Vérification admin pour {f.__name__}")
        
        # D'abord vérifier si l'utilisateur est connecté
        user_name = session.get('user_name') or session.get('user_id') or session.get('username')
        logged_in = session.get('logged_in', False)
        
        logger.debug(f"Session info: user_name={user_name}, logged_in={logged_in}")
        
        # Si pas connecté, rediriger vers login ou retourner erreur JSON
        if not (logged_in or user_name):
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': 'Authentification requise'
                }), 401
            return redirect(url_for('login'))
        
        # Ensuite vérifier le rôle admin
        user_role_value = session.get('user_role') or session.get('role')
        logger.debug(f"Role utilisateur: {user_role_value}")
        
        if user_role_value == 'admin' or user_role_value == UserRole.ADMIN.value:
            logger.debug(f"Accès autorisé pour {f.__name__}")
            return f(*args, **kwargs)
        
        # Retourner erreur appropriée selon le type de requête
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Droits administrateur requis'
            }), 403
        
        return render_template('errors/access_denied.html'), 403
    return decorated_function

def require_login(f):
    """Décorateur pour vérifier que l'utilisateur est connecté."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Support pour les différents formats de session (tests vs app)
        user_name = session.get('user_name') or session.get('user_id') or session.get('username')
        logged_in = session.get('logged_in', False)
        
        # En mode test, Ãªtre plus permissif avec les sessions
        if app.config.get('TESTING', False):
            if logged_in or user_name or session.get('username') or session.get('user_role'):
                return f(*args, **kwargs)
        
        if not user_name and not logged_in:
            # Redirection sans flash pour éviter les redirections 302 en cascade
            return redirect(url_for('login', next=request.url), code=302)
        return f(*args, **kwargs)
    return decorated_function

# Routes de l'application

@app.route('/')
def index():
    """Page d'accueil avec informations générales."""
    user_connected = 'user_name' in session
    user_role = session.get('user_role', '')
    return render_template('index.html', user_connected=user_connected, user_role=user_role)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Route de connexion avec authentification basée sur la base de données."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            return render_template('login_error.html', error_message='Veuillez saisir vos identifiants')
        
        try:
            # Initialiser les services si nécessaire
            if auth_service is None:
                init_services()
            
            # Authentification via le service avec base de données
            async def authenticate_user():
                return await auth_service.authenticate(username, password)
            
            # Exécuter l'authentification asynchrone
            authenticated_user = asyncio.run(authenticate_user())
            
            if authenticated_user:
                # Authentification réussie
                session['user_id'] = authenticated_user.username
                session['user_name'] = authenticated_user.full_name
                session['user_role'] = authenticated_user.role.value
                session['condo_unit'] = authenticated_user.condo_unit
                
                # Mettre à jour la derniÃ¨re connexion
                async def update_last_login():
                    authenticated_user.last_login = datetime.now()
                    await user_repository.save_user(authenticated_user)
                
                try:
                    asyncio.run(update_last_login())
                except Exception as e:
                    logger.warning(f"Erreur mise à jour derniÃ¨re connexion pour {username}: {e}")
                
                flash(f'Connexion réussie! Bienvenue {authenticated_user.full_name}', 'success')
                logger.info(f"Connexion réussie pour {username} ({authenticated_user.role.value})")
                return redirect(url_for('dashboard'))
            else:
                # Authentification échouée
                logger.warning(f"Ã‰chec d'authentification pour {username}")
                return render_template('login_error.html', error_message='Identifiants invalides')
                
        except Exception as e:
            logger.error(f"Erreur lors de l'authentification de {username}: {e}")
            return render_template('login_error.html', 
                                 error_message='Erreur systÃ¨me. Veuillez réessayer.')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Déconnexion utilisateur."""
    session.clear()
    flash('Déconnexion réussie.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Tableau de bord personnalisé selon le rÃ´le utilisateur."""
    # récupérer le rÃ´le utilisateur depuis la session avec gestion de None
    user_role_value = session.get('user_role') or session.get('role')
    user_name = session.get('user_name') or session.get('user_id')
    
    if user_role_value is None or user_name is None:
        # Rediriger vers la page de login si pas de rÃ´le en session
        return redirect(url_for('login'))
    
    # Normaliser le rÃ´le
    if user_role_value == 'admin':
        user_role = UserRole.ADMIN
    elif user_role_value == 'resident':
        user_role = UserRole.RESIDENT
    else:
        user_role = UserRole(user_role_value)
    
    # Programmation fonctionnelle avec des filtres
    can_access_finance = lambda role: role in [UserRole.ADMIN]
    can_manage_users = lambda role: role == UserRole.ADMIN
    can_view_condos = lambda role: role in [UserRole.ADMIN, UserRole.RESIDENT]
    
    # Récupérer le nombre d'utilisateurs depuis la base de données
    total_users = 0
    total_units = 0
    total_projects = 0
    try:
        # Approche directe avec SQLite pour éviter les problèmes de configuration
        import sqlite3
        db_path = 'data/condos.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Compter les utilisateurs
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Compter les unités (condos)
        cursor.execute("SELECT COUNT(*) FROM units")
        total_units = cursor.fetchone()[0]
        
        # Compter les projets
        cursor.execute("SELECT COUNT(*) FROM projects")
        total_projects = cursor.fetchone()[0]
        
        conn.close()
        logger.info(f"Statistiques récupérées - Utilisateurs: {total_users}, Unités: {total_units}, Projets: {total_projects}")
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        total_users = 0
        total_units = 0
        total_projects = 0
    
    dashboard_data = {
        'user_name': session.get('full_name') or user_name,  # Prioriser le nom complet si disponible
        'user_role': user_role.value,
        'condo_unit': session.get('condo_unit', 'A-101'),  # Ajouter l'unité de condo
        'total_users': total_users,  # Nombre dynamique d'utilisateurs
        'total_units': total_units,  # Nombre dynamique d'unités
        'total_projects': total_projects,  # Nombre dynamique de projets
        'can_access_finance': can_access_finance(user_role),
        'can_manage_users': can_manage_users(user_role),
        'can_view_condos': can_view_condos(user_role),
        'permissions': {
            'condos': can_view_condos(user_role),
            'finance': can_access_finance(user_role),
            'users': can_manage_users(user_role)
        }
    }
    
    return render_template('dashboard.html', **dashboard_data)

@app.route('/condos')
@require_login
def condos():
    """Liste des unités avec actions de gestion."""
    try:
        ensure_services_initialized()
        user_role = session.get('user_role', 'guest')
        
        # Initialiser le project_service s'il n'existe pas
        global project_service
        if project_service is None:
            from src.application.services.project_service import ProjectService
            project_service = ProjectService()
        
        # Vérifier si on filtre par projet
        project_id = request.args.get('project_id')
        logger.info(f"Route /condos appelée avec project_id={project_id}")
        
        units_list = []
        project_name = None
        
        if project_id:
            logger.info(f"Tentative de filtrage par projet ID: {project_id}")
            # Récupérer le projet spécifique et ses unités
            project_result = project_service.get_project_by_id(project_id)
            if project_result['success']:
                project = project_result['project']
                units_list = project.units
                project_name = project.name
                logger.info(f"Affichage de {len(units_list)} unités pour le projet {project_name}")
            else:
                logger.warning(f"Projet avec ID {project_id} non trouvé")
                flash(f"Projet avec ID {project_id} non trouvé", "warning")
                units_list = []
                project_name = None
        else:
            logger.info("Aucun filtrage - affichage de toutes les unités")
            # Récupérer toutes les unités de tous les projets
            all_projects_result = project_service.get_all_projects()
            if all_projects_result['success']:
                all_projects = all_projects_result['projects']
                for project in all_projects:
                    units_list.extend(project.units)
                logger.info(f"Affichage de {len(units_list)} unités (toutes)")
            else:
                logger.warning("Erreur lors de la récupération de tous les projets")
                units_list = []
        
        # Générer des statistiques basiques
        stats = {
            'total_units': len(units_list),
            'occupied_units': len([u for u in units_list if u.status == 'OCCUPIED']),
            'available_units': len([u for u in units_list if u.status == 'AVAILABLE']),
            'maintenance_units': len([u for u in units_list if u.status == 'MAINTENANCE'])
        }
        
        return render_template('condos.html', 
                             condos=units_list,  # Garde le nom 'condos' pour compatibilité template
                             user_role=user_role,
                             stats=stats,
                             project_filter=project_name,
                             current_project_id=project_id)
        
    except Exception as e:
        logger.error(f"Erreur dans la route /condos: {e}")
        flash("Erreur lors du chargement des unités", "error")
        return render_template('condos.html', condos=[], user_role='guest', stats={}, project_filter=None)

@app.route('/condos/<unit_number>/details')
@require_login
def condo_details(unit_number):
    """Page de détails d'un condo."""
    try:
        ensure_services_initialized()
        user_role = session.get('user_role', 'guest')
        
        # récupérer le condo
        condo = condo_service.get_condo_by_unit_number(unit_number)
        
        if not condo:
            flash(f"Condo {unit_number} non trouvé", "error")
            return redirect(url_for('condos'))
        
        return render_template('condo_details.html', condo=condo, user_role=user_role)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'affichage des détails du condo {unit_number}: {e}")
        flash("Erreur lors du chargement des détails", "error")
        return redirect(url_for('condos'))

@app.route('/condos/create', methods=['GET', 'POST'])
@require_admin
def create_condo():
    """Création d'un nouveau condo."""
    if request.method == 'GET':
        return render_template('condo_form.html', action='create')
    
    try:
        ensure_services_initialized()
        # récupérer les données du formulaire
        condo_data = {
            'unit_number': request.form.get('unit_number'),
            'owner_name': request.form.get('owner_name', 'Disponible'),
            'square_feet': request.form.get('square_feet'),
            'condo_type': request.form.get('condo_type', 'residential'),
            'status': request.form.get('status', 'available'),
            'monthly_fees': request.form.get('monthly_fees')
        }
        
        # Créer le condo
        if condo_service.create_condo(condo_data):
            flash(f"Condo {condo_data['unit_number']} créé avec succès", "success")
            return redirect(url_for('condos'))
        else:
            flash("Erreur lors de la création du condo", "error")
            return render_template('condo_form.html', action='create', form_data=condo_data)
            
    except Exception as e:
        logger.error(f"Erreur lors de la création du condo: {e}")
        flash("Erreur technique lors de la création", "error")
        return render_template('condo_form.html', action='create')

@app.route('/condos/<identifier>/edit', methods=['GET', 'POST'])
@require_admin
def edit_condo(identifier):
    """Modification d'un condo existant - Supporte ID et unit_number pour transition."""
    try:
        ensure_services_initialized()
        # Utiliser la nouvelle méthode qui supporte ID et unit_number
        condo = condo_service.get_condo_by_identifier(identifier)
        
        if not condo:
            flash(f"Condo {identifier} non trouvé", "error")
            # Essayer de préserver le project_id même si le condo n'est pas trouvé
            project_id = request.args.get('project_id')
            if project_id:
                return redirect(url_for('condos', project_id=project_id))
            else:
                return redirect(url_for('condos'))
        
        if request.method == 'GET':
            return render_template('condo_form.html', action='edit', condo=condo)
        
        # Traitement POST - mise à jour
        condo_data = {
            'unit_number': request.form.get('unit_number'),              # AJOUT: Récupérer le numéro d'unité
            'owner_name': request.form.get('owner_name'),
            'square_feet': request.form.get('square_feet'),
            'unit_type': request.form.get('unit_type', 'RESIDENTIAL'),  # Corriger le nom du champ
            'status': request.form.get('status', 'available'),           # Valeur par défaut
            'monthly_fees': request.form.get('monthly_fees')
        }
        
        if condo_service.update_condo(identifier, condo_data):  # CORRECTION: Utiliser identifier au lieu de condo.unit_number
            flash(f"Condo {condo.unit_number or identifier} modifié avec succès", "success")
            # Préserver le project_id dans la redirection si disponible
            if hasattr(condo, 'project_id') and condo.project_id:
                return redirect(url_for('condos', project_id=condo.project_id))
            else:
                return redirect(url_for('condos'))
        else:
            flash("Erreur lors de la modification", "error")
            return render_template('condo_form.html', action='edit', condo=condo)
            
    except Exception as e:
        logger.error(f"Erreur lors de la modification du condo {identifier}: {e}")
        flash("Erreur technique lors de la modification", "error")
        # Essayer de préserver le project_id même en cas d'erreur
        project_id = request.args.get('project_id') or request.form.get('project_id')
        if project_id:
            return redirect(url_for('condos', project_id=project_id))
        else:
            return redirect(url_for('condos'))

@app.route('/finance')
@require_admin  
@require_feature_flag('finance_module')
def finance():
    """Page financière réservée aux admins."""
    # Données financières fictives
    financial_data = {
        'total_condos': 15,
        'monthly_revenue': 15750.00,
        'average_fee': 1050.00,
        'monthly_expenses': 12400.00,
        'available_balance': 3350.00
    }
    
    return render_template('finance.html', **financial_data)

@app.route('/users')
@require_admin
def users():
    """Gestion des utilisateurs depuis la base de données."""
    global user_service
    ensure_services_initialized()
    
    try:
        # Utiliser le service utilisateur global pour récupérer les vraies données
        users_data = user_service.get_users_for_web_display()
        
        logger.info(f"Affichage de {len(users_data)} utilisateurs depuis la base de données")
        
        return render_template('users.html', users=users_data)
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des utilisateurs: {e}")
        # En cas d'erreur, afficher une liste vide plutÃ´t que planter
        return render_template('users.html', users=[])

@app.route('/users/<username>/details')
@require_login
def user_details(username):
    """Page de détails d'un utilisateur."""
    from src.application.services.user_service import UserService
    
    try:
        # ContrÃ´le d'Accès par rÃ´le
        current_user_role = session.get('user_role')
        current_username = session.get('user_id')
        
        # Vérifier les permissions
        if current_user_role == 'admin' or current_user_role == 'ADMIN':
            # Les admins peuvent voir tous les utilisateurs
            pass
        elif current_user_role == 'resident' or current_user_role == 'RESIDENT':
            # Les résidents ne peuvent voir que leurs propres détails
            if current_username != username:
                flash('Vous ne pouvez consulter que vos propres détails.', 'error')
                return redirect(url_for('users'))
        else:
            # Les invités ne peuvent pas voir de détails d'utilisateur
            flash('Accès non autorisé aux détails d\'utilisateur.', 'error')
            return redirect(url_for('dashboard'))
        
        # récupérer les détails de l'utilisateur
        global user_service
        ensure_services_initialized()
        user_details = user_service.get_user_details_by_username(username)
        
        if not user_details:
            flash(f'Utilisateur "{username}" non trouvé.', 'error')
            return redirect(url_for('users'))
        
        logger.info(f"Affichage des détails de l'utilisateur '{username}' par {current_username}")
        return render_template('user_details.html', user=user_details, current_user=current_username)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'affichage des détails de '{username}': {e}")
        flash('Erreur lors du chargement des détails utilisateur.', 'error')
        return redirect(url_for('users'))

@app.route('/users/new', methods=['GET', 'POST'])
@require_admin
def users_new():
    """Création d'un nouvel utilisateur."""
    if request.method == 'POST':
        try:
            # récupération des données du formulaire
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            full_name = request.form.get('full_name', '').strip()
            role_str = request.form.get('role', '').strip()
            condo_unit = request.form.get('condo_unit', '').strip()
            
            # Validation de base
            if not all([username, email, password, full_name, role_str]):
                logger.warning("Tentative de création d'utilisateur avec données manquantes")
                return render_template('users_new.html', 
                                     error="Tous les champs obligatoires doivent Ãªtre remplis"), 400
            
            # Conversion du rÃ´le
            try:
                from src.domain.entities.user import UserRole
                role = UserRole(role_str.lower())
            except ValueError:
                logger.warning(f"RÃ´le invalide: {role_str}")
                return render_template('users_new.html', 
                                     error="RÃ´le invalide"), 400
            
            # Utilisation du service de création
            asyncio.run(create_user_async(username, email, password, full_name, role, condo_unit))
            
            logger.info(f"Utilisateur créé avec succès: {username}")
            return render_template('success.html', 
                                 message=f"Utilisateur '{username}' créé avec succès",
                                 return_url="/users",
                                 return_text="Retour aux utilisateurs")
            
        except Exception as e:
            logger.error(f"Erreur lors de la création d'utilisateur: {e}")
            return render_template('users_new.html', 
                                 error=f"Erreur lors de la création: {str(e)}"), 400
    
    return render_template('users_new.html')

async def create_user_async(username, email, password, full_name, role, condo_unit):
    """Fonction asynchrone pour créer un utilisateur."""
    try:
        # Utiliser le repository global
        global user_repository
        
        # Initialiser les services si nécessaire
        if user_repository is None:
            init_services()
        
        from src.domain.services.user_creation_service import UserCreationService
        user_creation_service = UserCreationService(user_repository)
        
        # Créer l'utilisateur
        await user_creation_service.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role=role,
            condo_unit=condo_unit if condo_unit else None
        )
        
    except Exception as e:
        logger.error(f"Erreur dans create_user_async: {e}")
        raise

@app.route('/api/user/<username>')
@require_login
def api_user(username):
    """API pour récupérer les informations d'un utilisateur."""
    from src.application.services.user_service import UserService
    
    try:
        # ContrÃ´le d'Accès par rÃ´le
        current_user_role = session.get('user_role')
        current_username = session.get('user_id')
        
        # Vérifier les permissions
        if current_user_role == 'admin' or current_user_role == 'ADMIN':
            # Les admins peuvent voir tous les utilisateurs
            pass
        elif current_user_role == 'resident' or current_user_role == 'RESIDENT':
            # Les résidents ne peuvent voir que leurs propres détails
            if current_username != username:
                logger.warning(f"Tentative d'Accès non autorisé: {current_username} -> {username}")
                return jsonify({'success': False, 'error': 'Accès non autorisé'}), 403
        else:
            # Les invités ne peuvent pas voir de détails d'utilisateur
            logger.warning(f"Tentative d'Accès invité non autorisé: {current_username} -> {username}")
            return jsonify({'success': False, 'error': 'Accès non autorisé'}), 403
        
        # Initialiser le service utilisateur
        global user_service
        ensure_services_initialized()
        
        # récupérer les détails de l'utilisateur
        user_data = user_service.get_user_details_for_api(username)
        
        if not user_data.get('found', False):
            logger.debug(f"Utilisateur '{username}' non trouvé via API")
            return jsonify({'success': False, 'error': 'Utilisateur non trouvé'}), 404
        
        logger.info(f"Détails utilisateur '{username}' récupérés via API par {current_username}")
        # Retourner une structure cohérente avec success: true et les données utilisateur
        return jsonify({
            'success': True,
            'user': {
                'username': user_data.get('username', ''),
                'full_name': user_data.get('full_name', ''),
                'email': user_data.get('email', ''),
                'role': user_data.get('role', ''),
                'condo_unit': user_data.get('condo_unit', '') or ''
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur API utilisateur {username}: {e}")
        return jsonify({'success': False, 'error': 'Erreur systÃ¨me'}), 500

@app.route('/api/user/<username>', methods=['DELETE'])
@require_login
def api_delete_user(username):
    """API pour supprimer un utilisateur."""
    from src.application.services.user_service import UserService
    
    try:
        # ContrÃ´le d'Accès - seuls les admins peuvent supprimer
        current_user_role = session.get('user_role')
        current_username = session.get('user_id')
        
        if current_user_role not in ['admin', 'ADMIN']:
            logger.warning(f"Tentative de suppression non autorisée par {current_username} (rÃ´le: {current_user_role})")
            return jsonify({'success': False, 'error': 'Accès non autorisé - Seuls les administrateurs peuvent supprimer des utilisateurs'}), 403
        
        # Initialiser le service utilisateur
        global user_service
        ensure_services_initialized()
        
        # Vérifier l'auto-suppression
        if not user_service.can_delete_user(username, current_username):
            logger.warning(f"Tentative d'auto-suppression refusée: {current_username}")
            return jsonify({'success': False, 'error': 'Impossible de supprimer votre propre compte'}), 400
        
        # Supprimer l'utilisateur
        result = user_service.delete_user_by_username(username)
        
        if result:
            logger.info(f"Utilisateur '{username}' supprimé avec succès par {current_username}")
            return jsonify({
                'success': True, 
                'message': f"Utilisateur '{username}' supprimé avec succès"
            })
        else:
            logger.warning(f"Utilisateur '{username}' non trouvé pour suppression")
            return jsonify({'success': False, 'error': 'Utilisateur non trouvé'}), 404
        
    except Exception as e:
        logger.error(f"Erreur suppression utilisateur {username}: {e}")
        return jsonify({'success': False, 'error': 'Erreur systÃ¨me lors de la suppression'}), 500

@app.route('/api/user/<username>', methods=['PUT'])
@require_login
def api_update_user(username):
    """API pour mettre à jour un utilisateur."""
    from src.application.services.user_service import UserService
    
    try:
        # ContrÃ´le d'Accès par rÃ´le
        current_user_role = session.get('user_role')
        current_username = session.get('user_id')
        
        # Vérifier les permissions
        if current_user_role not in ['admin', 'ADMIN']:
            # Les non-admins ne peuvent modifier que leur propre profil
            if current_username != username:
                logger.warning(f"Tentative de modification non autorisée: {current_username} -> {username}")
                return jsonify({'success': False, 'error': 'Accès non autorisé'}), 403
        
        # récupérer les données du formulaire
        new_username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        role = request.form.get('role')
        password = request.form.get('password')  # Optionnel
        condo_unit = request.form.get('condo_unit')
        
        # SÉCURITÉ CRITIQUE: Empêcher un utilisateur de modifier son propre rôle
        if current_username == username and role:
            # Récupérer le rôle actuel de l'utilisateur
            try:
                user_service_temp = UserService()
                current_user_details = user_service_temp.get_user_by_username(current_username)
                if current_user_details and current_user_details.get('success', False):
                    current_role = current_user_details.get('user', {}).get('role')
                    if current_role and role != current_role:
                        logger.warning(f"SÉCURITÉ: Tentative de modification de rôle par soi-même: {current_username} (actuel: {current_role} -> demandé: {role})")
                        return jsonify({
                            'success': False, 
                            'error': 'Vous ne pouvez pas modifier votre propre rôle. Contactez un administrateur.'
                        }), 403
            except Exception as role_check_error:
                logger.error(f"Erreur lors de la vérification du rôle pour {current_username}: {role_check_error}")
                # En cas d'erreur, on refuse par sécurité
                return jsonify({
                    'success': False, 
                    'error': 'Erreur de sécurité lors de la vérification des permissions'
                }), 500
        
        # Validation basique
        if not all([new_username, email, full_name, role]):
            return jsonify({'success': False, 'error': 'Tous les champs obligatoires doivent Ãªtre remplis'}), 400
        
        # Initialiser le service utilisateur
        global user_service
        ensure_services_initialized()
        
        # Préparer les données de mise à jour
        update_data = {
            'username': new_username,
            'email': email,
            'full_name': full_name,
            'role': role,
            'condo_unit': condo_unit
        }
        
        # Ajouter le mot de passe seulement s'il est fourni
        if password and password.strip():
            if len(password) < 6:
                return jsonify({'success': False, 'error': 'Le mot de passe doit contenir au moins 6 caractÃ¨res'}), 400
            update_data['password'] = password
        
        # Mettre à jour l'utilisateur
        result = user_service.update_user_by_username(username, update_data)
        
        if result.get('success', False):
            logger.info(f"Utilisateur '{username}' mis à jour avec succès par {current_username}")
            return jsonify({
                'success': True, 
                'message': f"Utilisateur '{new_username}' mis à jour avec succès"
            })
        else:
            logger.warning(f"Erreur lors de la mise à jour de '{username}': {result.get('error', 'Erreur inconnue')}")
            return jsonify({'success': False, 'error': result.get('error', 'Erreur lors de la mise à jour')}), 400
        
    except Exception as e:
        logger.error(f"Erreur mise à jour utilisateur {username}: {e}")
        return jsonify({'success': False, 'error': 'Erreur systÃ¨me lors de la mise à jour'}), 500

@app.route('/api/profile', methods=['PUT'])
@require_login
def api_update_profile():
    """API pour mettre à jour le profil de l'utilisateur connecté."""
    from src.application.services.user_service import UserService
    
    try:
        # Récupérer l'utilisateur connecté
        current_username = session.get('user_id')
        
        if not current_username:
            return jsonify({'success': False, 'error': 'Session non valide'}), 401
        
        # Récupérer les données JSON du body
        if request.content_type == 'application/json':
            profile_data = request.get_json()
        else:
            # Fallback pour form data
            profile_data = {
                'full_name': request.form.get('full_name'),
                'email': request.form.get('email'),
                'condo_unit': request.form.get('condo_unit')
            }
        
        # Validation basique
        if not profile_data.get('full_name') or not profile_data.get('email'):
            return jsonify({'success': False, 'error': 'Le nom complet et l\'email sont obligatoires'}), 400
        
        # Validation email
        import re
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, profile_data.get('email', '')):
            return jsonify({'success': False, 'error': 'Format d\'email invalide'}), 400
        
        # Initialiser le service utilisateur
        global user_service
        ensure_services_initialized()
        
        # Préparer les données de mise à jour (sans changer le username et le rôle)
        update_data = {
            'full_name': profile_data.get('full_name'),
            'email': profile_data.get('email'),
            'condo_unit': profile_data.get('condo_unit', '')
        }
        
        # Mettre à jour le profil
        result = user_service.update_user_by_username(current_username, update_data)
        
        if result.get('success', False):
            logger.info(f"Profil mis à jour avec succès pour {current_username}")
            return jsonify({
                'success': True, 
                'message': 'Profil mis à jour avec succès'
            })
        else:
            logger.warning(f"Erreur lors de la mise à jour du profil pour '{current_username}': {result.get('error', 'Erreur inconnue')}")
            return jsonify({'success': False, 'error': result.get('error', 'Erreur lors de la mise à jour')}), 400
        
    except Exception as e:
        logger.error(f"Erreur mise à jour profil pour {session.get('user_id')}: {e}")
        return jsonify({'success': False, 'error': 'Erreur système lors de la mise à jour'}), 500

@app.route('/profile')
@require_login
def profile():
    """Page de profil utilisateur."""
    # récupérer les informations de session
    username = session.get('user_id')  # Le vrai username pour la recherche en base
    user_display_name = session.get('user_name')  # Le nom d'affichage (full_name)
    user_role_value = session.get('user_role') or session.get('role')
    
    # Initialiser les services si nécessaire
    global user_repository
    if user_repository is None:
        init_services()
    
    # récupérer les vraies données utilisateur depuis la base de données
    try:
        async def get_user_data():
            return await user_repository.get_user_by_username(username)
        
        user_data = asyncio.run(get_user_data())
        
        logger.info(f"Données utilisateur récupérées pour {username}: {user_data is not None}")
        if user_data:
            logger.info(f"User data trouvé: username={user_data.username}, last_login={user_data.last_login}")
            # Utiliser les vraies données
            full_name = user_data.full_name
            email = user_data.email
            member_since = user_data.created_at.strftime('%Y-%m-%d') if user_data.created_at else datetime.now().strftime('%Y-%m-%d')
            # Utiliser la vraie derniÃ¨re connexion ou l'heure actuelle si c'est la premiÃ¨re connexion
            if user_data.last_login:
                last_login = user_data.last_login.strftime('%Y-%m-%d %H:%M:%S')
                logger.debug(f"Vraie derniÃ¨re connexion trouvée: {last_login}")
            else:
                # Si pas de derniÃ¨re connexion enregistrée, utiliser l'heure actuelle (premiÃ¨re connexion)
                last_login = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                logger.debug(f"Pas de derniÃ¨re connexion, utilisation heure actuelle: {last_login}")
            condo_unit = user_data.condo_unit or 'Non assigné'
        else:
            # Fallback si l'utilisateur n'est pas trouvé
            logger.info(f"Utilisateur {username} non trouvé en base, utilisation fallback")
            full_name = user_display_name or f'Utilisateur {username}'
            email = f'{username}@condos.com'
            member_since = datetime.now().strftime('%Y-%m-%d')  # Date actuelle au lieu de hard-codée
            last_login = 'Jamais'
            condo_unit = session.get('condo_unit', 'A-101')
            
    except Exception as e:
        logger.error(f"Erreur récupération données utilisateur {username}: {e}")
        logger.info(f"Utilisation fallback d'erreur pour {username}")
        # Fallback en cas d'erreur
        full_name = user_display_name or f'Utilisateur {username}'
        email = f'{username}@condos.com'
        member_since = datetime.now().strftime('%Y-%m-%d')  # Date actuelle au lieu de hard-codée
        last_login = 'Jamais'
        condo_unit = session.get('condo_unit', 'A-101')
    
    # Normaliser le rÃ´le pour l'affichage
    if user_role_value == 'admin':
        role_display = 'Administrateur'
        role_description = 'Accès complet au systÃ¨me de gestion'
    elif user_role_value == 'resident':
        role_display = 'résident'
        role_description = 'Accès aux informations de condos et finances personnelles'
    else:
        role_display = 'Invité'
        role_description = 'Accès limité aux informations publiques'
    
    # Données du profil avec vraies données
    logger.debug(f"Données profil pour {username}: last_login='{last_login}', member_since='{member_since}'")
    profile_data = {
        'username': username,
        'full_name': full_name,
        'email': email,
        'role_display': role_display,
        'role_description': role_description,
        'condo_unit': condo_unit,
        'last_login': last_login,
        'last_login_relative': calculate_relative_time(last_login) if last_login != 'Jamais' else last_login,
        'member_since': member_since,
        'permissions': {
            'view_condos': user_role_value in ['admin', 'resident'],
            'manage_finance': user_role_value == 'admin',
            'manage_users': user_role_value == 'admin'
        }
    }
    
    return render_template('profile.html', **profile_data)

@app.route('/change_password', methods=['GET', 'POST'])
@require_login
def change_password():
    """Page de modification du mot de passe."""
    if request.method == 'GET':
        return render_template('change_password.html')
    
    # Traitement POST - changement de mot de passe
    try:
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validation cÃ´té serveur
        if not current_password:
            return render_template('change_password.html', 
                                 error="Le mot de passe actuel est requis")
        
        if not new_password:
            return render_template('change_password.html', 
                                 error="Le nouveau mot de passe est requis")
        
        if new_password != confirm_password:
            return render_template('change_password.html', 
                                 error="Les nouveaux mots de passe ne correspondent pas")
        
        if len(new_password) < 6:
            return render_template('change_password.html', 
                                 error="Le nouveau mot de passe doit contenir au moins 6 caractÃ¨res")
        
        # récupérer le nom d'utilisateur de la session (user_id contient le username, pas user_name qui contient le full_name)
        username = session.get('user_id') or session.get('username')
        if not username:
            flash('Session expirée. Veuillez vous reconnecter.', 'error')
            return redirect(url_for('login'))
        
        # Importer et utiliser le service de changement de mot de passe
        from src.domain.services.password_change_service import PasswordChangeService, PasswordChangeError
        
        # Utiliser le service global d'authentification - initialiser si nécessaire
        if not auth_service or not user_repository:
            logger.warning("Services non initialisés pour changement mot de passe, réinitialisation...")
            init_services()
            
        # Vérifier Ã  nouveau aprÃ¨s l'initialisation
        if not auth_service or not user_repository:
            logger.error("Impossible d'initialiser les services pour changement mot de passe")
            return render_template('change_password.html', 
                                 error="Service non disponible. réessayez plus tard.")
        
        password_service = PasswordChangeService(
            user_repository=user_repository,
            authentication_service=auth_service
        )
        
        # Exécuter le changement de mot de passe de maniÃ¨re asynchrone
        async def change_password_async():
            return await password_service.change_password(
                username, current_password, new_password
            )
        
        result = asyncio.run(change_password_async())
        
        if result:
            # Rediriger vers une page de succès
            return render_template('success.html',
                                 title="Mot de passe modifié",
                                 message="Votre mot de passe a été modifié avec succès.",
                                 return_url=url_for('profile'),
                                 return_text="Retour au profil")
        else:
            return render_template('change_password.html', 
                                 error="Ã‰chec de la modification du mot de passe")
        
    except PasswordChangeError as e:
        return render_template('change_password.html', error=str(e))
    except Exception as e:
        logger.error(f"Erreur lors du changement de mot de passe pour {username}: {e}")
        return render_template('change_password.html', 
                             error="Une erreur systÃ¨me s'est produite. réessayez plus tard.")

# === ROUTES ADMIN ===
@app.route('/admin')
@require_admin
def admin_dashboard():
    """Page d'administration principale."""
    return render_template('admin_dashboard.html', 
                         total_condos=5,
                         total_users=10,
                         monthly_revenue=15000,
                         maintenance_requests=3)

@app.route('/admin/condos')
@require_admin
def admin_condos():
    """Gestion des condos pour admin."""
    search = request.args.get('search', '')
    building = request.args.get('building', '')
    
    # Simulation de données de condos avec résidents
    condos_data = ['A-101 (Pierre Gagnon)', 'A-102', 'B-201', 'B-202', 'C-301']
    
    if search:
        condos_data = [c for c in condos_data if search in c]
    if building:
        condos_data = [c for c in condos_data if c.startswith(building)]
        # Ajouter information de bÃ¢timent
        building_info = f"BÃ¢timent {building}"
    else:
        building_info = ""
    
    # Préparation des variables pour le template
    search_value = search or ''
    building_a_selected = 'selected' if building == 'A' else ''
    building_b_selected = 'selected' if building == 'B' else ''
    building_c_selected = 'selected' if building == 'C' else ''
    
    # Statistiques
    total_condos = len(condos_data)
    occupied_condos = len([c for c in condos_data if '(' in c])
    available_condos = len([c for c in condos_data if '(' not in c])
    
    # Construction de l'en-tÃªte avec les informations de filtre
    header_info = "Liste des condos"
    if building_info:
        header_info += f" - résultats pour: {building_info}"
    if search:
        header_info += f" - Recherche: {search}"
    
    # Préparation des données pour le template
    condos_list = []
    for c in condos_data:
        unit = c.split(' ')[0]
        owner = c.split('(')[1].split(')')[0] if '(' in c else None
        condos_list.append({
            'id': unit.replace('-', ''),
            'unit_number': unit,
            'owner': owner
        })
    
    return render_template('admin_condos.html',
                         total_condos=total_condos,
                         occupied_condos=occupied_condos,
                         available_condos=available_condos,
                         header_info=header_info,
                         condos_list=condos_list)

@app.route('/admin/condos/new', methods=['GET', 'POST'])
@require_admin
def admin_condos_new():
    """Redirection vers la page moderne de création de condo."""
    return redirect(url_for('create_condo'))

@app.route('/admin/condos/<condo_id>')
@require_admin
def admin_condo_detail(condo_id):
    """Redirection vers la page moderne de détails d'un condo."""
    return redirect(url_for('condo_details', unit_number=condo_id))

@app.route('/admin/condos/<condo_id>/edit', methods=['GET', 'POST'])
@require_admin
def admin_condo_edit(condo_id):
    """Redirection vers la page moderne d'édition d'un condo."""
    return redirect(url_for('edit_condo', unit_number=condo_id))

@app.route('/admin/residents')
@require_admin
def admin_residents():
    """Gestion des résidents."""
    return render_template('admin_residents.html')

@app.route('/admin/residents/new', methods=['GET', 'POST'])
@require_admin
def admin_residents_new():
    """Création de nouveau résident."""
    if request.method == 'POST':
        return render_template('success.html',
                             message="résident créé avec succès",
                             return_url="/admin/residents",
                             return_text="Retour aux résidents")
    return render_template('resident_new.html')

@app.route('/admin/residents/<username>')
@require_admin
def admin_resident_detail(username):
    """Détail d'un résident."""
    if username == 'new_resident':
        return render_template('resident_form.html')

# === ROUTES RÃ‰SIDENTS ===
@app.route('/resident/my-condo')
@require_login
def resident_my_condo():
    """Page condo du résident connecté."""
    user_role_value = session.get('user_role') or session.get('role')
    if user_role_value not in ['resident', UserRole.RESIDENT.value]:
        return render_template('errors/access_denied.html', 
                             message="Seuls les résidents peuvent accéder Ã  cette page"), 403
    
    # Données du condo du résident
    condo_data = {
        'user_name': session.get('user_name', 'résident'),
        'condo_unit': session.get('condo_unit', 'A-101'),
        'condo_area': 85,
        'condo_type': 'Appartement',
        'monthly_fees': 425,
        'current_balance': 0  # 0 = à jour
    }
    
    return render_template('resident/my_condo.html', **condo_data)

@app.route('/resident/my-fees')
def resident_my_fees():
    """Page des frais pour les résidents."""
    user_role_value = session.get('user_role', 'GUEST')
    if user_role_value not in ['resident', UserRole.RESIDENT.value]:
        return render_template('errors/access_denied.html', 
                             message="Seuls les résidents peuvent accéder Ã  cette page"), 403
    
    # Données des frais du résident
    fees_data = {
        'user_name': session.get('user_name', 'résident'),
        'monthly_fees': 450,
        'current_balance': 0,  # Ã€ jour
        'yearly_total': 5400,  # 450 * 12
        'payment_history': [
            {
                'date': '2024-12-01',
                'description': 'Frais mensuels décembre',
                'amount': 450,
                'status': 'paid'
            },
            {
                'date': '2024-11-01', 
                'description': 'Frais mensuels novembre',
                'amount': 450,
                'status': 'paid'
            },
            {
                'date': '2024-10-01',
                'description': 'Frais mensuels octobre', 
                'amount': 450,
                'status': 'paid'
            }
        ]
    }
    
    return render_template('resident/my_fees.html', **fees_data)

# === ROUTES FINANCIÃˆRES ADMIN ===
@app.route('/admin/financial/monthly-report')
@require_admin
def admin_financial_monthly():
    """Rapport mensuel financier."""
    return render_template('admin/financial/monthly_report.html')

@app.route('/admin/financial/budget-analysis')
@require_admin
def admin_financial_budget():
    """Analyse budgétaire."""
    return render_template('admin/financial/budget_analysis.html')

@app.route('/admin/financial/special-assessments')
@require_admin
def admin_financial_special():
    """Cotisations spéciales."""
    return render_template('admin/financial/special_assessments.html')

@app.route('/admin/financial/special-assessments/new', methods=['POST'])
@require_admin
def admin_financial_special_new():
    """Nouvelle cotisation spéciale."""
    return render_template('success.html',
                         message="Cotisation créée avec succès",
                         return_url="/admin/financial/special-assessments",
                         return_text="Retour aux cotisations spéciales")

@app.route('/admin/financial/payment-status')
@require_admin
def admin_financial_payments():
    """Statut des paiements."""
    return render_template('admin/financial/payment_status.html')

@app.route('/admin/financial/payments/record', methods=['POST'])
@require_admin
def admin_financial_record_payment():
    """Enregistrer un paiement."""
    return render_template('admin/financial/payment_success.html')

@app.route('/admin/financial/delinquent-accounts')
@require_admin
def admin_financial_delinquent():
    """Comptes en souffrance."""
    return render_template('admin/financial/delinquent_accounts.html')

@app.route('/admin/financial/generate-notices', methods=['POST'])
@require_admin
def admin_financial_notices():
    """Générer des avis de paiement."""
    return render_template('admin/financial/notices_success.html')

@app.route('/admin/financial/notices/pending')
@require_admin
def admin_financial_notices_pending():
    """Avis en attente."""
    return render_template('admin/financial/notices_pending.html')

@app.route('/admin/financial/income-statement')
@require_admin
def admin_financial_income():
    """Ã‰tat des revenus."""
    return render_template('admin/financial/income_statement.html')

@app.route('/admin/financial/balance-sheet')
@require_admin
def admin_financial_balance():
    """Bilan financier."""
    return render_template('admin/financial/balance_sheet.html')

@app.route('/admin/financial/tax-calculations')
@require_admin
def admin_financial_tax():
    """Calculs fiscaux."""
    return render_template('admin/financial/tax_calculations.html')

@app.route('/admin/financial/variance-analysis')
@require_admin
def admin_financial_variance():
    """Analyse des écarts."""
    return render_template('admin/financial/variance_analysis.html')

@app.route('/admin/financial/cash-flow-projection')
@require_admin
def admin_financial_cashflow():
    """Projection de flux de trésorerie."""
    return render_template('admin/financial/cash_flow_projection.html')

# === ROUTES API SPÃ‰CIALISÃ‰ES ===
# === ROUTES GÃ‰NÃ‰RIQUES ===
@app.route('/admin/condos/bulk-action', methods=['POST'])
@require_admin
def admin_condos_bulk():
    """Actions en lot sur les condos."""
    action = request.form.get('action', 'Non spécifiée')
    selected_condos = request.form.getlist('selected_condos')
    condos_count = len(selected_condos)
    
    # Logique d'action en lot ici
    # Pour l'instant, on simule le succès
    
    return render_template('admin/bulk_operation_success.html', 
                         action=action, 
                         condos_count=condos_count)

@app.route('/admin/condos/export')
@require_admin
def admin_condos_export():
    """Export des données de condos en CSV."""
    csv_data = "unit_number,owner,building\nA-101,Pierre Gagnon,A\nA-102,Marie Dubois,A\nB-201,Jean Martin,B"
    
    response = app.response_class(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=condos_export.csv'}
    )
    return response

@app.route('/admin/export/condos')
@require_admin
def admin_export_condos():
    """Export des données de condos en CSV (route alternative)."""
    return admin_condos_export()

@app.route('/finance/expenses')
@require_admin
def finance_expenses():
    """Gestion des dépenses."""

@app.route('/finance/income')
@require_admin
def finance_income():
    """Gestion des revenus."""
    return render_template('finance_income.html')

@app.route('/projects')
@require_admin 
def projects():
    """Page de gestion des projets de condominiums."""
    try:
        # récupérer la liste des projets existants
        from src.application.services.project_service import ProjectService
        project_service = ProjectService()
        projects_summary = project_service.get_all_projects_summary()
        
        return render_template('projects.html', projects_data=projects_summary)
        
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la page projets: {e}")
        flash('Erreur lors du chargement des projets', 'error')
        return redirect(url_for('dashboard'))

# Routes pour la gestion des projets

@app.route('/projets')
@app.route('/projets/')
@require_login
def projets():
    """Affichage de la liste des projets avec statistiques."""
    try:
        from src.application.services.project_service import ProjectService
        project_service = ProjectService()
        result = project_service.get_all_projects()
        
        if result['success']:
            projects = result['projects']
            
            # Calcul des statistiques globales basées sur les vraies données
            total_units = sum(p.unit_count for p in projects)
            total_units_with_data = sum(len(p.units) for p in projects if p.units)
            
            # Calculer les unités vendues et disponibles
            occupied_units = 0
            available_units = 0
            for project in projects:
                if project.units:
                    for unit in project.units:
                        if hasattr(unit, 'is_available') and callable(getattr(unit, 'is_available')):
                            # Utiliser la méthode is_available() de l'entité Unit
                            if unit.is_available():
                                available_units += 1
                            else:
                                occupied_units += 1
                        elif hasattr(unit, 'status'):
                            # Fallback: Comparaison directe avec l'enum
                            from src.domain.entities.unit import UnitStatus
                            if unit.status == UnitStatus.AVAILABLE:
                                available_units += 1
                            else:
                                occupied_units += 1
                        elif hasattr(unit, 'owner_name'):
                            # Fallback final: Vérification par propriétaire
                            if unit.owner_name and unit.owner_name != 'Disponible':
                                occupied_units += 1
                            else:
                                available_units += 1
            
            # Statistiques pour la page
            stats = {
                'active_projects_count': len(projects),  # Tous les projets chargés sont actifs
                'completed_projects_count': 0,  # Pas de statut de projet pour l'instant
                'total_units': total_units,
                'occupied_units': occupied_units,
                'available_units': available_units,
                'construction_years': sorted(list(set(p.construction_year for p in projects))),
                'projects_with_units': sum(1 for p in projects if p.units)
            }
            
            logger.info(f"Page projets chargée: {len(projects)} projets, {total_units} unités totales")
            
            return render_template('projects.html', 
                                 projects=projects,
                                 current_year=datetime.now().year,
                                 **stats)
        else:
            flash(f"Impossible de charger les projets: {result['error']}", 'error')
            return render_template('projects.html', projects=[], 
                                 active_projects_count=0, completed_projects_count=0,
                                 total_units=0, occupied_units=0, available_units=0,
                                 construction_years=[], projects_with_units=0,
                                 current_year=datetime.now().year)
            
    except Exception as e:
        logger.error(f"Erreur lors du chargement des projets: {e}")
        flash('Erreur lors du chargement des projets', 'error')
        return render_template('projects.html', projects=[],
                             active_projects_count=0, completed_projects_count=0,
                             total_units=0, occupied_units=0, available_units=0,
                             construction_years=[], projects_with_units=0,
                             current_year=datetime.now().year)

@app.route('/projets/create', methods=['POST'])
@require_admin
def create_project():
    """Création d'un nouveau projet avec unités vierges automatiques."""
    try:
        from src.application.services.project_service import ProjectService
        
        # récupération des données du formulaire
        project_data = {
            'name': request.form.get('name'),
            'address': request.form.get('address'),
            'constructor': request.form.get('builder_name'),
            'construction_year': int(request.form.get('construction_year')),
            'building_area': float(request.form.get('building_area')),  # Utilise building_area directement
            'unit_count': int(request.form.get('unit_count')),
            'status': request.form.get('status', 'ACTIVE'),  # Ajout du statut avec valeur par défaut
        }
        
        # Validation supplémentaire cÃ´té serveur
        land_area = float(request.form.get('land_area'))
        building_area = float(request.form.get('building_area'))
        if building_area > land_area:
            flash('Erreur: La superficie du bÃ¢timent ne peut pas dépasser celle du terrain.', 'error')
            return redirect(url_for('projets'))
        
        # Création du projet avec unités automatiques
        project_service = ProjectService()
        result = project_service.create_project_with_units(project_data)
        
        if result['success']:
            project_name = project_data['name']
            unit_count = project_data['unit_count']
            flash(f"Projet '{project_name}' créé avec succès avec {unit_count} unités vierges!", 'success')
            logger.info(f"Nouveau projet créé: {project_name} avec {unit_count} unités vierges")
        else:
            flash(f"Erreur lors de la création: {result['error']}", 'error')
            
    except ValueError as e:
        flash(f"Données invalides: {str(e)}", 'error')
    except Exception as e:
        logger.error(f"Erreur lors de la création du projet: {e}")
        flash('Erreur lors de la création du projet', 'error')
    
    return redirect(url_for('projets'))

@app.route('/condominium/<project_id>')
@app.route('/condominium/<project_id>/')
@require_login
def condominium(project_id):
    """Affichage des condos d'un projet spécifique."""
    try:
        from src.application.services.project_service import ProjectService
        project_service = ProjectService()
        result = project_service.get_project_by_id(project_id)
        
        if result['success']:
            project = result['project']
            
            # récupérer les condos du projet
            condos = project.units if project.units else []
            
            # Si aucun condo, les créer automatiquement
            if not condos:
                logger.info(f"Création automatique des unités pour le projet {project.name}")
                condos = project.create_units()
                # Sauvegarder le projet avec les nouvelles unités
                project_service.update_project(project)
            
            return render_template('condos.html', 
                                 condos=condos,
                                 project=project,
                                 project_context=True)
        else:
            flash(f"Projet non trouvé: {result['error']}", 'error')
            return redirect(url_for('projets'))
            
    except Exception as e:
        logger.error(f"Erreur lors du chargement du condominium {project_id}: {e}")
        flash('Erreur lors du chargement du condominium', 'error')
        return redirect(url_for('projets'))

@app.route('/projets/update/<project_id>', methods=['POST'])
@require_admin
def update_project(project_id):
    """Mise à jour d'un projet existant."""
    try:
        from src.application.services.project_service import ProjectService
        project_service = ProjectService()
        
        # Récupérer le projet existant
        result = project_service.get_project_by_id(project_id)
        if not result['success']:
            flash(f"Projet non trouvé: {result['error']}", 'error')
            return redirect(url_for('projets'))
        
        project = result['project']
        
        # Mettre à jour uniquement les champs modifiables
        project.name = request.form.get('name', '').strip()
        project.address = request.form.get('address', '').strip()
        project.constructor = request.form.get('builder_name', '').strip()
        
        # Conversion sécurisée de l'année de construction
        try:
            project.construction_year = int(request.form.get('construction_year', project.construction_year))
        except (ValueError, TypeError):
            project.construction_year = project.construction_year  # Garder la valeur existante
        
        # Conversion sécurisée de la superficie
        try:
            land_area_form = float(request.form.get('land_area', project.land_area))
            building_area_form = float(request.form.get('building_area', project.building_area))
            
            # Validation: bâtiment <= terrain
            if building_area_form > land_area_form:
                flash('La superficie du bâtiment ne peut pas dépasser celle du terrain', 'error')
                return redirect(url_for('projets'))
            
            # Mettre à jour les deux valeurs
            project.building_area = building_area_form  # Modifie building_area directement
            project.land_area = land_area_form  # Stocke dans land_area
            
        except (ValueError, TypeError):
            # En cas d'erreur, garder la valeur existante
            pass
        
        # Gérer le statut avec une valeur par défaut sécurisée
        from src.domain.entities.project import ProjectStatus
        status_str = request.form.get('status', 'active').upper()
        try:
            project.status = ProjectStatus[status_str]
        except KeyError:
            project.status = ProjectStatus.ACTIVE  # Valeur par défaut
        
        # Note: unit_count n'est PAS modifiable (respecter les permis de construction)
        
        # Validation des champs obligatoires
        if not project.name:
            flash('Le nom du projet est requis', 'error')
            return redirect(url_for('projets'))
        
        # Sauvegarder les modifications
        save_result = project_service.update_project(project)
        if save_result['success']:
            flash(f'Projet "{project.name}" mis à jour avec succès', 'success')
            logger.info(f"Projet mis à jour avec succès: {project.name} (ID: {project.project_id})")
        else:
            flash(f'Erreur lors de la mise à jour: {save_result["error"]}', 'error')
            logger.error(f"Échec de la mise à jour du projet {project_id}: {save_result['error']}")
            
        return redirect(url_for('projets'))
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du projet {project_id}: {e}")
        flash('Erreur lors de la mise à jour du projet', 'error')
        return redirect(url_for('projets'))

@app.route('/api/projets/<project_id>')
@require_login
def project_api_get(project_id):
    """API pour récupérer les données d'un projet pour l'édition."""
    try:
        from src.application.services.project_service import ProjectService
        project_service = ProjectService()
        result = project_service.get_project_by_id(project_id)
        
        if result['success']:
            project = result['project']
            # Sérialiser le projet pour l'API avec le statut
            project_data = {
                'project_id': project.project_id,
                'name': project.name,
                'address': project.address,
                'constructor': project.constructor,
                'builder_name': project.constructor,  # Alias pour compatibilité
                'construction_year': project.construction_year,
                'land_area': project.land_area,
                'building_area': project.building_area,
                'unit_count': project.unit_count,
                'total_units': project.unit_count,  # Alias pour compatibilité
                'status': project.status.value if hasattr(project.status, 'value') else str(project.status)
            }
            
            return jsonify({
                'success': True,
                'project': project_data
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 404
            
    except Exception as e:
        logger.error(f"Erreur API lors de la récupération du projet {project_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur serveur lors de la récupération du projet'
        }), 500

@app.route('/api/projets/<project_id>/statistics')
@require_login
def project_api_statistics(project_id):
    """API pour les statistiques d'un projet."""
    try:
        from src.application.services.project_service import ProjectService
        project_service = ProjectService()
        result = project_service.get_project_by_id(project_id)
        
        if result['success']:
            project = result['project']
            stats = project.get_project_statistics()
            return jsonify({
                'success': True,
                'statistics': stats
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 404
            
    except Exception as e:
        logger.error(f"Erreur API statistiques pour {project_id}: {e}")
        return jsonify({
            'success': False,
            'error': f'Erreur systÃ¨me: {str(e)}'
        }), 500

@app.route('/projects/<project_name>/statistics')
@require_admin
def project_statistics(project_name):
    """Affichage des statistiques détaillées d'un projet."""
    try:
        from src.application.services.project_service import ProjectService
        project_service = ProjectService()
        
        # Obtenir le projet par nom en utilisant la méthode du service
        result = project_service.get_project_by_name(project_name)
        
        if not result['success']:
            flash(f"Projet '{project_name}' non trouvé", 'error')
            return redirect(url_for('projects'))
            
        project = result['project']
            
        # Utiliser la nouvelle méthode avec project_id
        result = project_service.get_project_statistics(project.project_id)
        
        if result['success']:
            return render_template('project_statistics.html', 
                                 project_name=project_name,
                                 statistics=result['statistics'])
        else:
            flash(f"Impossible de charger les statistiques: {result['error']}", 'error')
            return redirect(url_for('projects'))
            
    except Exception as e:
        logger.error(f"Erreur lors du chargement des statistiques pour {project_name}: {e}")
        flash('Erreur lors du chargement des statistiques', 'error')
        return redirect(url_for('projects'))

@app.route('/api/projects/<project_name>/update-units', methods=['POST'])
@require_admin
def update_project_units(project_name):
    """API pour mettre à jour le nombre d'unités d'un projet."""
    try:
        data = request.get_json()
        new_unit_count = int(data.get('unit_count', 0))
        
        from src.application.services.project_service import ProjectService
        project_service = ProjectService()
        
        # Obtenir le projet par nom en utilisant la méthode du service
        result = project_service.get_project_by_name(project_name)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': f'Projet "{project_name}" non trouvé'
            })
            
        project = result['project']
        # Utiliser la nouvelle méthode avec project_id
        result = project_service.update_project_units(project.project_id, new_unit_count)
        
        return jsonify(result)
        
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Le nombre d\'unités doit Ãªtre un nombre valide'
        }), 400
    except Exception as e:
        logger.error(f"Erreur API mise à jour unités pour {project_name}: {e}")
        return jsonify({
            'success': False, 
            'error': f'Erreur systÃ¨me: {str(e)}'
        }), 500

@app.route('/api/projects/<project_id>/delete', methods=['DELETE'])
@require_admin
def delete_project_by_id_api(project_id):
    """API pour supprimer un projet par son ID."""
    logger.info(f"Entrée dans delete_project_by_id_api avec project_id: {project_id}")
    try:
        logger.info(f"Début suppression projet par ID: {project_id}")
        from src.application.services.project_service import ProjectService
        project_service = ProjectService()
        
        # Supprimer directement par ID
        result = project_service.delete_project_by_id(project_id)
        logger.info(f"Résultat suppression: {result}")
        
        if result['success']:
            logger.info(f"Projet supprimé via API par ID: {project_id}")
            return jsonify(result)
        else:
            logger.error(f"Échec suppression projet ID {project_id}: {result.get('error', 'Erreur inconnue')}")
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Erreur API suppression projet par ID {project_id}: {e}")
        return jsonify({
            'success': False,
            'error': f'Erreur système: {str(e)}'
        }), 500

@app.route('/projets/update/<project_id>', methods=['POST'])
@require_admin
def update_project_route(project_id):
    """Met à jour un projet"""
    from src.infrastructure.logger_manager import get_logger
    logger = get_logger(__name__)
    
    try:
        name = request.form.get('name')
        description = request.form.get('description')
        status_str = request.form.get('status')
        
        if not name or not status_str:
            flash('Le nom et le statut sont requis', 'error')
            return redirect(url_for('projets'))
        
        # Récupérer le projet existant
        from src.application.services.project_service import ProjectService
        from src.domain.entities.project import ProjectStatus
        project_service = ProjectService()
        result = project_service.get_project_by_id(project_id)
        
        if not result['success']:
            flash('Projet non trouvé', 'error')
            return redirect(url_for('projets'))
        
        project = result['project']
        
        # Mettre à jour les propriétés
        project.name = name
        if hasattr(project, 'description'):
            project.description = description
        project.status = ProjectStatus(status_str)
        
        # Sauvegarder avec la méthode appropriée
        save_result = project_service.update_project(project)
        
        if save_result['success']:
            flash('Projet mis à jour avec succès', 'success')
        else:
            flash(f'Erreur lors de la mise à jour: {save_result["message"]}', 'error')
            
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du projet: {e}")
        flash('Erreur lors de la mise à jour du projet', 'error')
    
    return redirect(url_for('projets'))

# Routes de compatibilité /unites/ -> /condos/
@app.route('/unites')
def unites():
    """Route de compatibilité : /unites/ redirige vers /condos/"""
    return redirect(url_for('condos'))

@app.route('/unites/<unit_number>')
def unite_details_redirect(unit_number):
    """Route de compatibilité : /unites/<id> redirige vers /condos/<id>"""
    return redirect(url_for('condo_details', unit_number=unit_number))

@app.route('/unites/<unit_number>/details')
def unite_details_full_redirect(unit_number):
    """Route de compatibilité : /unites/<id>/details redirige vers /condos/<id>/details"""
    return redirect(url_for('condo_details', unit_number=unit_number))

@app.route('/unites/create', methods=['GET', 'POST'])
def create_unite():
    """Route de compatibilité : /unites/create redirige vers /condos/create"""
    if request.method == 'GET':
        return redirect(url_for('create_condo'))
    else:
        # Pour POST, traiter directement les données car les formulaires ne peuvent pas suivre les redirections POST
        return create_condo()

@app.route('/unites/<identifier>/edit', methods=['GET', 'POST'])
def edit_unite(identifier):
    """Route de compatibilité : /unites/<identifier>/edit -> /condos/<identifier>/edit"""
    if request.method == 'GET':
        return redirect(url_for('edit_condo', identifier=identifier))
    else:
        # Pour POST, traiter directement
        return edit_condo(identifier)

# Application Flask pour export
flask_app = app

if __name__ == '__main__':
    init_services()
    app.run(debug=True, host='0.0.0.0', port=5000)
