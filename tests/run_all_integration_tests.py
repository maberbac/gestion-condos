#!/usr/bin/env python3
"""
Runner simple pour tous les tests d'intégration
"""

import unittest
import sys
import os
import time

# Ajouter le répertoire racine au path pour imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Point d'entrée principal"""
    logger.info("Découverte des tests d'intégration...")
    
    # Découverte des tests depuis le répertoire integration
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'integration')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    test_count = suite.countTestCases()
    logger.info(f"Tests découverts: {test_count}")
    
    if test_count == 0:
        logger.error("ERREUR: Aucun test d'intégration trouvé dans tests/integration/")
        return 1
    
    logger.info("Exécution en cours...\n")
    
    # Exécution des tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    start_time = time.time()
    result = runner.run(suite)
    execution_time = time.time() - start_time
    
    # Statistiques et sommaire final
    total_tests = result.testsRun
    failed_count = len(result.failures) + len(result.errors)
    success_count = total_tests - failed_count
    all_passed = (failed_count == 0)
    
    # Résumé des échecs détaillé (si nécessaire)
    if failed_count > 0:
        logger.error(f"\nÉCHECS ({failed_count}):")
        for test, traceback in result.failures:
            logger.info(f"  - {test}")
        for test, traceback in result.errors:
            logger.info(f"  - {test}")
    
    # NOUVELLE approche: Créer un nouveau logger pour le sommaire
    # car les tests de logging peuvent avoir modifié l'état du logger principal
    import logging
    summary_logger = logging.getLogger("test_summary")
    
    # Configuration basique du nouveau logger
    if not summary_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        summary_logger.addHandler(handler)
        summary_logger.setLevel(logging.INFO)
    
    # Sommaire final avec formatage visuel
    summary_logger.info("=" * 60)
    summary_logger.info("SOMMAIRE FINAL - TESTS D'INTÉGRATION")
    summary_logger.info("=" * 60)
    
    status_text = "SUCCÈS" if all_passed else "ÉCHEC"
    
    summary_logger.info("")
    summary_logger.info(f"  Total: {total_tests} tests")
    summary_logger.info(f"  Succès: {success_count}")
    summary_logger.info(f"  Échecs: {failed_count}")
    summary_logger.info(f"  Temps: {execution_time:.3f}s")
    if total_tests > 0:
        success_rate = (success_count / total_tests) * 100
        summary_logger.info(f"  Taux: {success_rate:.1f}%")
    summary_logger.info("")
    
    if all_passed:
        summary_logger.info(f"RÉSULTAT: {status_text} - Tous les tests d'intégration passent")
    else:
        summary_logger.error(f"RÉSULTAT: {status_text} - {failed_count} test(s) en échec")
    
    summary_logger.info("=" * 60)
    
    # Mention finale très visible pour identification rapide
    if all_passed:
        summary_logger.info("STATUT FINAL: TESTS D'INTÉGRATION RÉUSSIS")
    else:
        summary_logger.error("STATUT FINAL: TESTS D'INTÉGRATION ÉCHOUÉS")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
