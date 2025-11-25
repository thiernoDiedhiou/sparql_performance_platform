"""
Configuration globale de l'application
"""

import os
import streamlit as st
from config.env_loader import get_env, load_env_file

# Charger le fichier .env au démarrage
load_env_file()

# ============================================================================
# INFORMATIONS SUR L'APPLICATION
# ============================================================================

APP_VERSION = "3.2.2"
APP_VERSION_NAME = "Professional"
APP_VERSION_FULL = f"v{APP_VERSION} {APP_VERSION_NAME}"
APP_NAME = "SPARQL Performance Platform"
APP_DESCRIPTION = "Plateforme professionnelle de benchmarking SPARQL"
APP_AUTHOR = "Mémoire de Master 2 - Informatique - Génie Logiciel"
APP_GITHUB = "https://github.com/thiernoDiedhiou/sparql_performance_platform"

# Configuration par défaut des endpoints
DEFAULT_VIRTUOSO_ENDPOINT = "http://localhost:8890/sparql"
DEFAULT_FUSEKI_ENDPOINT = "http://localhost:3030/dataset/query"

# Configuration par défaut des tests
DEFAULT_NUM_ITERATIONS = 5
DEFAULT_WARMUP_ITERATIONS = 2
DEFAULT_CONCURRENT_QUERIES = 1

# Jeux de données disponibles
AVAILABLE_DATASETS = ["LUBM", "DBpedia", "BSBM", "YAGO", "Personnalisé"]

# Types de requêtes disponibles
QUERY_TYPES = {
    "run_basic_queries": {"label": "Requêtes simples (pattern matching)", "default": True},
    "run_join_queries": {"label": "Requêtes de jointure", "default": True},
    "run_aggregation_queries": {"label": "Requêtes d'agrégation", "default": True},
    "run_filter_queries": {"label": "Requêtes avec filtres", "default": True},
    "run_optional_queries": {"label": "Requêtes avec OPTIONAL/UNION/MINUS", "default": True},
    "run_subqueries": {"label": "Requêtes avec sous-requêtes", "default": True}
}

# Configuration de timeout pour les requêtes
QUERY_TIMEOUT = 60  # secondes

# Configuration de timeout pour les tests de connectivité
CONNECTIVITY_TIMEOUT = 5  # secondes

# ============================================================================
# CONFIGURATION POUR SÉCURITÉ ET VALIDATION
# ============================================================================

# Validation de sécurité des requêtes
SECURITY_MAX_QUERY_LENGTH = 50000  # 50KB maximum par requête
SECURITY_MAX_NESTING_LEVEL = 10     # Maximum 10 niveaux d'imbrication

# ============================================================================
# CONFIGURATION POUR MÉTRIQUES SYSTÈME
# ============================================================================

# Intervalle de collecte CPU (secondes)
METRICS_CPU_INTERVAL = 0.1

# Taille maximale de l'historique des métriques (évite débordement mémoire)
METRICS_MAX_HISTORY_SIZE = 10000

# Intervalle de monitoring en temps réel (secondes)
METRICS_MONITORING_INTERVAL = 0.5

# ============================================================================
# CONFIGURATION POUR L'INTERFACE UTILISATEUR
# ============================================================================

# Options d'affichage des résultats
UI_MAX_ROWS_OPTIONS = [50, 100, 200, 500, "Toutes"]
UI_DEFAULT_MAX_ROWS = 50
UI_DEFAULT_PAGE_SIZE = 100

# Hauteur des graphiques (pixels)
UI_CHART_HEIGHT = 400
UI_CHART_HEIGHT_LARGE = 600

# Cache Streamlit (secondes)
UI_CACHE_TTL = 600  # 10 minutes

# Nombre maximum de requêtes affichées dans certains graphiques
UI_MAX_QUERIES_DISPLAY = 12

# Top N pour performances extrêmes
UI_TOP_N_EXTREME = 5

def configure_page():
    """Configure les paramètres de la page Streamlit"""
    st.set_page_config(
        page_title="SPARQL Performance Evaluation Platform",
        page_icon=":bar_chart:",  # Streamlit built-in icon (professional)
        layout="wide"
    )

def get_default_config():
    """Retourne la configuration par défaut"""
    return {
        "virtuoso_endpoint": DEFAULT_VIRTUOSO_ENDPOINT,
        "fuseki_endpoint": DEFAULT_FUSEKI_ENDPOINT,
        "num_iterations": DEFAULT_NUM_ITERATIONS,
        "warmup_iterations": DEFAULT_WARMUP_ITERATIONS,
        "concurrent_queries": DEFAULT_CONCURRENT_QUERIES,
        "datasets": AVAILABLE_DATASETS,
        "query_types": QUERY_TYPES,
        "query_timeout": QUERY_TIMEOUT,
        "connectivity_timeout": CONNECTIVITY_TIMEOUT
    }

# ============================================================================
# CONFIGURATION POUR LA SYNCHRONISATION DES DONNÉES
# ============================================================================

# Configuration pour la synchronisation
SYNCHRONIZATION_TIMEOUT = 300  # 5 minutes pour les opérations de sync
MAX_SYNC_TRIPLETS = 1000000    # Limite par défaut pour la synchronisation
AUTO_SYNC_THRESHOLD = 0.05     # Seuil de différence pour déclencher une alerte
SYNC_CHUNK_SIZE = 10000        # Taille des chunks pour la synchronisation (optimisé pour Virtuoso)

# Types de datasets supportés pour la détection automatique
SUPPORTED_DATASET_TYPES = {
    "LUBM": {
        "detection_query": "ASK { ?s a <http://www.lehigh.edu/~zhp2/2004/0401/univ-bench.owl#University> }",
        "description": "Lehigh University Benchmark",
        "typical_size": "small_to_medium"
    },
    "DBpedia": {
        "detection_query": "ASK { ?s a <http://dbpedia.org/ontology/Person> }",
        "description": "DBpedia Knowledge Base",
        "typical_size": "large"
    },
    "Generic": {
        "detection_query": "ASK { ?s a <http://example.org/Person> }",
        "description": "Generic Test Dataset",
        "typical_size": "small"
    },
    "FOAF": {
        "detection_query": "ASK { ?s a <http://xmlns.com/foaf/0.1/Person> }",
        "description": "Friend of a Friend",
        "typical_size": "small"
    },
    "Dublin Core": {
        "detection_query": "ASK { ?s <http://purl.org/dc/elements/1.1/title> ?o }",
        "description": "Dublin Core Metadata",
        "typical_size": "medium"
    }
}

# Configuration des alertes de synchronisation
SYNC_ALERTS = {
    "large_dataset_threshold": 500000,  # Alerter si > 500k triplets
    "time_estimation_factor": 0.001,   # Facteur pour estimer le temps (triplets/seconde)
    "memory_warning_threshold": 1024,  # MB - alerter si peu de mémoire
    "enable_auto_backup": True         # Sauvegarder avant synchronisation
}

# ============================================================================
# CONFIGURATION DE LA GESTION DES DATASETS
# ============================================================================

# Chemin par défaut vers les datasets
DEFAULT_DATASETS_PATH = "datasets"

# Fichier de métadonnées des datasets chargés
DATASETS_METADATA_FILE = "datasets_metadata.json"

# ============================================================================
# AUTHENTIFICATION (chargée depuis .env pour sécurité)
# ============================================================================

# Authentification Virtuoso (depuis .env)
VIRTUOSO_DEFAULT_USERNAME = get_env("VIRTUOSO_USERNAME", "SPARQL")
VIRTUOSO_DEFAULT_PASSWORD = get_env("VIRTUOSO_PASSWORD", None)

# Authentification Fuseki (optionnel, depuis .env)
FUSEKI_DEFAULT_USERNAME = get_env("FUSEKI_USERNAME", None)
FUSEKI_DEFAULT_PASSWORD = get_env("FUSEKI_PASSWORD", None)

# Préfixe par défaut pour les URIs de graphe
DEFAULT_GRAPH_URI_PREFIX = get_env("DEFAULT_GRAPH_URI_PREFIX", "http://example.org/dataset")

# AVERTISSEMENT: Ne jamais hardcoder de mots de passe en production!
# Toujours utiliser des variables d'environnement (.env)

# Taille de chunk pour le chargement par morceaux
DATASET_LOAD_CHUNK_SIZE = 1000

# Timeout pour le chargement de datasets (secondes)
DATASET_LOAD_TIMEOUT = 300

# Configuration des datasets disponibles
DATASET_CONFIGURATIONS = {
    "DBpedia": {
        "folder": "DBpedia",
        "format": "N-Triples",
        "ontology": "http://dbpedia.org/ontology/",
        "color": "🔵",
        "sizes": ["10K", "100K", "1M"]
    },
    "LUBM": {
        "folder": "LUBM",
        "format": "Turtle",
        "ontology": "http://www.lehigh.edu/~zhp2/2004/0401/univ-bench.owl#",
        "color": "🟢",
        "sizes": ["10K", "100K", "1M"]
    },
    "Generic": {
        "folder": "Generic",
        "format": "Turtle",
        "ontology": "http://example.org/",
        "color": "🟡",
        "sizes": ["10K", "100K"]
    }
}

def get_datasets_config():
    """Retourne la configuration complète des datasets"""
    return {
        "datasets_path": DEFAULT_DATASETS_PATH,
        "metadata_file": DATASETS_METADATA_FILE,
        "virtuoso_auth": {
            "username": VIRTUOSO_DEFAULT_USERNAME,
            "password": VIRTUOSO_DEFAULT_PASSWORD
        },
        "fuseki_auth": {
            "username": FUSEKI_DEFAULT_USERNAME,
            "password": FUSEKI_DEFAULT_PASSWORD
        },
        "graph_uri_prefix": DEFAULT_GRAPH_URI_PREFIX,
        "chunk_size": DATASET_LOAD_CHUNK_SIZE,
        "load_timeout": DATASET_LOAD_TIMEOUT,
        "available_datasets": DATASET_CONFIGURATIONS
    }