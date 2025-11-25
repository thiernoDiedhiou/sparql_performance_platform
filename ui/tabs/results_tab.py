"""
Onglet d'affichage des résultats de tests
"""

import streamlit as st
import pandas as pd
from utils.data_manager import get_test_results, is_test_completed
from visualization.visualizer import ResultVisualizer
from utils.helpers import (
    format_duration,
    create_benchmark_summary,
    validate_results_schema,
    compute_summary_stats,
    compute_extreme_performances,
    filter_results_cached,
    handle_visualization_errors
)
from config.settings import UI_MAX_ROWS_OPTIONS, UI_DEFAULT_MAX_ROWS, UI_TOP_N_EXTREME

@handle_visualization_errors(default_return=None, show_error=True)
def render_results_tab():
    """Affiche l'onglet des résultats"""
    st.header("Résultats des tests")

    if not is_test_completed():
        st.info("ℹ️ Aucun test n'a encore été exécuté. Allez dans l'onglet 'Configuration et tests' pour lancer les tests.")
        return

    results_df = get_test_results()

    if results_df is None or results_df.empty:
        st.warning("⚠️ Aucun résultat disponible.")
        return

    # Validation du schéma des données
    validation = validate_results_schema(results_df)
    if not validation["valid"]:
        st.error(f"❌ Données invalides: {', '.join(validation['errors'])}")
        return

    if validation["warnings"]:
        with st.expander("⚠️ Avertissements de validation"):
            for warning in validation["warnings"]:
                st.warning(warning)
    
    # Résumé exécutif
    render_executive_summary(results_df)
    
    # Filtrage des résultats
    filtered_df = render_results_filters(results_df)
    
    if filtered_df.empty:
        st.warning("Aucun résultat disponible après filtrage.")
        return
    
    # Tableau récapitulatif
    render_summary_table(filtered_df)
    
    # Résultats détaillés
    render_detailed_results(filtered_df)
    
    # Statistiques de performance
    render_performance_statistics(filtered_df)
    
    # Performances extrêmes
    render_extreme_performances(filtered_df)

def render_executive_summary(results_df: pd.DataFrame):
    """
    Affiche un résumé exécutif des résultats
    
    Args:
        results_df: DataFrame des résultats
    """
    st.subheader("Résumé exécutif")
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_executions = len(results_df)
        st.metric("Exécutions totales", total_executions)
    
    with col2:
        if 'query_name' in results_df.columns:
            unique_queries = results_df['query_name'].nunique()
        else:
            unique_queries = 1
        st.metric("Requêtes testées", unique_queries)
    
    with col3:
        if 'engine' in results_df.columns:
            engines_tested = results_df['engine'].nunique()
        else:
            engines_tested = 1
        st.metric("Moteurs testés", engines_tested)
    
    with col4:
        if 'success' in results_df.columns:
            success_rate = results_df['success'].mean() * 100
        else:
            success_rate = 0
        st.metric("Taux de succès", f"{success_rate:.1f}%")
    
    # Performance globale
    st.subheader("Performance globale")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'execution_time' in results_df.columns:
            avg_time = results_df['execution_time'].mean()
            st.metric("Temps moyen", format_duration(avg_time))
        
    with col2:
        if 'execution_time' in results_df.columns:
            min_time = results_df['execution_time'].min()
            st.metric("Temps minimum", format_duration(min_time))
    
    with col3:
        if 'execution_time' in results_df.columns:
            max_time = results_df['execution_time'].max()
            st.metric("Temps maximum", format_duration(max_time))
    
    # Comparaison par moteur
    if 'engine' in results_df.columns and 'execution_time' in results_df.columns:
        st.subheader("Comparaison par moteur")
        
        engine_comparison = results_df.groupby('engine').agg({
            'execution_time': ['mean', 'count'],
            'success': 'mean'
        }).round(4)
        
        engine_comparison.columns = ['Temps moyen (s)', 'Exécutions', 'Taux de succès']
        engine_comparison['Taux de succès'] = (engine_comparison['Taux de succès'] * 100).round(2)
        
        st.dataframe(engine_comparison, use_container_width=True)
        
        # Recommandation rapide
        best_engine = engine_comparison['Temps moyen (s)'].idxmin()
        st.success(f"**Moteur le plus performant:** {best_engine}")

@handle_visualization_errors(default_return=pd.DataFrame(), show_error=True)
def render_results_filters(results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Affiche les filtres pour les résultats et retourne les données filtrées

    Args:
        results_df: DataFrame des résultats

    Returns:
        DataFrame filtré
    """
    st.subheader("Filtrage des résultats")

    col1, col2, col3 = st.columns(3)

    engine_filter = []
    query_filter = []
    success_only = False

    with col1:
        # Filtre par moteur
        if 'engine' in results_df.columns:
            engines = list(results_df['engine'].unique())
            engine_filter = st.multiselect(
                "Moteur SPARQL",
                options=engines,
                default=engines,
                help="Sélectionnez les moteurs à afficher"
            )

    with col2:
        # Filtre par requête
        if 'query_name' in results_df.columns:
            queries = list(results_df['query_name'].unique())
            query_filter = st.multiselect(
                "Requête",
                options=queries,
                default=queries,
                help="Sélectionnez les requêtes à afficher"
            )

    with col3:
        # Filtre par statut de succès
        success_filter = st.radio(
            "Statut",
            options=["Tous", "Succès seulement", "Échecs seulement"],
            index=0,
            help="Filtrer par statut d'exécution"
        )

    # Déterminer le mode de filtrage de succès
    if success_filter == "Succès seulement":
        success_only = True
    elif success_filter == "Échecs seulement":
        # Gérer ce cas séparément car filter_results_cached ne le supporte pas directement
        success_only = False

    # Utilisation de la fonction cachée pour le filtrage
    filtered_df = filter_results_cached(
        results_df,
        engine_filter=engine_filter,
        query_filter=query_filter,
        success_only=success_only
    )

    # Filtrer les échecs si nécessaire
    if success_filter == "Échecs seulement" and 'success' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['success'] == False]

    # Affichage du nombre de résultats après filtrage
    st.info(f"{len(filtered_df)} résultats affichés (sur {len(results_df)} au total)")

    return filtered_df

def render_summary_table(filtered_df: pd.DataFrame):
    """
    Affiche le tableau récapitulatif des performances
    
    Args:
        filtered_df: DataFrame filtré des résultats
    """
    st.subheader("📋 Tableau récapitulatif")
    
    try:
        visualizer = ResultVisualizer()
        summary_table = visualizer.create_summary_table(filtered_df)
        
        # Configuration de l'affichage du dataframe
        st.dataframe(
            summary_table,
            use_container_width=True,
            height=400
        )
        
        # Bouton de téléchargement du résumé
        csv_summary = summary_table.to_csv(index=False)
        st.download_button(
            label="📥 Télécharger le résumé (CSV)",
            data=csv_summary,
            file_name="resume_performance_sparql.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"Erreur lors de la création du tableau récapitulatif: {str(e)}")

def render_detailed_results(filtered_df: pd.DataFrame):
    """
    Affiche les résultats détaillés
    
    Args:
        filtered_df: DataFrame filtré des résultats
    """
    st.subheader("📄 Résultats détaillés")
    
    # Options d'affichage
    col1, col2 = st.columns(2)
    
    with col1:
        show_all_columns = st.checkbox("Afficher toutes les colonnes", value=False)
    
    with col2:
        max_rows = st.selectbox(
            "Nombre de lignes à afficher",
            options=UI_MAX_ROWS_OPTIONS,
            index=0
        )
    
    # Préparation des données
    display_df = filtered_df.copy()
    
    if not show_all_columns:
        # Colonnes essentielles
        essential_columns = ['query_name', 'engine', 'iteration', 'execution_time', 'success', 'result_count']
        available_columns = [col for col in essential_columns if col in display_df.columns]
        display_df = display_df[available_columns]
    
    # Formatage des colonnes numériques
    if 'execution_time' in display_df.columns:
        display_df['execution_time'] = display_df['execution_time'].round(4)
    if 'cpu_usage' in display_df.columns:
        display_df['cpu_usage'] = display_df['cpu_usage'].round(2)
    if 'memory_usage' in display_df.columns:
        display_df['memory_usage'] = display_df['memory_usage'].round(2)
    
    # Limitation du nombre de lignes
    if max_rows != "Toutes":
        display_df = display_df.head(max_rows)
    
    # Affichage
    st.dataframe(
        display_df,
        use_container_width=True,
        height=500
    )
    
    # Bouton de téléchargement des résultats détaillés
    csv_detailed = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Télécharger les résultats détaillés (CSV)",
        data=csv_detailed,
        file_name="resultats_detailles_sparql.csv",
        mime="text/csv"
    )

def render_performance_statistics(filtered_df: pd.DataFrame):
    """
    Affiche les statistiques de performance
    
    Args:
        filtered_df: DataFrame filtré des résultats
    """
    st.subheader("Statistiques de performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Temps d'exécution (secondes)**")
        if 'execution_time' in filtered_df.columns:
            execution_stats = filtered_df.groupby(['query_name', 'engine'])['execution_time'].describe()
            st.dataframe(execution_stats.round(4), use_container_width=True)
        else:
            st.info("Données de temps d'exécution non disponibles")
    
    with col2:
        st.write("**Utilisation des ressources**")
        if all(col in filtered_df.columns for col in ['cpu_usage', 'memory_usage']):
            resource_stats = filtered_df.groupby(['query_name', 'engine']).agg({
                'cpu_usage': ['mean', 'max'],
                'memory_usage': ['mean', 'max']
            }).round(2)
            
            resource_stats.columns = ['CPU moy.', 'CPU max', 'Mém. moy.', 'Mém. max']
            st.dataframe(resource_stats, use_container_width=True)
        else:
            st.info("Données de ressources non disponibles")

@handle_visualization_errors(default_return=None, show_error=True)
def render_extreme_performances(filtered_df: pd.DataFrame):
    """
    Affiche les performances extrêmes (meilleures et pires)

    Args:
        filtered_df: DataFrame filtré des résultats
    """
    st.subheader("🏁 Performances extrêmes")

    if 'execution_time' not in filtered_df.columns:
        st.info("Données de temps d'exécution non disponibles")
        return

    # Utilisation de la fonction cachée
    extreme_perfs = compute_extreme_performances(filtered_df, top_n=UI_TOP_N_EXTREME)

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**🚀 Top {UI_TOP_N_EXTREME} des exécutions les plus rapides**")
        fastest = extreme_perfs["fastest"]

        if not fastest.empty:
            fastest = fastest.copy()
            fastest['execution_time'] = fastest['execution_time'].apply(format_duration)
            fastest.columns = ['Moteur', 'Requête', 'Temps', 'Itération'] if len(fastest.columns) == 4 else fastest.columns
            st.dataframe(fastest, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune donnée disponible")

    with col2:
        st.write(f"**🐌 Top {UI_TOP_N_EXTREME} des exécutions les plus lentes**")
        slowest = extreme_perfs["slowest"]

        if not slowest.empty:
            slowest = slowest.copy()
            slowest['execution_time'] = slowest['execution_time'].apply(format_duration)
            slowest.columns = ['Moteur', 'Requête', 'Temps', 'Itération'] if len(slowest.columns) == 4 else slowest.columns
            st.dataframe(slowest, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune donnée disponible")
    
    # Analyse des écarts de performance
    if 'query_name' in filtered_df.columns and 'engine' in filtered_df.columns:
        st.subheader("Analyse des écarts de performance")
        
        # Calcul des ratios de performance entre moteurs
        try:
            performance_analysis = analyze_performance_gaps(filtered_df)
            
            if performance_analysis:
                st.write("**Comparaison Virtuoso vs Jena Fuseki:**")
                
                for analysis in performance_analysis:
                    if analysis['ratio'] < 0.95:
                        emoji = "🟢"
                        status = "Virtuoso plus rapide"
                    elif analysis['ratio'] > 1.05:
                        emoji = "🔴"
                        status = "Fuseki plus rapide"
                    else:
                        emoji = "🟡"
                        status = "Performances similaires"
                    
                    st.write(f"{emoji} **{analysis['query']}**: {status} (ratio: {analysis['ratio']:.2f})")
            
        except Exception as e:
            st.error(f"Erreur lors de l'analyse des écarts: {str(e)}")

def analyze_performance_gaps(df: pd.DataFrame) -> list:
    """
    Analyse les écarts de performance entre moteurs
    
    Args:
        df: DataFrame des résultats
        
    Returns:
        Liste des analyses par requête
    """
    try:
        # Grouper par requête et moteur
        grouped = df.groupby(['query_name', 'engine'])['execution_time'].mean().reset_index()
        
        analysis_results = []
        
        # Pour chaque requête, comparer Virtuoso et Fuseki
        for query in grouped['query_name'].unique():
            query_data = grouped[grouped['query_name'] == query]
            
            virtuoso_data = query_data[query_data['engine'].str.contains('Virtuoso', case=False)]
            fuseki_data = query_data[query_data['engine'].str.contains('Fuseki', case=False)]
            
            if not virtuoso_data.empty and not fuseki_data.empty:
                virtuoso_time = virtuoso_data['execution_time'].iloc[0]
                fuseki_time = fuseki_data['execution_time'].iloc[0]
                
                ratio = virtuoso_time / fuseki_time if fuseki_time > 0 else float('inf')
                
                analysis_results.append({
                    'query': query,
                    'virtuoso_time': virtuoso_time,
                    'fuseki_time': fuseki_time,
                    'ratio': ratio
                })
        
        return analysis_results
        
    except Exception as e:
        return []