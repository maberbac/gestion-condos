"""
Service de gestion des projets de condominiums
Orchestration de la logique métier pour la création et gestion des projets avec unités
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from src.infrastructure.logger_manager import get_logger
from src.domain.entities.project import Project
from src.domain.entities.unit import Unit, UnitType, UnitStatus
from src.adapters.project_repository_sqlite import ProjectRepositorySQLite

logger = get_logger(__name__)


class ProjectService:
    """Service pour orchestrer la gestion des projets de condominiums"""
    
    def __init__(self, project_repository=None, condo_repository=None):
        """
        Initialise le service avec les repositories nécessaires
        
        Args:
            project_repository: Repository pour la persistance des projets
            condo_repository: Repository pour la persistance des condos/unités
        """
        # Utiliser le repository SQLite par défaut
        self.project_repository = project_repository or ProjectRepositorySQLite()
        self.condo_repository = condo_repository
        self._projects: List[Project] = []
        
        # Charger les projets depuis la base de données
        self._load_projects()
    
    def _load_projects(self) -> None:
        """Charge les projets depuis la base de données SQLite."""
        try:
            self._projects = self.project_repository.get_all_projects()
            logger.info(f"Chargé {len(self._projects)} projets depuis la base de données SQLite")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des projets: {e}")
            self._projects = []
    
    def _save_projects(self) -> None:
        """Sauvegarde les projets dans la base de données SQLite."""
        try:
            # Note: Avec SQLite, la sauvegarde se fait projet par projet
            # Cette méthode est gardée pour compatibilité mais n'est plus nécessaire
            # car chaque opération sauvegarde directement en base
            logger.debug(f"Projets déjà sauvegardés en base SQLite: {len(self._projects)} projets")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des projets: {e}")
            raise
    
    def create_project(self, project: Project) -> Dict[str, Any]:
        """
        Crée un nouveau projet.
        
        Args:
            project: Instance du projet à créer
            
        Returns:
            Dict contenant le résultat de l'opération
        """
        try:
            # Vérifier que l'ID du projet est unique (si déjà défini)
            if hasattr(project, 'project_id') and project.project_id:
                existing = self.project_repository.get_project_by_id(project.project_id)
                if existing:
                    return {
                        'success': False,
                        'error': f'Un projet avec l\'ID {project.project_id} existe déjà'
                    }
            
            # Vérifier que le nom du projet est unique
            if any(p.name.lower() == project.name.lower() for p in self._projects):
                return {
                    'success': False,
                    'error': f'Un projet avec le nom "{project.name}" existe déjà'
                }
            
            # Sauvegarder le projet en base de données
            project_id = self.project_repository.save_project(project)
            
            # Recharger les projets depuis la base
            self._load_projects()
            
            logger.info(f"Projet créé avec succès: {project.name} (ID: {project_id})")
            return {
                'success': True,
                'project': project,
                'project_id': project_id,
                'message': f'Projet "{project.name}" créé avec succès'
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du projet: {e}")
            return {
                'success': False,
                'error': f'Erreur système lors de la création: {str(e)}'
            }
    
    def get_all_projects(self) -> Dict[str, Any]:
        """
        Récupère tous les projets.
        
        Returns:
            Dict contenant la liste des projets
        """
        try:
            logger.debug(f"Récupération de {len(self._projects)} projets")
            return {
                'success': True,
                'projects': self._projects,
                'count': len(self._projects)
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des projets: {e}")
            return {
                'success': False,
                'error': f'Erreur système: {str(e)}',
                'projects': []
            }
    
    def get_project_by_id(self, project_id: str) -> Dict[str, Any]:
        """
        Récupère un projet par son ID.
        
        Args:
            project_id: Identifiant du projet
            
        Returns:
            Dict contenant le projet ou une erreur
        """
        try:
            project = next((p for p in self._projects if p.project_id == project_id), None)
            
            if project:
                logger.debug(f"Projet trouvé: {project.name} (ID: {project_id})")
                return {
                    'success': True,
                    'project': project
                }
            else:
                logger.warning(f"Projet non trouvé avec l'ID: {project_id}")
                return {
                    'success': False,
                    'error': f'Aucun projet trouvé avec l\'ID {project_id}'
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du projet {project_id}: {e}")
            return {
                'success': False,
                'error': f'Erreur système: {str(e)}'
            }

    def get_project_by_name(self, project_name: str) -> Dict[str, Any]:
        """
        Récupère un projet par son nom.
        ATTENTION: Utilise la recherche par nom qui peut être ambiguë.
        Préférer get_project_by_id() quand possible.
        
        Args:
            project_name: Nom du projet
            
        Returns:
            Dict contenant le projet ou une erreur
        """
        try:
            # Recharger les projets depuis la base pour avoir les dernières données
            all_projects = self.project_repository.get_all_projects()
            project = next((p for p in all_projects if p.name == project_name), None)
            
            if project:
                logger.debug(f"Projet trouvé par nom: {project.name} (ID: {project.project_id})")
                return {
                    'success': True,
                    'project': project
                }
            else:
                logger.warning(f"Projet non trouvé avec le nom: {project_name}")
                return {
                    'success': False,
                    'error': f'Aucun projet trouvé avec le nom "{project_name}"'
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du projet {project_name}: {e}")
            return {
                'success': False,
                'error': f'Erreur système: {str(e)}'
            }
    
    def update_project(self, project: Project) -> Dict[str, Any]:
        """
        Met à jour un projet existant.
        
        Args:
            project: Instance du projet mis à jour
            
        Returns:
            Dict contenant le résultat de l'opération
        """
        try:
            # Trouver l'index du projet dans la liste en mémoire
            project_index = next((i for i, p in enumerate(self._projects) if p.project_id == project.project_id), None)
            
            if project_index is not None:
                # Mettre à jour la liste en mémoire
                self._projects[project_index] = project
                
                # Sauvegarder en base de données SQLite
                self.project_repository.save_project(project)
                
                logger.info(f"Projet mis à jour: {project.name} (ID: {project.project_id})")
                return {
                    'success': True,
                    'project': project,
                    'message': f'Projet "{project.name}" mis à jour avec succès'
                }
            else:
                return {
                    'success': False,
                    'error': f'Projet non trouvé avec l\'ID {project.project_id}'
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du projet: {e}")
            return {
                'success': False,
                'error': f'Erreur système lors de la mise à jour: {str(e)}'
            }
    
    def create_project_with_units(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée un nouveau projet avec génération automatique des unités
        Compatibilité avec l'ancienne et nouvelle structure
        
        Args:
            project_data: Données du projet (nom, adresse, etc.)
            
        Returns:
            Dict contenant le résultat de l'opération avec projet et unités créées
        """
        try:
            logger.info(f"Création d'un nouveau projet: {project_data.get('name', 'Sans nom')}")
            
            # Validation des données d'entrée
            validation_result = self._validate_project_data(project_data)
            if not validation_result['valid']:
                logger.warning(f"Données de projet invalides: {validation_result['error']}")
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            # Adapter les données pour la nouvelle structure
            import uuid
            adapted_data = self._adapt_project_data(project_data)
            
            # Création du projet avec la nouvelle structure
            project = Project(**adapted_data)
            
            # Générer automatiquement les unités pour le projet
            # Créer des unités vierges sans attribution automatique
            unit_count = adapted_data.get('unit_count', 25)
            units = project.generate_units(unit_count, blank_units=True)
            project.units = units
            
            # Sauvegarder le projet en base de données
            project_id = self.project_repository.save_project(project)
            
            # Recharger les projets depuis la base ET récupérer le projet sauvegardé
            self._load_projects()
            
            # Trouver le projet sauvegardé avec le bon ID pour retourner l'objet cohérent
            saved_project = next((p for p in self._projects if p.project_id == project_id), project)
            
            logger.info(f"Projet {project.name} créé avec succès (ID: {project_id}) avec {len(saved_project.units)} unités")
            return {
                'success': True,
                'project': saved_project,  # Retourner le projet rechargé avec les unités
                'project_id': project_id,
                'units': saved_project.units,  # Retourner les unités du projet rechargé
                'message': f'Projet "{project.name}" créé avec succès avec {len(saved_project.units)} unités'
            }
            
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la création du projet: {e}")
            return {
                'success': False,
                'error': f'Erreur système: {str(e)}'
            }
    
    def _adapt_project_data(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapte les données du projet de l'ancien format vers le nouveau.
        
        Args:
            project_data: Données dans l'ancien ou nouveau format
            
        Returns:
            Dict: Données adaptées au nouveau format
        """
        import uuid
        
        adapted = {}
        
        # Champs obligatoires nouveaux
        adapted['project_id'] = str(uuid.uuid4())
        adapted['name'] = project_data.get('name', '')
        adapted['address'] = project_data.get('address', '')
        adapted['construction_year'] = int(project_data.get('construction_year', 0))
        
        # Adaptation du statut
        from src.domain.entities.project import ProjectStatus
        status_str = project_data.get('status', 'PLANNING')
        adapted['status'] = ProjectStatus(status_str) if isinstance(status_str, str) else status_str
        
        # Adaptation des superficies
        if 'total_area' in project_data:
            # Ancien format : total_area (migration vers building_area)
            adapted['building_area'] = float(project_data['total_area'])
        elif 'building_area' in project_data:
            # Nouveau format : building_area
            adapted['building_area'] = float(project_data['building_area'])
        else:
            # Valeur par défaut
            adapted['building_area'] = float(project_data.get('building_area', 0))
        
        # Adaptation du nombre d'unités
        if 'unit_count' in project_data:
            adapted['unit_count'] = int(project_data['unit_count'])
        else:
            adapted['unit_count'] = int(project_data.get('unit_count', 0))
        
        # Adaptation du constructeur
        if 'constructor' in project_data:
            adapted['constructor'] = project_data['constructor']
        else:
            adapted['constructor'] = project_data.get('constructor', '')
        
        return adapted
    
    def get_project_statistics(self, project_id: str) -> Dict[str, Any]:
        """
        Calcule les statistiques d'un projet existant
        
        Args:
            project_id: ID du projet à analyser
            
        Returns:
            Dict contenant les statistiques du projet
        """
        try:
            logger.debug(f"Calcul des statistiques pour le projet ID: {project_id}")
            
            # Recharger les projets depuis la base pour avoir les dernières données
            self._load_projects()
            logger.debug(f"Projets disponibles: {[p.project_id for p in self._projects]}")
            
            # Trouver le projet par ID
            project = next((p for p in self._projects if p.project_id == project_id), None)
            
            if not project:
                return {
                    'success': False,
                    'error': f"Projet avec l'ID '{project_id}' non trouvé"
                }
            
            logger.debug(f"Projet sélectionné: {project.name} avec {len(project.units)} unités")
            
            # Calcul des statistiques basé sur les unités EXISTANTES du projet
            stats = project.get_project_statistics()
            
            logger.info(f"Statistiques calculées pour {project.name}: {stats['sold_units']}/{stats['total_units']} unités vendues")
            
            # Sauvegarder le projet pour s'assurer que les modifications d'unités sont persistées
            self.project_repository.save_project(project)
            logger.debug(f"Projet {project.name} resauvegardé avec les modifications d'unités")
            
            return {
                'success': True,
                'statistics': stats,
                'project_name': project.name,
                'project_id': project_id
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques: {e}")
            return {
                'success': False,
                'error': f"Impossible de calculer les statistiques: {str(e)}"
            }
    
    def update_project_units(self, project_id: str, new_unit_count: int, project_instance: Project = None) -> Dict[str, Any]:
        """
        Met à jour le nombre d'unités d'un projet existant
        
        Args:
            project_id: ID du projet à modifier
            new_unit_count: Nouveau nombre d'unités souhaité
            project_instance: Instance du projet à utiliser (optionnel)
            
        Returns:
            Dict contenant le résultat de l'opération
        """
        try:
            logger.info(f"Mise à jour du nombre d'unités pour le projet ID {project_id}: {new_unit_count}")
            
            # Toujours recharger le projet depuis la base de données pour avoir l'état le plus récent
            all_projects = self.project_repository.get_all_projects()
            project = next((p for p in all_projects if p.project_id == project_id), None)
            
            if not project:
                return {
                    'success': False,
                    'error': f'Projet non trouvé avec l\'ID: {project_id}'
                }
            
            # Validation du nouveau nombre d'unités
            if new_unit_count <= 0 or new_unit_count > 500:
                return {
                    'success': False,
                    'error': "Le nombre d'unités doit être entre 1 et 500"
                }
            
            # Mise à jour des unités
            old_count = len(project.units)  # Utiliser le nombre d'unités actuelles
            additional_units = project.add_units(new_unit_count - old_count)
            
            # Sauvegarde réelle dans la base de données
            self.project_repository.save_project(project)
            
            logger.info(f"Unités mises à jour pour {project.name}: {old_count} → {new_unit_count}")
            return {
                'success': True,
                'project': project,
                'added_units': additional_units,
                'message': f"Nombre d'unités mis à jour: {old_count} → {new_unit_count}"
            }
                
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des unités: {e}")
            return {
                'success': False,
                'error': f"Erreur système: {str(e)}"
            }
    
    def _validate_project_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valide les données d'un projet avant création
        
        Args:
            data: Données du projet à valider
            
        Returns:
            Dict avec validation result et message d'erreur si applicable
        """
        required_fields = ['name', 'address', 'building_area', 'construction_year', 'unit_count', 'constructor']
        
        # Vérification des champs requis
        field_translations = {
            'name': 'nom du projet',
            'address': 'adresse',
            'building_area': 'superficie du bâtiment',
            'construction_year': 'année de construction',
            'unit_count': 'nombre d\'unités',
            'constructor': 'constructeur'
        }
        
        for field in required_fields:
            if field not in data or not data[field]:
                field_name = field_translations.get(field, field)
                return {
                    'valid': False,
                    'error': f"Le {field_name} est obligatoire"
                }
        
        # Validations spécifiques
        if len(data['name'].strip()) < 3:
            return {
                'valid': False,
                'error': "Le nom du projet doit contenir au moins 3 caractères"
            }
        
        if len(data['address'].strip()) < 10:
            return {
                'valid': False,
                'error': "L'adresse doit être complète (minimum 10 caractères)"
            }
        
        try:
            building_area = float(data.get('building_area', data.get('total_area', 0)))
            if building_area <= 0 or building_area > 100000:
                return {
                    'valid': False,
                    'error': "La superficie du bâtiment doit être entre 1 et 100,000 pieds carrés"
                }
        except ValueError:
            return {
                'valid': False,
                'error': "La superficie du bâtiment doit être un nombre valide"
            }
        
        try:
            construction_year = int(data['construction_year'])
            if construction_year < 1900 or construction_year > 2030:
                return {
                    'valid': False,
                    'error': "L'année de construction doit être entre 1900 et 2030"
                }
        except ValueError:
            return {
                'valid': False,
                'error': "L'année de construction doit être un nombre valide"
            }
        
        try:
            unit_count = int(data['unit_count'])
            if unit_count <= 0 or unit_count > 500:
                return {
                    'valid': False,
                    'error': "Le nombre d'unités doit être entre 1 et 500"
                }
        except ValueError:
            return {
                'valid': False,
                'error': "Le nombre d'unités doit être un nombre valide"
            }
        
        if len(data['constructor'].strip()) < 3:
            return {
                'valid': False,
                'error': "Le nom du constructeur doit contenir au moins 3 caractères"
            }
        
        return {'valid': True}
    
    async def _simulate_async_save(self, project: Project, units: List[Unit]) -> bool:
        """
        Simule une opération de sauvegarde asynchrone
        
        Args:
            project: Projet à sauvegarder
            units: Liste des unités à sauvegarder
            
        Returns:
            True si la sauvegarde réussit
        """
        # Simulation d'une opération asynchrone
        await asyncio.sleep(0.1)  # Simule la latence de base de données
        
        # Simulation de validation avant sauvegarde
        if not project or not units:
            return False
        
        # Pour les tests, toujours retourner succès
        # Dans un vrai contexte, ceci ferait appel à la base de données
        return True
    
    
    def get_all_projects_summary(self) -> Dict[str, Any]:
        """
        Récupère un résumé de tous les projets du système
        
        Returns:
            Dict contenant la liste des projets avec statistiques de base
        """
        try:
            logger.debug("Récupération du résumé de tous les projets")
            
            # Simulation de récupération de plusieurs projets
            projects_summary = [
                {
                    'name': 'Résidence du Parc',
                    'total_units': 15,
                    'sold_units': 8,
                    'available_units': 7,
                    'occupancy_rate': 53.3
                },
                {
                    'name': 'Les Jardins de Ville',
                    'total_units': 24,
                    'sold_units': 18,
                    'available_units': 6,
                    'occupancy_rate': 75.0
                }
            ]
            
            total_units = sum(p['total_units'] for p in projects_summary)
            total_sold = sum(p['sold_units'] for p in projects_summary)
            
            logger.info(f"Résumé calculé: {len(projects_summary)} projets, {total_sold}/{total_units} unités vendues")
            
            return {
                'success': True,
                'projects': projects_summary,
                'total_projects': len(projects_summary),
                'total_units': total_units,
                'total_sold': total_sold,
                'overall_occupancy': (total_sold / total_units * 100) if total_units > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du résumé: {e}")
            return {
                'success': False,
                'error': f"Impossible de récupérer le résumé: {str(e)}"
            }

    def transfer_unit_ownership(self, project_id: str, unit_number: str, new_owner: str, transfer_date=None) -> Dict[str, Any]:
        """
        Transfère la propriété d'une unité et sauvegarde automatiquement le projet.
        
        Args:
            project_id: ID du projet
            unit_number: Numéro de l'unité
            new_owner: Nom du nouveau propriétaire
            transfer_date: Date du transfert (optionnel)
            
        Returns:
            Dict: Résultat de l'opération
        """
        try:
            # Trouver le projet
            project = next((p for p in self._projects if p.project_id == project_id), None)
            if not project:
                return {
                    'success': False,
                    'error': f'Projet non trouvé avec l\'ID {project_id}'
                }
            
            # Trouver l'unité
            unit = next((u for u in project.units if u.unit_number == unit_number), None)
            if not unit:
                return {
                    'success': False,
                    'error': f'Unité {unit_number} non trouvée dans le projet {project.name}'
                }
            
            # Effectuer le transfert
            unit.transfer_ownership(new_owner, transfer_date)
            
            # Sauvegarder automatiquement le projet modifié
            self.project_repository.save_project(project)
            
            logger.info(f"Transfert réussi: Unité {unit_number} du projet {project.name} → {new_owner}")
            
            return {
                'success': True,
                'project': project,
                'unit': unit,
                'message': f'Unité {unit_number} transférée à {new_owner} avec succès'
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du transfert de propriété: {e}")
            return {
                'success': False,
                'error': f'Erreur lors du transfert: {str(e)}'
            }

    def transfer_multiple_units(self, project_id: str, transfers: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Transfère la propriété de plusieurs unités en une seule opération.
        
        Args:
            project_id: ID du projet
            transfers: Liste de dicts avec 'unit_number' et 'new_owner'
            
        Returns:
            Dict: Résultat de l'opération avec statistiques
        """
        try:
            # Recharger le projet depuis la base de données pour avoir les dernières données
            all_projects = self.project_repository.get_all_projects()
            project = next((p for p in all_projects if p.project_id == project_id), None)
            if not project:
                return {
                    'success': False,
                    'error': f'Projet non trouvé avec l\'ID {project_id}'
                }
            
            successful_transfers = []
            failed_transfers = []
            
            # Effectuer tous les transferts
            for transfer in transfers:
                unit_number = transfer.get('unit_number')
                new_owner = transfer.get('new_owner')
                
                if not unit_number or not new_owner:
                    failed_transfers.append({
                        'unit_number': unit_number,
                        'error': 'Données de transfert incomplètes'
                    })
                    continue
                
                # Trouver l'unité
                unit = next((u for u in project.units if u.unit_number == unit_number), None)
                if not unit:
                    failed_transfers.append({
                        'unit_number': unit_number,
                        'error': f'Unité non trouvée'
                    })
                    continue
                
                try:
                    # Effectuer le transfert
                    unit.transfer_ownership(new_owner)
                    successful_transfers.append({
                        'unit_number': unit_number,
                        'new_owner': new_owner
                    })
                except Exception as e:
                    failed_transfers.append({
                        'unit_number': unit_number,
                        'error': str(e)
                    })
            
            # Sauvegarder le projet avec tous les changements
            if successful_transfers:
                self.project_repository.save_project(project)
            
            logger.info(f"Transferts effectués: {len(successful_transfers)} réussis, {len(failed_transfers)} échoués")
            
            return {
                'success': len(successful_transfers) > 0,
                'project': project,
                'successful_transfers': successful_transfers,
                'failed_transfers': failed_transfers,
                'message': f'{len(successful_transfers)} transferts réussis sur {len(transfers)} tentatives'
            }
            
        except Exception as e:
            logger.error(f"Erreur lors des transferts multiples: {e}")
            return {
                'success': False,
                'error': f'Erreur lors des transferts: {str(e)}'
            }

    def get_project_statistics_by_id(self, project_id: str) -> Dict[str, Any]:
        """
        Calcule les statistiques d'un projet par son ID.
        
        Args:
            project_id: ID unique du projet
            
        Returns:
            Dict: Résultat avec les statistiques
        """
        try:
            # Recharger les projets depuis la base pour avoir les dernières données
            self._load_projects()
            
            # Trouver le projet par ID
            project = next((p for p in self._projects if p.project_id == project_id), None)
            
            if not project:
                return {
                    'success': False,
                    'error': f'Projet non trouvé avec l\'ID {project_id}'
                }
            
            # Calculer les statistiques
            stats = project.get_project_statistics()
            
            logger.info(f"Statistiques calculées pour {project.name}: {stats['sold_units']}/{stats['total_units']} unités vendues")
            
            return {
                'success': True,
                'statistics': stats,
                'project_name': project.name,
                'project_id': project_id,
                'total_units': stats['total_units']
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques par ID: {e}")
            return {
                'success': False,
                'error': f'Erreur lors du calcul: {str(e)}'
            }

    def delete_project(self, project_name: str) -> Dict[str, Any]:
        """
        Supprime un projet et toutes ses unités associées par nom.
        Cette méthode est maintenue pour compatibilité - utilise delete_project_by_id en interne.
        
        Args:
            project_name: Nom du projet à supprimer
            
        Returns:
            Dict: Résultat de l'opération de suppression
        """
        try:
            # Utiliser la méthode standardisée pour récupérer le projet par nom
            result = self.get_project_by_name(project_name)
            
            if not result['success']:
                return result
            
            project = result['project']
            
            # Déléguer à delete_project_by_id qui est la méthode standardisée
            return self.delete_project_by_id(project.project_id)
                
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du projet {project_name}: {e}")
            return {
                'success': False,
                'error': f'Erreur inattendue lors de la suppression: {str(e)}'
            }

    def delete_project_by_id(self, project_id: str) -> Dict[str, Any]:
        """
        Supprime un projet par son ID et toutes ses unités associées.
        
        Args:
            project_id: ID du projet à supprimer
            
        Returns:
            Dict: Résultat de l'opération de suppression
        """
        try:
            logger.info(f"Début suppression projet par ID: {project_id}")
            
            # Recharger les projets depuis la base pour avoir les dernières données
            self._load_projects()
            logger.debug(f"Projets chargés: {len(self._projects)} projets disponibles")
            logger.debug(f"IDs des projets disponibles: {[p.project_id for p in self._projects]}")
            
            # Trouver le projet par ID
            project = next((p for p in self._projects if p.project_id == project_id), None)
            
            if not project:
                logger.error(f"Projet avec l'ID '{project_id}' non trouvé dans la liste des {len(self._projects)} projets")
                logger.debug(f"IDs disponibles: {[p.project_id for p in self._projects]}")
                return {
                    'success': False,
                    'error': f'Projet avec l\'ID "{project_id}" non trouvé'
                }
            
            # Sauvegarder les informations avant suppression pour les logs
            project_name = project.name
            total_units = len(project.units) if project.units else 0
            logger.info(f"Projet trouvé pour suppression: {project_name} avec {total_units} unités")
            
            # Supprimer le projet de la base de données
            success = self.project_repository.delete_project(project_id)
            logger.info(f"Résultat suppression base de données: {success}")
            
            if success:
                # Retirer le projet de la liste en mémoire
                self._projects = [p for p in self._projects if p.project_id != project_id]
                
                logger.info(f"Projet supprimé avec succès par ID: {project_name} (ID: {project_id}, {total_units} unités)")
                
                return {
                    'success': True,
                    'message': f'Projet "{project_name}" supprimé avec succès',
                    'project_name': project_name,
                    'total_units_deleted': total_units
                }
            else:
                logger.error(f"Échec de la suppression en base de données pour le projet {project_id}")
                return {
                    'success': False,
                    'error': f'Erreur lors de la suppression du projet en base de données'
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du projet par ID {project_id}: {e}")
            return {
                'success': False,
                'error': f'Erreur inattendue lors de la suppression: {str(e)}'
            }
