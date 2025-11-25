"""
Fonctions utilitaires et helpers pour l'application
Version intégrée avec support de la synchronisation des données
"""

import logging
import streamlit as st
from datetime import datetime
from typing import Any, Dict, List, Optional
import os
import sys
import json
import pandas as pd
from functools import wraps

# Configuration cache UI (défini localement pour éviter import circulaire)
# Note: Dupliqué depuis config.settings pour éviter circular import
UI_CACHE_TTL = 600  # 10 minutes

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def log_message(message: str, level: str = "info"):
    """
    Enregistre un message dans les logs
    
    Args:
        message: Message à enregistrer
        level: Niveau de log (info, warning, error, debug)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    
    if level.lower() == "info":
        logger.info(formatted_message)
    elif level.lower() == "warning":
        logger.warning(formatted_message)
    elif level.lower() == "error":
        logger.error(formatted_message)
    elif level.lower() == "debug":
        logger.debug(formatted_message)
    else:
        logger.info(formatted_message)

def format_duration(seconds: float) -> str:
    """
    Formate une durée en secondes en format lisible
    
    Args:
        seconds: Durée en secondes
        
    Returns:
        Durée formatée sous forme de chaîne
    """
    if seconds < 1:
        return f"{seconds*1000:.2f} ms"
    elif seconds < 60:
        return f"{seconds:.3f} s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        remaining_seconds = seconds % 60
        return f"{hours}h {minutes}m {remaining_seconds:.1f}s"

def format_memory_size(bytes_size: float) -> str:
    """
    Formate une taille en bytes en format lisible
    
    Args:
        bytes_size: Taille en bytes
        
    Returns:
        Taille formatée sous forme de chaîne
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Division sécurisée qui évite la division par zéro
    
    Args:
        numerator: Numérateur
        denominator: Dénominateur
        default: Valeur par défaut si division par zéro
        
    Returns:
        Résultat de la division ou valeur par défaut
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calcule le pourcentage de changement entre deux valeurs
    
    Args:
        old_value: Ancienne valeur
        new_value: Nouvelle valeur
        
    Returns:
        Pourcentage de changement
    """
    if old_value == 0:
        return 0.0 if new_value == 0 else 100.0
    
    return ((new_value - old_value) / old_value) * 100

def validate_endpoint_url(url: str) -> Dict[str, Any]:
    """
    Valide une URL d'endpoint SPARQL
    
    Args:
        url: URL à valider
        
    Returns:
        Dictionnaire contenant le résultat de validation
    """
    import re
    
    if not url:
        return {"valid": False, "error": "URL vide"}
    
    # Regex basique pour valider une URL
    url_pattern = re.compile(
        r'^https?://'  # http:// ou https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domaine
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # adresse IP
        r'(?::\d+)?'  # port optionnel
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        return {"valid": False, "error": "Format d'URL invalide"}
    
    # Vérifications spécifiques aux endpoints SPARQL
    if not any(keyword in url.lower() for keyword in ['sparql', 'query', 'endpoint']):
        return {
            "valid": True, 
            "error": "", 
            "warning": "L'URL ne semble pas être un endpoint SPARQL typique"
        }
    
    return {"valid": True, "error": ""}

def get_system_info_summary() -> Dict[str, str]:
    """
    Récupère un résumé des informations système
    
    Returns:
        Dictionnaire contenant les informations système formatées
    """
    try:
        import psutil
        
        # Informations CPU
        cpu_count = psutil.cpu_count(logical=True)
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Informations mémoire
        memory = psutil.virtual_memory()
        memory_total_gb = memory.total / (1024**3)
        memory_used_percent = memory.percent
        
        # Informations disque
        disk = psutil.disk_usage('/')
        disk_total_gb = disk.total / (1024**3)
        disk_used_percent = (disk.used / disk.total) * 100
        
        return {
            "CPU": f"{cpu_count} cœurs, {cpu_percent:.1f}% utilisé",
            "Mémoire": f"{memory_total_gb:.1f} GB total, {memory_used_percent:.1f}% utilisée",
            "Disque": f"{disk_total_gb:.1f} GB total, {disk_used_percent:.1f}% utilisé",
            "OS": f"{os.name}, {sys.platform}",
            "Python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        }
        
    except Exception as e:
        log_message(f"Erreur lors de la récupération des informations système: {str(e)}", "error")
        return {"Erreur": "Impossible de récupérer les informations système"}

def create_progress_callback(progress_bar, status_text):
    """
    Crée une fonction de callback pour mettre à jour la barre de progression
    
    Args:
        progress_bar: Objet barre de progression Streamlit
        status_text: Objet texte de statut Streamlit
        
    Returns:
        Fonction de callback
    """
    def update_progress(current: int, total: int, message: str = ""):
        progress = current / total if total > 0 else 0
        progress_bar.progress(progress)
        if message:
            status_text.text(message)
    
    return update_progress

def filter_queries_by_selection(all_queries: Dict[str, str], 
                               query_types: Dict[str, bool]) -> Dict[str, str]:
    """
    Filtre les requêtes selon la sélection de l'utilisateur
    
    Args:
        all_queries: Toutes les requêtes disponibles
        query_types: Configuration des types de requêtes sélectionnés
        
    Returns:
        Dictionnaire des requêtes filtrées
    """
    selected_queries = {}
    
    # Mapping des types de requêtes aux mots-clés
    type_keywords = {
        "run_basic_queries": ["Simple"],
        "run_join_queries": ["Jointure"],
        "run_aggregation_queries": ["Agrégation"],
        "run_filter_queries": ["Filtre"],
        "run_optional_queries": ["OPTIONAL", "UNION"],
        "run_subqueries": ["Sous-requête"]
    }
    
    for query_name, query in all_queries.items():
        # Vérifier si cette requête correspond à un type sélectionné
        for type_key, is_selected in query_types.items():
            if is_selected and type_key in type_keywords:
                keywords = type_keywords[type_key]
                if any(keyword in query_name for keyword in keywords):
                    selected_queries[query_name] = query
                    break
    
    return selected_queries

def generate_query_statistics(queries: Dict[str, str]) -> Dict[str, Any]:
    """
    Génère des statistiques sur un ensemble de requêtes
    
    Args:
        queries: Dictionnaire des requêtes
        
    Returns:
        Dictionnaire contenant les statistiques
    """
    stats = {
        "total_queries": len(queries),
        "query_types": {},
        "avg_query_length": 0,
        "complexity_distribution": {"simple": 0, "medium": 0, "complex": 0}
    }
    
    if not queries:
        return stats
    
    total_length = 0
    
    for query_name, query in queries.items():
        # Longueur de la requête
        query_length = len(query.strip())
        total_length += query_length
        
        # Type de requête
        if "Simple" in query_name:
            stats["query_types"]["simple"] = stats["query_types"].get("simple", 0) + 1
        elif "Jointure" in query_name:
            stats["query_types"]["jointure"] = stats["query_types"].get("jointure", 0) + 1
        elif "Agrégation" in query_name:
            stats["query_types"]["aggregation"] = stats["query_types"].get("aggregation", 0) + 1
        elif "Filtre" in query_name:
            stats["query_types"]["filtre"] = stats["query_types"].get("filtre", 0) + 1
        elif any(keyword in query_name for keyword in ["OPTIONAL", "UNION"]):
            stats["query_types"]["optional"] = stats["query_types"].get("optional", 0) + 1
        elif "Sous-requête" in query_name:
            stats["query_types"]["subquery"] = stats["query_types"].get("subquery", 0) + 1
        
        # Complexité basée sur la longueur et les mots-clés
        complexity_score = 0
        if "GROUP BY" in query.upper():
            complexity_score += 2
        if "ORDER BY" in query.upper():
            complexity_score += 1
        if "UNION" in query.upper():
            complexity_score += 2
        if "OPTIONAL" in query.upper():
            complexity_score += 1
        if query.upper().count("SELECT") > 1:
            complexity_score += 3
        
        if complexity_score <= 1:
            stats["complexity_distribution"]["simple"] += 1
        elif complexity_score <= 4:
            stats["complexity_distribution"]["medium"] += 1
        else:
            stats["complexity_distribution"]["complex"] += 1
    
    stats["avg_query_length"] = total_length / len(queries)
    
    return stats

def export_results_to_json(results_df, filename: str = None) -> str:
    """
    Exporte les résultats vers un format JSON
    
    Args:
        results_df: DataFrame des résultats
        filename: Nom du fichier (optionnel)
        
    Returns:
        JSON string des résultats
    """
    try:
        # Conversion des timestamps et autres types non sérialisables
        export_df = results_df.copy()
        
        # Conversion des colonnes datetime si elles existent
        for col in export_df.columns:
            if export_df[col].dtype == 'datetime64[ns]':
                export_df[col] = export_df[col].dt.isoformat()
        
        # Métadonnées d'export
        export_data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "total_records": len(export_df),
                "columns": list(export_df.columns)
            },
            "results": export_df.to_dict('records')
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
        
    except Exception as e:
        log_message(f"Erreur lors de l'export JSON: {str(e)}", "error")
        return json.dumps({"error": "Erreur lors de l'export"})

def create_benchmark_summary(results_df) -> Dict[str, Any]:
    """
    Crée un résumé complet des benchmarks
    
    Args:
        results_df: DataFrame des résultats
        
    Returns:
        Dictionnaire contenant le résumé
    """
    # Vérification préalable des données
    if results_df is None:
        return _get_empty_summary("DataFrame est None")
    
    if results_df.empty:
        return _get_empty_summary("DataFrame est vide")
    
    try:
        # Vérification des colonnes critiques
        required_columns = ['execution_time', 'success', 'engine']
        missing_columns = [col for col in required_columns if col not in results_df.columns]
        
        if missing_columns:
            return _get_empty_summary(f"Colonnes manquantes: {', '.join(missing_columns)}")
        
        summary = {
            "overview": {
                "total_executions": len(results_df),
                "unique_queries": results_df['query_name'].nunique() if 'query_name' in results_df.columns else 0,
                "engines_tested": results_df['engine'].nunique() if 'engine' in results_df.columns else 0,
                "success_rate": results_df['success'].mean() * 100 if 'success' in results_df.columns else 0
            },
            "performance": {
                "avg_execution_time": results_df['execution_time'].mean() if 'execution_time' in results_df.columns else 0,
                "min_execution_time": results_df['execution_time'].min() if 'execution_time' in results_df.columns else 0,
                "max_execution_time": results_df['execution_time'].max() if 'execution_time' in results_df.columns else 0,
                "std_execution_time": results_df['execution_time'].std() if 'execution_time' in results_df.columns else 0
            },
            "resources": {
                "avg_cpu_usage": results_df['cpu_usage'].mean() if 'cpu_usage' in results_df.columns else 0,
                "avg_memory_usage": results_df['memory_usage'].mean() if 'memory_usage' in results_df.columns else 0,
                "max_cpu_usage": results_df['cpu_usage'].max() if 'cpu_usage' in results_df.columns else 0,
                "max_memory_usage": results_df['memory_usage'].max() if 'memory_usage' in results_df.columns else 0
            }
        }
        
        # Performance par moteur (avec gestion d'erreur)
        if 'engine' in results_df.columns and 'execution_time' in results_df.columns:
            try:
                engine_performance = results_df.groupby('engine').agg({
                    'execution_time': ['mean', 'min', 'max'],
                    'success': 'mean'
                }).round(4)
                
                summary["by_engine"] = engine_performance.to_dict()
            except Exception as e:
                log_message(f"Erreur lors du calcul des performances par moteur: {str(e)}", "warning")
                summary["by_engine"] = {}
        
        # Performance par requête (avec gestion d'erreur)
        if 'query_name' in results_df.columns and 'execution_time' in results_df.columns:
            try:
                query_performance = results_df.groupby('query_name').agg({
                    'execution_time': ['mean', 'min', 'max'],
                    'success': 'mean'
                }).round(4)
                
                summary["by_query"] = query_performance.to_dict()
            except Exception as e:
                log_message(f"Erreur lors du calcul des performances par requête: {str(e)}", "warning")
                summary["by_query"] = {}
        
        return summary
        
    except Exception as e:
        error_msg = f"Erreur lors de la création du résumé: {str(e)}"
        log_message(error_msg, "error")
        return _get_empty_summary(error_msg)

def _get_empty_summary(reason: str = "Aucune donnée disponible") -> Dict[str, Any]:
    """
    Retourne un résumé vide avec des valeurs par défaut
    
    Args:
        reason: Raison de l'absence de données
        
    Returns:
        Dictionnaire de résumé avec valeurs par défaut
    """
    return {
        "overview": {
            "total_executions": 0,
            "unique_queries": 0,
            "engines_tested": 0,
            "success_rate": 0
        },
        "performance": {
            "avg_execution_time": 0,
            "min_execution_time": 0,
            "max_execution_time": 0,
            "std_execution_time": 0
        },
        "resources": {
            "avg_cpu_usage": 0,
            "avg_memory_usage": 0,
            "max_cpu_usage": 0,
            "max_memory_usage": 0
        },
        "by_engine": {},
        "by_query": {},
        "error": reason
    }

def validate_configuration(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valide une configuration de test
    
    Args:
        config: Configuration à valider
        
    Returns:
        Dictionnaire contenant le résultat de validation
    """
    errors = []
    warnings = []
    
    # Validation des endpoints
    if not config.get("virtuoso_endpoint"):
        errors.append("Endpoint Virtuoso manquant")
    else:
        virtuoso_validation = validate_endpoint_url(config["virtuoso_endpoint"])
        if not virtuoso_validation["valid"]:
            errors.append(f"Endpoint Virtuoso invalide: {virtuoso_validation['error']}")
    
    if not config.get("fuseki_endpoint"):
        errors.append("Endpoint Fuseki manquant")
    else:
        fuseki_validation = validate_endpoint_url(config["fuseki_endpoint"])
        if not fuseki_validation["valid"]:
            errors.append(f"Endpoint Fuseki invalide: {fuseki_validation['error']}")
    
    # Validation des paramètres numériques
    if config.get("num_iterations", 0) <= 0:
        errors.append("Le nombre d'itérations doit être supérieur à 0")
    
    if config.get("num_iterations", 0) > 50:
        warnings.append("Un grand nombre d'itérations peut prendre beaucoup de temps")
    
    if config.get("concurrent_queries", 0) > 10:
        warnings.append("Un niveau de concurrence élevé peut surcharger le système")
    
    # Validation de la sélection de requêtes
    query_types_selected = any(config.get("query_types", {}).values())
    if not query_types_selected:
        errors.append("Aucun type de requête sélectionné")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def format_test_results_summary(results_df) -> str:
    """
    Formate un résumé textuel des résultats de test
    
    Args:
        results_df: DataFrame des résultats
        
    Returns:
        Résumé formaté sous forme de chaîne
    """
    try:
        summary = create_benchmark_summary(results_df)
        
        # Vérifier s'il y a une erreur dans le résumé
        if "error" in summary:
            return f"Impossible de générer le résumé: {summary['error']}"
        
        text_summary = f"""
Résumé des tests de performance SPARQL
======================================

Aperçu général:
- Nombre total d'exécutions: {summary['overview']['total_executions']}
- Requêtes testées: {summary['overview']['unique_queries']}
- Moteurs testés: {summary['overview']['engines_tested']}
- Taux de succès global: {summary['overview']['success_rate']:.2f}%

Performance globale:
- Temps d'exécution moyen: {format_duration(summary['performance']['avg_execution_time'])}
- Temps d'exécution minimum: {format_duration(summary['performance']['min_execution_time'])}
- Temps d'exécution maximum: {format_duration(summary['performance']['max_execution_time'])}
- Écart-type: {format_duration(summary['performance']['std_execution_time'])}

Utilisation des ressources:
- CPU moyen: {summary['resources']['avg_cpu_usage']:.2f}%
- Mémoire moyenne: {format_memory_size(summary['resources']['avg_memory_usage'] * 1024 * 1024)}
- CPU maximum: {summary['resources']['max_cpu_usage']:.2f}%
- Mémoire maximum: {format_memory_size(summary['resources']['max_memory_usage'] * 1024 * 1024)}

Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return text_summary.strip()
        
    except Exception as e:
        log_message(f"Erreur lors du formatage du résumé: {str(e)}", "error")
        return f"Erreur lors de la génération du résumé: {str(e)}"

# ============================================================================
# NOUVELLES FONCTIONS POUR LA SYNCHRONISATION DES DONNÉES
# ============================================================================

def validate_endpoint_accessibility(endpoint_url: str) -> bool:
    """
    Valide qu'un endpoint SPARQL est accessible
    
    Args:
        endpoint_url: URL de l'endpoint
        
    Returns:
        True si l'endpoint est accessible
    """
    try:
        from core.executor import QueryExecutor
        executor = QueryExecutor(timeout=10)
        
        result = executor.test_connectivity(endpoint_url)
        return result["status"] == "online"
        
    except Exception as e:
        log_message(f"Erreur de validation d'endpoint {endpoint_url}: {str(e)}", "error")
        return False

def format_sync_status(virtuoso_count: int, fuseki_count: int) -> Dict[str, Any]:
    """
    Formate le statut de synchronisation pour l'affichage
    
    Args:
        virtuoso_count: Nombre de triplets dans Virtuoso
        fuseki_count: Nombre de triplets dans Fuseki
        
    Returns:
        Dictionnaire formaté du statut
    """
    status = {
        "synchronized": False,
        "message": "",
        "action_needed": "",
        "icon": ""
    }
    
    if virtuoso_count == fuseki_count and virtuoso_count > 0:
        status.update({
            "synchronized": True,
            "message": f"Datasets synchronisés ({virtuoso_count:,} triplets)",
            "action_needed": "Aucune",
            "icon": "✅"
        })
    elif virtuoso_count > 0 and fuseki_count == 0:
        status.update({
            "synchronized": False,
            "message": f"Virtuoso a {virtuoso_count:,} triplets, Fuseki est vide",
            "action_needed": "Synchroniser Virtuoso → Fuseki",
            "icon": "⚠️"
        })
    elif virtuoso_count == 0 and fuseki_count > 0:
        status.update({
            "synchronized": False,
            "message": f"Fuseki a {fuseki_count:,} triplets, Virtuoso est vide",
            "action_needed": "Charger des données dans Virtuoso",
            "icon": "⚠️"
        })
    elif virtuoso_count == 0 and fuseki_count == 0:
        status.update({
            "synchronized": True,
            "message": "Les deux moteurs sont vides",
            "action_needed": "Charger des données dans les deux moteurs",
            "icon": "ℹ️"
        })
    else:
        difference = abs(virtuoso_count - fuseki_count)
        status.update({
            "synchronized": False,
            "message": f"Différence de {difference:,} triplets détectée",
            "action_needed": "Vérifier et synchroniser les datasets",
            "icon": "❌"
        })
    
    return status

def get_sync_status_summary() -> Dict[str, Any]:
    """
    Retourne un résumé rapide du statut de synchronisation avec support des graphes nommés

    Returns:
        Résumé du statut de synchronisation
    """
    if ('virtuoso_endpoint' not in st.session_state or
        'fuseki_endpoint' not in st.session_state):
        return {
            "status": "not_configured",
            "message": "Endpoints non configurés",
            "can_test": False
        }

    try:
        from utils.data_synchronizer import DataSynchronizer
        from utils.dataset_manager import DatasetManager

        synchronizer = DataSynchronizer(
            st.session_state['virtuoso_endpoint'],
            st.session_state['fuseki_endpoint']
        )

        # Charger les métadonnées pour obtenir les graph_uri
        dataset_manager = DatasetManager(datasets_path="datasets")
        metadata = dataset_manager.load_all_metadata()
        virtuoso_graph_uri = metadata.get('virtuoso', {}).get('graph_uri') if metadata else None
        fuseki_graph_uri = metadata.get('fuseki', {}).get('graph_uri') if metadata else None

        # Compter les triplets dans les graphes nommés
        v_count = synchronizer.count_triplets(st.session_state['virtuoso_endpoint'], virtuoso_graph_uri)
        f_count = synchronizer.count_triplets(st.session_state['fuseki_endpoint'], fuseki_graph_uri)

        status_info = format_sync_status(v_count, f_count)

        return {
            "status": "synchronized" if status_info["synchronized"] else "not_synchronized",
            "message": status_info["message"],
            "action_needed": status_info["action_needed"],
            "virtuoso_count": v_count,
            "fuseki_count": f_count,
            "can_test": status_info["synchronized"] and v_count > 0
        }

    except Exception as e:
        log_message(f"Erreur lors de l'obtention du statut de synchronisation: {str(e)}", "error")
        return {
            "status": "error",
            "message": f"Erreur: {str(e)}",
            "can_test": False
        }

# ============================================================================
# FONCTIONS DE CACHE POUR L'INTERFACE UTILISATEUR
# ============================================================================

@st.cache_data(ttl=UI_CACHE_TTL)
def compute_summary_stats(results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les statistiques récapitulatives avec cache

    Args:
        results_df: DataFrame des résultats

    Returns:
        DataFrame des statistiques agrégées
    """
    if results_df.empty or 'execution_time' not in results_df.columns:
        return pd.DataFrame()

    try:
        summary = results_df.groupby(['query_name', 'engine']).agg({
            'execution_time': ['mean', 'std', 'min', 'max', 'count'],
            'success': 'mean',
            'result_count': 'mean' if 'result_count' in results_df.columns else 'count',
            'cpu_usage': 'mean' if 'cpu_usage' in results_df.columns else 'count',
            'memory_usage': 'mean' if 'memory_usage' in results_df.columns else 'count'
        }).round(4)

        return summary
    except Exception as e:
        log_message(f"Erreur lors du calcul des statistiques: {str(e)}", "error")
        return pd.DataFrame()

@st.cache_data(ttl=UI_CACHE_TTL)
def compute_percentiles(results_df: pd.DataFrame, percentiles: List[int] = [50, 95, 99]) -> Dict[str, Any]:
    """
    Calcule les percentiles de performance avec cache

    Args:
        results_df: DataFrame des résultats
        percentiles: Liste des percentiles à calculer

    Returns:
        Dictionnaire des percentiles par moteur
    """
    if results_df.empty or 'execution_time' not in results_df.columns:
        return {}

    try:
        percentile_data = {}

        for engine in results_df['engine'].unique():
            engine_data = results_df[results_df['engine'] == engine]['execution_time']
            percentile_data[engine] = {
                f"P{p}": engine_data.quantile(p / 100) for p in percentiles
            }

        return percentile_data
    except Exception as e:
        log_message(f"Erreur lors du calcul des percentiles: {str(e)}", "error")
        return {}

@st.cache_data(ttl=UI_CACHE_TTL)
def filter_results_cached(results_df: pd.DataFrame,
                          engine_filter: List[str],
                          query_filter: List[str],
                          success_only: bool = False) -> pd.DataFrame:
    """
    Filtre les résultats avec cache pour améliorer les performances

    Args:
        results_df: DataFrame des résultats
        engine_filter: Liste des moteurs à inclure
        query_filter: Liste des requêtes à inclure
        success_only: Si True, ne garde que les succès

    Returns:
        DataFrame filtré
    """
    if results_df.empty:
        return results_df

    try:
        filtered = results_df.copy()

        if engine_filter and 'engine' in filtered.columns:
            filtered = filtered[filtered['engine'].isin(engine_filter)]

        if query_filter and 'query_name' in filtered.columns:
            filtered = filtered[filtered['query_name'].isin(query_filter)]

        if success_only and 'success' in filtered.columns:
            filtered = filtered[filtered['success'] == True]

        return filtered
    except Exception as e:
        log_message(f"Erreur lors du filtrage: {str(e)}", "error")
        return results_df

@st.cache_data(ttl=UI_CACHE_TTL)
def compute_extreme_performances(results_df: pd.DataFrame, top_n: int = 5) -> Dict[str, pd.DataFrame]:
    """
    Identifie les performances extrêmes (meilleures et pires) avec cache

    Args:
        results_df: DataFrame des résultats
        top_n: Nombre de résultats à retourner

    Returns:
        Dictionnaire contenant 'fastest' et 'slowest' DataFrames
    """
    if results_df.empty or 'execution_time' not in results_df.columns:
        return {"fastest": pd.DataFrame(), "slowest": pd.DataFrame()}

    try:
        essential_cols = ['engine', 'query_name', 'execution_time', 'iteration']
        available_cols = [col for col in essential_cols if col in results_df.columns]

        fastest = results_df.nsmallest(top_n, 'execution_time')[available_cols]
        slowest = results_df.nlargest(top_n, 'execution_time')[available_cols]

        return {
            "fastest": fastest,
            "slowest": slowest
        }
    except Exception as e:
        log_message(f"Erreur lors du calcul des performances extrêmes: {str(e)}", "error")
        return {"fastest": pd.DataFrame(), "slowest": pd.DataFrame()}

# ============================================================================
# VALIDATION DES DONNÉES
# ============================================================================

def validate_results_schema(results_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Valide le schéma du DataFrame de résultats

    Args:
        results_df: DataFrame à valider

    Returns:
        Dictionnaire avec le statut de validation et les erreurs
    """
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }

    # Vérification que ce n'est pas None
    if results_df is None:
        validation_result["valid"] = False
        validation_result["errors"].append("DataFrame est None")
        return validation_result

    # Vérification que ce n'est pas vide
    if results_df.empty:
        validation_result["valid"] = False
        validation_result["errors"].append("DataFrame est vide")
        return validation_result

    # Colonnes requises
    required_columns = ['query_name', 'engine', 'execution_time', 'success']
    missing_columns = [col for col in required_columns if col not in results_df.columns]

    if missing_columns:
        validation_result["valid"] = False
        validation_result["errors"].append(f"Colonnes manquantes: {', '.join(missing_columns)}")

    # Colonnes optionnelles mais recommandées
    optional_columns = ['iteration', 'result_count', 'cpu_usage', 'memory_usage']
    missing_optional = [col for col in optional_columns if col not in results_df.columns]

    if missing_optional:
        validation_result["warnings"].append(f"Colonnes optionnelles manquantes: {', '.join(missing_optional)}")

    # Validation des types de données
    if validation_result["valid"]:
        try:
            # execution_time doit être numérique
            if 'execution_time' in results_df.columns:
                if not pd.api.types.is_numeric_dtype(results_df['execution_time']):
                    validation_result["errors"].append("'execution_time' doit être numérique")
                    validation_result["valid"] = False
                elif (results_df['execution_time'] < 0).any():
                    validation_result["errors"].append("'execution_time' contient des valeurs négatives")
                    validation_result["valid"] = False

            # success doit être booléen
            if 'success' in results_df.columns:
                if not pd.api.types.is_bool_dtype(results_df['success']):
                    # Tenter une conversion
                    try:
                        results_df['success'] = results_df['success'].astype(bool)
                        validation_result["warnings"].append("'success' a été converti en booléen")
                    except:
                        validation_result["errors"].append("'success' doit être booléen")
                        validation_result["valid"] = False

        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Erreur lors de la validation des types: {str(e)}")

    return validation_result

# ============================================================================
# DÉCORATEUR POUR GESTION D'ERREURS VISUALISATIONS
# ============================================================================

def handle_visualization_errors(default_return=None, show_error=True):
    """
    Décorateur pour gérer les erreurs dans les fonctions de visualisation

    Args:
        default_return: Valeur par défaut à retourner en cas d'erreur
        show_error: Si True, affiche l'erreur avec st.error()

    Returns:
        Décorateur
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = f"Erreur dans {func.__name__}: {str(e)}"
                log_message(error_msg, "error")

                if show_error:
                    st.error(f"❌ {error_msg}")

                    # Afficher un expander avec les détails pour le débogage
                    with st.expander("Détails de l'erreur"):
                        st.code(str(e))
                        import traceback
                        st.code(traceback.format_exc())

                return default_return
        return wrapper
    return decorator