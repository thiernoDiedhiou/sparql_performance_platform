"""
Interface de la barre latérale OPTIMISÉE (Version 2.0)
Allégée de 50% - Éléments essentiels uniquement dans la sidebar
"""

import streamlit as st

# Valeurs par défaut
try:
    from config.settings import (
        DEFAULT_VIRTUOSO_ENDPOINT, DEFAULT_FUSEKI_ENDPOINT,
        DEFAULT_NUM_ITERATIONS, DEFAULT_WARMUP_ITERATIONS,
        DEFAULT_CONCURRENT_QUERIES, AVAILABLE_DATASETS
    )
except ImportError:
    # Valeurs de fallback si config.settings n'est pas accessible
    DEFAULT_VIRTUOSO_ENDPOINT = "http://localhost:8890/sparql"
    DEFAULT_FUSEKI_ENDPOINT = "http://localhost:3030/dataset/query"
    DEFAULT_NUM_ITERATIONS = 5
    DEFAULT_WARMUP_ITERATIONS = 2
    DEFAULT_CONCURRENT_QUERIES = 1
    AVAILABLE_DATASETS = ["LUBM", "DBpedia", "BSBM", "YAGO", "Personnalisé"]


def render_sidebar_optimized() -> dict:
    """
    Version OPTIMISÉE de la sidebar - 50% plus légère
    Garde uniquement les contrôles essentiels

    Returns:
        Dictionnaire contenant la configuration utilisateur
    """
    with st.sidebar:

        # ============================================================
        # SECTION 1: MODE RAPIDE (NOUVEAU)
        # ============================================================
        st.subheader("⚡ Mode rapide")

        quick_mode = st.radio(
            "Profil de test",
            options=["⚡ Rapide (3 min)", "⚙️ Standard (10 min)", "🔬 Complet (30 min)", "⚙️ Personnalisé"],
            index=1,
            help="Choisissez un profil prédéfini pour démarrer rapidement"
        )

        # Application automatique du profil
        if quick_mode == "⚡ Rapide (3 min)":
            num_iterations = 3
            warmup_iterations = 1
            concurrent_queries = 1
            query_timeout = 30
            # Sélection automatique des requêtes pour profil rapide
            # Utilise les clés internes attendues par filter_queries_by_selection()
            default_query_types = {
                "run_basic_queries": True,
                "run_filter_queries": False,
                "run_optional_queries": False,
                "run_join_queries": False,
                "run_aggregation_queries": False,
                "run_subqueries": False
            }
            # Pour l'affichage visuel
            display_query_types = {
                "Requêtes SELECT basiques": True,
                "Requêtes avec FILTER": False,
                "Requêtes avec OPTIONAL": False,
                "Requêtes complexes (JOIN)": False,
                "Requêtes d'agrégation": False,
                "Sous-requêtes": False
            }
        elif quick_mode == "⚙️ Standard (10 min)":
            num_iterations = 5
            warmup_iterations = 2
            concurrent_queries = 1
            query_timeout = 60
            # Sélection automatique des requêtes pour profil standard
            default_query_types = {
                "run_basic_queries": True,
                "run_filter_queries": True,
                "run_optional_queries": True,
                "run_join_queries": True,
                "run_aggregation_queries": True,
                "run_subqueries": False
            }
            # Pour l'affichage visuel
            display_query_types = {
                "Requêtes SELECT basiques": True,
                "Requêtes avec FILTER": True,
                "Requêtes avec OPTIONAL": True,
                "Requêtes complexes (JOIN)": True,
                "Requêtes d'agrégation": True,
                "Sous-requêtes": False
            }
        elif quick_mode == "🔬 Complet (30 min)":
            num_iterations = 10
            warmup_iterations = 3
            concurrent_queries = 2
            query_timeout = 120
            # Sélection automatique des requêtes pour profil complet
            default_query_types = {
                "run_basic_queries": True,
                "run_filter_queries": True,
                "run_optional_queries": True,
                "run_join_queries": True,
                "run_aggregation_queries": True,
                "run_subqueries": True
            }
            # Pour l'affichage visuel
            display_query_types = {
                "Requêtes SELECT basiques": True,
                "Requêtes avec FILTER": True,
                "Requêtes avec OPTIONAL": True,
                "Requêtes complexes (JOIN)": True,
                "Requêtes d'agrégation": True,
                "Sous-requêtes": True
            }
        else:  # Personnalisé
            default_query_types = None
            display_query_types = None
            # Afficher les contrôles détaillés seulement si personnalisé
            with st.expander("⚙️ Paramètres avancés", expanded=False):
                num_iterations = st.slider(
                    "Itérations",
                    min_value=1,
                    max_value=20,
                    value=DEFAULT_NUM_ITERATIONS
                )

                warmup_iterations = st.slider(
                    "Échauffement",
                    min_value=0,
                    max_value=5,
                    value=DEFAULT_WARMUP_ITERATIONS
                )

                concurrent_queries = st.slider(
                    "Concurrence",
                    min_value=1,
                    max_value=10,
                    value=DEFAULT_CONCURRENT_QUERIES
                )

                query_timeout = st.slider(
                    "Timeout (s)",
                    min_value=10,
                    max_value=300,
                    value=60
                )

        # Affichage visuel du profil sélectionné
        if quick_mode != "⚙️ Personnalisé":
            with st.expander("📋 Requêtes sélectionnées", expanded=False):
                selected_count = sum(1 for v in display_query_types.values() if v)
                st.info(f"✅ {selected_count} types de requêtes activés")

                for query_type, is_selected in display_query_types.items():
                    if is_selected:
                        st.text(f"✓ {query_type}")

        st.markdown("---")

        # ============================================================
        # SECTION 2: ENDPOINTS (SIMPLIFIÉ)
        # ============================================================
        st.subheader("🔗 Endpoints")

        # Détection automatique depuis .env
        use_env_config = st.checkbox(
            "Utiliser configuration .env",
            value=True,
            help="Charger automatiquement depuis le fichier .env"
        )

        if use_env_config:
            try:
                from config.env_loader import get_env
                virtuoso_endpoint = get_env("VIRTUOSO_ENDPOINT", DEFAULT_VIRTUOSO_ENDPOINT)
                fuseki_endpoint = get_env("FUSEKI_ENDPOINT", DEFAULT_FUSEKI_ENDPOINT)

                st.success("✅ Config .env chargée")
                with st.expander("Voir les endpoints"):
                    st.code(f"Virtuoso: {virtuoso_endpoint}")
                    st.code(f"Fuseki: {fuseki_endpoint}")
            except:
                st.warning("⚠️ Fichier .env non trouvé, utilisation valeurs par défaut")
                virtuoso_endpoint = DEFAULT_VIRTUOSO_ENDPOINT
                fuseki_endpoint = DEFAULT_FUSEKI_ENDPOINT
        else:
            # Configuration manuelle (dans expander pour économiser l'espace)
            with st.expander("✏️ Configuration manuelle"):
                virtuoso_endpoint = st.text_input(
                    "Virtuoso",
                    value=DEFAULT_VIRTUOSO_ENDPOINT
                )
                fuseki_endpoint = st.text_input(
                    "Fuseki",
                    value=DEFAULT_FUSEKI_ENDPOINT
                )

        st.markdown("---")

        # ============================================================
        # SECTION 3: JEU DE DONNÉES (SIMPLIFIÉ)
        # ============================================================
        st.subheader("📊 Dataset")

        dataset_choice = st.selectbox(
            "Type",
            AVAILABLE_DATASETS,
            index=0,
            help="Type de jeu de données pour les requêtes"
        )

        dataset_file = None
        if dataset_choice == "Personnalisé":
            dataset_file = st.file_uploader(
                "Fichier RDF",
                type=["rdf", "ttl", "nt", "n3"]
            )

        st.markdown("---")

        # ============================================================
        # SECTION 4: ACTIONS RAPIDES (NOUVEAU)
        # ============================================================
        st.subheader("⚡ Actions rapides")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔍 Test", use_container_width=True, help="Tester la connectivité"):
                st.session_state['action_requested'] = 'test_connectivity'

        with col2:
            if st.button("💾 Save", use_container_width=True, help="Sauvegarder la configuration"):
                st.session_state['action_requested'] = 'save_config'

        # Bouton de réinitialisation
        if st.button("🔄 Réinitialiser", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.rerun()

        st.markdown("---")

        # ============================================================
        # SECTION 5: STATUT (NOUVEAU - COMPACT)
        # ============================================================
        st.subheader("📊 Statut")

        # Indicateurs de connectivité compacts
        virtuoso_status = st.session_state.get('virtuoso_connected', None)
        fuseki_status = st.session_state.get('fuseki_connected', None)

        status_col1, status_col2 = st.columns(2)

        with status_col1:
            if virtuoso_status is True:
                st.success("✅ Virtuoso")
            elif virtuoso_status is False:
                st.error("❌ Virtuoso")
            else:
                st.info("⚪ Virtuoso")

        with status_col2:
            if fuseki_status is True:
                st.success("✅ Fuseki")
            elif fuseki_status is False:
                st.error("❌ Fuseki")
            else:
                st.info("⚪ Fuseki")

        # Indicateur de synchronisation
        sync_status = st.session_state.get('datasets_synchronized', None)
        if sync_status is True:
            st.success("🔄 Datasets synchronisés")
        elif sync_status is False:
            st.warning("⚠️ Datasets non synchronisés")

        st.markdown("---")

        # ============================================================
        # SECTION 6: AIDE CONTEXTUELLE (COMPACT)
        # ============================================================
        with st.expander("❓ Aide rapide"):
            st.markdown("""
            **Workflow recommandé:**
            1. Choisir un profil rapide
            2. Tester la connectivité
            3. Lancer les tests
            4. Analyser les résultats

            [📖 Documentation complète →](docs/README.md)
            """)

        # ============================================================
        # FOOTER (COMPACT)
        # ============================================================
        st.markdown("---")
        st.caption("v2.0 | Mémoire M2 GL")

    # ============================================================
    # RETOUR DE LA CONFIGURATION
    # ============================================================
    # Les query_types sont automatiquement définis selon le profil choisi
    # ou récupérés depuis session_state pour le mode personnalisé

    # Si on a des query_types par défaut (profils prédéfinis), on les stocke dans session_state
    if 'default_query_types' in locals() and default_query_types is not None:
        st.session_state['query_types'] = default_query_types
        query_types_to_use = default_query_types
    else:
        # Mode personnalisé : récupérer depuis session_state ou utiliser vide
        query_types_to_use = st.session_state.get('query_types', {})

    return {
        "virtuoso_endpoint": virtuoso_endpoint,
        "fuseki_endpoint": fuseki_endpoint,
        "dataset_choice": dataset_choice,
        "dataset_file": dataset_file,
        "num_iterations": num_iterations,
        "warmup_iterations": warmup_iterations,
        "concurrent_queries": concurrent_queries,
        "query_timeout": query_timeout,
        "quick_mode": quick_mode,
        # Query types automatiquement définis selon le profil
        "query_types": query_types_to_use,
        # Options avancées depuis session_state
        "metrics_mode": st.session_state.get('metrics_mode', 'Standard'),
        "collect_network_metrics": st.session_state.get('collect_network_metrics', False),
        "auto_save_results": st.session_state.get('auto_save_results', True),
        "debug_mode": st.session_state.get('debug_mode', False),
        "metrics_interval": st.session_state.get('metrics_interval', 1000),
        "test_profile": quick_mode
    }


def render_sidebar_legacy() -> dict:
    """
    Version LEGACY de la sidebar (ancienne version complète)
    Gardée pour compatibilité

    Returns:
        Dictionnaire contenant la configuration utilisateur
    """
    # Import de l'ancienne version
    from ui.sidebar import render_sidebar
    return render_sidebar()


def get_sidebar_version() -> str:
    """
    Retourne la version de sidebar à utiliser depuis session_state

    Returns:
        'optimized' ou 'legacy'
    """
    return st.session_state.get('sidebar_version', 'optimized')


def toggle_sidebar_version():
    """
    Permet de basculer entre la version optimisée et legacy
    """
    current = get_sidebar_version()
    new_version = 'legacy' if current == 'optimized' else 'optimized'
    st.session_state['sidebar_version'] = new_version


# ============================================================
# FONCTION PRINCIPALE À UTILISER
# ============================================================
def render_sidebar_v2() -> dict:
    """
    Point d'entrée principal pour la sidebar v2
    Utilise la version optimisée par défaut, avec option de basculer

    Returns:
        Dictionnaire contenant la configuration utilisateur 
    """
    version = get_sidebar_version()

    if version == 'optimized':
        return render_sidebar_optimized()
    else:
        return render_sidebar_legacy()
