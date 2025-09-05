"""
File Adapter - Implémentation concrète pour la lecture de fichiers.

Cet adapter démontre l'implémentation du concept technique obligatoire

Il implémente les ports FileHandlerPort et CondoRepositoryPort pour
fournir une persistance basée sur fichiers JSON et CSV.
"""

from src.infrastructure.logger_manager import get_logger
logger = get_logger(__name__)

import json
import csv
import asyncio
import aiofiles
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from src.domain.entities.condo import Condo, CondoStatus, CondoType
from src.ports.condo_repository import (
    CondoRepositoryPort,
    FileHandlerPort,
    CondoRepositoryError,
    FileReadError
)

class FileAdapter(CondoRepositoryPort, FileHandlerPort):
    """
    Adapter pour la persistance et lecture de fichiers.


    Cet adapter démontre :
    - Lecture asynchrone de fichiers JSON et CSV
    - Gestion robuste des erreurs de fichiers
    - Validation des formats de données
    - Sérialisation/désérialisation d'entités métier
    - Opérations de persistance des données

    - Implémente les ports définis par le domaine métier
    - Isole la logique de fichiers du core business
    - Permet tests unitaires avec mocks facilement
    """

    def __init__(self, data_directory: str = "data",
                 condos_file: str = "condos.json"):
        """
        Initialise l'adapter avec les chemins de fichiers.

        Args:
            data_directory: Répertoire principal des données
            condos_file: Nom du fichier principal des condos
        """
        self.data_dir = Path(data_directory)
        self.condos_file_path = self.data_dir / condos_file

        # Créer le répertoire s'il n'existe pas
        self.data_dir.mkdir(exist_ok=True)

        self.logger = logging.getLogger(__name__)

        # Cache en mémoire pour améliorer les performances
        self._condos_cache: Optional[List[Condo]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_validity_seconds = 60  # Cache valide 1 minute

    # ==================== Implémentation FileHandlerPort ====================

    async def read_json_file(self, filepath: str) -> Dict[str, Any]:
        """
        Lecture asynchrone de fichier JSON.

        - Lecture asynchrone non-bloquante
        - Gestion spécifique des erreurs JSON
        - Validation du format
        - Logging des opérations
        """
        try:
            file_path = Path(filepath)

            # Vérifier l'existence du fichier
            if not file_path.exists():
                raise FileReadError(f"Fichier non trouvé: {filepath}")

            # Lecture asynchrone du fichier
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                content = await file.read()

            # Parsing JSON avec gestion d'erreurs spécifique
            try:
                data = json.loads(content)
                self.logger.info(f"Fichier JSON lu avec succès: {filepath}")
                return data

            except json.JSONDecodeError as e:
                self.logger.error(f"Erreur de format JSON dans {filepath}: {e}")
                raise FileReadError(f"Format JSON invalide: {e}")

        except FileNotFoundError:
            raise FileReadError(f"Fichier non trouvé: {filepath}")
        except PermissionError:
            raise FileReadError(f"Permission refusée pour: {filepath}")
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors de la lecture de {filepath}: {e}")
            raise FileReadError(f"Erreur de lecture: {e}")

    async def write_json_file(self, filepath: str, data: Dict[str, Any]) -> bool:
        """

        """
        try:
            file_path = Path(filepath)

            # Créer le répertoire parent si nécessaire
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Sérialisation JSON avec formatage lisible
            json_content = json.dumps(data, indent=2, ensure_ascii=False, default=str)

            # Écriture asynchrone
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
                await file.write(json_content)

            self.logger.info(f"Fichier JSON écrit avec succès: {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Erreur lors de l'écriture de {filepath}: {e}")
            return False

    async def read_csv_file(self, filepath: str) -> List[Dict[str, str]]:
        """
        Lecture asynchrone de fichier CSV.
        """
        try:
            file_path = Path(filepath)

            if not file_path.exists():
                raise FileReadError(f"Fichier CSV non trouvé: {filepath}")

            # Lecture du contenu complet
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                content = await file.read()

            # Parsing CSV
            reader = csv.DictReader(content.splitlines())
            data = list(reader)

            self.logger.info(f"Fichier CSV lu avec succès: {filepath} ({len(data)} enregistrements)")
            return data

        except Exception as e:
            self.logger.error(f"Erreur lors de la lecture CSV {filepath}: {e}")
            raise FileReadError(f"Erreur de lecture CSV: {e}")

    async def write_csv_file(self, filepath: str, data: List[Dict[str, str]],
                           fieldnames: List[str]) -> bool:
        """

        """
        try:
            file_path = Path(filepath)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Création du contenu CSV en mémoire
            import io
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
            csv_content = output.getvalue()

            # Écriture asynchrone
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
                await file.write(csv_content)

            self.logger.info(f"Fichier CSV écrit avec succès: {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Erreur lors de l'écriture CSV {filepath}: {e}")
            return False

    # ==================== Implémentation CondoRepositoryPort ====================

    async def _load_condos_from_file(self) -> List[Condo]:
        """
        Charge tous les condos depuis le fichier principal.
        Utilise un cache pour optimiser les performances.
        """
        # Vérifier la validité du cache
        if (self._condos_cache is not None and
            self._cache_timestamp is not None and
            (datetime.now() - self._cache_timestamp).seconds < self._cache_validity_seconds):
            return self._condos_cache

        try:
            # Si le fichier n'existe pas, créer une structure vide
            if not self.condos_file_path.exists():
                await self._create_empty_condos_file()
                return []

            # Charger les données depuis le fichier
            data = await self.read_json_file(str(self.condos_file_path))

            # Convertir les dictionnaires en entités Condo
            condos = []
            for condo_data in data.get('condos', []):
                try:
                    condo = Condo.from_dict(condo_data)
                    condos.append(condo)
                except Exception as e:
                    self.logger.warning(f"Condo invalide ignoré: {condo_data}, erreur: {e}")

            # Mettre à jour le cache
            self._condos_cache = condos
            self._cache_timestamp = datetime.now()

            self.logger.info(f"{len(condos)} condos chargés depuis {self.condos_file_path}")
            return condos

        except FileReadError:
            # Si le fichier est corrompu, créer un fichier vide
            self.logger.warning("Fichier condos corrompu, création d'un nouveau fichier")
            await self._create_empty_condos_file()
            return []

    async def _save_condos_to_file(self, condos: List[Condo]) -> bool:
        """
        Sauvegarde tous les condos dans le fichier principal.
        """
        try:
            # Convertir les entités en dictionnaires
            condos_data = [condo.to_dict() for condo in condos]

            # Structure du fichier avec métadonnées
            file_data = {
                'metadata': {
                    'version': '1.0',
                    'last_updated': datetime.now().isoformat(),
                    'total_condos': len(condos)
                },
                'condos': condos_data
            }

            # Sauvegarder dans le fichier
            success = await self.write_json_file(str(self.condos_file_path), file_data)

            if success:
                # Mettre à jour le cache
                self._condos_cache = condos.copy()
                self._cache_timestamp = datetime.now()
                self.logger.info(f"{len(condos)} condos sauvegardés dans {self.condos_file_path}")

            return success

        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde des condos: {e}")
            return False

    async def _create_empty_condos_file(self) -> None:
        """Crée un fichier condos vide avec la structure de base."""
        empty_data = {
            'metadata': {
                'version': '1.0',
                'created': datetime.now().isoformat(),
                'total_condos': 0
            },
            'condos': []
        }
        await self.write_json_file(str(self.condos_file_path), empty_data)

    async def save_condo(self, condo: Condo) -> bool:
        """
        Sauvegarde ou met à jour un condo.
        """
        try:
            condos = await self._load_condos_from_file()

            # Chercher si le condo existe déjà
            existing_index = None
            for i, existing_condo in enumerate(condos):
                if existing_condo.unit_number == condo.unit_number:
                    existing_index = i
                    break

            # Mettre à jour ou ajouter
            if existing_index is not None:
                condos[existing_index] = condo
                self.logger.info(f"Condo {condo.unit_number} mis à jour")
            else:
                condos.append(condo)
                self.logger.info(f"Nouveau condo {condo.unit_number} ajouté")

            return await self._save_condos_to_file(condos)

        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde du condo {condo.unit_number}: {e}")
            raise CondoRepositoryError(f"Impossible de sauvegarder le condo: {e}")

    async def get_condo_by_unit_number(self, unit_number: str) -> Optional[Condo]:
        """Récupère un condo par son numéro d'unité."""
        condos = await self._load_condos_from_file()

        for condo in condos:
            if condo.unit_number == unit_number:
                return condo

        return None

    async def get_all_condos(self) -> List[Condo]:
        """Récupère tous les condos."""
        return await self._load_condos_from_file()

    async def get_condos_by_owner(self, owner_name: str) -> List[Condo]:
        """Récupère tous les condos d'un propriétaire."""
        condos = await self._load_condos_from_file()
        return [condo for condo in condos if condo.owner_name.lower() == owner_name.lower()]

    async def get_condos_by_status(self, status: CondoStatus) -> List[Condo]:
        """Récupère tous les condos avec un statut spécifique."""
        condos = await self._load_condos_from_file()
        return [condo for condo in condos if condo.status == status]

    async def get_condos_by_type(self, condo_type: CondoType) -> List[Condo]:
        """Récupère tous les condos d'un type spécifique."""
        condos = await self._load_condos_from_file()
        return [condo for condo in condos if condo.condo_type == condo_type]

    async def delete_condo(self, unit_number: str) -> bool:
        """Supprime un condo."""
        condos = await self._load_condos_from_file()

        initial_count = len(condos)
        condos = [condo for condo in condos if condo.unit_number != unit_number]

        if len(condos) < initial_count:
            await self._save_condos_to_file(condos)
            self.logger.info(f"Condo {unit_number} supprimé")
            return True

        return False

    async def get_condos_with_filters(self, filters: Dict[str, Any]) -> List[Condo]:
        """Récupère des condos selon des critères de filtrage."""
        condos = await self._load_condos_from_file()

        filtered_condos = condos

        if 'min_square_feet' in filters:
            filtered_condos = [c for c in filtered_condos if c.square_feet >= filters['min_square_feet']]

        if 'max_square_feet' in filters:
            filtered_condos = [c for c in filtered_condos if c.square_feet <= filters['max_square_feet']]

        if 'max_monthly_fees' in filters:
            filtered_condos = [c for c in filtered_condos if c.calculate_monthly_fees() <= filters['max_monthly_fees']]

        if 'condo_type' in filters:
            filtered_condos = [c for c in filtered_condos if c.condo_type.value == filters['condo_type']]

        return filtered_condos

    async def count_condos(self) -> int:
        """Compte le nombre total de condos."""
        condos = await self._load_condos_from_file()
        return len(condos)

    async def get_statistics(self) -> Dict[str, Any]:
        """Récupère des statistiques sur les condos."""
        condos = await self._load_condos_from_file()

        stats = {
            'total_condos': len(condos),
            'by_type': {},
            'by_status': {},
            'total_square_feet': sum(condo.square_feet for condo in condos),
            'total_monthly_fees': sum(condo.calculate_monthly_fees() for condo in condos),
        }

        # Statistiques par type
        for condo_type in CondoType:
            count = sum(1 for condo in condos if condo.condo_type == condo_type)
            stats['by_type'][condo_type.value] = count

        # Statistiques par statut
        for status in CondoStatus:
            count = sum(1 for condo in condos if condo.status == status)
            stats['by_status'][status.value] = count

        return stats

# Exemple d'utilisation de l'adapter
if __name__ == "__main__":
    async def demo_file_adapter():
        # Créer l'adapter
        adapter = FileAdapter()

        # Créer quelques condos de test
        condos = [
            Condo("A-101", "Jean Dupont", 850.0, CondoType.RESIDENTIAL),
            Condo("B-205", "Marie Tremblay", 950.0, CondoType.RESIDENTIAL),
            Condo("C-001", "Entreprise ABC", 200.0, CondoType.COMMERCIAL)
        ]

        # Sauvegarder les condos
        for condo in condos:
            await adapter.save_condo(condo)

        # Récupérer et afficher les statistiques
        stats = await adapter.get_statistics()
        logger.info(f"Statistiques: {stats}")

        large_condos = await adapter.get_condos_with_filters({'min_square_feet': 900})
        logger.info(f"Condos de plus de 900 sq ft: {[c.unit_number for c in large_condos]}")

    asyncio.run(demo_file_adapter())
