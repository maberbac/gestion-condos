"""
Service de gestion des condos pour l'interface web.

Ce service fournit les méthodes nécessaires pour l'interface web
de gestion des condos, similaire au UserService.
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

from typing import List, Dict, Any, Optional
from src.domain.entities.condo import Condo, CondoType, CondoStatus
from decimal import Decimal


class CondoService:
    """Service pour la gestion des condos dans l'interface web."""
    
    def __init__(self):
        """Initialise le service avec des données de démo."""
        # Pour l'instant, utilise des données fictives
        # Dans une implémentation complète, ceci utiliserait un repository
        self._demo_condos = [
            {
                'unit_number': 'A-101',
                'owner_name': 'Jean Dupont',
                'square_feet': 850,
                'condo_type': CondoType.RESIDENTIAL,
                'status': CondoStatus.ACTIVE,
                'monthly_fees': 450,
                'building_name': 'Tour A',
                'is_sold': True
            },
            {
                'unit_number': 'A-102', 
                'owner_name': 'Marie Martin',
                'square_feet': 920,
                'condo_type': CondoType.RESIDENTIAL,
                'status': CondoStatus.ACTIVE,
                'monthly_fees': 520,
                'building_name': 'Tour A',
                'is_sold': True
            },
            {
                'unit_number': 'B-201',
                'owner_name': 'Disponible',
                'square_feet': 775,
                'condo_type': CondoType.RESIDENTIAL,
                'status': CondoStatus.ACTIVE,
                'monthly_fees': 420,
                'building_name': 'Tour B',
                'is_sold': False
            },
            {
                'unit_number': 'C-301',
                'owner_name': 'Pierre Tremblay',
                'square_feet': 1200,
                'condo_type': CondoType.COMMERCIAL,
                'status': CondoStatus.ACTIVE,
                'monthly_fees': 680,
                'building_name': 'Tour C',
                'is_sold': True
            },
            {
                'unit_number': 'C-302',
                'owner_name': 'Entreprise ABC Inc.',
                'square_feet': 950,
                'condo_type': CondoType.COMMERCIAL,
                'status': CondoStatus.MAINTENANCE,
                'monthly_fees': 560,
                'building_name': 'Tour C',
                'is_sold': True
            },
            {
                'unit_number': 'P-001',
                'owner_name': 'Stationnement Public',
                'square_feet': 250,
                'condo_type': CondoType.PARKING,
                'status': CondoStatus.ACTIVE,
                'monthly_fees': 75,
                'building_name': 'Garage',
                'is_sold': False
            }
        ]
    
    def get_all_condos(self, user_role: str = 'guest') -> List[Dict[str, Any]]:
        """
        Récupère tous les condos selon le rôle de l'utilisateur.
        
        Args:
            user_role: Rôle de l'utilisateur pour filtrer les données
            
        Returns:
            List[Dict]: Liste des condos visibles pour ce rôle
        """
        try:
            condos = []
            
            for condo_data in self._demo_condos:
                # Filtrage selon le rôle
                if user_role == 'admin':
                    # Admin voit tout
                    visible = True
                elif user_role == 'resident':
                    # Résident voit seulement les condos résidentiels et commerciaux
                    visible = condo_data['condo_type'] in [CondoType.RESIDENTIAL, CondoType.COMMERCIAL]
                else:
                    # Invité voit seulement les condos disponibles
                    visible = not condo_data['is_sold']
                
                if visible:
                    # Formatage pour l'affichage
                    condo = {
                        'unit_number': condo_data['unit_number'],
                        'owner_name': condo_data['owner_name'],
                        'square_feet': condo_data['square_feet'],
                        'unit_type': {'name': condo_data['condo_type'].value.upper()},
                        'status': condo_data['status'].value.upper(),
                        'monthly_fees': condo_data['monthly_fees'],
                        'building_name': condo_data['building_name'],
                        'is_available': not condo_data['is_sold'],
                        'type_icon': self._get_type_icon(condo_data['condo_type']),
                        'status_icon': self._get_status_icon(condo_data['status'])
                    }
                    condos.append(condo)
            
            logger.info(f"Récupération de {len(condos)} condos pour rôle {user_role}")
            return condos
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des condos: {e}")
            return []
    
    def get_condo_by_unit_number(self, unit_number: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un condo par son numéro d'unité.
        
        Args:
            unit_number: Numéro d'unité à rechercher
            
        Returns:
            Optional[Dict]: Données du condo ou None si introuvable
        """
        try:
            for condo_data in self._demo_condos:
                if condo_data['unit_number'] == unit_number:
                    return {
                        'unit_number': condo_data['unit_number'],
                        'owner_name': condo_data['owner_name'],
                        'square_feet': condo_data['square_feet'],
                        'condo_type': condo_data['condo_type'],
                        'status': condo_data['status'],
                        'monthly_fees': condo_data['monthly_fees'],
                        'building_name': condo_data['building_name'],
                        'is_sold': condo_data['is_sold']
                    }
            
            logger.warning(f"Condo non trouvé: {unit_number}")
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche du condo {unit_number}: {e}")
            return None
    
    def create_condo(self, condo_data: Dict[str, Any]) -> bool:
        """
        Crée un nouveau condo.
        
        Args:
            condo_data: Données du nouveau condo
            
        Returns:
            bool: True si création réussie, False sinon
        """
        try:
            # Validation de base
            if not condo_data.get('unit_number'):
                logger.error("Numéro d'unité requis")
                return False
            
            # Vérifier l'unicité
            if self.get_condo_by_unit_number(condo_data['unit_number']):
                logger.error(f"Unité {condo_data['unit_number']} existe déjà")
                return False
            
            # Ajouter le nouveau condo
            new_condo = {
                'unit_number': condo_data['unit_number'],
                'owner_name': condo_data.get('owner_name', 'Disponible'),
                'square_feet': int(condo_data.get('square_feet', 800)),
                'condo_type': CondoType(condo_data.get('condo_type', 'residential')),
                'status': CondoStatus(condo_data.get('status', 'active')),
                'monthly_fees': int(condo_data.get('monthly_fees', 400)),
                'building_name': condo_data.get('building_name', 'Bâtiment Principal'),
                'is_sold': condo_data.get('is_sold', False)
            }
            
            self._demo_condos.append(new_condo)
            logger.info(f"Condo créé: {new_condo['unit_number']}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du condo: {e}")
            return False
    
    def update_condo(self, unit_number: str, condo_data: Dict[str, Any]) -> bool:
        """
        Met à jour un condo existant.
        
        Args:
            unit_number: Numéro d'unité à modifier
            condo_data: Nouvelles données
            
        Returns:
            bool: True si modification réussie, False sinon
        """
        try:
            for i, condo in enumerate(self._demo_condos):
                if condo['unit_number'] == unit_number:
                    # Mise à jour des champs modifiables
                    self._demo_condos[i].update({
                        'owner_name': condo_data.get('owner_name', condo['owner_name']),
                        'square_feet': int(condo_data.get('square_feet', condo['square_feet'])),
                        'condo_type': CondoType(condo_data.get('condo_type', condo['condo_type'].value)),
                        'status': CondoStatus(condo_data.get('status', condo['status'].value)),
                        'monthly_fees': int(condo_data.get('monthly_fees', condo['monthly_fees'])),
                        'building_name': condo_data.get('building_name', condo['building_name']),
                        'is_sold': condo_data.get('is_sold', condo['is_sold'])
                    })
                    
                    logger.info(f"Condo modifié: {unit_number}")
                    return True
            
            logger.error(f"Condo non trouvé pour modification: {unit_number}")
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de la modification du condo {unit_number}: {e}")
            return False
    
    def delete_condo(self, unit_number: str) -> bool:
        """
        Supprime un condo.
        
        Args:
            unit_number: Numéro d'unité à supprimer
            
        Returns:
            bool: True si suppression réussie, False sinon
        """
        try:
            initial_count = len(self._demo_condos)
            self._demo_condos = [c for c in self._demo_condos if c['unit_number'] != unit_number]
            
            if len(self._demo_condos) < initial_count:
                logger.info(f"Condo supprimé: {unit_number}")
                return True
            else:
                logger.error(f"Condo non trouvé pour suppression: {unit_number}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du condo {unit_number}: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Calcule les statistiques des condos.
        
        Returns:
            Dict: Statistiques globales
        """
        try:
            total = len(self._demo_condos)
            occupied = len([c for c in self._demo_condos if c['is_sold']])
            vacant = total - occupied
            
            residential = len([c for c in self._demo_condos if c['condo_type'] == CondoType.RESIDENTIAL])
            commercial = len([c for c in self._demo_condos if c['condo_type'] == CondoType.COMMERCIAL])
            parking = len([c for c in self._demo_condos if c['condo_type'] == CondoType.PARKING])
            
            total_revenue = sum(c['monthly_fees'] for c in self._demo_condos if c['is_sold'])
            total_area = sum(c['square_feet'] for c in self._demo_condos)
            
            return {
                'total_condos': total,
                'occupied': occupied,
                'vacant': vacant,
                'residential': residential,
                'commercial': commercial,
                'parking': parking,
                'total_monthly_revenue': total_revenue,
                'total_area': total_area,
                'average_area': round(total_area / total if total > 0 else 0, 1)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques: {e}")
            return {}
    
    def _get_type_icon(self, condo_type: CondoType) -> str:
        """Retourne l'icône appropriée pour le type de condo."""
        icons = {
            CondoType.RESIDENTIAL: '🏠',
            CondoType.COMMERCIAL: '🏢',
            CondoType.PARKING: '🚗',
            CondoType.STORAGE: '📦'
        }
        return icons.get(condo_type, '🏠')
    
    def _get_status_icon(self, status: CondoStatus) -> str:
        """Retourne l'icône appropriée pour le statut."""
        icons = {
            CondoStatus.ACTIVE: '✅',
            CondoStatus.INACTIVE: '❌',
            CondoStatus.MAINTENANCE: '🔧',
            CondoStatus.SOLD: '💰'
        }
        return icons.get(status, '❓')
