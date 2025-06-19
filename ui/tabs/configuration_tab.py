"""
Onglet de configuration et exécution des tests
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

def render_configuration_tab(sidebar_config: Dict[str, Any]):
    """
    Affiche l'onglet de configuration et tests
    
    Args:
        sidebar_config: Configuration de la barre latérale
    """
    st.header("Configuration et exécution des tests")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Vérification de la connectivité")
        
        # Composant de vérification de connectivité
        connectivity_checker = ConnectivityChecker()
        
        if st.button("Tester la connectivité"):
            with st.spinner("Test de connectivité en cours..."):
                virtuoso_status = connectivity_checker.test_endpoint(
                    sidebar_config["virtuoso_endpoint"], "Virtuoso"
                )
                fuseki_status = connectivity_checker.test_endpoint(
                    sidebar_config["fuseki_endpoint"], "Jena Fuseki"
                )
                
                st.write(f"**Virtuoso:** {virtuoso_status['message']}")
                st.write(f"**Jena Fuseki:** {fuseki_status['message']}")
                
                if virtuoso_status['status'] == 'online' and fuseki_status['status'] == 'online':
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
    
    # Bouton d'exécution des tests
    if st.button("🚀 Exécuter les tests", type="primary", use_container_width=True):
        if not selected_queries:
            st.error("❌ Veuillez sélectionner au moins une requête à tester.")
        else:
            execute_tests(selected_queries, sidebar_config)

def execute_tests(selected_queries: Dict[str, str], config: Dict[str, Any]):
    """
    Exécute les tests de performance
    
    Args:
        selected_queries: Dictionnaire des requêtes à tester
        config: Configuration des tests
    """
    try:
        # Initialisation du testeur
        tester = SPARQLPerformanceTester(
            config["virtuoso_endpoint"],
            config["fuseki_endpoint"]
        )
        
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
            
            st.info("📊 Consultez l'onglet 'Résultats' pour une analyse détaillée et l'onglet 'Visualisation' pour les graphiques.")
            
        else:
            st.error("❌ Aucun résultat généré. Vérifiez la connectivité et les requêtes.")
            
    except Exception as e:
        log_message(f"Erreur générale lors de l'exécution des tests: {str(e)}", "error")
        st.error(f"❌ Erreur lors de l'exécution des tests: {str(e)}")
        
        # Suggestions de dépannage
        with st.expander("💡 Suggestions de dépannage"):
            st.markdown("""
            **Problèmes courants et solutions:**
            
            1. **Endpoints non accessibles:**
               - Vérifiez que Virtuoso et Fuseki sont démarrés
               - Testez la connectivité manuellement
               
            2. **Timeout des requêtes:**
               - Augmentez le timeout dans la barre latérale
               - Utilisez des requêtes plus simples pour commencer
               
            3. **Erreurs de mémoire:**
               - Réduisez le nombre d'itérations
               - Diminuez le niveau de concurrence
               
            4. **Erreurs de syntaxe SPARQL:**
               - Vérifiez vos requêtes personnalisées
               - Utilisez les requêtes prédéfinies pour commencer
            """)
    
    finally:
        # Nettoyage
        progress_bar.empty()
        status_text.empty()