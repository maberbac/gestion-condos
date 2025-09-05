#!/usr/bin/env python3
"""
Script de migration - Recréation automatique des schémas de condos1.db

Ce script recrée automatiquement toutes les tables et structures de la base de données
condos1.db en analysant la base existante et en générant les scripts SQL appropriés.

Usage:
    python scripts/recreate_schemas.py [options]
    
Options:
    --source-db PATH    : Chemin vers la base source (défaut: data/condos1.db)
    --output-dir PATH   : Répertoire de sortie (défaut: data/migrations/)
    --backup           : Créer une sauvegarde avant migration
    --execute          : Exécuter directement les migrations générées
"""

import sqlite3
import sys
import os
import argparse
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

def setup_logging():
    """Configure le système de logging pour les migrations."""
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # Handler console uniquement pour éviter les conflits de fichiers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Désactiver la propagation vers le logger parent
    logger.propagate = False
    
    return logger

logger = setup_logging()

class SchemaRecreator:
    """Classe pour recréer automatiquement les schémas de base de données."""
    
    def __init__(self, source_db_path: str, output_dir: str):
        """
        Initialise le recréateur de schémas.
        
        Args:
            source_db_path: Chemin vers la base de données source
            output_dir: Répertoire de sortie pour les scripts de migration
        """
        self.source_db_path = Path(source_db_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.source_db_path.exists():
            raise FileNotFoundError(f"Base de données source introuvable: {source_db_path}")
    
    def analyze_database_structure(self) -> Dict[str, Any]:
        """
        Analyse la structure complète de la base de données.
        
        Returns:
            Dict contenant toutes les informations structurelles
        """
        logger.info(f"Analyse de la structure de {self.source_db_path}")
        
        with sqlite3.connect(self.source_db_path) as conn:
            cursor = conn.cursor()
            
            # Obtenir toutes les tables (sauf système)
            cursor.execute("""
                SELECT name, sql FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Obtenir tous les index
            cursor.execute("""
                SELECT name, sql FROM sqlite_master 
                WHERE type='index' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            indexes = {row[0]: row[1] for row in cursor.fetchall() if row[1] is not None}
            
            # Obtenir tous les triggers
            cursor.execute("""
                SELECT name, sql FROM sqlite_master 
                WHERE type='trigger'
                ORDER BY name
            """)
            triggers = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Obtenir toutes les vues
            cursor.execute("""
                SELECT name, sql FROM sqlite_master 
                WHERE type='view'
                ORDER BY name
            """)
            views = {row[0]: row[1] for row in cursor.fetchall()}
        
        structure = {
            'tables': tables,
            'indexes': indexes,
            'triggers': triggers,
            'views': views,
            'analyzed_at': datetime.now().isoformat()
        }
        
        logger.info(f"Structure analysée: {len(tables)} tables, {len(indexes)} index, {len(triggers)} triggers, {len(views)} vues")
        return structure
    
    def generate_schema_migration(self, structure: Dict[str, Any]) -> str:
        """
        Génère le script SQL complet de migration des schémas.
        
        Args:
            structure: Structure de base de données analysée
            
        Returns:
            str: Script SQL complet
        """
        logger.info("Génération du script de migration des schémas")
        
        migration_sql = []
        
        # Header du script
        migration_sql.append("-- =====================================================")
        migration_sql.append("-- MIGRATION AUTOMATIQUE - SCHÉMAS DE BASE DE DONNÉES")
        migration_sql.append("-- =====================================================")
        migration_sql.append(f"-- Généré automatiquement le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        migration_sql.append(f"-- Source: {self.source_db_path}")
        migration_sql.append("")
        
        # Activer les clés étrangères
        migration_sql.append("-- Configuration SQLite")
        migration_sql.append("PRAGMA foreign_keys = ON;")
        migration_sql.append("")
        
        # Tables dans l'ordre de dépendance
        table_order = self._determine_table_order(structure['tables'])
        
        # Créer les tables
        migration_sql.append("-- ==================== CRÉATION DES TABLES ====================")
        for table_name in table_order:
            if table_name in structure['tables']:
                sql = structure['tables'][table_name]
                migration_sql.append(f"-- Table: {table_name}")
                migration_sql.append(sql + ";")
                migration_sql.append("")
        
        # Créer les index
        if structure['indexes']:
            migration_sql.append("-- ==================== CRÉATION DES INDEX ====================")
            for index_name, sql in structure['indexes'].items():
                migration_sql.append(f"-- Index: {index_name}")
                migration_sql.append(sql + ";")
                migration_sql.append("")
        
        # Créer les vues
        if structure['views']:
            migration_sql.append("-- ==================== CRÉATION DES VUES ====================")
            for view_name, sql in structure['views'].items():
                migration_sql.append(f"-- Vue: {view_name}")
                migration_sql.append(sql + ";")
                migration_sql.append("")
        
        # Créer les triggers
        if structure['triggers']:
            migration_sql.append("-- ==================== CRÉATION DES TRIGGERS ====================")
            for trigger_name, sql in structure['triggers'].items():
                migration_sql.append(f"-- Trigger: {trigger_name}")
                migration_sql.append(sql + ";")
                migration_sql.append("")
        
        migration_sql.append("-- ==================== FIN MIGRATION SCHÉMAS ====================")
        
        return "\n".join(migration_sql)
    
    def _determine_table_order(self, tables: Dict[str, str]) -> List[str]:
        """
        Détermine l'ordre optimal de création des tables selon les dépendances.
        
        Args:
            tables: Dictionnaire des tables et leurs SQL
            
        Returns:
            Liste des noms de tables dans l'ordre de création
        """
        # Ordre logique basé sur les dépendances connues
        priority_order = [
            'schema_migrations',    # Table système en premier
            'system_config',       # Configuration système
            'feature_flags',       # Flags de fonctionnalités
            'projects',           # Projets (référencés par units)
            'units',              # Unités (dépend de projects)
            'users',              # Utilisateurs
            'financial_records'   # Records financiers (dépend potentiellement d'autres tables)
        ]
        
        # Ajouter les tables connues dans l'ordre de priorité
        ordered_tables = []
        for table in priority_order:
            if table in tables:
                ordered_tables.append(table)
        
        # Ajouter les tables restantes
        for table in tables:
            if table not in ordered_tables:
                ordered_tables.append(table)
        
        return ordered_tables
    
    def save_schema_migration(self, migration_sql: str) -> Path:
        """
        Sauvegarde le script de migration des schémas.
        
        Args:
            migration_sql: Script SQL de migration
            
        Returns:
            Path: Chemin du fichier créé
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"001_recreate_schemas_{timestamp}.sql"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(migration_sql)
        
        logger.info(f"Script de migration des schémas sauvegardé: {filepath}")
        return filepath
    
    def create_backup(self, target_db_path: str) -> str:
        """
        Crée une sauvegarde de la base de données cible.
        
        Args:
            target_db_path: Chemin vers la base de données à sauvegarder
            
        Returns:
            str: Chemin du fichier de sauvegarde
        """
        if not os.path.exists(target_db_path):
            logger.info("Aucune base de données cible à sauvegarder")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{target_db_path}.backup_{timestamp}"
        
        shutil.copy2(target_db_path, backup_path)
        logger.info(f"Sauvegarde créée: {backup_path}")
        return backup_path
    
    def execute_migration(self, migration_sql: str, target_db_path: str) -> bool:
        """
        Exécute la migration des schémas sur la base de données cible.
        
        Args:
            migration_sql: Script SQL de migration
            target_db_path: Chemin vers la base de données cible
            
        Returns:
            bool: True si succès, False sinon
        """
        logger.info(f"Exécution de la migration sur {target_db_path}")
        
        try:
            # Créer le répertoire parent si nécessaire
            os.makedirs(os.path.dirname(target_db_path), exist_ok=True)
            
            with sqlite3.connect(target_db_path) as conn:
                # Exécuter le script de migration
                conn.executescript(migration_sql)
                conn.commit()
            
            logger.info("Migration des schémas exécutée avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la migration: {e}")
            return False

def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(description='Recréation automatique des schémas de base de données')
    parser.add_argument('--source-db', default='data/condos1.db',
                       help='Chemin vers la base source (défaut: data/condos1.db)')
    parser.add_argument('--output-dir', default='data/migrations/',
                       help='Répertoire de sortie (défaut: data/migrations/)')
    parser.add_argument('--target-db', default='data/condos_recreated.db',
                       help='Chemin vers la base cible (défaut: data/condos_recreated.db)')
    parser.add_argument('--backup', action='store_true',
                       help='Créer une sauvegarde avant migration')
    parser.add_argument('--execute', action='store_true',
                       help='Exécuter directement les migrations générées')
    
    args = parser.parse_args()
    
    try:
        logger.info("Démarrage de la recréation automatique des schémas")
        
        # Initialiser le recréateur
        recreator = SchemaRecreator(args.source_db, args.output_dir)
        
        # Analyser la structure
        structure = recreator.analyze_database_structure()
        
        # Générer la migration
        migration_sql = recreator.generate_schema_migration(structure)
        
        # Sauvegarder le script
        migration_file = recreator.save_schema_migration(migration_sql)
        
        # Exécuter si demandé
        if args.execute:
            if args.backup:
                recreator.create_backup(args.target_db)
            
            success = recreator.execute_migration(migration_sql, args.target_db)
            if success:
                logger.info(f"Schémas recréés avec succès dans {args.target_db}")
            else:
                logger.error("Échec de la recréation des schémas")
                return 1
        else:
            logger.info(f"Script de migration généré: {migration_file}")
            logger.info("Utilisez --execute pour appliquer la migration")
        
        return 0
        
    except Exception as e:
        logger.error(f"Erreur critique: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
