"""
Chargeur de configuration depuis fichier .env
Support complet des variables d'environnement
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from utils.logging_config import get_logger


logger = get_logger("env_loader")


def str_to_bool(value: str) -> bool:
    """
    Convertit une chaîne en booléen

    Args:
        value: Chaîne à convertir

    Returns:
        Boolean
    """
    return value.lower() in ('true', 'yes', '1', 'on')


def load_env_file(env_file: str = ".env") -> Dict[str, str]:
    """
    Charge les variables depuis un fichier .env

    Args:
        env_file: Chemin vers le fichier .env

    Returns:
        Dictionnaire des variables d'environnement
    """
    env_path = Path(env_file)
    env_vars = {}

    if not env_path.exists():
        logger.warning(f"Fichier {env_file} introuvable, utilisation des valeurs par défaut")
        return env_vars

    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Ignorer les lignes vides et les commentaires
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Parser la ligne KEY=VALUE
                if '=' not in line:
                    logger.warning(f"Ligne {line_num} ignorée (format invalide): {line}")
                    continue

                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Enlever les quotes si présentes
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                env_vars[key] = value

        logger.info(f"✅ Fichier {env_file} chargé: {len(env_vars)} variables")
        return env_vars

    except Exception as e:
        logger.error(f"Erreur lors du chargement de {env_file}: {str(e)}")
        return {}


def get_env(key: str, default: Any = None, cast_type: type = str) -> Any:
    """
    Récupère une variable d'environnement avec conversion de type

    Args:
        key: Nom de la variable
        default: Valeur par défaut
        cast_type: Type de conversion (str, int, float, bool)

    Returns:
        Valeur convertie ou default
    """
    value = os.getenv(key)

    if value is None:
        return default

    try:
        if cast_type == bool:
            return str_to_bool(value)
        elif cast_type == int:
            return int(value)
        elif cast_type == float:
            return float(value)
        else:
            return str(value)

    except (ValueError, TypeError) as e:
        logger.warning(
            f"Impossible de convertir {key}='{value}' en {cast_type.__name__}, "
            f"utilisation de la valeur par défaut: {default}"
        )
        return default


def load_configuration() -> Dict[str, Any]:
    """
    Charge la configuration complète depuis .env et variables d'environnement

    Returns:
        Dictionnaire de configuration
    """
    # Charger le fichier .env dans l'environnement
    env_vars = load_env_file()
    for key, value in env_vars.items():
        os.environ.setdefault(key, value)

    # Construire la configuration
    config = {
        # Endpoints
        "virtuoso_endpoint": get_env(
            "VIRTUOSO_ENDPOINT",
            "http://localhost:8890/sparql"
        ),
        "fuseki_endpoint": get_env(
            "FUSEKI_ENDPOINT",
            "http://localhost:3030/dataset/query"
        ),
        "fuseki_update_endpoint": get_env(
            "FUSEKI_UPDATE_ENDPOINT",
            "http://localhost:3030/dataset/update"
        ),

        # Paramètres de test
        "num_iterations": get_env("DEFAULT_NUM_ITERATIONS", 5, int),
        "warmup_iterations": get_env("DEFAULT_WARMUP_ITERATIONS", 2, int),
        "concurrent_queries": get_env("DEFAULT_CONCURRENT_QUERIES", 1, int),
        "dataset_type": get_env("DEFAULT_DATASET_TYPE", "LUBM"),

        # Timeouts
        "query_timeout": get_env("QUERY_TIMEOUT", 60, int),
        "connectivity_timeout": get_env("CONNECTIVITY_TIMEOUT", 5, int),
        "synchronization_timeout": get_env("SYNCHRONIZATION_TIMEOUT", 300, int),

        # Synchronisation
        "sync_chunk_size": get_env("SYNC_CHUNK_SIZE", 10000, int),  # Optimisé pour limite Virtuoso CONSTRUCT
        "max_sync_triplets": get_env("MAX_SYNC_TRIPLETS", 1000000, int),
        "auto_sync_threshold": get_env("AUTO_SYNC_THRESHOLD", 0.05, float),
        "enable_auto_backup": get_env("ENABLE_AUTO_BACKUP", True, bool),

        # Logging
        "log_level": get_env("LOG_LEVEL", "INFO"),
        "console_log_level": get_env("CONSOLE_LOG_LEVEL", "INFO"),
        "log_dir": get_env("LOG_DIR", "logs"),
        "log_file": get_env("LOG_FILE", "sparql_platform.log"),
        "log_max_bytes": get_env("LOG_MAX_BYTES", 10485760, int),
        "log_backup_count": get_env("LOG_BACKUP_COUNT", 5, int),
        "log_colored_console": get_env("LOG_COLORED_CONSOLE", True, bool),

        # Métriques
        "large_dataset_threshold": get_env("LARGE_DATASET_THRESHOLD", 500000, int),
        "memory_warning_threshold": get_env("MEMORY_WARNING_THRESHOLD", 1024, int),
        "enable_system_metrics": get_env("ENABLE_SYSTEM_METRICS", True, bool),
        "metrics_collection_interval": get_env("METRICS_COLLECTION_INTERVAL", 1.0, float),

        # Export
        "results_dir": get_env("RESULTS_DIR", "results"),
        "temp_dir": get_env("TEMP_DIR", "temp"),
        "default_export_format": get_env("DEFAULT_EXPORT_FORMAT", "excel"),

        # Streamlit
        "streamlit_port": get_env("STREAMLIT_PORT", 8501, int),
        "streamlit_address": get_env("STREAMLIT_ADDRESS", "0.0.0.0"),
        "app_title": get_env("APP_TITLE", "Plateforme SPARQL Performance Testing"),
        "streamlit_debug": get_env("STREAMLIT_DEBUG", False, bool),

        # Sécurité
        "enable_authentication": get_env("ENABLE_AUTHENTICATION", False, bool),
        "admin_username": get_env("ADMIN_USERNAME", "admin"),
        "admin_password": get_env("ADMIN_PASSWORD", "changeme"),

        # Développement
        "dev_mode": get_env("DEV_MODE", False, bool),
        "auto_reload": get_env("AUTO_RELOAD", False, bool),
        "show_python_warnings": get_env("SHOW_PYTHON_WARNINGS", False, bool)
    }

    logger.info(f"✅ Configuration chargée: {len(config)} paramètres")

    return config


def print_configuration(config: Dict[str, Any], hide_sensitive: bool = True):
    """
    Affiche la configuration de manière formatée

    Args:
        config: Configuration à afficher
        hide_sensitive: Masquer les mots de passe
    """
    print("\n" + "=" * 80)
    print("CONFIGURATION ACTUELLE")
    print("=" * 80)

    sensitive_keys = ["password", "secret", "key", "token"]

    for key, value in sorted(config.items()):
        # Masquer les valeurs sensibles
        if hide_sensitive and any(s in key.lower() for s in sensitive_keys):
            value = "***MASKED***"

        print(f"  {key:30s} = {value}")

    print("=" * 80 + "\n")


if __name__ == "__main__":
    """Test du chargement de configuration"""

    # Charger la configuration
    config = load_configuration()

    # Afficher la configuration
    print_configuration(config)

    # Quelques tests
    print("\nTests de récupération:")
    print(f"  Virtuoso endpoint: {config['virtuoso_endpoint']}")
    print(f"  Nombre d'itérations: {config['num_iterations']}")
    print(f"  Logging activé: {config['log_level']}")
    print(f"  Mode dev: {config['dev_mode']}")
