"""
SQLite Adapter - Implémentation concrète pour la persistance SQLite.

[ARCHITECTURE HEXAGONALE + STANDARDS DE CONFIGURATION]
Cet adapter implémente la persistance des données en utilisant SQLite
selon les standards définis dans copilot-instructions.md :
- Configuration JSON obligatoire (database.json)
- SQLite comme base de données principale
- Migrations avec scripts SQL
- Persistance et gestion des données

NOTE: Version synchrone pour compatibilité initiale.
Version asynchrone disponible après installation d'aiosqlite.
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)


import sqlite3
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import threading

from src.domain.entities.condo import Condo, CondoStatus, CondoType
from src.ports.condo_repository_sync import (
    CondoRepositoryPort, 
    CondoRepositoryError
)


class SQLiteAdapter(CondoRepositoryPort):
    """
    Adapter SQLite pour la persistance des données de condos.
    
    [STANDARDS OBLIGATOIRES]
    - Configuration via config/database.json
    - Base de données SQLite principale
    - Migrations automatiques
    - Gestion des données persistantes
    
    Architecture Hexagonale:
    - Implémente CondoRepositoryPort du domaine métier
    - Isole la logique SQLite du core business
    - Permet tests unitaires avec base en mémoire
    """
    
    def __init__(self, config_path: str = "config/database.json"):
        """
        Initialise l'adapter avec configuration JSON obligatoire.
        
        Args:
            config_path: Chemin vers fichier de configuration JSON
        """
        # Initialiser le logger en premier
        self.logger = logging.getLogger(__name__)
        
        # Charger la configuration
        self.config = self._load_database_config(config_path)
        self.db_path = Path(self.config['database']['path'])
        self.migrations_dir = Path(self.config['database']['migrations_path'])
        
        # Créer les répertoires s'ils n'existent pas
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
        
        # Thread lock pour opérations concurrentes
        self._db_lock = threading.Lock()
        
        # Initialiser la base de données
        self._initialize_database()
    
    def _load_database_config(self, config_path: str) -> Dict[str, Any]:
        """
        [STANDARD: Configuration JSON obligatoire]
        Charge la configuration depuis fichier JSON avec validation.
        """
        try:
            # Résoudre le chemin de façon robuste par rapport à la racine du projet
            if not os.path.isabs(config_path):
                # Trouver la racine du projet (répertoire contenant src/)
                current_dir = Path(__file__).resolve()
                while current_dir.parent != current_dir:
                    if (current_dir / 'src').is_dir():
                        project_root = current_dir
                        break
                    current_dir = current_dir.parent
                else:
                    # Fallback : utiliser le répertoire courant
                    project_root = Path.cwd()
                
                resolved_config_path = project_root / config_path
            else:
                resolved_config_path = Path(config_path)
            
            with open(resolved_config_path, 'r', encoding='utf-8') as file:
                config = json.load(file)
            
            # Validation basique de la configuration
            required_keys = ['database']
            for key in required_keys:
                if key not in config:
                    raise ValueError(f"Clé manquante dans la configuration: {key}")
            
            # Validation spécifique SQLite
            db_config = config['database']
            if db_config.get('type') != 'sqlite':
                raise ValueError("Type de base de données doit être 'sqlite'")
            
            self.logger.info(f"Configuration base de données chargée: {config_path}")
            return config
            
        except FileNotFoundError:
            raise CondoRepositoryError(f"Fichier de configuration introuvable: {config_path}")
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            # Si erreur d'encodage, retourner config par défaut
            self.logger.warning(f"Erreur de lecture de config {config_path}: {e}, utilisation config par défaut")
            return {
                "database": {
                    "type": "sqlite",
                    "name": "condos.db",
                    "path": "data/condos.db",
                    "migrations_path": "data/migrations/"
                },
                "connection": {
                    "pool_size": 5,
                    "timeout_seconds": 30,
                    "retry_attempts": 3
                },
                "migrations": {
                    "auto_migrate": False,
                    "validate_schema": True
                },
                "performance": {
                    "enable_wal_mode": True,
                    "cache_size_kb": 2048,
                    "synchronous": "NORMAL"
                }
            }
    
    def _initialize_database(self) -> None:
        """
        [STANDARD: SQLite + Migrations]
        Initialise la base de données et exécute les migrations.
        """
        try:
            # Créer la base de données si elle n'existe pas
            if not self.db_path.exists():
                self.logger.info("Création de la base de données SQLite")
                self._create_database()
            
            # Exécuter les migrations
            self._run_migrations()
            
            # Configurer SQLite selon les standards
            self._configure_sqlite()
            
            self.logger.info("Base de données SQLite initialisée avec succès")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation SQLite: {e}")
            raise CondoRepositoryError(f"Impossible d'initialiser la base: {e}")
    
    def _create_database(self) -> None:
        """Crée le fichier de base de données SQLite vide."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("SELECT 1")  # Test de connexion
            conn.commit()
    
    def _run_migrations(self) -> None:
        """
        [STANDARD: Migrations SQL]
        Exécute les scripts de migration dans l'ordre en utilisant schema_migrations.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Créer la table de suivi des migrations
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        version TEXT PRIMARY KEY,
                        applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Vérifier quelles migrations ont été appliquées
                cursor = conn.execute("SELECT version FROM schema_migrations")
                applied_migrations = {row[0] for row in cursor.fetchall()}
                
                # Obtenir tous les fichiers de migration
                migration_files = sorted(self.migrations_dir.glob("*.sql"))
                
                # Appliquer les nouvelles migrations
                for migration_file in migration_files:
                    migration_name = migration_file.name
                    if migration_name not in applied_migrations:
                        self._execute_migration_with_tracking(migration_file, conn)
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erreur lors des migrations: {e}")
            raise CondoRepositoryError(f"Migrations échouées: {e}")
    
    def _execute_migration_with_tracking(self, migration_file: Path, conn: sqlite3.Connection) -> None:
        """Exécute une migration et l'enregistre dans schema_migrations."""
        try:
            # Lire et exécuter le script SQL
            with open(migration_file, 'r', encoding='utf-8') as file:
                migration_sql = file.read()
            
            # Exécuter la migration
            conn.executescript(migration_sql)
            
            # Marquer comme appliquée
            conn.execute(
                "INSERT INTO schema_migrations (version) VALUES (?)",
                (migration_file.name,)
            )
            
            self.logger.info(f"Migration exécutée: {migration_file.name}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la migration {migration_file.name}: {e}")
            raise CondoRepositoryError(f"Migration échouée: {e}")
    
    def _configure_sqlite(self) -> None:
        """
        [STANDARD: Performance SQLite]
        Configure SQLite selon les bonnes pratiques.
        """
        perf_config = self.config.get('performance', {})
        
        with sqlite3.connect(self.db_path) as conn:
            # Mode WAL pour meilleures performances
            if perf_config.get('enable_wal_mode', True):
                conn.execute("PRAGMA journal_mode = WAL")
            
            # Taille du cache
            cache_size = perf_config.get('cache_size_kb', 2048)
            conn.execute(f"PRAGMA cache_size = -{cache_size}")
            
            # Mode synchrone
            sync_mode = perf_config.get('synchronous', 'NORMAL')
            conn.execute(f"PRAGMA synchronous = {sync_mode}")
            
            # Activer les clés étrangères
            conn.execute("PRAGMA foreign_keys = ON")
            
            conn.commit()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Crée une nouvelle connexion SQLite avec configuration."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Pour accès par nom de colonne
        return conn
    
    # ==================== Implémentation CondoRepositoryPort ====================
    
    def save_condo(self, condo: Condo) -> bool:
        """
        Sauvegarde ou met à jour un condo dans SQLite.
        """
        try:
            with self._db_lock:
                with self._get_connection() as conn:
                    # Vérifier si le condo existe
                    cursor = conn.execute(
                        "SELECT id FROM condos WHERE unit_number = ?", 
                        (condo.unit_number,)
                    )
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Mise à jour
                        conn.execute("""
                            UPDATE condos SET 
                                owner_name = ?, square_feet = ?, condo_type = ?, 
                                status = ?, purchase_date = ?, monthly_fees_base = ?
                            WHERE unit_number = ?
                        """, (
                            condo.owner_name, condo.square_feet, condo.condo_type.value,
                            condo.status.value, 
                            condo.purchase_date.isoformat() if condo.purchase_date else None,
                            float(condo.monthly_fees_base) if condo.monthly_fees_base else None,
                            condo.unit_number
                        ))
                        self.logger.info(f"Condo {condo.unit_number} mis à jour")
                    else:
                        # Insertion
                        conn.execute("""
                            INSERT INTO condos (unit_number, owner_name, square_feet, condo_type, 
                                              status, purchase_date, monthly_fees_base)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            condo.unit_number, condo.owner_name, condo.square_feet,
                            condo.condo_type.value, condo.status.value,
                            condo.purchase_date.isoformat() if condo.purchase_date else None,
                            float(condo.monthly_fees_base) if condo.monthly_fees_base else None
                        ))
                        self.logger.info(f"Nouveau condo {condo.unit_number} créé")
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde du condo {condo.unit_number}: {e}")
            raise CondoRepositoryError(f"Impossible de sauvegarder le condo: {e}")
    
    def get_condo_by_unit_number(self, unit_number: str) -> Optional[Condo]:
        """Récupère un condo par son numéro d'unité."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    SELECT unit_number, owner_name, square_feet, condo_type, 
                           status, purchase_date, monthly_fees_base
                    FROM condos WHERE unit_number = ?
                """, (unit_number,))
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_condo(row)
                return None
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche du condo {unit_number}: {e}")
            raise CondoRepositoryError(f"Impossible de récupérer le condo: {e}")
    
    def get_all_condos(self) -> List[Condo]:
        """Récupère tous les condos."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    SELECT unit_number, owner_name, square_feet, condo_type, 
                           status, purchase_date, monthly_fees_base
                    FROM condos ORDER BY unit_number
                """)
                
                rows = cursor.fetchall()
                return [self._row_to_condo(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des condos: {e}")
            raise CondoRepositoryError(f"Impossible de récupérer les condos: {e}")
    
    def get_condos_by_status(self, status: CondoStatus) -> List[Condo]:
        """Récupère tous les condos avec un statut spécifique."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    SELECT unit_number, owner_name, square_feet, condo_type, 
                           status, purchase_date, monthly_fees_base
                    FROM condos WHERE status = ? ORDER BY unit_number
                """, (status.value,))
                
                rows = cursor.fetchall()
                return [self._row_to_condo(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche par statut {status}: {e}")
            raise CondoRepositoryError(f"Impossible de filtrer par statut: {e}")
    
    def get_condos_by_type(self, condo_type: CondoType) -> List[Condo]:
        """Récupère tous les condos d'un type spécifique."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    SELECT unit_number, owner_name, square_feet, condo_type, 
                           status, purchase_date, monthly_fees_base
                    FROM condos WHERE condo_type = ? ORDER BY unit_number
                """, (condo_type.value,))
                
                rows = cursor.fetchall()
                return [self._row_to_condo(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche par type {condo_type}: {e}")
            raise CondoRepositoryError(f"Impossible de filtrer par type: {e}")
    
    def delete_condo(self, unit_number: str) -> bool:
        """Supprime un condo."""
        try:
            with self._db_lock:
                with self._get_connection() as conn:
                    cursor = conn.execute("DELETE FROM condos WHERE unit_number = ?", (unit_number,))
                    conn.commit()
                    
                    if cursor.rowcount > 0:
                        self.logger.info(f"Condo {unit_number} supprimé")
                        return True
                    return False
                    
        except Exception as e:
            self.logger.error(f"Erreur lors de la suppression du condo {unit_number}: {e}")
            raise CondoRepositoryError(f"Impossible de supprimer le condo: {e}")
    
    def count_condos(self) -> int:
        """Compte le nombre total de condos."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM condos")
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except Exception as e:
            self.logger.error(f"Erreur lors du comptage des condos: {e}")
            raise CondoRepositoryError(f"Impossible de compter les condos: {e}")
    
    def _row_to_condo(self, row) -> Condo:
        """Convertit une ligne SQLite en entité Condo."""
        unit_number = row['unit_number'] if hasattr(row, '__getitem__') else row[0]
        owner_name = row['owner_name'] if hasattr(row, '__getitem__') else row[1]
        square_feet = row['square_feet'] if hasattr(row, '__getitem__') else row[2]
        condo_type = row['condo_type'] if hasattr(row, '__getitem__') else row[3]
        status = row['status'] if hasattr(row, '__getitem__') else row[4]
        purchase_date = row['purchase_date'] if hasattr(row, '__getitem__') else row[5]
        monthly_fees_base = row['monthly_fees_base'] if hasattr(row, '__getitem__') else row[6]
        
        return Condo(
            unit_number=unit_number,
            owner_name=owner_name,
            square_feet=square_feet,
            condo_type=CondoType(condo_type),
            status=CondoStatus(status),
            purchase_date=datetime.fromisoformat(purchase_date) if purchase_date else None,
            monthly_fees_base=monthly_fees_base
        )
    
    # Méthodes additionnelles pour compléter l'interface
    def get_condos_by_owner(self, owner_name: str) -> List[Condo]:
        """Récupère tous les condos d'un propriétaire."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    SELECT unit_number, owner_name, square_feet, condo_type, 
                           status, purchase_date, monthly_fees_base
                    FROM condos WHERE LOWER(owner_name) = LOWER(?) ORDER BY unit_number
                """, (owner_name,))
                
                rows = cursor.fetchall()
                return [self._row_to_condo(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche par propriétaire {owner_name}: {e}")
            raise CondoRepositoryError(f"Impossible de filtrer par propriétaire: {e}")
    
    def get_condos_with_filters(self, filters: Dict[str, Any]) -> List[Condo]:
        """Récupère des condos selon des critères de filtrage."""
        try:
            where_clauses = []
            params = []
            
            if 'min_square_feet' in filters:
                where_clauses.append("square_feet >= ?")
                params.append(filters['min_square_feet'])
            
            if 'max_square_feet' in filters:
                where_clauses.append("square_feet <= ?")
                params.append(filters['max_square_feet'])
            
            if 'condo_type' in filters:
                where_clauses.append("condo_type = ?")
                params.append(filters['condo_type'])
            
            if 'status' in filters:
                where_clauses.append("status = ?")
                params.append(filters['status'])
            
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            with self._get_connection() as conn:
                cursor = conn.execute(f"""
                    SELECT unit_number, owner_name, square_feet, condo_type, 
                           status, purchase_date, monthly_fees_base
                    FROM condos WHERE {where_sql} ORDER BY unit_number
                """, params)
                
                rows = cursor.fetchall()
                return [self._row_to_condo(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Erreur lors du filtrage: {e}")
            raise CondoRepositoryError(f"Impossible de filtrer les condos: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Récupère des statistiques sur les condos."""
        try:
            with self._get_connection() as conn:
                # Statistiques générales
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total,
                        COALESCE(SUM(square_feet), 0) as total_square_feet,
                        COALESCE(AVG(square_feet), 0) as avg_square_feet
                    FROM condos
                """)
                general_stats = cursor.fetchone()
                
                # Statistiques par type
                cursor = conn.execute("""
                    SELECT condo_type, COUNT(*) as count
                    FROM condos 
                    GROUP BY condo_type
                """)
                type_stats = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Statistiques par statut
                cursor = conn.execute("""
                    SELECT status, COUNT(*) as count
                    FROM condos 
                    GROUP BY status
                """)
                status_stats = {row[0]: row[1] for row in cursor.fetchall()}
                
                return {
                    'total_condos': general_stats[0],
                    'total_square_feet': general_stats[1],
                    'average_square_feet': round(general_stats[2], 2),
                    'by_type': type_stats,
                    'by_status': status_stats
                }
                
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul des statistiques: {e}")
            raise CondoRepositoryError(f"Impossible de calculer les statistiques: {e}")


# Exemple d'utilisation
if __name__ == "__main__":
    import logging
    
    # Configuration basique du logging pour le test
    logging.basicConfig(level=logging.INFO)
    
    def demo_sqlite_adapter():
        # Créer l'adapter SQLite
        adapter = SQLiteAdapter()
        
        # Créer quelques condos de test
        condos = [
            Condo("A-101", "Jean Dupont", 850.0, CondoType.RESIDENTIAL),
            Condo("B-205", "Marie Tremblay", 950.0, CondoType.RESIDENTIAL),
            Condo("C-001", "Entreprise ABC", 200.0, CondoType.COMMERCIAL)
        ]
        
        # Sauvegarder les condos
        for condo in condos:
            adapter.save_condo(condo)
        
        # Récupérer et afficher les statistiques
        stats = adapter.get_statistics()
        logger.info(f"Statistiques: {stats}")
    
    # Exécuter la démonstration
    try:
        demo_sqlite_adapter()
    except Exception as e:
        logger.error(f"Erreur lors de la démonstration: {e}")
