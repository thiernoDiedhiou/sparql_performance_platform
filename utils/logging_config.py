"""
Configuration professionnelle du système de logging
Supporte rotation de fichiers, niveaux multiples, et formatage personnalisé
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# Niveaux de logging disponibles
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}


class ColoredFormatter(logging.Formatter):
    """Formatter coloré pour la console"""

    # Codes couleur ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Vert
        'WARNING': '\033[33m',    # Jaune
        'ERROR': '\033[31m',      # Rouge
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record):
        """Formate le message avec couleur"""
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"

        return super().format(record)


def setup_logging(
    log_dir: str = "logs",
    log_file: str = "sparql_platform.log",
    log_level: str = "INFO",
    console_level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True,
    enable_file: bool = True,
    colored_console: bool = True
) -> logging.Logger:
    """
    Configure le système de logging professionnel

    Args:
        log_dir: Répertoire pour les fichiers de log
        log_file: Nom du fichier de log
        log_level: Niveau de log pour le fichier
        console_level: Niveau de log pour la console
        max_bytes: Taille maximale d'un fichier de log avant rotation
        backup_count: Nombre de fichiers de backup à conserver
        enable_console: Activer la sortie console
        enable_file: Activer la sortie fichier
        colored_console: Activer les couleurs dans la console

    Returns:
        Logger configuré
    """

    # Créer le répertoire de logs si nécessaire
    if enable_file:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

    # Créer le logger principal
    logger = logging.getLogger("sparql_platform")
    logger.setLevel(logging.DEBUG)  # Niveau le plus bas pour capturer tout

    # Éviter les doublons de handlers
    if logger.handlers:
        logger.handlers.clear()

    # Format détaillé pour le fichier
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Format simple pour la console
    if colored_console and sys.platform != 'win32':
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
    else:
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )

    # Handler pour le fichier avec rotation
    if enable_file:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(LOG_LEVELS.get(log_level.upper(), logging.INFO))
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Handler pour la console
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(LOG_LEVELS.get(console_level.upper(), logging.INFO))
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # Log de démarrage
    logger.info("=" * 80)
    logger.info(f"Système de logging initialisé - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Niveau fichier: {log_level}, Niveau console: {console_level}")
    if enable_file:
        logger.info(f"Fichier de log: {os.path.join(log_dir, log_file)}")
    logger.info("=" * 80)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Récupère un logger enfant du logger principal

    Args:
        name: Nom du logger (optionnel)

    Returns:
        Logger configuré
    """
    if name:
        return logging.getLogger(f"sparql_platform.{name}")
    return logging.getLogger("sparql_platform")


def log_exception(logger: logging.Logger, exception: Exception, message: str = ""):
    """
    Log une exception avec sa trace complète

    Args:
        logger: Logger à utiliser
        exception: Exception à logger
        message: Message contextuel optionnel
    """
    if message:
        logger.error(message)
    logger.exception(f"Exception: {type(exception).__name__}: {str(exception)}")


def log_performance(
    logger: logging.Logger,
    operation: str,
    duration: float,
    details: Optional[dict] = None
):
    """
    Log des métriques de performance

    Args:
        logger: Logger à utiliser
        operation: Nom de l'opération
        duration: Durée en secondes
        details: Détails supplémentaires (optionnel)
    """
    message = f"Performance | {operation} | {duration:.3f}s"

    if details:
        details_str = " | ".join([f"{k}={v}" for k, v in details.items()])
        message += f" | {details_str}"

    logger.info(message)


def log_query(
    logger: logging.Logger,
    query_name: str,
    engine: str,
    execution_time: float,
    success: bool,
    result_count: int = 0,
    error: str = ""
):
    """
    Log spécifique pour les requêtes SPARQL

    Args:
        logger: Logger à utiliser
        query_name: Nom de la requête
        engine: Nom du moteur SPARQL
        execution_time: Temps d'exécution
        success: Succès ou échec
        result_count: Nombre de résultats
        error: Message d'erreur si échec
    """
    status = "SUCCESS" if success else "FAILURE"
    message = f"Query | {engine} | {query_name} | {status} | {execution_time:.3f}s"

    if success:
        message += f" | Results: {result_count}"
        logger.info(message)
    else:
        message += f" | Error: {error}"
        logger.error(message)


def log_sync(
    logger: logging.Logger,
    operation: str,
    source_count: int,
    target_count: int,
    success: bool,
    duration: Optional[float] = None
):
    """
    Log spécifique pour les opérations de synchronisation

    Args:
        logger: Logger à utiliser
        operation: Type d'opération (sync, verify, etc.)
        source_count: Nombre de triplets source
        target_count: Nombre de triplets cible
        success: Succès ou échec
        duration: Durée de l'opération (optionnel)
    """
    status = "SUCCESS" if success else "FAILURE"
    message = f"Sync | {operation} | {status} | Source: {source_count:,} | Target: {target_count:,}"

    if duration:
        message += f" | Duration: {duration:.2f}s"

    if success:
        logger.info(message)
    else:
        logger.warning(message)


class ContextLogger:
    """Context manager pour logger automatiquement la durée d'une opération"""

    def __init__(self, logger: logging.Logger, operation: str, level: str = "INFO"):
        self.logger = logger
        self.operation = operation
        self.level = level
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.log(
            LOG_LEVELS.get(self.level.upper(), logging.INFO),
            f"Début: {self.operation}"
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()

        if exc_type is None:
            self.logger.log(
                LOG_LEVELS.get(self.level.upper(), logging.INFO),
                f"Fin: {self.operation} | Durée: {duration:.3f}s"
            )
        else:
            self.logger.error(
                f"Échec: {self.operation} | Durée: {duration:.3f}s | Erreur: {exc_val}"
            )

        return False  # Ne supprime pas l'exception


# Logger global par défaut (lazy initialization)
_default_logger: Optional[logging.Logger] = None


def get_default_logger() -> logging.Logger:
    """Récupère ou crée le logger par défaut"""
    global _default_logger

    if _default_logger is None:
        _default_logger = setup_logging()

    return _default_logger


# Exemples d'utilisation
if __name__ == "__main__":
    # Configuration du logger
    logger = setup_logging(
        log_level="DEBUG",
        console_level="INFO",
        colored_console=True
    )

    # Exemples de logs
    logger.debug("Message de debug détaillé")
    logger.info("Information générale")
    logger.warning("Avertissement important")
    logger.error("Erreur critique")

    # Log de performance
    log_performance(logger, "Test de requête", 1.234, {"engine": "Virtuoso", "results": 100})

    # Log de requête
    log_query(logger, "Simple SELECT", "Virtuoso", 0.5, True, 50)
    log_query(logger, "Complex JOIN", "Fuseki", 2.1, False, error="Timeout")

    # Log de synchronisation
    log_sync(logger, "Full sync", 10000, 10000, True, 45.6)

    # Context manager
    with ContextLogger(logger, "Opération complexe"):
        import time
        time.sleep(0.1)
        logger.info("Traitement en cours...")

    # Log d'exception
    try:
        raise ValueError("Erreur de test")
    except ValueError as e:
        log_exception(logger, e, "Erreur lors du test")
