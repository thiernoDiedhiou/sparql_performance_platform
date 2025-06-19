"""
Configuration globale de l'application
"""

import streamlit as st

# Configuration par défaut des endpoints
DEFAULT_VIRTUOSO_ENDPOINT = "http://localhost:8890/sparql"
DEFAULT_FUSEKI_ENDPOINT = "http://localhost:3030/dataset/query"

# Configuration par défaut des tests
DEFAULT_NUM_ITERATIONS = 5
DEFAULT_WARMUP_ITERATIONS = 2
DEFAULT_CONCURRENT_QUERIES = 1

# Jeux de données disponibles
AVAILABLE_DATASETS = ["LUBM", "BSBM", "DBpedia", "YAGO", "Personnalisé"]

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

def configure_page():
    """Configure les paramètres de la page Streamlit"""
    st.set_page_config(
        page_title="Comparaison des performances de requêtes SPARQL",
        page_icon="📊",
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