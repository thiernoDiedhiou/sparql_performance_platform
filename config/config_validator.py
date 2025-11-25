"""
Module de validation de configuration au démarrage
Vérifie que toutes les configurations sont valides avant l'exécution
"""

import os
import sys
from typing import Dict, List, Tuple, Any
from pathlib import Path
import requests
from urllib.parse import urlparse
from utils.logging_config import get_logger
from utils.status_formatter import format_status


logger = get_logger("config_validator")


class ConfigurationError(Exception):
    """Exception levée pour les erreurs de configuration"""
    pass


class ConfigValidator:
    """Validateur de configuration pour la plateforme"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialise le validateur

        Args:
            config: Dictionnaire de configuration à valider
        """
        self.config = config
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_url(self, url: str, name: str, required: bool = True) -> bool:
        """
        Valide une URL

        Args:
            url: URL à valider
            name: Nom du paramètre (pour messages)
            required: Si True, l'URL est obligatoire

        Returns:
            True si valide
        """
        if not url:
            if required:
                self.errors.append(f"{name} est obligatoire")
                return False
            return True

        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                self.errors.append(f"{name} invalide: {url}")
                return False

            if result.scheme not in ['http', 'https']:
                self.errors.append(
                    f"{name} doit utiliser HTTP ou HTTPS: {url}"
                )
                return False

            logger.debug(f"URL valide: {name} = {url}")
            return True

        except Exception as e:
            self.errors.append(f"{name} invalide ({str(e)}): {url}")
            return False

    def test_endpoint_connectivity(
        self,
        endpoint_url: str,
        name: str,
        timeout: int = 5
    ) -> bool:
        """
        Teste la connectivité d'un endpoint

        Args:
            endpoint_url: URL de l'endpoint
            name: Nom de l'endpoint
            timeout: Timeout en secondes

        Returns:
            True si accessible
        """
        try:
            logger.debug(f"Test connectivité: {name}")

            # Requête de test simple
            test_query = "ASK { ?s ?p ?o }"
            params = {"query": test_query}

            response = requests.get(
                endpoint_url,
                params=params,
                timeout=timeout
            )

            if response.status_code == 200:
                logger.info(format_status("success", f"{name} accessible"))
                return True
            else:
                self.warnings.append(
                    f"{name} retourne HTTP {response.status_code}"
                )
                return False

        except requests.exceptions.Timeout:
            self.warnings.append(f"{name} timeout ({timeout}s)")
            return False

        except requests.exceptions.ConnectionError:
            self.warnings.append(f"{name} non accessible (connexion refusée)")
            return False

        except Exception as e:
            self.warnings.append(f"{name} erreur: {str(e)}")
            return False

    def validate_endpoints(self) -> bool:
        """
        Valide tous les endpoints SPARQL

        Returns:
            True si tous les endpoints sont valides
        """
        logger.info("Validation des endpoints SPARQL...")

        virtuoso_url = self.config.get("virtuoso_endpoint")
        fuseki_url = self.config.get("fuseki_endpoint")

        # Validation URLs
        virtuoso_valid = self.validate_url(
            virtuoso_url,
            "VIRTUOSO_ENDPOINT",
            required=True
        )

        fuseki_valid = self.validate_url(
            fuseki_url,
            "FUSEKI_ENDPOINT",
            required=True
        )

        if not (virtuoso_valid and fuseki_valid):
            return False

        # Test de connectivité (warnings seulement)
        connectivity_timeout = self.config.get("connectivity_timeout", 5)

        self.test_endpoint_connectivity(
            virtuoso_url,
            "Virtuoso",
            timeout=connectivity_timeout
        )

        self.test_endpoint_connectivity(
            fuseki_url,
            "Fuseki",
            timeout=connectivity_timeout
        )

        return True

    def validate_numeric_range(
        self,
        value: Any,
        name: str,
        min_val: float = None,
        max_val: float = None,
        required: bool = True
    ) -> bool:
        """
        Valide une valeur numérique dans une plage

        Args:
            value: Valeur à valider
            name: Nom du paramètre
            min_val: Valeur minimale acceptée
            max_val: Valeur maximale acceptée
            required: Si True, la valeur est obligatoire

        Returns:
            True si valide
        """
        if value is None:
            if required:
                self.errors.append(f"{name} est obligatoire")
                return False
            return True

        try:
            num_value = float(value)

            if min_val is not None and num_value < min_val:
                self.errors.append(
                    f"{name} doit être >= {min_val} (actuel: {num_value})"
                )
                return False

            if max_val is not None and num_value > max_val:
                self.warnings.append(
                    f"{name} est très élevé: {num_value} (max recommandé: {max_val})"
                )

            logger.debug(f"Valeur numérique valide: {name} = {num_value}")
            return True

        except (ValueError, TypeError):
            self.errors.append(f"{name} doit être un nombre: {value}")
            return False

    def validate_test_parameters(self) -> bool:
        """
        Valide les paramètres de test

        Returns:
            True si tous les paramètres sont valides
        """
        logger.info("Validation des paramètres de test...")

        valid = True

        # Nombre d'itérations
        valid &= self.validate_numeric_range(
            self.config.get("num_iterations"),
            "DEFAULT_NUM_ITERATIONS",
            min_val=1,
            max_val=100
        )

        # Itérations de warmup
        valid &= self.validate_numeric_range(
            self.config.get("warmup_iterations"),
            "DEFAULT_WARMUP_ITERATIONS",
            min_val=0,
            max_val=20
        )

        # Concurrence
        valid &= self.validate_numeric_range(
            self.config.get("concurrent_queries"),
            "DEFAULT_CONCURRENT_QUERIES",
            min_val=1,
            max_val=20
        )

        return valid

    def validate_timeouts(self) -> bool:
        """
        Valide les timeouts

        Returns:
            True si tous les timeouts sont valides
        """
        logger.info("Validation des timeouts...")

        valid = True

        valid &= self.validate_numeric_range(
            self.config.get("query_timeout"),
            "QUERY_TIMEOUT",
            min_val=5,
            max_val=600
        )

        valid &= self.validate_numeric_range(
            self.config.get("connectivity_timeout"),
            "CONNECTIVITY_TIMEOUT",
            min_val=1,
            max_val=30
        )

        valid &= self.validate_numeric_range(
            self.config.get("synchronization_timeout"),
            "SYNCHRONIZATION_TIMEOUT",
            min_val=10,
            max_val=3600
        )

        return valid

    def validate_directories(self) -> bool:
        """
        Valide et crée les répertoires nécessaires

        Returns:
            True si tous les répertoires sont valides
        """
        logger.info("Validation des répertoires...")

        directories = [
            ("log_dir", "logs"),
            ("results_dir", "results"),
            ("temp_dir", "temp")
        ]

        for config_key, default_value in directories:
            dir_path = self.config.get(config_key, default_value)

            try:
                path = Path(dir_path)
                path.mkdir(parents=True, exist_ok=True)

                # Vérifier les permissions d'écriture
                test_file = path / ".write_test"
                try:
                    test_file.touch()
                    test_file.unlink()
                    logger.debug(f"Répertoire accessible en écriture: {dir_path}")
                except Exception as e:
                    self.errors.append(
                        f"Répertoire {dir_path} non accessible en écriture: {str(e)}"
                    )
                    return False

            except Exception as e:
                self.errors.append(
                    f"Impossible de créer le répertoire {dir_path}: {str(e)}"
                )
                return False

        return True

    def validate_sync_parameters(self) -> bool:
        """
        Valide les paramètres de synchronisation

        Returns:
            True si valides
        """
        logger.info("Validation des paramètres de synchronisation...")

        valid = True

        valid &= self.validate_numeric_range(
            self.config.get("sync_chunk_size"),
            "SYNC_CHUNK_SIZE",
            min_val=1000,
            max_val=1000000
        )

        # Avertir si sync_chunk_size > 10000 (limite Virtuoso CONSTRUCT)
        sync_chunk_size = self.config.get("sync_chunk_size", 10000)
        if sync_chunk_size > 10000:
            self.warnings.append(
                f"SYNC_CHUNK_SIZE ({sync_chunk_size:,}) > 10,000. "
                f"Virtuoso a une limite CONSTRUCT de ~10,000 lignes. "
                f"Vous risquez une synchronisation partielle (< 100%). "
                f"Valeur recommandee : 10000."
            )

        valid &= self.validate_numeric_range(
            self.config.get("max_sync_triplets"),
            "MAX_SYNC_TRIPLETS",
            min_val=1000,
            max_val=100000000
        )

        return valid

    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """
        Valide toute la configuration

        Returns:
            Tuple (valid, errors, warnings)
        """
        logger.info("=" * 80)
        logger.info("VALIDATION DE LA CONFIGURATION")
        logger.info("=" * 80)

        # Réinitialiser les listes
        self.errors = []
        self.warnings = []

        # Exécuter toutes les validations
        self.validate_endpoints()
        self.validate_test_parameters()
        self.validate_timeouts()
        self.validate_directories()
        self.validate_sync_parameters()

        # Résultats
        is_valid = len(self.errors) == 0

        if is_valid:
            logger.info(format_status("success", "Configuration valid"))
        else:
            logger.error(format_status("error", f"Invalid configuration ({len(self.errors)} errors)"))

        if self.warnings:
            logger.warning(format_status("warning", f"{len(self.warnings)} warnings"))

        logger.info("=" * 80)

        return is_valid, self.errors, self.warnings

    def print_report(self):
        """Affiche un rapport de validation sur la console"""
        print("\n" + "=" * 80)
        print("RAPPORT DE VALIDATION DE CONFIGURATION")
        print("=" * 80)

        if self.errors:
            print(f"\n{format_status('error', f'ERRORS ({len(self.errors)})')}")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")

        if self.warnings:
            print(f"\n{format_status('warning', f'WARNINGS ({len(self.warnings)})')}")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")

        if not self.errors and not self.warnings:
            print(f"\n{format_status('success', 'No issues detected')}")

        print("\n" + "=" * 80 + "\n")


def validate_configuration(config: Dict[str, Any], strict: bool = False) -> bool:
    """
    Fonction utilitaire pour valider une configuration

    Args:
        config: Dictionnaire de configuration
        strict: Si True, les warnings sont traités comme des erreurs

    Returns:
        True si la configuration est valide

    Raises:
        ConfigurationError: Si la configuration est invalide
    """
    validator = ConfigValidator(config)
    is_valid, errors, warnings = validator.validate_all()

    if not is_valid or (strict and warnings):
        validator.print_report()

        if not is_valid:
            raise ConfigurationError(
                f"Configuration invalide: {len(errors)} erreurs"
            )

        if strict and warnings:
            raise ConfigurationError(
                f"Configuration a des warnings en mode strict: {len(warnings)}"
            )

    return True


if __name__ == "__main__":
    """Test de validation avec configuration d'exemple"""

    # Configuration de test
    test_config = {
        "virtuoso_endpoint": "http://localhost:8890/sparql",
        "fuseki_endpoint": "http://localhost:3030/dataset/query",
        "num_iterations": 5,
        "warmup_iterations": 2,
        "concurrent_queries": 1,
        "query_timeout": 60,
        "connectivity_timeout": 5,
        "synchronization_timeout": 300,
        "sync_chunk_size": 100000,
        "max_sync_triplets": 1000000,
        "log_dir": "logs",
        "results_dir": "results",
        "temp_dir": "temp"
    }

    try:
        validate_configuration(test_config, strict=False)
        print(format_status("success", "Test configuration valid"))
    except ConfigurationError as e:
        print(format_status("error", f"Configuration error: {e}"))
        sys.exit(1)
