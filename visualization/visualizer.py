"""
Module principal pour la visualisation des résultats de performance
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional
from functools import wraps
from utils.helpers import log_message
from config.settings import UI_CHART_HEIGHT, UI_CHART_HEIGHT_LARGE

def safe_visualization(func):
    """
    Décorateur pour gérer les erreurs dans les méthodes de visualisation

    Args:
        func: Fonction à décorer

    Returns:
        Fonction décorée avec gestion d'erreurs
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            error_msg = f"Erreur dans {func.__name__}: {str(e)}"
            log_message(error_msg, "error")
            return self._create_error_figure(error_msg)
    return wrapper

class ResultVisualizer:
    """Classe principale pour la visualisation des résultats"""
    
    def __init__(self):
        """Initialise le visualiseur"""
        self.color_palette = {
            'virtuoso': '#1f77b4',
            'fuseki': '#ff7f0e',
            'concurrent_virtuoso': '#2ca02c',
            'concurrent_fuseki': '#d62728'
        }
    
    @safe_visualization
    def plot_execution_times(self, df: pd.DataFrame, query_name: Optional[str] = None) -> go.Figure:
        """
        Visualise les temps d'exécution pour une ou toutes les requêtes

        Args:
            df: DataFrame contenant les résultats
            query_name: Nom de la requête spécifique (optionnel)

        Returns:
            Figure Plotly
        """
        if query_name and query_name != "Toutes les requêtes":
            plot_df = df[df['query_name'] == query_name]
            title = f"Temps d'exécution pour: {query_name}"
            x_axis = 'engine'
        else:
            plot_df = df.groupby(['query_name', 'engine'])['execution_time'].mean().reset_index()
            title = "Temps d'exécution moyen par requête et moteur"
            x_axis = 'query_name'

        fig = px.bar(
            plot_df,
            x=x_axis,
            y='execution_time',
            color='engine',
            title=title,
            labels={
                'execution_time': 'Temps d\'exécution (s)',
                'query_name': 'Requête',
                'engine': 'Moteur'
            },
            barmode='group',
            color_discrete_map=self._get_color_mapping(plot_df['engine'].unique()),
            height=UI_CHART_HEIGHT
        )

        fig.update_layout(
            xaxis_title="Requête" if x_axis == 'query_name' else "Moteur",
            yaxis_title="Temps d'exécution (secondes)",
            legend_title="Moteur SPARQL",
            template="plotly_white"
        )

        # Rotation des labels pour une meilleure lisibilité
        if x_axis == 'query_name':
            fig.update_xaxes(tickangle=45)

        return fig
    
    @safe_visualization
    def plot_resource_usage(self, df: pd.DataFrame, resource_type: str) -> go.Figure:
        """
        Visualise l'utilisation des ressources (CPU ou mémoire)

        Args:
            df: DataFrame contenant les résultats
            resource_type: Type de ressource ('cpu' ou 'memory')

        Returns:
            Figure Plotly
        """
        if resource_type == 'cpu':
            y_col = 'cpu_usage'
            title = "Utilisation CPU par moteur et requête"
            y_label = "Utilisation CPU (%)"
        else:  # memory
            y_col = 'memory_usage'
            title = "Utilisation mémoire par moteur et requête"
            y_label = "Utilisation mémoire (MB)"

        plot_df = df.groupby(['query_name', 'engine'])[y_col].mean().reset_index()

        fig = px.bar(
            plot_df,
            x='query_name',
            y=y_col,
            color='engine',
            title=title,
            labels={
                'query_name': 'Requête',
                'engine': 'Moteur',
                y_col: y_label
            },
            barmode='group',
            color_discrete_map=self._get_color_mapping(plot_df['engine'].unique()),
            height=UI_CHART_HEIGHT
        )

        fig.update_layout(
            xaxis_title="Requête",
            yaxis_title=y_label,
            legend_title="Moteur SPARQL",
            template="plotly_white"
        )

        fig.update_xaxes(tickangle=45)

        return fig
    
    @safe_visualization
    def plot_scatter_comparison(self, df: pd.DataFrame) -> go.Figure:
        """
        Crée un graphique de dispersion pour comparer les performances

        Args:
            df: DataFrame contenant les résultats

        Returns:
            Figure Plotly
        """
        virtuoso_data = df[df['engine'].str.contains('Virtuoso')].groupby('query_name')['execution_time'].mean()
        fuseki_data = df[df['engine'].str.contains('Fuseki')].groupby('query_name')['execution_time'].mean()

        # Fusionner les données des deux moteurs
        comparison_df = pd.DataFrame({
            'query_name': virtuoso_data.index,
            'Virtuoso': virtuoso_data.values,
            'Jena Fuseki': fuseki_data.values
        })

        fig = px.scatter(
            comparison_df,
            x='Virtuoso',
            y='Jena Fuseki',
            hover_name='query_name',
            title='Comparaison des temps d\'exécution: Virtuoso vs Jena Fuseki',
            labels={
                'Virtuoso': 'Temps Virtuoso (s)',
                'Jena Fuseki': 'Temps Jena Fuseki (s)'
            },
            height=UI_CHART_HEIGHT
        )

        # Ajouter une ligne diagonale pour référence (x=y)
        max_val = max(df['execution_time'].max(), 0.1)
        fig.add_trace(go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            line=dict(dash='dash', color='gray'),
            name='Performances égales',
            showlegend=True
        ))

        fig.update_layout(
            template="plotly_white",
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )

        return fig
    
    def plot_performance_trends(self, df: pd.DataFrame, max_queries: int = 12) -> go.Figure:
        """
        Crée un graphique des tendances de performance par itération

        Args:
            df: DataFrame contenant les résultats
            max_queries: Nombre maximum de requêtes à afficher (défaut: 12 pour lisibilité)

        Returns:
            Figure Plotly
        """
        try:
            # Limiter le nombre de requêtes pour améliorer la lisibilité
            unique_queries = df['query_name'].unique()

            if len(unique_queries) > max_queries:
                # Sélectionner les requêtes les plus longues
                top_queries = df.groupby('query_name')['execution_time'].mean().nlargest(max_queries).index
                plot_df = df[df['query_name'].isin(top_queries)]
                title = f'Tendances de performance par itération (Top {max_queries} requêtes les plus longues)'
            else:
                plot_df = df
                title = 'Tendances de performance par itération'

            fig = px.line(
                plot_df,
                x='iteration',
                y='execution_time',
                color='engine',
                facet_col='query_name',
                facet_col_wrap=3,
                title=title,
                labels={
                    'iteration': 'Itération',
                    'execution_time': 'Temps d\'exécution (s)',
                    'engine': 'Moteur'
                },
                color_discrete_map=self._get_color_mapping(plot_df['engine'].unique())
            )

            fig.update_layout(
                template="plotly_white",
                showlegend=True,
                height=400 * ((len(plot_df['query_name'].unique()) - 1) // 3 + 1)  # Ajuster hauteur dynamiquement
            )

            return fig

        except Exception as e:
            log_message(f"Erreur lors de la création du graphique de tendances: {str(e)}")
            return self._create_error_figure("Erreur lors de la création du graphique")
    
    def create_summary_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crée un tableau récapitulatif des performances
        
        Args:
            df: DataFrame contenant les résultats
            
        Returns:
            DataFrame formaté pour l'affichage
        """
        try:
            # Vérification préventive
            if 'query_name' not in df.columns or 'engine' not in df.columns:
                raise ValueError("Le DataFrame ne contient pas les colonnes 'query_name' et/ou 'engine'.")

            # Calcul des métriques
            summary = df.groupby(['query_name', 'engine']).agg({
                'execution_time': ['mean', 'min', 'max', 'std'],
                'cpu_usage': ['mean'],
                'memory_usage': ['mean'],
                'success': ['mean'],
                'result_count': ['mean']
            }).reset_index()
            
            # Formatage des colonnes multiindex
            summary.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] for col in summary.columns]
            
            # Formatage des valeurs pour l'affichage
            summary['execution_time_mean'] = summary['execution_time_mean'].round(4)
            summary['execution_time_min'] = summary['execution_time_min'].round(4)
            summary['execution_time_max'] = summary['execution_time_max'].round(4)
            summary['execution_time_std'] = summary['execution_time_std'].round(4)
            summary['cpu_usage_mean'] = summary['cpu_usage_mean'].round(2)
            summary['memory_usage_mean'] = summary['memory_usage_mean'].round(2)
            summary['success_mean'] = (summary['success_mean'] * 100).round(2)
            
            # Renommage des colonnes pour plus de clarté
            summary = summary.rename(columns={
                'execution_time_mean': 'Temps moyen (s)',
                'execution_time_min': 'Temps min (s)',
                'execution_time_max': 'Temps max (s)',
                'execution_time_std': 'Écart-type (s)',
                'cpu_usage_mean': 'CPU moyen (%)',
                'memory_usage_mean': 'Mémoire moyenne (MB)',
                'success_mean': 'Taux de succès (%)',
                'result_count_mean': 'Résultats moyens'
            })
            
            return summary
            
        except Exception as e:
            log_message(f"Erreur lors de la création du tableau récapitulatif: {str(e)}")
            return pd.DataFrame({"Erreur": ["Impossible de créer le tableau récapitulatif"]})
    
    def create_performance_heatmap(self, df: pd.DataFrame) -> go.Figure:
        """
        Crée une heatmap des performances
        
        Args:
            df: DataFrame contenant les résultats
            
        Returns:
            Figure Plotly
        """
        try:
            # Pivot des données pour la heatmap
            pivot_df = df.pivot_table(
                index='query_name',
                columns='engine',
                values='execution_time',
                aggfunc='mean'
            )
            
            fig = px.imshow(
                pivot_df,
                title='Heatmap des temps d\'exécution moyens',
                labels=dict(x="Moteur", y="Requête", color="Temps (s)"),
                aspect="auto",
                color_continuous_scale="RdYlBu_r"
            )
            
            fig.update_layout(
                template="plotly_white",
                xaxis_title="Moteur SPARQL",
                yaxis_title="Requête"
            )
            
            return fig
            
        except Exception as e:
            log_message(f"Erreur lors de la création de la heatmap: {str(e)}")
            return self._create_error_figure("Erreur lors de la création de la heatmap")
    
    def _get_color_mapping(self, engines: list) -> dict:
        """
        Retourne un mapping de couleurs pour les moteurs
        
        Args:
            engines: Liste des moteurs
            
        Returns:
            Dictionnaire de mapping des couleurs
        """
        color_map = {}
        for engine in engines:
            if 'virtuoso' in engine.lower():
                if 'concurrent' in engine.lower():
                    color_map[engine] = self.color_palette['concurrent_virtuoso']
                else:
                    color_map[engine] = self.color_palette['virtuoso']
            elif 'fuseki' in engine.lower():
                if 'concurrent' in engine.lower():
                    color_map[engine] = self.color_palette['concurrent_fuseki']
                else:
                    color_map[engine] = self.color_palette['fuseki']
            else:
                # Couleur par défaut pour les moteurs non reconnus
                color_map[engine] = '#9467bd'
        
        return color_map
    
    def _create_error_figure(self, error_message: str) -> go.Figure:
        """
        Crée une figure d'erreur
        
        Args:
            error_message: Message d'erreur à afficher
            
        Returns:
            Figure Plotly avec le message d'erreur
        """
        fig = go.Figure()
        
        fig.add_annotation(
            text=error_message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="red")
        )
        
        fig.update_layout(
            template="plotly_white",
            title="Erreur de visualisation"
        )
        
        return fig
    
    def generate_performance_insights(self, df: pd.DataFrame) -> dict:
        """
        Génère des insights automatiques sur les performances
        
        Args:
            df: DataFrame contenant les résultats
            
        Returns:
            Dictionnaire contenant les insights
        """
        try:
            insights = {}
            
            # Performance moyenne par moteur
            avg_by_engine = df.groupby('engine')['execution_time'].mean()
            best_engine = avg_by_engine.idxmin()
            worst_engine = avg_by_engine.idxmax()
            
            insights['best_engine'] = best_engine
            insights['worst_engine'] = worst_engine
            insights['performance_gap'] = avg_by_engine[worst_engine] / avg_by_engine[best_engine]
            
            # Requêtes les plus/moins performantes
            avg_by_query = df.groupby('query_name')['execution_time'].mean()
            insights['fastest_query'] = avg_by_query.idxmin()
            insights['slowest_query'] = avg_by_query.idxmax()
            
            # Stabilité des performances (écart-type)
            stability = df.groupby('engine')['execution_time'].std()
            insights['most_stable'] = stability.idxmin()
            insights['least_stable'] = stability.idxmax()
            
            # Taux de succès
            success_rate = df.groupby('engine')['success'].mean()
            insights['most_reliable'] = success_rate.idxmax()
            insights['success_rates'] = success_rate.to_dict()
            
            return insights
            
        except Exception as e:
            log_message(f"Erreur lors de la génération des insights: {str(e)}")
            return {"error": "Impossible de générer les insights"}

    def plot_boxplot(self, df: pd.DataFrame) -> go.Figure:
        """
        Crée un box plot pour visualiser la distribution des temps d'exécution

        Args:
            df: DataFrame contenant les résultats

        Returns:
            Figure Plotly
        """
        try:
            fig = px.box(
                df,
                x='engine',
                y='execution_time',
                color='engine',
                points='all',  # Afficher tous les points individuels
                title='Distribution des temps d\'exécution (Box Plot)',
                labels={
                    'execution_time': 'Temps d\'exécution (s)',
                    'engine': 'Moteur SPARQL'
                },
                color_discrete_map=self._get_color_mapping(df['engine'].unique())
            )

            fig.update_layout(
                template="plotly_white",
                showlegend=True,
                yaxis_title="Temps d'exécution (secondes)",
                xaxis_title="Moteur"
            )

            return fig

        except Exception as e:
            log_message(f"Erreur lors de la création du box plot: {str(e)}")
            return self._create_error_figure("Erreur lors de la création du box plot")

    def plot_violin(self, df: pd.DataFrame) -> go.Figure:
        """
        Crée un violin plot pour visualiser la densité de probabilité

        Args:
            df: DataFrame contenant les résultats

        Returns:
            Figure Plotly
        """
        try:
            fig = px.violin(
                df,
                x='engine',
                y='execution_time',
                color='engine',
                box=True,  # Ajouter un box plot à l'intérieur
                points='all',  # Afficher tous les points
                title='Distribution de densité des temps d\'exécution (Violin Plot)',
                labels={
                    'execution_time': 'Temps d\'exécution (s)',
                    'engine': 'Moteur SPARQL'
                },
                color_discrete_map=self._get_color_mapping(df['engine'].unique())
            )

            fig.update_layout(
                template="plotly_white",
                showlegend=True,
                yaxis_title="Temps d'exécution (secondes)",
                xaxis_title="Moteur"
            )

            return fig

        except Exception as e:
            log_message(f"Erreur lors de la création du violin plot: {str(e)}")
            return self._create_error_figure("Erreur lors de la création du violin plot")

    def plot_cdf(self, df: pd.DataFrame) -> go.Figure:
        """
        Crée une Cumulative Distribution Function (CDF) pour l'analyse des percentiles

        Args:
            df: DataFrame contenant les résultats

        Returns:
            Figure Plotly
        """
        try:
            fig = px.ecdf(
                df,
                x='execution_time',
                color='engine',
                title='CDF: Pourcentage de requêtes terminées en moins de X secondes',
                labels={
                    'execution_time': 'Temps d\'exécution (s)',
                    'engine': 'Moteur SPARQL'
                },
                color_discrete_map=self._get_color_mapping(df['engine'].unique())
            )

            # Ajouter des lignes de référence pour P95 et P99
            for engine in df['engine'].unique():
                engine_data = df[df['engine'] == engine]['execution_time']
                p95 = engine_data.quantile(0.95)
                p99 = engine_data.quantile(0.99)

                # Ligne P95 (pointillé)
                fig.add_hline(
                    y=0.95,
                    line_dash="dash",
                    line_color="gray",
                    annotation_text="P95 (95%)",
                    annotation_position="right"
                )

                # Ligne P99 (pointillé)
                fig.add_hline(
                    y=0.99,
                    line_dash="dot",
                    line_color="darkgray",
                    annotation_text="P99 (99%)",
                    annotation_position="right"
                )

            fig.update_layout(
                template="plotly_white",
                showlegend=True,
                xaxis_title="Temps d'exécution (secondes)",
                yaxis_title="Pourcentage cumulatif (%)",
                yaxis_tickformat='.0%'
            )

            return fig

        except Exception as e:
            log_message(f"Erreur lors de la création de la CDF: {str(e)}")
            return self._create_error_figure("Erreur lors de la création de la CDF")

    def plot_waterfall(self, df: pd.DataFrame) -> go.Figure:
        """
        Crée un waterfall chart montrant la contribution de chaque requête au temps total

        Args:
            df: DataFrame contenant les résultats

        Returns:
            Figure Plotly
        """
        try:
            # Calculer le temps total par requête
            query_times = df.groupby('query_name')['execution_time'].sum().sort_values(ascending=False)

            # Limiter aux 15 requêtes les plus longues pour la lisibilité
            top_queries = query_times.head(15)

            # Calculer le temps des autres requêtes
            other_time = query_times[15:].sum() if len(query_times) > 15 else 0

            # Préparer les données pour le waterfall
            labels = list(top_queries.index) + (['Autres requêtes'] if other_time > 0 else []) + ['Total']
            values = list(top_queries.values) + ([other_time] if other_time > 0 else []) + [query_times.sum()]

            # Créer les mesures (relative pour les contributions, total pour la fin)
            measures = ['relative'] * (len(values) - 1) + ['total']

            fig = go.Figure(go.Waterfall(
                name="Contribution",
                orientation="v",
                measure=measures,
                x=labels,
                y=values,
                text=[f"{v:.2f}s" for v in values],
                textposition="outside",
                connector={"line": {"color": "rgb(63, 63, 63)"}},
                decreasing={"marker": {"color": "#ff7f0e"}},
                increasing={"marker": {"color": "#1f77b4"}},
                totals={"marker": {"color": "#2ca02c"}}
            ))

            fig.update_layout(
                title='Contribution de chaque requête au temps total d\'exécution',
                template="plotly_white",
                showlegend=False,
                xaxis_title="Requête",
                yaxis_title="Temps d'exécution (secondes)",
                xaxis_tickangle=45,
                height=500
            )

            return fig

        except Exception as e:
            log_message(f"Erreur lors de la création du waterfall chart: {str(e)}")
            return self._create_error_figure("Erreur lors de la création du waterfall chart")