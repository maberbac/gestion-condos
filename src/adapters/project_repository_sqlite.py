"""
Project Repository SQLite - Persistance des projets et unités dans SQLite.

[ARCHITECTURE HEXAGONALE + STANDARDS DE CONFIGURATION]
Repository SQLite pour la gestion des projets et leurs unités associées
selon les standards définis dans copilot-instructions.md :
- Configuration JSON obligatoire (database.json)
- SQLite comme base de données principale
- Migrations avec scripts SQL
- Persistance et gestion des données
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

import sqlite3
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from src.domain.entities.project import Project
from src.domain.entities.unit import Unit, UnitStatus, UnitType


class ProjectRepositorySQLite:
    """
    Repository SQLite pour la persistance des projets et unités.
    
    [STANDARDS OBLIGATOIRES]
    - Configuration via config/database.json
    - Base de données SQLite principale
    - Migrations automatiques
    - Gestion des données persistantes
    
    Architecture Hexagonale:
    - Implémente la persistance des entités Project
    - Isole la logique SQLite du core business
    - Permet tests unitaires avec base en mémoire
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialise le repository SQLite pour les projets.
        
        Args:
            db_path: Chemin vers la base de données (optionnel)
        """
        self.db_path = db_path or self._get_database_path()
        self._ensure_database_exists()
        
        logger.info(f"ProjectRepositorySQLite initialisé avec DB: {self.db_path}")
        logger.info(f"Chargé {len(self.get_all_projects())} projets depuis la base de données")
    
    def _get_database_path(self) -> str:
        """Récupère le chemin de la base de données depuis la configuration."""
        try:
            config_path = Path(__file__).parent.parent.parent / "config" / "database.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('database_path', 'data/condos.db')
            else:
                logger.warning(f"Fichier de config database.json non trouvé: {config_path}")
                return 'data/condos.db'
        except Exception as e:
            logger.warning(f"Erreur de lecture de config database.json: {e}, utilisation config par défaut")
            return 'data/condos.db'
    
    def _ensure_database_exists(self):
        """S'assure que le fichier de base de données existe."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    def save_project(self, project: Project) -> str:
        """
        Sauvegarde un projet et ses unités dans la base de données.
        
        Args:
            project: Instance du projet à sauvegarder
            
        Returns:
            str: ID du projet sauvegardé
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Générer un project_id s'il n'existe pas
                if not hasattr(project, 'project_id') or not project.project_id:
                    project.project_id = str(uuid.uuid4())
                
                # Insérer ou mettre à jour le projet
                conn.execute("""
                    INSERT OR REPLACE INTO projects 
                    (project_id, name, address, building_area, land_area, construction_year, 
                     unit_count, constructor, creation_date, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    project.project_id,
                    project.name,
                    project.address,
                    project.building_area,
                    project.land_area,
                    project.construction_year,
                    project.unit_count,
                    project.constructor,
                    project.creation_date.isoformat(),
                    project.status.value  # Utiliser la valeur du statut du projet
                ))
                
                # Supprimer les anciennes unités
                conn.execute("DELETE FROM units WHERE project_id = ?", (project.project_id,))
                
                # Insérer les nouvelles unités
                if project.units:
                    for unit in project.units:
                        self._save_unit(conn, unit, project.project_id)
                
                conn.commit()
                logger.info(f"Projet sauvegardé: {project.name} avec {len(project.units)} unités")
                return project.project_id
                
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du projet {project.name}: {e}")
            raise
    
    def _save_unit(self, conn: sqlite3.Connection, unit, project_id: str):
        """Sauvegarde une unité dans la base de données."""
        # Gérer les différents formats d'unités (dict, objet Unit, ou objet Condo)
        if isinstance(unit, dict):
            unit_number = unit.get('unit_number', '')
            area = unit.get('square_feet', unit.get('area', 0))
            condo_type = unit.get('condo_type', 'residential')
            status = unit.get('status', 'active')
            owner_name = unit.get('owner_name', 'Disponible')
            purchase_date = unit.get('purchase_date')
            monthly_fees = unit.get('calculated_monthly_fees', unit.get('monthly_fees_base'))
        else:
            # Objet Unit ou Condo - gérer les différents attributs
            unit_number = unit.unit_number
            
            # Gérer les différents noms d'attributs pour la superficie
            if hasattr(unit, 'area'):
                area = unit.area  # Objet Unit
            elif hasattr(unit, 'square_feet'):
                area = unit.square_feet  # Objet Condo
            else:
                area = 0
                
            # Gérer les types et statuts
            if hasattr(unit, 'unit_type'):
                # Objet Unit
                condo_type = unit.unit_type.value if hasattr(unit.unit_type, 'value') else str(unit.unit_type)
                status = unit.status.value if hasattr(unit.status, 'value') else str(unit.status)
            elif hasattr(unit, 'condo_type'):
                # Objet Condo
                condo_type = unit.condo_type.value if hasattr(unit.condo_type, 'value') else str(unit.condo_type)
                status = unit.status.value if hasattr(unit.status, 'value') else str(unit.status)
            else:
                condo_type = 'residential'
                status = 'active'
                
            owner_name = getattr(unit, 'owner_name', 'Disponible')
            purchase_date = getattr(unit, 'purchase_date', None)
            monthly_fees = getattr(unit, 'calculated_monthly_fees', getattr(unit, 'monthly_fees_base', None))
        
        conn.execute("""
            INSERT INTO units 
            (unit_number, project_id, area, condo_type, status, 
             owner_name, purchase_date, calculated_monthly_fees)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            unit_number,
            project_id,
            area,
            condo_type,
            status,
            owner_name,
            purchase_date,
            str(monthly_fees) if monthly_fees else None
        ))
    
    def get_all_projects(self) -> List[Project]:
        """
        Récupère tous les projets avec leurs unités.
        
        Returns:
            List[Project]: Liste de tous les projets
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Récupérer tous les projets
                cursor = conn.execute("""
                    SELECT project_id, name, address, building_area, land_area, construction_year,
                           unit_count, constructor, creation_date, status
                    FROM projects 
                    ORDER BY creation_date DESC
                """)
                
                projects = []
                for row in cursor.fetchall():
                    # Créer l'objet projet
                    project = Project(
                        name=row['name'],
                        address=row['address'],
                        building_area=row['building_area'],
                        construction_year=row['construction_year'],
                        unit_count=row['unit_count'],
                        constructor=row['constructor'],
                        creation_date=datetime.fromisoformat(row['creation_date'])
                    )
                    
                    # Ajouter le project_id
                    project.project_id = row['project_id']
                    
                    # Restaurer le statut depuis la base de données
                    from src.domain.entities.project import ProjectStatus
                    if row['status']:
                        try:
                            project.status = ProjectStatus(row['status'])
                        except ValueError:
                            # Si le statut en DB n'est pas valide, utiliser PLANNING par défaut
                            project.status = ProjectStatus.PLANNING
                    
                    # Restaurer land_area si présent
                    if row['land_area'] is not None:
                        project.land_area = row['land_area']
                    
                    # Récupérer les unités du projet
                    unit_cursor = conn.execute("""
                        SELECT id, unit_number, area, condo_type, status,
                               owner_name, purchase_date, calculated_monthly_fees
                        FROM units 
                        WHERE project_id = ?
                        ORDER BY unit_number
                    """, (row['project_id'],))
                    
                    units = []
                    for unit_row in unit_cursor.fetchall():
                        # Créer les unités comme objets Unit appropriés
                        from src.domain.entities.unit import Unit, UnitType, UnitStatus
                        
                        # Conversion du type et statut depuis les valeurs string de la DB
                        try:
                            unit_type = UnitType(unit_row['condo_type'])
                        except (ValueError, KeyError):
                            unit_type = UnitType.RESIDENTIAL  # Valeur par défaut
                            
                        # Mapping des anciens CondoStatus vers UnitStatus
                        try:
                            old_status = unit_row['status']
                            if old_status == 'active':
                                status = UnitStatus.AVAILABLE
                            elif old_status == 'inactive':
                                status = UnitStatus.AVAILABLE  # Inactif devient disponible
                            elif old_status == 'sold':
                                status = UnitStatus.SOLD
                            elif old_status == 'maintenance':
                                status = UnitStatus.MAINTENANCE
                            else:
                                # Essayer conversion directe si nouvelles valeurs
                                status = UnitStatus(old_status)
                        except (ValueError, KeyError):
                            status = UnitStatus.AVAILABLE  # Valeur par défaut
                        
                        # Conversion date d'achat
                        purchase_date = None
                        if unit_row['purchase_date']:
                            try:
                                purchase_date = datetime.fromisoformat(unit_row['purchase_date'])
                            except (ValueError, TypeError):
                                purchase_date = None
                        
                        unit = Unit(
                            unit_number=unit_row['unit_number'],
                            area=float(unit_row['area']),
                            unit_type=unit_type,
                            status=status,
                            owner_name=unit_row['owner_name'] or "Disponible",
                            purchase_date=purchase_date,
                            estimated_price=float(unit_row['price'] if 'price' in unit_row.keys() else 0),  # Si pas de colonne price, défaut à 0
                            project_id=row['project_id'],          # Ajouter l'ID du projet
                            id=unit_row['id']  # Utiliser l'attribut id directement
                        )
                        units.append(unit)
                    
                    logger.debug(f"Récupéré {len(units)} unités pour le projet {row['name']}")
                    project.units = units
                    projects.append(project)
                
                logger.info(f"Chargé {len(projects)} projets depuis la base de données")
                return projects
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des projets: {e}")
            return []
    
    def get_project_by_id(self, project_id: str) -> Optional[Project]:
        """
        Récupère un projet par son ID.
        
        Args:
            project_id: ID du projet
            
        Returns:
            Optional[Project]: Le projet trouvé ou None
        """
        try:
            projects = self.get_all_projects()
            for project in projects:
                if hasattr(project, 'project_id') and project.project_id == project_id:
                    return project
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du projet {project_id}: {e}")
            return None
    
    def get_unit_by_db_id(self, unit_db_id: int) -> Optional[tuple]:
        """
        Récupère une unité par son ID de base de données.
        
        Args:
            unit_db_id: ID de l'unité dans la base de données
            
        Returns:
            Optional[tuple]: (unit, project) si trouvée, None sinon
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Récupérer l'unité et le projet associé
                cursor = conn.execute("""
                    SELECT u.id, u.unit_number, u.area, u.condo_type, u.status,
                           u.owner_name, u.purchase_date, u.calculated_monthly_fees,
                           p.project_id, p.name as project_name
                    FROM units u
                    JOIN projects p ON u.project_id = p.project_id
                    WHERE u.id = ?
                """, (unit_db_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Créer l'objet Unit
                from src.domain.entities.unit import Unit, UnitType, UnitStatus
                
                # Conversion du type et statut
                try:
                    unit_type = UnitType(row['condo_type'])
                except (ValueError, KeyError):
                    unit_type = UnitType.RESIDENTIAL
                    
                try:
                    old_status = row['status']
                    if old_status == 'active':
                        status = UnitStatus.AVAILABLE
                    elif old_status == 'inactive':
                        status = UnitStatus.AVAILABLE
                    elif old_status == 'sold':
                        status = UnitStatus.SOLD
                    elif old_status == 'maintenance':
                        status = UnitStatus.MAINTENANCE
                    else:
                        status = UnitStatus(old_status)
                except (ValueError, KeyError):
                    status = UnitStatus.AVAILABLE
                
                # Conversion date d'achat
                purchase_date = None
                if row['purchase_date']:
                    try:
                        purchase_date = datetime.fromisoformat(row['purchase_date'])
                    except (ValueError, TypeError):
                        purchase_date = None
                
                unit = Unit(
                    unit_number=row['unit_number'],
                    area=float(row['area']),
                    unit_type=unit_type,
                    status=status,
                    owner_name=row['owner_name'] or "Disponible",
                    purchase_date=purchase_date,
                    estimated_price=0.0,  # À récupérer depuis estimated_price si nécessaire
                    project_id=row['project_id'],
                    id=row['id']  # Utiliser l'attribut id directement
                )
                
                # Récupérer le projet minimal pour le contexte
                from src.domain.entities.project import Project
                project = Project(
                    name=row['project_name'],
                    project_id=row['project_id'],
                    address="Adresse temporaire",
                    building_area=100.0,  # Superficie positive requise par la validation
                    construction_year=2000,
                    unit_count=1,  # Nombre d'unités positif requis
                    constructor="Constructeur temporaire"
                )
                
                return (unit, project)
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'unité ID {unit_db_id}: {e}")
            return None
    
    def delete_project(self, project_id: str) -> bool:
        """
        Supprime un projet et ses unités.
        
        Args:
            project_id: ID du projet à supprimer
            
        Returns:
            bool: True si supprimé avec succès
        """
        try:
            logger.info(f"Tentative de suppression du projet ID: {project_id}")
            
            with sqlite3.connect(self.db_path) as conn:
                # Vérifier d'abord si le projet existe
                cursor = conn.execute("SELECT project_id, name FROM projects WHERE project_id = ?", (project_id,))
                existing_project = cursor.fetchone()
                
                if not existing_project:
                    logger.warning(f"Projet non trouvé en base de données: {project_id}")
                    return False
                
                logger.info(f"Projet trouvé en base: {existing_project[1]} (ID: {existing_project[0]})")
                
                # Supprimer les unités d'abord (FK cascade)
                units_cursor = conn.execute("DELETE FROM units WHERE project_id = ?", (project_id,))
                units_deleted = units_cursor.rowcount
                logger.info(f"Unités supprimées: {units_deleted}")
                
                # Supprimer le projet
                project_cursor = conn.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
                
                conn.commit()
                
                if project_cursor.rowcount > 0:
                    logger.info(f"Projet supprimé avec succès: {project_id} ({units_deleted} unités)")
                    return True
                else:
                    logger.error(f"Échec de la suppression du projet: {project_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du projet {project_id}: {e}")
            return False
    
    def migrate_from_json(self, json_file_path: str) -> bool:
        """
        Migre les données depuis un fichier JSON vers la base de données.
        
        Args:
            json_file_path: Chemin vers le fichier JSON
            
        Returns:
            bool: True si migration réussie
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            projects_data = data.get('projects', [])
            migrated_count = 0
            
            for project_data in projects_data:
                try:
                    # Créer l'objet Project depuis les données JSON
                    project = Project.from_dict(project_data)
                    
                    # Ajouter le project_id depuis les données
                    if 'project_id' in project_data:
                        project.project_id = project_data['project_id']
                    
                    # Sauvegarder dans la base
                    self.save_project(project)
                    migrated_count += 1
                    
                except Exception as e:
                    logger.error(f"Erreur lors de la migration du projet {project_data.get('name', 'Inconnu')}: {e}")
                    continue
            
            logger.info(f"Migration terminée: {migrated_count} projets migrés depuis {json_file_path}")
            return migrated_count > 0
            
        except Exception as e:
            logger.error(f"Erreur lors de la migration depuis {json_file_path}: {e}")
            return False

    def update_unit(self, unit_id: int, unit_data: dict) -> bool:
        """
        Met à jour une unité spécifique sans affecter les autres unités du projet.
        
        Args:
            unit_id: ID de l'unité à mettre à jour
            unit_data: Dictionnaire avec les données à mettre à jour
            
        Returns:
            bool: True si mise à jour réussie
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Construire la requête de mise à jour dynamiquement
                set_clauses = []
                values = []
                
                # Mapper les champs de condo_data aux colonnes de la base
                field_mapping = {
                    'owner_name': 'owner_name',
                    'square_feet': 'area',
                    'area': 'area',
                    'monthly_fees': 'calculated_monthly_fees',
                    'monthly_fees_base': 'calculated_monthly_fees',
                    'condo_type': 'condo_type',
                    'unit_type': 'condo_type',
                    'status': 'status',
                    'is_sold': 'status'  # Gérer is_sold → status
                }
                
                for field, db_column in field_mapping.items():
                    if field in unit_data:
                        if field == 'is_sold':
                            # Convertir is_sold en status approprié
                            if unit_data[field]:
                                set_clauses.append(f"{db_column} = ?")
                                values.append('sold')
                        else:
                            set_clauses.append(f"{db_column} = ?")
                            values.append(unit_data[field])
                
                if not set_clauses:
                    logger.warning(f"Aucune donnée à mettre à jour pour l'unité {unit_id}")
                    return True
                
                # Ajouter l'ID à la fin pour la clause WHERE
                values.append(unit_id)
                
                # Construire et exécuter la requête
                query = f"UPDATE units SET {', '.join(set_clauses)} WHERE id = ?"
                
                cursor = conn.execute(query, values)
                
                if cursor.rowcount == 0:
                    logger.error(f"Aucune unité trouvée avec l'ID {unit_id}")
                    return False
                
                conn.commit()
                logger.info(f"Unité {unit_id} mise à jour avec succès")
                return True
                
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'unité {unit_id}: {e}")
            return False
