"""
Utilitaires pour la plateforme d'évaluation SPARQL
"""

from .helpers import (
    log_message,
    format_duration,
    format_memory_size,
    validate_endpoint_url,
    create_benchmark_summary,
    format_sync_status,
    get_sync_status_summary,
    validate_endpoint_accessibility
)

# Import du formateur de statuts professionnel
from .status_formatter import (
    format_status,
    format_connectivity_status,
    format_percentage,
    format_count,
    format_tab_name,
    get_tab_symbols,
    set_display_mode,
    success,
    error,
    warning,
    info
)

# Import conditionnel du gestionnaire de données
try:
    from .data_manager import (
        save_test_results,
        get_test_results,
        is_test_completed,
        initialize_session_state
    )
    DATA_MANAGER_AVAILABLE = True
except ImportError:
    DATA_MANAGER_AVAILABLE = False
    def save_test_results(*args, **kwargs):
        pass
    def get_test_results(*args, **kwargs):
        return None
    def is_test_completed(*args, **kwargs):
        return False
    def initialize_session_state(*args, **kwargs):
        pass

# Import conditionnel du synchroniseur
try:
    from .data_synchronizer import DataSynchronizer
    SYNC_AVAILABLE = True
except ImportError:
    SYNC_AVAILABLE = False
    class DataSynchronizer:
        def __init__(self, *args, **kwargs):
            raise ImportError("Module de synchronisation non disponible")

__all__ = [
    # Helpers
    'log_message',
    'format_duration',
    'format_memory_size',
    'validate_endpoint_url',
    'create_benchmark_summary',
    'format_sync_status',
    'get_sync_status_summary',
    'validate_endpoint_accessibility',
    # Status formatters (NEW - Professional design)
    'format_status',
    'format_connectivity_status',
    'format_percentage',
    'format_count',
    'format_tab_name',
    'get_tab_symbols',
    'set_display_mode',
    'success',
    'error',
    'warning',
    'info',
    # Data management
    'save_test_results',
    'get_test_results',
    'is_test_completed',
    'initialize_session_state',
    'DataSynchronizer',
    'DATA_MANAGER_AVAILABLE',
    'SYNC_AVAILABLE'
]