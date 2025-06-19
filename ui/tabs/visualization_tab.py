"""
Onglet de visualisation des performances
"""

import streamlit as st
from utils.data_manager import get_test_results, is_test_completed
from visualization.visualizer import ResultVisualizer
from utils.helpers import log_message

def render_visualization_tab():
    """Affiche l'onglet de visualisation"""
    st.header("📊 Visualisation des performances")
    
    if not is_test_completed():
        st.info("ℹ️ Aucun test n'a encore été exécuté. Allez dans l'onglet 'Configuration et tests' pour lancer les tests.")
        return
    
    results_df = get_test_results()
    
    if results_df is None or results_df.empty:
        st.warning("⚠️ Aucun résultat disponible pour la visualisation.")
        return
    
    # Initialisation du visualiseur
    visualizer = ResultVisualizer()
    
    # Sélection du type de visualisation
    viz_type = st.radio(
        "🎨 Type de visualisation",
        options=[
            "Temps d'exécution", 
            "Utilisation ressources", 
            "Comparaison directe", 
            "Tendances de performance",
            "Heatmap des performances",
            "Tableau de bord complet"
        ],
        help="Choisissez le type de visualisation à afficher"
    )
    
    try:
        if viz_type == "Temps d'exécution":
            render_execution_time_charts(visualizer, results_df)
        
        elif viz_type == "Utilisation ressources":
            render_resource_usage_charts(visualizer, results_df)
        
        elif viz_type == "Comparaison directe":
            render_comparison_charts(visualizer, results_df)
        
        elif viz_type == "Tendances de performance":
            render_performance_trends(visualizer, results_df)
        
        elif viz_type == "Heatmap des performances":
            render_performance_heatmap(visualizer, results_df)
        
        elif viz_type == "Tableau de bord complet":
            render_dashboard(visualizer, results_df)
    
    except Exception as e:
        st.error(f"❌ Erreur lors de la génération de la visualisation: {str(e)}")
        log_message(f"Erreur de visualisation: {str(e)}", "error")

def render_execution_time_charts(visualizer: ResultVisualizer, results_df):
    """
    Affiche les graphiques de temps d'exécution
    
    Args:
        visualizer: Instance du visualiseur
        results_df: DataFrame des résultats
    """
    st.subheader("⏱️ Temps d'exécution")
    
    # Sélection de requête spécifique (optionnel)
    query_options = ["Toutes les requêtes"]
    if 'query_name' in results_df.columns:
        query_options.extend(list(results_df['query_name'].unique()))
    
    selected_query = st.selectbox(
        "Sélectionner une requête spécifique (optionnel)",
        options=query_options,
        help="Choisissez une requête pour un affichage détaillé"
    )
    
    # Génération du graphique
    if selected_query == "Toutes les requêtes":
        fig = visualizer.plot_execution_times(results_df)
    else:
        fig = visualizer.plot_execution_times(results_df, selected_query)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Insights automatiques
    insights = visualizer.generate_performance_insights(results_df)
    if 'best_engine' in insights:
        st.success(f"🏆 **Moteur le plus performant:** {insights['best_engine']}")
        
        if 'performance_gap' in insights:
            gap_percent = (insights['performance_gap'] - 1) * 100
            st.info(f"📊 **Écart de performance:** {gap_percent:.1f}% plus lent pour le moteur le moins performant")

def render_resource_usage_charts(visualizer: ResultVisualizer, results_df):
    """
    Affiche les graphiques d'utilisation des ressources
    
    Args:
        visualizer: Instance du visualiseur
        results_df: DataFrame des résultats
    """
    st.subheader("💻 Utilisation des ressources")
    
    # Sélection du type de ressource
    resource_type = st.radio(
        "Type de ressource",
        options=["CPU", "Mémoire"],
        horizontal=True,
        help="Choisissez le type de ressource à analyser"
    )
    
    # Vérification de la disponibilité des données
    required_column = 'cpu_usage' if resource_type == "CPU" else 'memory_usage'
    
    if required_column not in results_df.columns:
        st.warning(f"⚠️ Les données d'utilisation {resource_type.lower()} ne sont pas disponibles.")
        return
    
    # Génération du graphique
    fig = visualizer.plot_resource_usage(results_df, resource_type.lower())
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistiques de ressources
    col1, col2 = st.columns(2)
    
    with col1:
        avg_usage = results_df[required_column].mean()
        st.metric(f"Utilisation {resource_type} moyenne", f"{avg_usage:.2f}{'%' if resource_type == 'CPU' else ' MB'}")
    
    with col2:
        max_usage = results_df[required_column].max()
        st.metric(f"Utilisation {resource_type} maximale", f"{max_usage:.2f}{'%' if resource_type == 'CPU' else ' MB'}")

def render_comparison_charts(visualizer: ResultVisualizer, results_df):
    """
    Affiche les graphiques de comparaison directe
    
    Args:
        visualizer: Instance du visualiseur
        results_df: DataFrame des résultats
    """
    st.subheader("⚖️ Comparaison directe")
    
    # Graphique de dispersion
    fig = visualizer.plot_scatter_comparison(results_df)
    st.plotly_chart(fig, use_container_width=True)
    
    # Analyse comparative détaillée
    st.subheader("📈 Analyse comparative")
    
    try:
        # Calcul des ratios de performance
        virtuoso_times = results_df[results_df['engine'].str.contains('Virtuoso')].groupby('query_name')['execution_time'].mean()
        fuseki_times = results_df[results_df['engine'].str.contains('Fuseki')].groupby('query_name')['execution_time'].mean()
        
        if not virtuoso_times.empty and not fuseki_times.empty:
            ratio = virtuoso_times / fuseki_times
            
            comparison_df = pd.DataFrame({
                'Virtuoso (s)': virtuoso_times.round(4),
                'Jena Fuseki (s)': fuseki_times.round(4),
                'Ratio (V/F)': ratio.round(3)
            }).sort_values('Ratio (V/F)')
            
            st.dataframe(comparison_df, use_container_width=True)
            
            # Messages d'analyse
            virtuoso_better = comparison_df[comparison_df['Ratio (V/F)'] < 0.95].index.tolist()
            fuseki_better = comparison_df[comparison_df['Ratio (V/F)'] > 1.05].index.tolist()
            similar = comparison_df[
                (comparison_df['Ratio (V/F)'] >= 0.95) & 
                (comparison_df['Ratio (V/F)'] <= 1.05)
            ].index.tolist()
            
            if virtuoso_better:
                st.success("**🟢 Virtuoso significativement plus rapide pour:**")
                for query in virtuoso_better[:5]:  # Limiter à 5 pour l'affichage
                    improvement = 1 / comparison_df.loc[query, 'Ratio (V/F)']
                    st.write(f"- {query} ({improvement:.1f}x plus rapide)")
            
            if fuseki_better:
                st.error("**🔴 Jena Fuseki significativement plus rapide pour:**")
                for query in fuseki_better[:5]:
                    improvement = comparison_df.loc[query, 'Ratio (V/F)']
                    st.write(f"- {query} ({improvement:.1f}x plus rapide)")
            
            if similar:
                st.info(f"**🟡 Performances similaires pour {len(similar)} requêtes**")
    
    except Exception as e:
        st.error(f"Erreur lors de l'analyse comparative: {str(e)}")

def render_performance_trends(visualizer: ResultVisualizer, results_df):
    """
    Affiche les tendances de performance
    
    Args:
        visualizer: Instance du visualiseur
        results_df: DataFrame des résultats
    """
    st.subheader("📈 Tendances de performance")
    
    if 'iteration' not in results_df.columns:
        st.warning("⚠️ Les données d'itération ne sont pas disponibles pour l'analyse des tendances.")
        return
    
    # Graphique des tendances
    fig = visualizer.plot_performance_trends(results_df)
    st.plotly_chart(fig, use_container_width=True)
    
    # Analyse de stabilité
    st.subheader("🎯 Analyse de stabilité")
    
    stability_stats = results_df.groupby(['query_name', 'engine'])['execution_time'].agg(['std', 'mean']).reset_index()
    stability_stats['cv'] = (stability_stats['std'] / stability_stats['mean']) * 100  # Coefficient de variation
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🔄 Requêtes les plus stables** (faible variation)")
        most_stable = stability_stats.nsmallest(5, 'cv')[['query_name', 'engine', 'cv']]
        most_stable.columns = ['Requête', 'Moteur', 'Variation (%)']
        st.dataframe(most_stable.round(2), hide_index=True)
    
    with col2:
        st.write("**⚡ Requêtes les plus variables** (forte variation)")
        most_variable = stability_stats.nlargest(5, 'cv')[['query_name', 'engine', 'cv']]
        most_variable.columns = ['Requête', 'Moteur', 'Variation (%)']
        st.dataframe(most_variable.round(2), hide_index=True)

def render_performance_heatmap(visualizer: ResultVisualizer, results_df):
    """
    Affiche la heatmap des performances
    
    Args:
        visualizer: Instance du visualiseur
        results_df: DataFrame des résultats
    """
    st.subheader("🔥 Heatmap des performances")
    
    # Heatmap principale
    fig = visualizer.create_performance_heatmap(results_df)
    st.plotly_chart(fig, use_container_width=True)
    
    # Interprétation
    st.info("""
    **💡 Comment lire cette heatmap:**
    - Les couleurs chaudes (rouge) indiquent des temps d'exécution plus longs
    - Les couleurs froides (bleu) indiquent des temps d'exécution plus courts
    - Comparez horizontalement pour voir les différences entre moteurs
    - Comparez verticalement pour voir la complexité relative des requêtes
    """)

def render_dashboard(visualizer: ResultVisualizer, results_df):
    """
    Affiche un tableau de bord complet
    
    Args:
        visualizer: Instance du visualiseur
        results_df: DataFrame des résultats
    """
    st.subheader("🚀 Tableau de bord complet")
    
    # Vue d'ensemble des métriques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_time = results_df['execution_time'].mean()
        st.metric("⏱️ Temps moyen", f"{avg_time:.3f}s")
    
    with col2:
        success_rate = results_df['success'].mean() * 100
        st.metric("✅ Taux de succès", f"{success_rate:.1f}%")
    
    with col3:
        if 'result_count' in results_df.columns:
            avg_results = results_df['result_count'].mean()
            st.metric("📊 Résultats moyens", f"{avg_results:.0f}")
    
    with col4:
        total_time = results_df['execution_time'].sum()
        st.metric("🕐 Temps total", f"{total_time:.1f}s")
    
    # Graphiques principaux
    st.subheader("📊 Temps d'exécution par requête et moteur")
    fig1 = visualizer.plot_execution_times(results_df)
    st.plotly_chart(fig1, use_container_width=True)
    
    # Graphiques de ressources côte à côte
    col1, col2 = st.columns(2)
    
    with col1:
        if 'cpu_usage' in results_df.columns:
            st.subheader("💻 Utilisation CPU")
            fig2 = visualizer.plot_resource_usage(results_df, 'cpu')
            st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        if 'memory_usage' in results_df.columns:
            st.subheader("🧠 Utilisation mémoire")
            fig3 = visualizer.plot_resource_usage(results_df, 'memory')
            st.plotly_chart(fig3, use_container_width=True)
    
    # Comparaison directe
    st.subheader("⚖️ Comparaison Virtuoso vs Jena Fuseki")
    fig4 = visualizer.plot_scatter_comparison(results_df)
    st.plotly_chart(fig4, use_container_width=True)
    
    # Insights automatiques
    insights = visualizer.generate_performance_insights(results_df)
    
    if insights and 'error' not in insights:
        st.subheader("🔍 Insights automatiques")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"🏆 **Meilleur moteur:** {insights.get('best_engine', 'N/A')}")
            st.info(f"🎯 **Plus stable:** {insights.get('most_stable', 'N/A')}")
        
        with col2:
            st.warning(f"🐌 **Moins performant:** {insights.get('worst_engine', 'N/A')}")
            st.error(f"📊 **Moins stable:** {insights.get('least_stable', 'N/A')}")
        
        # Recommandations
        st.subheader("💡 Recommandations")
        
        performance_gap = insights.get('performance_gap', 1)
        if performance_gap > 2:
            st.warning("⚠️ Écart de performance important détecté. Considérez l'optimisation du moteur le moins performant.")
        elif performance_gap < 1.1:
            st.success("✅ Les performances des moteurs sont très similaires.")
        else:
            st.info("ℹ️ Écart de performance modéré entre les moteurs.")

# Import nécessaire pour pandas
import pandas as pd