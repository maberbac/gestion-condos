#!/usr/bin/env python3
"""
Runner global pour tous les tests du projet.

Ce script exécute tous les types de tests (unitaires, intégration, acceptance)
et génère un rapport consolidé des résultats.

Usage:
    python tests/run_all_tests.py [options]
    
Options:
    -v, --verbose     : Mode verbeux avec détails des tests
    --with-coverage   : Générer un rapport de couverture
    --report          : Générer un rapport détaillé
    --json            : Générer un rapport JSON
    --fast            : Arrêter au premier échec (mode CI)
    --unit-only       : Exécuter seulement les tests unitaires
    --html            : Générer un rapport HTML de couverture
"""

import subprocess
import sys
import os
import time
import argparse
import json
from dataclasses import dataclass
from typing import List, Tuple

# Ajouter le répertoire racine au path pour imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)


@dataclass
class TestSuiteResults:
    """Résultats d'exécution d'une suite de tests"""
    name: str
    test_count: int = 0
    failures: int = 0
    errors: int = 0
    execution_time: float = 0.0
    success: bool = False


def run_test_suite(runner_script, runner_args=None):
    """Exécute une suite de tests et retourne les résultats."""
    if runner_args is None:
        runner_args = []
    
    try:
        start_time = time.time()
        
        # Exécuter le runner avec capture de sortie
        result = subprocess.run(
            [sys.executable, os.path.join("tests", runner_script)] + runner_args,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True,
            timeout=120  # Timeout de 2 minutes
        )
        
        execution_time = time.time() - start_time
        
        # Analyse de l'output pour extraire les statistiques
        full_output = result.stdout + result.stderr
        stderr = result.stderr
        
        output = full_output
        test_count = 0
        failures = 0
        errors = 0
        success = False
        
        # Extraire le nombre de tests exécutés
        for line in full_output.split('\n'):
            line = line.strip()
            if "Ran " in line and " tests in " in line:
                parts = line.split()
                try:
                    test_count = int(parts[1])
                except (ValueError, IndexError):
                    pass
                break
        
        # Logique de détection du succès basée PRIORITAIREMENT sur le code de retour
        # Car c'est le plus fiable
        if result.returncode == 0:
            # Code de retour 0 = succès, confirmer avec l'output
            has_ok = ("\nOK\n" in full_output or full_output.strip().endswith("OK") or 
                      "\nOK\n" in stderr or stderr.strip().endswith("OK"))
            
            if has_ok:
                success = True
                failures = 0
                errors = 0
            else:
                # Cas rare: code 0 mais pas de "OK" détecté
                # Faire confiance au code de retour (plus fiable)
                success = True
                failures = 0
                errors = 0
        else:
            # Code de retour != 0 = échec
            success = False
            
            # Rechercher patterns d'échec dans l'output pour détails
            has_failed = "FAILED (" in full_output
            if has_failed:
                # Extraire le nombre d'échecs et d'erreurs depuis FAILED (failures=X, errors=Y)
                for line in full_output.split('\n'):
                    if "FAILED (" in line:
                        try:
                            # Extraire failures
                            if "failures=" in line:
                                failures_part = line.split("failures=")[1].split(")")[0].split(",")[0]
                                failures = int(failures_part)
                            
                            # Extraire errors si présent
                            if "errors=" in line:
                                errors_part = line.split("errors=")[1].split(")")[0].split(",")[0]
                                errors = int(errors_part)
                        except (ValueError, IndexError):
                            # Si parsing échoue, assumer au moins 1 échec
                            failures = 1 if failures == 0 else failures
                        break
            else:
                # Échec détecté mais pas de détails, assumer 1 échec
                failures = 1
        
        return TestSuiteResults(
            name=os.path.basename(runner_script).replace('.py', ''),
            test_count=test_count,
            failures=failures,
            errors=errors,
            execution_time=execution_time,
            success=success
        ), output
        
    except Exception as e:
        return TestSuiteResults(
            name=os.path.basename(runner_script).replace('.py', ''),
            success=False
        ), f"Erreur d'exécution: {e}"


def generate_consolidated_report(results_list, total_time, with_coverage=False):
    """Génère un rapport consolidé de tous les tests"""
    logger.info("=" * 80)
    logger.info("RAPPORT CONSOLIDÉ - PIPELINE DE TESTS COMPLET")
    logger.info("=" * 80)
    
    total_tests = sum(r.test_count for r in results_list)
    total_failures = sum(r.failures for r in results_list)
    total_errors = sum(r.errors for r in results_list)
    all_success = all(r.success for r in results_list)
    
    logger.info(f"\nRésumé Global:")
    logger.info(f"  Tests totaux exécutés: {total_tests}")
    logger.info(f"  Succès: {total_tests - total_failures - total_errors}")
    logger.info(f"  Échecs: {total_failures}")
    logger.info(f"  Erreurs: {total_errors}")
    logger.info(f"  Temps total: {total_time:.2f}s")
    
    logger.info(f"\nDétail par Type:")
    for result in results_list:
        status = "OK SUCCÈS" if result.success else " ÉCHEC"
        logger.info(f"  {result.name:<25} : {result.test_count:3d} tests | {result.execution_time:6.2f}s | {status}")
    
    # Mention finale de statut
    logger.info("")
    if all_success:
        logger.info("=" * 80)
        logger.info("STATUT FINAL: PIPELINE RÉUSSI - TOUS LES TESTS PASSENT")
        logger.info("=" * 80)
    else:
        logger.error("=" * 80)
        logger.error("STATUT FINAL: PIPELINE ÉCHOUÉ - DES TESTS ONT ÉCHOUÉ")
        logger.error("=" * 80)
    
    return all_success


def generate_json_report(results_list, total_time, output_file="reports/test_results.json"):
    """Génère un rapport JSON détaillé"""
    # Créer le répertoire reports s'il n'existe pas
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_execution_time": total_time,
        "global_success": all(r.success for r in results_list),
        "summary": {
            "total_tests": sum(r.test_count for r in results_list),
            "total_failures": sum(r.failures for r in results_list),
            "total_errors": sum(r.errors for r in results_list)
        },
        "suites": [
            {
                "name": r.name,
                "test_count": r.test_count,
                "failures": r.failures,
                "errors": r.errors,
                "execution_time": r.execution_time,
                "success": r.success
            }
            for r in results_list
        ]
    }
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Rapport JSON généré: {output_file}")
    return output_file


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description='Runner global pour tous les tests')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Mode verbeux avec détails des tests')
    parser.add_argument('--with-coverage', action='store_true',
                       help='Générer un rapport de couverture')
    parser.add_argument('--report', action='store_true',
                       help='Générer un rapport détaillé')
    parser.add_argument('--json', action='store_true',
                       help='Générer un rapport JSON')
    parser.add_argument('--fast', action='store_true',
                       help='Arrêter au premier échec (mode CI)')
    parser.add_argument('--unit-only', action='store_true',
                       help='Exécuter seulement les tests unitaires')
    parser.add_argument('--html', action='store_true',
                       help='Générer un rapport HTML de couverture')
    
    args = parser.parse_args()
    
    logger.info("Démarrage du pipeline de tests complet")
    logger.info("=" * 60)
    
    total_start_time = time.time()
    results = []
    
    # Liste des runners à exécuter
    runners = [
        ('run_all_unit_tests.py', 'Tests Unitaires'),
        ('run_all_integration_tests.py', 'Tests d\'Intégration'),
        ('run_all_acceptance_tests.py', 'Tests d\'Acceptance Modernes')
    ]
    
    if args.unit_only:
        runners = [runners[0]]  # Seulement les tests unitaires
    
    # Exécution séquentielle des suites de tests
    for runner_file, description in runners:
        logger.info(f"\nExécution: {description}")
        logger.info("-" * 40)
        
        runner_args = []
        if not args.verbose:
            runner_args.append('--no-summary')
        
        result, output = run_test_suite(runner_file, runner_args)
        results.append(result)
        
        if args.verbose:
            logger.info(output)
        else:
            # Affichage condensé
            status = "OK" if result.success else ""
            logger.info(f"{status} {description}: {result.test_count} tests en {result.execution_time:.1f}s")
        
        # Arrêt rapide en cas d'échec (mode CI)
        if args.fast and not result.success:
            logger.info(f"\nArrêt rapide: {description} a échoué")
            break
    
    total_execution_time = time.time() - total_start_time
    
    # Génération des rapports
    if args.report or not args.fast:
        logger.info("\n")
        success = generate_consolidated_report(results, total_execution_time, args.with_coverage)
    else:
        success = all(r.success for r in results)
    
    if args.json:
        generate_json_report(results, total_execution_time)
    
    # Couverture de code si demandée
    if args.with_coverage:
        logger.info(f"\nGénération du rapport de couverture...")
        try:
            # Exécuter tous les tests avec coverage
            subprocess.run([
                'coverage', 'run', '--source=src', 
                os.path.join(os.path.dirname(__file__), 'run_all_tests.py'),
                '--unit-only'
            ], check=True)
            
            subprocess.run(['coverage', 'report', '-m'], check=True)
            
            if args.html:
                subprocess.run(['coverage', 'html'], check=True)
                logger.info("Rapport HTML de couverture généré dans htmlcov/")
                
        except subprocess.CalledProcessError:
            logger.error("ATTENTION: Erreur lors de la génération du rapport de couverture")
    
    # Code de sortie
    return 0 if success else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
