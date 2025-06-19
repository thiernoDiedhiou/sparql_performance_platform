"""
Module principal pour la visualisation des résultats de performance
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional
from utils.helpers import log_message

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
    
    def plot_execution_times(self, df: pd.DataFrame, query_name: Optional[str] = None) -> go.Figure:
        """
        Visualise les temps d'exécution pour une ou toutes les requêtes
        
        Args:
            df: DataFrame contenant les résultats
            query_name: Nom de la requête spécifique (optionnel)
            
        Returns:
            Figure Plotly
        """
        try:
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
                color_discrete_map=self._get_color_mapping(plot_df['engine'].unique())
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
            
        except Exception as e:
            log_message(f"Erreur lors de la création du graphique d'exécution: {str(e)}")
            return self._create_error_figure("Erreur lors de la création du graphique")
    
    def plot_resource_usage(self, df: pd.DataFrame, resource_type: str) -> go.Figure:
        """
        Visualise l'utilisation des ressources (CPU ou mémoire)
        
        Args:
            df: DataFrame contenant les résultats
            resource_type: Type de ressource ('cpu' ou 'memory')
            
        Returns:
            Figure Plotly
        """
        try:
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
                color_discrete_map=self._get_color_mapping(plot_df['engine'].unique())
            )
            
            fig.update_layout(
                xaxis_title="Requête",
                yaxis_title=y_label,
                legend_title="Moteur SPARQL",
                template="plotly_white"
            )
            
            fig.update_xaxes(tickangle=45)
            
            return fig
            
        except Exception as e:
            log_message(f"Erreur lors de la création du graphique de ressources: {str(e)}")
            return self._create_error_figure("Erreur lors de la création du graphique")
    
    def plot_scatter_comparison(self, df: pd.DataFrame) -> go.Figure:
        """
        Crée un graphique de dispersion pour comparer les performances
        
        Args:
            df: DataFrame contenant les résultats
            
        Returns:
            Figure Plotly
        """
        try:
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
                }
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
            
        except Exception as e:
            log_message(f"Erreur lors de la création du graphique de comparaison: {str(e)}")
            return self._create_error_figure("Erreur lors de la création du graphique")
    
    def plot_performance_trends(self, df: pd.DataFrame) -> go.Figure:
        """
        Crée un graphique des tendances de performance par itération
        
        Args:
            df: DataFrame contenant les résultats
            
        Returns:
            Figure Plotly
        """
        try:
            fig = px.line(
                df,
                x='iteration',
                y='execution_time',
                color='engine',
                facet_col='query_name',
                facet_col_wrap=3,
                title='Tendances de performance par itération',
                labels={
                    'iteration': 'Itération',
                    'execution_time': 'Temps d\'exécution (s)',
                    'engine': 'Moteur'
                },
                color_discrete_map=self._get_color_mapping(df['engine'].unique())
            )
            
            fig.update_layout(
                template="plotly_white",
                showlegend=True
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