#!/usr/bin/env python3
"""
Script de migration - Recréation automatique des données (inserts) de condos1.db

Ce script extrait et recrée automatiquement toutes les données de la base de données
condos1.db en générant les scripts SQL INSERT appropriés.

Usage:
    python scripts/recreate_inserts.py [options]
    
Options:
    --source-db PATH    : Chemin vers la base source (défaut: data/condos1.db)
    --output-dir PATH   : Répertoire de sortie (défaut: data/migrations/)
    --backup           : Créer une sauvegarde avant migration
    --execute          : Exécuter directement les migrations générées
    --exclude-tables   : Tables à exclure (séparées par virgules)
"""

import sqlite3
import sys
import os
import argparse
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

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

class DataRecreator:
    """Classe pour recréer automatiquement les données de base de données."""
    
    def __init__(self, source_db_path: str, output_dir: str):
        """
        Initialise le recréateur de données.
        
        Args:
            source_db_path: Chemin vers la base de données source
            output_dir: Répertoire de sortie pour les scripts de migration
        """
        self.source_db_path = Path(source_db_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.source_db_path.exists():
            raise FileNotFoundError(f"Base de données source introuvable: {source_db_path}")
    
    def analyze_table_data(self, exclude_tables: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyse toutes les données des tables.
        
        Args:
            exclude_tables: Liste des tables à exclure
            
        Returns:
            Dict contenant toutes les données des tables
        """
        if exclude_tables is None:
            exclude_tables = ['sqlite_sequence', 'schema_migrations']
        
        logger.info(f"Analyse des données de {self.source_db_path}")
        
        with sqlite3.connect(self.source_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Obtenir toutes les tables utilisateur
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            all_tables = [row[0] for row in cursor.fetchall()]
            
            # Filtrer les tables à exclure
            tables_to_process = [t for t in all_tables if t not in exclude_tables]
            
            table_data = {}
            
            for table_name in tables_to_process:
                # Obtenir les informations sur les colonnes
                cursor.execute(f"PRAGMA table_info({table_name})")
                column_info = cursor.fetchall()
                columns = [col[1] for col in column_info]  # col[1] est le nom de la colonne
                
                # Obtenir toutes les données
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Convertir en format utilisable
                table_rows = []
                for row in rows:
                    # Convertir Row en dict
                    row_dict = {col: row[col] for col in columns}
                    table_rows.append(row_dict)
                
                table_data[table_name] = {
                    'columns': columns,
                    'rows': table_rows,
                    'count': len(table_rows)
                }
                
                logger.info(f"Table {table_name}: {len(table_rows)} lignes extraites")
        
        data_summary = {
            'tables': table_data,
            'excluded_tables': exclude_tables,
            'extracted_at': datetime.now().isoformat(),
            'total_tables': len(table_data),
            'total_rows': sum(t['count'] for t in table_data.values())
        }
        
        logger.info(f"Données analysées: {len(table_data)} tables, {data_summary['total_rows']} lignes totales")
        return data_summary
    
    def generate_insert_migration(self, data_summary: Dict[str, Any]) -> str:
        """
        Génère le script SQL complet d'insertion des données.
        
        Args:
            data_summary: Données analysées de la base
            
        Returns:
            str: Script SQL complet
        """
        logger.info("Génération du script de migration des données")
        
        migration_sql = []
        
        # Header du script
        migration_sql.append("-- =====================================================")
        migration_sql.append("-- MIGRATION AUTOMATIQUE - DONNÉES DE BASE DE DONNÉES")
        migration_sql.append("-- =====================================================")
        migration_sql.append(f"-- Généré automatiquement le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        migration_sql.append(f"-- Source: {self.source_db_path}")
        migration_sql.append(f"-- Tables: {data_summary['total_tables']}")
        migration_sql.append(f"-- Lignes totales: {data_summary['total_rows']}")
        migration_sql.append("")
        
        # Configuration SQLite
        migration_sql.append("-- Configuration SQLite")
        migration_sql.append("PRAGMA foreign_keys = OFF;  -- Désactiver temporairement pour les inserts")
        migration_sql.append("BEGIN TRANSACTION;")
        migration_sql.append("")
        
        # Ordre optimal d'insertion (selon les dépendances)
        table_order = self._determine_insert_order(data_summary['tables'])
        
        # Générer les INSERT pour chaque table
        for table_name in table_order:
            if table_name in data_summary['tables']:
                table_info = data_summary['tables'][table_name]
                
                if table_info['count'] > 0:
                    migration_sql.append(f"-- ==================== DONNÉES TABLE: {table_name} ====================")
                    migration_sql.append(f"-- {table_info['count']} lignes à insérer")
                    migration_sql.append("")
                    
                    # Générer les INSERT statements
                    insert_statements = self._generate_table_inserts(table_name, table_info)
                    migration_sql.extend(insert_statements)
                    migration_sql.append("")
                else:
                    migration_sql.append(f"-- Table {table_name}: Aucune donnée à insérer")
                    migration_sql.append("")
        
        # Footer du script
        migration_sql.append("-- Réactiver les clés étrangères")
        migration_sql.append("PRAGMA foreign_keys = ON;")
        migration_sql.append("COMMIT;")
        migration_sql.append("")
        migration_sql.append("-- ==================== FIN MIGRATION DONNÉES ====================")
        
        return "\n".join(migration_sql)
    
    def _determine_insert_order(self, tables: Dict[str, Any]) -> List[str]:
        """
        Détermine l'ordre optimal d'insertion selon les dépendances.
        
        Args:
            tables: Dictionnaire des tables et leurs données
            
        Returns:
            Liste des noms de tables dans l'ordre d'insertion
        """
        # Ordre logique basé sur les dépendances
        priority_order = [
            'system_config',       # Configuration système en premier
            'feature_flags',       # Flags de fonctionnalités
            'users',              # Utilisateurs (indépendants)
            'projects',           # Projets (référencés par units)
            'units',              # Unités (dépend de projects)
            'financial_records'   # Records financiers (dépend d'autres tables)
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
    
    def _generate_table_inserts(self, table_name: str, table_info: Dict[str, Any]) -> List[str]:
        """
        Génère les statements INSERT pour une table.
        
        Args:
            table_name: Nom de la table
            table_info: Informations et données de la table
            
        Returns:
            Liste des statements INSERT
        """
        columns = table_info['columns']
        rows = table_info['rows']
        
        statements = []
        
        # Statement de base
        columns_str = ', '.join(columns)
        placeholders = ', '.join(['?' for _ in columns])
        
        statements.append(f"-- Insertion des données dans {table_name}")
        
        # Générer un INSERT pour chaque ligne
        for i, row in enumerate(rows, 1):
            values = []
            for col in columns:
                value = row.get(col)
                if value is None:
                    values.append('NULL')
                elif isinstance(value, str):
                    # Échapper les guillemets simples
                    escaped_value = value.replace("'", "''")
                    values.append(f"'{escaped_value}'")
                elif isinstance(value, (int, float)):
                    values.append(str(value))
                elif isinstance(value, bool):
                    values.append('1' if value else '0')
                else:
                    # Pour les autres types, convertir en string
                    escaped_value = str(value).replace("'", "''")
                    values.append(f"'{escaped_value}'")
            
            values_str = ', '.join(values)
            statements.append(f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});")
            
            # Ajouter un commentaire de progression tous les 50 inserts
            if i % 50 == 0:
                statements.append(f"-- {i}/{len(rows)} lignes insérées...")
        
        statements.append(f"-- {table_name}: {len(rows)} lignes insérées au total")
        
        return statements
    
    def save_insert_migration(self, migration_sql: str) -> Path:
        """
        Sauvegarde le script de migration des données.
        
        Args:
            migration_sql: Script SQL de migration
            
        Returns:
            Path: Chemin du fichier créé
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"002_recreate_inserts_{timestamp}.sql"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(migration_sql)
        
        logger.info(f"Script de migration des données sauvegardé: {filepath}")
        return filepath
    
    def create_data_summary_report(self, data_summary: Dict[str, Any]) -> Path:
        """
        Crée un rapport de résumé des données extraites.
        
        Args:
            data_summary: Résumé des données analysées
            
        Returns:
            Path: Chemin du rapport JSON créé
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data_summary_{timestamp}.json"
        filepath = self.output_dir / filename
        
        # Préparer le résumé pour JSON (sans les données complètes)
        summary_for_report = {
            'extraction_info': {
                'source_database': str(self.source_db_path),
                'extracted_at': data_summary['extracted_at'],
                'total_tables': data_summary['total_tables'],
                'total_rows': data_summary['total_rows'],
                'excluded_tables': data_summary['excluded_tables']
            },
            'tables_summary': {}
        }
        
        for table_name, table_info in data_summary['tables'].items():
            summary_for_report['tables_summary'][table_name] = {
                'column_count': len(table_info['columns']),
                'columns': table_info['columns'],
                'row_count': table_info['count']
            }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary_for_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Rapport de résumé des données sauvegardé: {filepath}")
        return filepath
    
    def execute_migration(self, migration_sql: str, target_db_path: str) -> bool:
        """
        Exécute la migration des données sur la base de données cible.
        
        Args:
            migration_sql: Script SQL de migration
            target_db_path: Chemin vers la base de données cible
            
        Returns:
            bool: True si succès, False sinon
        """
        logger.info(f"Exécution de la migration des données sur {target_db_path}")
        
        try:
            # Vérifier que la base cible existe
            if not os.path.exists(target_db_path):
                logger.error(f"Base de données cible introuvable: {target_db_path}")
                logger.error("Veuillez d'abord créer les schémas avec recreate_schemas.py")
                return False
            
            with sqlite3.connect(target_db_path) as conn:
                # Exécuter le script de migration
                conn.executescript(migration_sql)
                conn.commit()
            
            logger.info("Migration des données exécutée avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la migration des données: {e}")
            return False

def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(description='Recréation automatique des données de base de données')
    parser.add_argument('--source-db', default='data/condos1.db',
                       help='Chemin vers la base source (défaut: data/condos1.db)')
    parser.add_argument('--output-dir', default='data/migrations/',
                       help='Répertoire de sortie (défaut: data/migrations/)')
    parser.add_argument('--target-db', default='data/condos_recreated.db',
                       help='Chemin vers la base cible (défaut: data/condos_recreated.db)')
    parser.add_argument('--exclude-tables', 
                       help='Tables à exclure (séparées par virgules)')
    parser.add_argument('--backup', action='store_true',
                       help='Créer une sauvegarde avant migration')
    parser.add_argument('--execute', action='store_true',
                       help='Exécuter directement les migrations générées')
    parser.add_argument('--with-report', action='store_true',
                       help='Générer un rapport de résumé des données')
    
    args = parser.parse_args()
    
    try:
        logger.info("Démarrage de la recréation automatique des données")
        
        # Traiter les tables à exclure
        exclude_tables = ['sqlite_sequence', 'schema_migrations']
        if args.exclude_tables:
            additional_excludes = [t.strip() for t in args.exclude_tables.split(',')]
            exclude_tables.extend(additional_excludes)
        
        # Initialiser le recréateur
        recreator = DataRecreator(args.source_db, args.output_dir)
        
        # Analyser les données
        data_summary = recreator.analyze_table_data(exclude_tables)
        
        # Générer la migration
        migration_sql = recreator.generate_insert_migration(data_summary)
        
        # Sauvegarder le script
        migration_file = recreator.save_insert_migration(migration_sql)
        
        # Générer un rapport si demandé
        if args.with_report:
            recreator.create_data_summary_report(data_summary)
        
        # Exécuter si demandé
        if args.execute:
            success = recreator.execute_migration(migration_sql, args.target_db)
            if success:
                logger.info(f"Données recréées avec succès dans {args.target_db}")
            else:
                logger.error("Échec de la recréation des données")
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
