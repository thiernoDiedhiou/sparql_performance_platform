"""
Onglet de visualisation des performances
"""

import streamlit as st
import pandas as pd
from utils.data_manager import get_test_results, is_test_completed
from visualization.visualizer import ResultVisualizer
from utils.helpers import (
    log_message,
    validate_results_schema,
    handle_visualization_errors,
    compute_percentiles
)
from config.settings import UI_CHART_HEIGHT, UI_CHART_HEIGHT_LARGE

@handle_visualization_errors(default_return=None, show_error=True)
def render_visualization_tab():
    """Affiche l'onglet de visualisation"""
    st.header("Visualisation des performances")

    if not is_test_completed():
        st.info("ℹ️ Aucun test n'a encore été exécuté. Allez dans l'onglet 'Configuration et tests' pour lancer les tests.")
        return

    results_df = get_test_results()

    if results_df is None or results_df.empty:
        st.warning("⚠️ Aucun résultat disponible pour la visualisation.")
        return

    # Validation du schéma des données
    validation = validate_results_schema(results_df)
    if not validation["valid"]:
        st.error(f"❌ Données invalides: {', '.join(validation['errors'])}")
        return

    # Initialisation du visualiseur
    visualizer = ResultVisualizer()

    # Sélection du type de visualisation
    viz_type = st.radio(
        "Type de visualisation",
        options=[
            "Temps d'exécution",
            "Utilisation ressources",
            "Comparaison directe",
            "Tendances de performance",
            "Distribution (Box Plot)",
            "Distribution (Violin Plot)",
            "Analyse percentiles (CDF)",
            "Contribution requêtes (Waterfall)",
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

        elif viz_type == "Distribution (Box Plot)":
            render_boxplot(visualizer, results_df)

        elif viz_type == "Distribution (Violin Plot)":
            render_violin_plot(visualizer, results_df)

        elif viz_type == "Analyse percentiles (CDF)":
            render_cdf(visualizer, results_df)

        elif viz_type == "Contribution requêtes (Waterfall)":
            render_waterfall(visualizer, results_df)

        elif viz_type == "Heatmap des performances":
            render_performance_heatmap(visualizer, results_df)

        elif viz_type == "Tableau de bord complet":
            render_dashboard(visualizer, results_df)
    
    except Exception as e:
        st.error(f"❌ Erreur lors de la génération de la visualisation: {str(e)}")
        log_message(f"Erreur de visualisation: {str(e)}", "error")

@handle_visualization_errors(default_return=None, show_error=True)
def render_execution_time_charts(visualizer: ResultVisualizer, results_df):
    """
    Affiche les graphiques de temps d'exécution

    Args:
        visualizer: Instance du visualiseur
        results_df: DataFrame des résultats
    """
    st.subheader("Temps d'exécution")
    
    # Sélection de requête spécifique (optionnel)
    query_options = ["Toutes les requêtes"]
    if 'query_name' in results_df.columns:
        query_options.extend(list(results_df['query_name'].unique()))
    
    selected_query = st.selectbox(
        "Sélectionner une requête spécifique (optionnel)",
        options=query_options,
        help="Choisissez une requête pour un affichage détaillé"
    )
    
    # Filtrer les données selon la sélection
    if selected_query == "Toutes les requêtes":
        filtered_df = results_df
        fig = visualizer.plot_execution_times(results_df)
    else:
        filtered_df = results_df[results_df['query_name'] == selected_query]
        fig = visualizer.plot_execution_times(results_df, selected_query)

    st.plotly_chart(fig, use_container_width=True)

    # Insights automatiques (calculés sur les données filtrées)
    insights = visualizer.generate_performance_insights(filtered_df)
    if 'best_engine' in insights:
        st.success(f"**Moteur le plus performant:** {insights['best_engine']}")

        if 'performance_gap' in insights:
            gap_percent = (insights['performance_gap'] - 1) * 100
            st.info(f"**Écart de performance:** {gap_percent:.1f}% plus lent pour le moteur le moins performant")

@handle_visualization_errors(default_return=None, show_error=True)
def render_resource_usage_charts(visualizer: ResultVisualizer, results_df):
    """
    Affiche les graphiques d'utilisation des ressources

    Args:
        visualizer: Instance du visualiseur
        results_df: DataFrame des résultats
    """
    st.subheader("Utilisation des ressources")
    
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

@handle_visualization_errors(default_return=None, show_error=True)
def render_comparison_charts(visualizer: ResultVisualizer, results_df):
    """
    Affiche les graphiques de comparaison directe

    Args:
        visualizer: Instance du visualiseur
        results_df: DataFrame des résultats
    """
    st.subheader("Comparaison directe")
    
    # Graphique de dispersion
    fig = visualizer.plot_scatter_comparison(results_df)
    st.plotly_chart(fig, use_container_width=True)
    
    # Analyse comparative détaillée
    st.subheader("Analyse comparative")
    
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

@handle_visualization_errors(default_return=None, show_error=True)
def render_performance_trends(visualizer: ResultVisualizer, results_df):
    """
    Affiche les tendances de performance

    Args:
        visualizer: Instance du visualiseur
        results_df: DataFrame des résultats
    """
    st.subheader("Tendances de performance")
    
    if 'iteration' not in results_df.columns:
        st.warning("⚠️ Les données d'itération ne sont pas disponibles pour l'analyse des tendances.")
        return
    
    # Graphique des tendances
    fig = visualizer.plot_performance_trends(results_df)
    st.plotly_chart(fig, use_container_width=True)
    
    # Analyse de stabilité
    st.subheader("Analyse de stabilité")
    
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

@handle_visualization_errors(default_return=None, show_error=True)
def render_performance_heatmap(visualizer: ResultVisualizer, results_df):
    """
    Affiche la heatmap des performances

    Args:
        visualizer: Instance du visualiseur
        results_df: DataFrame des résultats
    """
    st.subheader("Heatmap des performances")
    
    # Heatmap principale
    fig = visualizer.create_performance_heatmap(results_df)
    st.plotly_chart(fig, use_container_width=True)
    
    # Interprétation
    st.info("""
    **Comment lire cette heatmap:**
    - Les couleurs chaudes (rouge) indiquent des temps d'exécution plus longs
    - Les couleurs froides (bleu) indiquent des temps d'exécution plus courts
    - Comparez horizontalement pour voir les différences entre moteurs
    - Comparez verticalement pour voir la complexité relative des requêtes
    """)

@handle_visualization_errors(default_return=None, show_error=True)
def render_dashboard(visualizer: ResultVisualizer, results_df):
    """
    Affiche un tableau de bord complet

    Args:
        visualizer: Instance du visualiseur
        results_df: DataFrame des résultats
    """
    st.subheader("Tableau de bord complet")
    
    # Vue d'ensemble des métriques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_time = results_df['execution_time'].mean()
        st.metric("Temps moyen", f"{avg_time:.3f}s")
    
    with col2:
        success_rate = results_df['success'].mean() * 100
        st.metric("✅ Taux de succès", f"{success_rate:.1f}%")
    
    with col3:
        if 'result_count' in results_df.columns:
            avg_results = results_df['result_count'].mean()
            st.metric("Résultats moyens", f"{avg_results:.0f}")
    
    with col4:
        total_time = results_df['execution_time'].sum()
        st.metric("🕐 Temps total", f"{total_time:.1f}s")
    
    # Graphiques principaux
    st.subheader("Temps d'exécution par requête et moteur")
    fig1 = visualizer.plot_execution_times(results_df)
    st.plotly_chart(fig1, use_container_width=True)
    
    # Graphiques de ressources côte à côte
    col1, col2 = st.columns(2)
    
    with col1:
        if 'cpu_usage' in results_df.columns:
            st.subheader("Utilisation CPU")
            fig2 = visualizer.plot_resource_usage(results_df, 'cpu')
            st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        if 'memory_usage' in results_df.columns:
            st.subheader("Utilisation mémoire")
            fig3 = visualizer.plot_resource_usage(results_df, 'memory')
            st.plotly_chart(fig3, use_container_width=True)
    
    # Comparaison directe
    st.subheader("Comparaison Virtuoso vs Jena Fuseki")
    fig4 = visualizer.plot_scatter_comparison(results_df)
    st.plotly_chart(fig4, use_container_width=True)

    # === NOUVEAUX GRAPHIQUES PROFESSIONNELS ===

    # Section 1: Analyse de distribution
    st.markdown("---")
    st.header("Analyse de Distribution")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Box Plot")
        fig_box = visualizer.plot_boxplot(results_df)
        st.plotly_chart(fig_box, use_container_width=True)

    with col2:
        st.subheader("Violin Plot")
        fig_violin = visualizer.plot_violin(results_df)
        st.plotly_chart(fig_violin, use_container_width=True)

    # Section 2: Analyse percentiles et contribution
    st.markdown("---")
    st.header("Analyse Avancée")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("CDF (Percentiles)")
        fig_cdf = visualizer.plot_cdf(results_df)
        st.plotly_chart(fig_cdf, use_container_width=True)

        # Affichage des percentiles clés de manière compacte
        st.markdown("**Percentiles clés:**")
        for engine in results_df['engine'].unique():
            engine_data = results_df[results_df['engine'] == engine]['execution_time']
            p95 = engine_data.quantile(0.95)
            p99 = engine_data.quantile(0.99)
            st.write(f"- **{engine}**: P95={p95:.3f}s | P99={p99:.3f}s")

    with col2:
        st.subheader("Waterfall (Contribution)")
        fig_waterfall = visualizer.plot_waterfall(results_df)
        st.plotly_chart(fig_waterfall, use_container_width=True)

        # Analyse de contribution compacte
        query_times = results_df.groupby('query_name')['execution_time'].sum().sort_values(ascending=False)
        total_time = query_times.sum()
        top_5_pct = (query_times.head(5).sum() / total_time * 100)

        st.markdown("**Concentration:**")
        st.write(f"- Top 5 requêtes: **{top_5_pct:.1f}%** du temps total")

    # Insights automatiques
    st.markdown("---")
    insights = visualizer.generate_performance_insights(results_df)

    if insights and 'error' not in insights:
        st.subheader("Insights automatiques")

        col1, col2 = st.columns(2)

        with col1:
            st.success(f"**Meilleur moteur:** {insights.get('best_engine', 'N/A')}")
            st.info(f"**Plus stable:** {insights.get('most_stable', 'N/A')}")

        with col2:
            st.warning(f"**Moins performant:** {insights.get('worst_engine', 'N/A')}")
            st.error(f"**Moins stable:** {insights.get('least_stable', 'N/A')}")

        # Recommandations
        st.subheader("Recommandations")

        performance_gap = insights.get('performance_gap', 1)
        if performance_gap > 2:
            st.warning("⚠️ Écart de performance important détecté. Considérez l'optimisation du moteur le moins performant.")
        elif performance_gap < 1.1:
            st.success("✅ Les performances des moteurs sont très similaires.")
        else:
            st.info("ℹ️ Écart de performance modéré entre les moteurs.")

@handle_visualization_errors(default_return=None, show_error=True)
def render_boxplot(visualizer: ResultVisualizer, results_df):
    """
    Affiche le box plot de distribution des temps d'exécution

    Args:
        visualizer: Instance du visualiseur
        results_df: DataFrame des résultats
    """
    st.subheader("Distribution des temps (Box Plot)")

    # Génération du graphique
    fig = visualizer.plot_boxplot(results_df)
    st.plotly_chart(fig, use_container_width=True)

    # Guide d'interprétation
    st.info("""
    **Comment lire ce graphique:**
    - La boîte montre l'intervalle interquartile (Q1-Q3) - 50% des valeurs centrales
    - La ligne centrale (orange) est la médiane
    - Les points individuels montrent chaque mesure
    - Les lignes extérieures (whiskers) montrent les valeurs min/max (hors outliers)
    - Les points isolés au-delà des whiskers sont des valeurs aberrantes
    """)

    # Statistiques complémentaires
    col1, col2 = st.columns(2)

    for idx, engine in enumerate(results_df['engine'].unique()):
        engine_data = results_df[results_df['engine'] == engine]['execution_time']
        q1 = engine_data.quantile(0.25)
        q3 = engine_data.quantile(0.75)
        iqr = q3 - q1

        with col1 if idx == 0 else col2:
            st.write(f"**{engine}**")
            st.metric("IQR (Intervalle Interquartile)", f"{iqr:.3f}s", help="Écart entre Q1 et Q3")
            st.metric("Q1 (25%)", f"{q1:.3f}s")
            st.metric("Q3 (75%)", f"{q3:.3f}s")

@handle_visualization_errors(default_return=None, show_error=True)
def render_violin_plot(visualizer: ResultVisualizer, results_df):
    """
    Affiche le violin plot de densité de probabilité

    Args:
        visualizer: Instance du visualiseur
        results_df: DataFrame des résultats
    """
    st.subheader("Distribution de densité (Violin Plot)")

    # Génération du graphique
    fig = visualizer.plot_violin(results_df)
    st.plotly_chart(fig, use_container_width=True)

    # Guide d'interprétation
    st.info("""
    **Comment lire ce graphique:**
    - La largeur du violon montre la densité de probabilité à chaque niveau
    - Plus c'est large, plus il y a de valeurs à ce temps d'exécution
    - La boîte intérieure blanche est un box plot miniature (médiane + quartiles)
    - Les points montrent toutes les mesures individuelles
    - Permet de voir si la distribution est unimodale, bimodale, ou multimodale
    """)

    # Analyse de la distribution
    st.subheader("Analyse de la forme de distribution")

    for engine in results_df['engine'].unique():
        engine_data = results_df[results_df['engine'] == engine]['execution_time']

        # Calcul du coefficient d'asymétrie (skewness)
        skewness = engine_data.skew()

        # Interprétation
        if abs(skewness) < 0.5:
            distribution_type = "symétrique (normale)"
            interpretation = "Les temps sont uniformément répartis autour de la médiane"
        elif skewness > 0.5:
            distribution_type = "asymétrique à droite (positive)"
            interpretation = "Présence de quelques requêtes très lentes qui tirent la moyenne vers le haut"
        else:
            distribution_type = "asymétrique à gauche (négative)"
            interpretation = "La majorité des requêtes sont lentes avec quelques rapides"

        st.write(f"**{engine}**: Distribution {distribution_type}")
        st.write(f"  ➜ {interpretation}")

@handle_visualization_errors(default_return=None, show_error=True)
def render_cdf(visualizer: ResultVisualizer, results_df):
    """
    Affiche la CDF (Cumulative Distribution Function) pour analyse des percentiles

    Args:
        visualizer: Instance du visualiseur
        results_df: DataFrame des résultats
    """
    st.subheader("Analyse des percentiles (CDF)")

    # Génération du graphique
    fig = visualizer.plot_cdf(results_df)
    st.plotly_chart(fig, use_container_width=True)

    # Guide d'interprétation
    st.info("""
    **Comment lire ce graphique:**
    - L'axe X montre le temps d'exécution (secondes)
    - L'axe Y montre le pourcentage cumulé de requêtes terminées
    - La ligne en pointillés à 95% montre le P95 (95ème percentile)
    - La ligne en pointillés à 99% montre le P99 (99ème percentile)
    - Plus la courbe monte rapidement, plus les performances sont consistantes
    """)

    # Calcul et affichage des percentiles clés
    st.subheader("Percentiles clés (SLA Standards)")

    col1, col2 = st.columns(2)

    for idx, engine in enumerate(results_df['engine'].unique()):
        engine_data = results_df[results_df['engine'] == engine]['execution_time']

        p50 = engine_data.quantile(0.50)
        p90 = engine_data.quantile(0.90)
        p95 = engine_data.quantile(0.95)
        p99 = engine_data.quantile(0.99)
        p999 = engine_data.quantile(0.999)

        with col1 if idx == 0 else col2:
            st.write(f"**{engine}**")
            st.metric("P50 (Médiane)", f"{p50:.3f}s", help="50% des requêtes terminées en moins de")
            st.metric("P90", f"{p90:.3f}s", help="90% des requêtes terminées en moins de")
            st.metric("P95", f"{p95:.3f}s", help="95% des requêtes terminées en moins de")
            st.metric("P99", f"{p99:.3f}s", help="99% des requêtes terminées en moins de")
            st.metric("P99.9", f"{p999:.3f}s", help="99.9% des requêtes terminées en moins de")

    # Analyse comparative P95/P99
    st.subheader("Comparaison P95 vs P99")

    engines_list = results_df['engine'].unique().tolist()
    if len(engines_list) == 2:
        engine1_p95 = results_df[results_df['engine'] == engines_list[0]]['execution_time'].quantile(0.95)
        engine2_p95 = results_df[results_df['engine'] == engines_list[1]]['execution_time'].quantile(0.95)

        engine1_p99 = results_df[results_df['engine'] == engines_list[0]]['execution_time'].quantile(0.99)
        engine2_p99 = results_df[results_df['engine'] == engines_list[1]]['execution_time'].quantile(0.99)

        p95_ratio = engine1_p95 / engine2_p95
        p99_ratio = engine1_p99 / engine2_p99

        if p95_ratio < 0.9:
            st.success(f"✅ **{engines_list[0]} est {(1/p95_ratio):.1f}x plus rapide au P95**")
        elif p95_ratio > 1.1:
            st.error(f"❌ **{engines_list[1]} est {p95_ratio:.1f}x plus rapide au P95**")
        else:
            st.info("ℹ️ Performances similaires au P95")

        if p99_ratio < 0.9:
            st.success(f"✅ **{engines_list[0]} est {(1/p99_ratio):.1f}x plus rapide au P99**")
        elif p99_ratio > 1.1:
            st.error(f"❌ **{engines_list[1]} est {p99_ratio:.1f}x plus rapide au P99**")
        else:
            st.info("ℹ️ Performances similaires au P99")

@handle_visualization_errors(default_return=None, show_error=True)
def render_waterfall(visualizer: ResultVisualizer, results_df):
    """
    Affiche le waterfall chart montrant la contribution de chaque requête au temps total

    Args:
        visualizer: Instance du visualiseur
        results_df: DataFrame des résultats
    """
    st.subheader("Contribution au temps total (Waterfall)")

    # Génération du graphique
    fig = visualizer.plot_waterfall(results_df)
    st.plotly_chart(fig, use_container_width=True)

    # Guide d'interprétation
    st.info("""
    **Comment lire ce graphique:**
    - Chaque barre montre le temps cumulé d'une requête (toutes itérations)
    - Les requêtes sont triées de la plus coûteuse à la moins coûteuse
    - La barre "Total" montre le temps cumulé de toutes les requêtes
    - Les 15 requêtes les plus lentes sont affichées individuellement
    - "Autres requêtes" regroupe les requêtes moins coûteuses
    """)

    # Analyse de contribution détaillée
    st.subheader("Analyse de contribution")

    query_times = results_df.groupby('query_name')['execution_time'].sum().sort_values(ascending=False)
    total_time = query_times.sum()

    # Top 5 et Top 10
    top_5_time = query_times.head(5).sum()
    top_5_pct = (top_5_time / total_time) * 100

    top_10_time = query_times.head(10).sum()
    top_10_pct = (top_10_time / total_time) * 100

    # Affichage des métriques
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Temps total", f"{total_time:.2f}s")

    with col2:
        st.metric("Top 5 requêtes", f"{top_5_pct:.1f}%", help=f"{top_5_time:.2f}s sur {total_time:.2f}s")

    with col3:
        st.metric("Top 10 requêtes", f"{top_10_pct:.1f}%", help=f"{top_10_time:.2f}s sur {total_time:.2f}s")

    # Recommandations basées sur la concentration
    if top_5_pct > 70:
        st.warning(f"**Top 5 requêtes représentent {top_5_pct:.1f}% du temps total**")
        st.write("**Recommandation:** Forte concentration du temps sur peu de requêtes. Optimiser ces 5 requêtes aura un impact majeur sur les performances globales.")
    elif top_5_pct > 50:
        st.info(f"**Top 5 requêtes représentent {top_5_pct:.1f}% du temps total**")
        st.write("**Recommandation:** Concentration modérée. Prioriser l'optimisation des requêtes les plus coûteuses.")
    else:
        st.success(f"**✅ Top 5 requêtes représentent {top_5_pct:.1f}% du temps total**")
        st.write("**Recommandation:** Temps bien distribué entre les requêtes. Pas de goulot d'étranglement évident.")

    # Tableau détaillé des Top 15
    st.subheader("Top 15 requêtes les plus coûteuses")

    top_15 = query_times.head(15).reset_index()
    top_15.columns = ['Requête', 'Temps total (s)']
    top_15['% du total'] = (top_15['Temps total (s)'] / total_time * 100).round(1)
    top_15['Cumul %'] = top_15['% du total'].cumsum().round(1)
    top_15.index = range(1, len(top_15) + 1)

    st.dataframe(
        top_15,
        use_container_width=True,
        column_config={
            "Requête": st.column_config.TextColumn("Requête", width="large"),
            "Temps total (s)": st.column_config.NumberColumn("Temps total (s)", format="%.3f"),
            "% du total": st.column_config.NumberColumn("% du total", format="%.1f%%"),
            "Cumul %": st.column_config.NumberColumn("Cumul %", format="%.1f%%")
        }
    )