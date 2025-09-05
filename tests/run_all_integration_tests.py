#!/usr/bin/env python3
"""
Runner simple pour tous les tests d'intégration
"""

import unittest
import sys
import os
import time
import logging

# Ajouter le répertoire racine au path pour imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_test_logger():
    """Configure un logger spécial pour les tests pour éviter les conflits de fichiers"""
    # Créer un logger unique pour les tests
    test_logger = logging.getLogger("test_integration_runner")
    test_logger.setLevel(logging.INFO)
    
    # Supprimer tous les handlers existants pour éviter les conflits
    for handler in test_logger.handlers[:]:
        test_logger.removeHandler(handler)
    
    # Ajouter seulement un handler console
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(formatter)
    test_logger.addHandler(console_handler)
    
    # Empêcher la propagation vers le logger racine
    test_logger.propagate = False
    
    return test_logger

def main():
    """Point d'entrée principal"""
    logger = setup_test_logger()
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
    
    # Sommaire final avec formatage visuel
    logger.info("=" * 60)
    logger.info("SOMMAIRE FINAL - TESTS D'INTÉGRATION")
    logger.info("=" * 60)
    
    status_text = "SUCCÈS" if all_passed else "ÉCHEC"
    
    logger.info("")
    logger.info(f"  Total: {total_tests} tests")
    logger.info(f"  Succès: {success_count}")
    logger.info(f"  Échecs: {failed_count}")
    logger.info(f"  Temps: {execution_time:.3f}s")
    if total_tests > 0:
        success_rate = (success_count / total_tests) * 100
        logger.info(f"  Taux: {success_rate:.1f}%")
    logger.info("")
    
    if all_passed:
        logger.info(f"RÉSULTAT: {status_text} - Tous les tests d'intégration passent")
    else:
        logger.error(f"RÉSULTAT: {status_text} - {failed_count} test(s) en échec")
    
    logger.info("=" * 60)
    
    # Mention finale très visible pour identification rapide
    if all_passed:
        logger.info("STATUT FINAL: TESTS D'INTÉGRATION RÉUSSIS")
    else:
        logger.error("STATUT FINAL: TESTS D'INTÉGRATION ÉCHOUÉS")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
