"""
Onglet de configuration et exécution des tests
Version mise à jour avec support de la synchronisation des données
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any
from core.tester import SPARQLPerformanceTester
from queries.catalog import SPARQLQueryCatalog
from ui.components.connectivity_checker import ConnectivityChecker
from ui.components.system_info import SystemInfoDisplay
from utils.data_manager import save_test_results
from utils.helpers import log_message, filter_queries_by_selection
from utils.dataset_manager import DatasetManager


def render_configuration_tab(sidebar_config: Dict[str, Any]):
    """
    Affiche l'onglet de configuration et tests avec support de synchronisation
    
    Args:
        sidebar_config: Configuration de la barre latérale
    """
    st.header("Configuration et exécution des tests") 
    
    # En-tête avec informations
    st.markdown("""
        Cette section permet de configurer les endpoints, sélectionner les requêtes,
        vérifier la connectivité, synchroniser les datasets et exécuter les tests de performance.
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Vérification de la connectivité")
        
        # Composant de vérification de connectivité
        connectivity_checker = ConnectivityChecker()

        # Charger les métadonnées pour obtenir les graph_uri
        dataset_manager = DatasetManager(datasets_path="datasets")
        metadata = dataset_manager.load_all_metadata()
        virtuoso_graph_uri = metadata.get('virtuoso', {}).get('graph_uri') if metadata else None
        fuseki_graph_uri = metadata.get('fuseki', {}).get('graph_uri') if metadata else None

        if st.button("Tester la connectivité"):
            with st.spinner("Test de connectivité en cours..."):
                virtuoso_status = connectivity_checker.test_endpoint(
                    sidebar_config["virtuoso_endpoint"], "Virtuoso", virtuoso_graph_uri
                )
                fuseki_status = connectivity_checker.test_endpoint(
                    sidebar_config["fuseki_endpoint"], "Jena Fuseki", fuseki_graph_uri
                )
                
                st.write(f"**Virtuoso:** {virtuoso_status['message']}")
                st.write(f"**Jena Fuseki:** {fuseki_status['message']}")
                
                # Stockage de l'état de connectivité dans session_state (NOUVEAU)
                st.session_state['virtuoso_connected'] = virtuoso_status['status'] == 'online'
                st.session_state['fuseki_connected'] = fuseki_status['status'] == 'online'
                st.session_state['all_endpoints_connected'] = (
                    st.session_state['virtuoso_connected'] and st.session_state['fuseki_connected']
                )
                
                # Stockage des endpoints pour la synchronisation (NOUVEAU)
                st.session_state['virtuoso_endpoint'] = sidebar_config["virtuoso_endpoint"]
                st.session_state['fuseki_endpoint'] = sidebar_config["fuseki_endpoint"]
                
                if st.session_state['all_endpoints_connected']:
                    st.success("✅ Tous les endpoints sont accessibles!")
                else:
                    st.warning("⚠️ Certains endpoints ne sont pas accessibles")
    
    with col2:
        st.subheader("Informations sur l'environnement")
        
        # Composant d'information système
        system_info = SystemInfoDisplay()
        
        if st.button("Afficher les informations système"):
            info = system_info.get_system_summary()
            for key, value in info.items():
                st.write(f"**{key}:** {value}")
    
    # ============================================================================
    # NOUVELLE SECTION: SYNCHRONISATION DES DONNÉES
    # ============================================================================
    if st.session_state.get('all_endpoints_connected', False):
        st.markdown("---")
        st.subheader("🔄 Synchronisation des données")
        
        try:
            # Import conditionnel pour éviter les erreurs
            from ui.components.data_sync_ui import render_data_synchronization_ui
            
            render_data_synchronization_ui(
                sidebar_config["virtuoso_endpoint"],
                sidebar_config["fuseki_endpoint"]
            )
            
        except ImportError:
            st.warning("⚠️ Module de synchronisation non disponible")
            st.info("Les fonctionnalités de synchronisation seront disponibles après l'installation complète du module.")
            
            # Interface basique de vérification (FALLBACK)
            if st.button("Vérification basique des datasets"):
                try:
                    from utils.helpers import get_sync_status_summary
                    status = get_sync_status_summary()
                    
                    if status["status"] == "synchronized":
                        st.success(f"✅ {status['message']}")
                    elif status["status"] == "not_synchronized":
                        st.warning(f"⚠️ {status['message']}")
                        st.info(f"{status['action_needed']}")
                    else:
                        st.error(f"❌ {status['message']}")
                        
                except Exception as e:
                    st.error(f"Erreur lors de la vérification: {str(e)}")
        
        except Exception as e:
            st.warning(f"⚠️ Synchronisation non disponible: {str(e)}")
            
        st.markdown("---")
    
    # ============================================================================
    # SECTION ORIGINALE: SÉLECTION DES REQUÊTES (INCHANGÉE)
    # ============================================================================
    st.subheader("Sélection des requêtes")
    
    # Récupération du catalogue de requêtes
    query_catalog = SPARQLQueryCatalog()
    all_queries = query_catalog.get_queries_by_type(sidebar_config["dataset_choice"])
    
    # Filtrage des requêtes selon la sélection
    selected_queries = filter_queries_by_selection(all_queries, sidebar_config["query_types"])
    
    # Affichage des requêtes sélectionnées
    if selected_queries:
        st.write(f"**{len(selected_queries)} requêtes sélectionnées:**")
        
        # Affichage en accordéon
        for query_name, query in selected_queries.items():
            with st.expander(f"📝 {query_name}"):
                st.code(query, language="sparql")
                
                # Estimation de complexité
                complexity = query_catalog.get_query_complexity_estimate(query)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Complexité", complexity["level"])
                with col2:
                    st.metric("Score", complexity["score"])
                with col3:
                    st.metric("Temps estimé", complexity["estimated_execution_time"])
    else:
        st.warning("Aucune requête sélectionnée. Veuillez choisir au moins un type de requête dans la barre latérale.")
    
    # Requête personnalisée
    st.subheader("Requête personnalisée")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        custom_query_name = st.text_input(
            "Nom de la requête personnalisée", 
            value="Ma requête personnalisée"
        )
        
        custom_query = st.text_area(
            "Entrez votre requête SPARQL personnalisée",
            value="""SELECT ?s ?p ?o
WHERE {
    ?s ?p ?o .
}
LIMIT 10""",
            height=150
        )
    
    with col2:
        st.write("**Validation:**")
        if custom_query.strip():
            validation = query_catalog.validate_query(custom_query)
            if validation["valid"]:
                st.success("✅ Syntaxe valide")
                complexity = query_catalog.get_query_complexity_estimate(custom_query)
                st.info(f"Complexité: {complexity['level']}")
            else:
                st.error(f"❌ {validation['error']}")
    
    include_custom = st.checkbox("Inclure la requête personnalisée", value=False)
    
    if include_custom and custom_query.strip():
        selected_queries[custom_query_name] = custom_query
    
    # Résumé de la configuration
    st.subheader("Résumé de la configuration")
    
    config_summary = f"""
    **Endpoints:**
    - Virtuoso: `{sidebar_config["virtuoso_endpoint"]}`
    - Jena Fuseki: `{sidebar_config["fuseki_endpoint"]}`
    
    **Jeu de données:** {sidebar_config["dataset_choice"]}
    
    **Paramètres de test:**
    - Itérations: {sidebar_config["num_iterations"]}
    - Échauffement: {sidebar_config["warmup_iterations"]}
    - Concurrence: {sidebar_config["concurrent_queries"]}
    - Timeout: {sidebar_config["query_timeout"]}s
    
    **Requêtes sélectionnées:** {len(selected_queries)}
    """
    
    st.markdown(config_summary)
    
    # ============================================================================
    # VÉRIFICATION DE LA SYNCHRONISATION AVANT LES TESTS (NOUVEAU)
    # ============================================================================
    sync_status = None
    if st.session_state.get('all_endpoints_connected', False):
        try:
            from utils.helpers import get_sync_status_summary
            sync_status = get_sync_status_summary()
            
            if not sync_status.get("can_test", False):
                st.warning("⚠️ Les datasets ne sont pas synchronisés. Les tests pourraient donner des résultats incorrects.")
                
        except Exception:
            pass  # Ignorer les erreurs de vérification de synchronisation
    
    # ============================================================================
    # BOUTON D'EXÉCUTION DES TESTS (MODIFIÉ)
    # ============================================================================
    if st.button("Exécuter les tests", type="primary", use_container_width=True):
        if not selected_queries:
            st.error("❌ Veuillez sélectionner au moins une requête à tester.")
        elif not st.session_state.get('all_endpoints_connected', False):
            st.error("❌ Veuillez d'abord vérifier la connectivité des endpoints.")
        else:
            # Avertissement de synchronisation si nécessaire (NOUVEAU)
            if sync_status and not sync_status.get("can_test", False):
                st.warning("⚠️ Attention: Les datasets ne semblent pas synchronisés. Voulez-vous continuer ?")
                if not st.button("Continuer malgré tout"):
                    st.stop()
            
            # Appel de la nouvelle fonction avec validation (MODIFIÉ)
            execute_tests_with_validation(selected_queries, sidebar_config)


# ============================================================================
# NOUVELLE FONCTION: EXÉCUTION DES TESTS AVEC VALIDATION
# ============================================================================
def execute_tests_with_validation(selected_queries: Dict[str, str], config: Dict[str, Any]):
    """
    Version mise à jour de execute_tests avec validation des datasets

    Args:
        selected_queries: Dictionnaire des requêtes sélectionnées
        config: Configuration des tests
    """
    try:
        # Charger les graph URIs depuis les métadonnées pour des benchmarks équitables
        import json
        from pathlib import Path

        metadata_file = Path("datasets_metadata.json")
        virtuoso_graph_uri = None
        fuseki_graph_uri = None

        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

                if "virtuoso" in metadata and "graph_uri" in metadata["virtuoso"]:
                    virtuoso_graph_uri = metadata["virtuoso"]["graph_uri"]
                    log_message(f"Graph URI Virtuoso chargé: {virtuoso_graph_uri}", "debug")

                if "fuseki" in metadata and "graph_uri" in metadata["fuseki"]:
                    fuseki_graph_uri = metadata["fuseki"]["graph_uri"]
                    log_message(f"Graph URI Fuseki chargé: {fuseki_graph_uri}", "debug")
        else:
            log_message("Fichier datasets_metadata.json non trouvé, wrapping désactivé", "warning")

        # Initialisation du testeur avec graph URIs pour benchmarks équitables
        tester = SPARQLPerformanceTester(
            config["virtuoso_endpoint"],
            config["fuseki_endpoint"],
            virtuoso_graph_uri=virtuoso_graph_uri,
            fuseki_graph_uri=fuseki_graph_uri
        )

        # NOUVELLE ÉTAPE: Validation des datasets
        st.subheader("Validation des datasets")
        
        # Validation avec gestion d'erreur
        validation_passed = False
        
        try:
            from utils.helpers import get_sync_status_summary
            status = get_sync_status_summary()
            
            if status["status"] == "error":
                st.error(f"❌ {status['message']}")
                return
            elif status["status"] == "not_synchronized":
                st.warning(f"⚠️ {status['message']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Synchroniser maintenant"):
                        try:
                            from utils.data_synchronizer import DataSynchronizer
                            synchronizer = DataSynchronizer(
                                config["virtuoso_endpoint"],
                                config["fuseki_endpoint"]
                            )
                            success = synchronizer.synchronize_datasets()
                            if success:
                                st.success("✅ Synchronisation réussie")
                                validation_passed = True
                                st.rerun()
                            else:
                                st.error("❌ Échec de la synchronisation")
                                return
                        except Exception as e:
                            st.error(f"❌ Erreur de synchronisation: {str(e)}")
                            return
                
                with col2:
                    if st.button("Continuer sans synchronisation"):
                        st.warning("⚠️ Les résultats peuvent être incorrects avec des datasets différents")
                        validation_passed = True
                
                if not validation_passed:
                    return
            else:
                st.success(f"✅ {status['message']}")
                validation_passed = True
                
        except Exception as e:
            st.warning(f"⚠️ Impossible de vérifier la synchronisation: {str(e)}")
            validation_passed = st.button("Continuer sans vérification")
        
        if not validation_passed:
            st.error("❌ Impossible de procéder aux tests")
            return
        
        # Configuration du timeout
        tester.executor.set_timeout(config["query_timeout"])
        
        # Création des barres de progression
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Conteneur pour les résultats intermédiaires
        results_container = st.empty()
        
        # Stockage des résultats
        results_df = pd.DataFrame()
        total_queries = len(selected_queries)
        
        log_message(f"Début des tests: {total_queries} requêtes")
        
        # Exécution des tests pour chaque requête
        for i, (query_name, query) in enumerate(selected_queries.items()):
            progress = i / total_queries
            progress_bar.progress(progress)
            status_text.text(f"🔄 Test en cours: {query_name}")
            
            try:
                # Phase d'échauffement
                if config["warmup_iterations"] > 0:
                    status_text.text(f"🔥 Échauffement: {query_name}")
                    tester.run_benchmark(
                        query_name, 
                        query, 
                        config["warmup_iterations"], 
                        config["warmup_iterations"], 
                        is_warmup=True
                    )
                
                # Exécution principale
                status_text.text(f"⚡ Exécution: {query_name}")
                query_results = tester.run_benchmark(
                    query_name, 
                    query, 
                    config["num_iterations"], 
                    config["warmup_iterations"]
                )
                
                if query_results is not None and not query_results.empty:
                    results_df = pd.concat([results_df, query_results], ignore_index=True)
                
                # Exécution concurrente si demandée
                if config["concurrent_queries"] > 1:
                    status_text.text(f"🔀 Test concurrent: {query_name}")
                    concurrent_results = tester.run_concurrent_benchmark(
                        query_name, 
                        query, 
                        config["num_iterations"], 
                        config["concurrent_queries"]
                    )
                    
                    if concurrent_results is not None and not concurrent_results.empty:
                        results_df = pd.concat([results_df, concurrent_results], ignore_index=True)
                
                # Affichage des résultats intermédiaires
                if not results_df.empty:
                    with results_container.container():
                        st.write(f"**Résultats intermédiaires** ({i+1}/{total_queries} requêtes traitées)")
                        
                        # Statistiques rapides
                        latest_results = results_df[results_df['query_name'].str.contains(query_name)]
                        if not latest_results.empty:
                            avg_time = latest_results['execution_time'].mean()
                            success_rate = latest_results['success'].mean() * 100
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Temps moyen", f"{avg_time:.3f}s")
                            with col2:
                                st.metric("Taux de succès", f"{success_rate:.1f}%")
                            with col3:
                                st.metric("Exécutions", len(latest_results))
                
            except Exception as e:
                log_message(f"Erreur lors du test de {query_name}: {str(e)}", "error")
                st.error(f"❌ Erreur lors du test de {query_name}: {str(e)}")
        
        # Finalisation
        progress_bar.progress(1.0)
        status_text.text("✅ Tests terminés !")
        
        if not results_df.empty:
            # Sauvegarde des résultats
            save_test_results(results_df, config)
            
            # Affichage du résumé final
            st.success(f"🎉 Tests terminés avec succès!")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Requêtes testées", total_queries)
            with col2:
                st.metric("Exécutions totales", len(results_df))
            with col3:
                avg_time = results_df['execution_time'].mean()
                st.metric("Temps moyen", f"{avg_time:.3f}s")
            with col4:
                success_rate = results_df['success'].mean() * 100
                st.metric("Taux de succès global", f"{success_rate:.1f}%")
            
            # Aperçu des résultats
            st.subheader("Aperçu des résultats")
            
            # Comparaison rapide par moteur
            engine_comparison = results_df.groupby('engine').agg({
                'execution_time': 'mean',
                'success': 'mean',
                'cpu_usage': 'mean',
                'memory_usage': 'mean'
            }).round(4)
            
            st.dataframe(engine_comparison, use_container_width=True)
            
            st.info("Consultez l'onglet 'Résultats' pour une analyse détaillée et l'onglet 'Visualisation' pour les graphiques.")
            
        else:
            st.error("❌ Aucun résultat généré. Vérifiez la connectivité et les requêtes.")
            
    except Exception as e:
        log_message(f"Erreur générale lors de l'exécution des tests: {str(e)}", "error")
        st.error(f"❌ Erreur lors de l'exécution des tests: {str(e)}")
        
        # Suggestions de dépannage (MISES À JOUR)
        with st.expander("Suggestions de dépannage"):
            st.markdown("""
            **Problèmes courants et solutions:**
            
            1. **Endpoints non accessibles:**
               - Vérifiez que Virtuoso et Fuseki sont démarrés
               - Testez la connectivité manuellement
               
            2. **Datasets non synchronisés:**
               - Utilisez la fonction de synchronisation
               - Vérifiez que les mêmes données sont chargées
               
            3. **Timeout des requêtes:**
               - Augmentez le timeout dans la barre latérale
               - Utilisez des requêtes plus simples pour commencer
               
            4. **Erreurs de mémoire:**
               - Réduisez le nombre d'itérations
               - Diminuez le niveau de concurrence
               
            5. **Erreurs de synchronisation:**
               - Vérifiez l'espace disque disponible
               - Redémarrez les moteurs SPARQL si nécessaire
               
            6. **Erreurs de syntaxe SPARQL:**
               - Vérifiez vos requêtes personnalisées
               - Utilisez les requêtes prédéfinies pour commencer
            """)
    
    finally:
        # Nettoyage sécurisé
        try:
            if 'progress_bar' in locals():
                progress_bar.empty()
            if 'status_text' in locals():
                status_text.empty()
        except:
            pass  # Ignorer les erreurs de nettoyage


# ============================================================================
# FONCTION ORIGINALE: GARDÉE POUR COMPATIBILITÉ
# ============================================================================
def execute_tests(selected_queries: Dict[str, str], config: Dict[str, Any]):
    """
    Fonction originale d'exécution des tests (gardée pour compatibilité)
    
    Args:
        selected_queries: Dictionnaire des requêtes à tester
        config: Configuration des tests
    """
    # Redirection vers la nouvelle fonction avec validation
    execute_tests_with_validation(selected_queries, config)