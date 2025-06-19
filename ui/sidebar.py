"""
Interface de la barre latérale pour la configuration
"""

import streamlit as st

# Valeurs par défaut (au cas où config.settings ne serait pas disponible)
try:
    from config.settings import (
        DEFAULT_VIRTUOSO_ENDPOINT, DEFAULT_FUSEKI_ENDPOINT,
        DEFAULT_NUM_ITERATIONS, DEFAULT_WARMUP_ITERATIONS,
        DEFAULT_CONCURRENT_QUERIES, AVAILABLE_DATASETS, QUERY_TYPES
    )
except ImportError:
    # Valeurs de fallback si config.settings n'est pas accessible
    DEFAULT_VIRTUOSO_ENDPOINT = "http://localhost:8890/sparql"
    DEFAULT_FUSEKI_ENDPOINT = "http://localhost:3030/dataset/query"
    DEFAULT_NUM_ITERATIONS = 5
    DEFAULT_WARMUP_ITERATIONS = 2
    DEFAULT_CONCURRENT_QUERIES = 1
    AVAILABLE_DATASETS = ["LUBM", "BSBM", "DBpedia", "YAGO", "Personnalisé"]
    QUERY_TYPES = {
        "run_basic_queries": {"label": "Requêtes simples (pattern matching)", "default": True},
        "run_join_queries": {"label": "Requêtes de jointure", "default": True},
        "run_aggregation_queries": {"label": "Requêtes d'agrégation", "default": True},
        "run_filter_queries": {"label": "Requêtes avec filtres", "default": True},
        "run_optional_queries": {"label": "Requêtes avec OPTIONAL/UNION/MINUS", "default": True},
        "run_subqueries": {"label": "Requêtes avec sous-requêtes", "default": True}
    }

def render_sidebar() -> dict:
    """
    Affiche l'interface de la barre latérale et retourne la configuration
    
    Returns:
        Dictionnaire contenant la configuration utilisateur
    """
    with st.sidebar:
        st.header("Configuration")
        
        # Configuration des endpoints
        st.subheader("Endpoints SPARQL")
        virtuoso_endpoint = st.text_input(
            "Endpoint Virtuoso", 
            value=DEFAULT_VIRTUOSO_ENDPOINT,
            help="URL de l'endpoint Virtuoso (ex: http://localhost:8890/sparql)"
        )
        
        fuseki_endpoint = st.text_input(
            "Endpoint Jena Fuseki", 
            value=DEFAULT_FUSEKI_ENDPOINT,
            help="URL de l'endpoint Jena Fuseki (ex: http://localhost:3030/dataset/query)"
        )
        
        # Configuration des jeux de données
        st.subheader("Jeux de données")
        dataset_choice = st.selectbox(
            "Sélectionner un jeu de données",
            AVAILABLE_DATASETS,
            help="Choisissez le type de jeu de données pour adapter les requêtes"
        )
        
        dataset_file = None
        if dataset_choice == "Personnalisé":
            dataset_file = st.file_uploader(
                "Charger un jeu de données RDF", 
                type=["rdf", "ttl", "nt", "n3"],
                help="Chargez votre propre jeu de données RDF"
            )
        
        # Configuration des tests
        st.subheader("Configuration des tests")
        
        num_iterations = st.slider(
            "Nombre d'itérations par requête", 
            min_value=1, 
            max_value=20, 
            value=DEFAULT_NUM_ITERATIONS,
            help="Nombre de fois que chaque requête sera exécutée"
        )
        
        warmup_iterations = st.slider(
            "Nombre d'itérations d'échauffement", 
            min_value=0, 
            max_value=5, 
            value=DEFAULT_WARMUP_ITERATIONS,
            help="Itérations d'échauffement pour stabiliser les performances"
        )
        
        concurrent_queries = st.slider(
            "Niveau de concurrence", 
            min_value=1, 
            max_value=10, 
            value=DEFAULT_CONCURRENT_QUERIES,
            help="Nombre de requêtes exécutées simultanément"
        )
        
        # Timeout des requêtes
        query_timeout = st.slider(
            "Timeout des requêtes (secondes)",
            min_value=10,
            max_value=300,
            value=60,
            help="Timeout maximum pour l'exécution d'une requête"
        )
        
        # Types de tests
        st.subheader("Types de tests")
        
        query_type_config = {}
        for key, config in QUERY_TYPES.items():
            query_type_config[key] = st.checkbox(
                config["label"], 
                value=config["default"],
                help=f"Inclure les {config['label'].lower()} dans les tests"
            )
        
        # Options avancées
        with st.expander("Options avancées"):
            st.subheader("Configuration avancée")
            
            # Mode de mesure des métriques
            metrics_mode = st.selectbox(
                "Mode de mesure des métriques",
                ["Standard", "Détaillé", "Minimal"],
                index=0,
                help="Niveau de détail pour la collecte des métriques système"
            )
            
            # Collecte de métriques réseau
            collect_network_metrics = st.checkbox(
                "Collecter les métriques réseau",
                value=False,
                help="Surveiller l'utilisation du réseau pendant les tests"
            )
            
            # Sauvegarde automatique
            auto_save_results = st.checkbox(
                "Sauvegarde automatique des résultats",
                value=True,
                help="Sauvegarder automatiquement les résultats après chaque test"
            )
            
            # Mode debug
            debug_mode = st.checkbox(
                "Mode debug",
                value=False,
                help="Afficher des informations de débogage détaillées"
            )
            
            # Intervalle de collecte des métriques
            metrics_interval = st.slider(
                "Intervalle de collecte des métriques (ms)",
                min_value=100,
                max_value=5000,
                value=1000,
                step=100,
                help="Fréquence de collecte des métriques système"
            )
        
        # Profils de test prédéfinis
        st.subheader("Profils de test")
        
        test_profile = st.selectbox(
            "Profil de test prédéfini",
            ["Personnalisé", "Test rapide", "Test complet", "Test de stress", "Test de comparaison"],
            help="Profils préconfigurés pour différents types de tests"
        )
        
        if test_profile != "Personnalisé":
            if st.button("Appliquer le profil"):
                profile_config = _get_test_profile_config(test_profile)
                st.session_state.update(profile_config)
                st.success(f"Profil '{test_profile}' appliqué!")
                st.rerun()
        
        # Aide contextuelle
        st.markdown("---")
        with st.expander("Aide & Documentation"):
            st.markdown("""
            ### Guide d'utilisation rapide
            
            1. **Configuration**: Paramétrez les endpoints SPARQL et choisissez un jeu de données.
            2. **Sélection de requêtes**: Choisissez les types de requêtes à tester.
            3. **Exécution**: Lancez les tests avec le bouton "Exécuter les tests".
            4. **Analyse**: Examinez les résultats et visualisations dans les autres onglets.
            5. **Exportation**: Téléchargez les résultats ou générez un rapport.
            
            ### Métriques mesurées
            
            - **Temps d'exécution**: Durée totale de chaque requête en secondes.
            - **Utilisation CPU**: Pourcentage d'utilisation du CPU pendant l'exécution.
            - **Utilisation mémoire**: Quantité de mémoire utilisée en MB.
            - **Taux de succès**: Pourcentage de requêtes réussies sans erreur.
            - **Nombre de résultats**: Nombre moyen de résultats retournés par requête.
            
            ### Conseils pour de meilleurs résultats
            
            - Utilisez plusieurs itérations pour des résultats plus fiables
            - Les itérations d'échauffement améliorent la consistance
            - Fermez les autres applications pour des mesures plus précises
            - Testez avec différents niveaux de concurrence selon votre usage
            """)
    
    # Retourner la configuration complète
    return {
        "virtuoso_endpoint": virtuoso_endpoint,
        "fuseki_endpoint": fuseki_endpoint,
        "dataset_choice": dataset_choice,
        "dataset_file": dataset_file,
        "num_iterations": num_iterations,
        "warmup_iterations": warmup_iterations,
        "concurrent_queries": concurrent_queries,
        "query_timeout": query_timeout,
        "query_types": query_type_config,
        "metrics_mode": metrics_mode,
        "collect_network_metrics": collect_network_metrics,
        "auto_save_results": auto_save_results,
        "debug_mode": debug_mode,
        "metrics_interval": metrics_interval,
        "test_profile": test_profile
    }

def _get_test_profile_config(profile_name: str) -> dict:
    """
    Retourne la configuration pour un profil de test donné
    
    Args:
        profile_name: Nom du profil de test
        
    Returns:
        Dictionnaire de configuration
    """
    profiles = {
        "Test rapide": {
            "num_iterations": 3,
            "warmup_iterations": 1,
            "concurrent_queries": 1,
            "query_timeout": 30,
            "run_basic_queries": True,
            "run_join_queries": False,
            "run_aggregation_queries": False,
            "run_filter_queries": False,
            "run_optional_queries": False,
            "run_subqueries": False
        },
        "Test complet": {
            "num_iterations": 10,
            "warmup_iterations": 3,
            "concurrent_queries": 1,
            "query_timeout": 120,
            "run_basic_queries": True,
            "run_join_queries": True,
            "run_aggregation_queries": True,
            "run_filter_queries": True,
            "run_optional_queries": True,
            "run_subqueries": True
        },
        "Test de stress": {
            "num_iterations": 20,
            "warmup_iterations": 5,
            "concurrent_queries": 5,
            "query_timeout": 180,
            "run_basic_queries": True,
            "run_join_queries": True,
            "run_aggregation_queries": True,
            "run_filter_queries": True,
            "run_optional_queries": True,
            "run_subqueries": True
        },
        "Test de comparaison": {
            "num_iterations": 15,
            "warmup_iterations": 3,
            "concurrent_queries": 2,
            "query_timeout": 90,
            "run_basic_queries": True,
            "run_join_queries": True,
            "run_aggregation_queries": True,
            "run_filter_queries": True,
            "run_optional_queries": True,
            "run_subqueries": True
        }
    }
    
    return profiles.get(profile_name, {})