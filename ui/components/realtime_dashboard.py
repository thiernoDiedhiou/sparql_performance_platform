"""
Dashboard temps réel pour suivre les tests en cours d'exécution
Affichage dynamique des métriques et de la progression
"""

import streamlit as st
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime


class RealtimeDashboard:
    """Dashboard temps réel pour les tests de performance"""

    def __init__(self):
        """Initialise le dashboard"""
        self.start_time = time.time()
        self.queries_completed = 0
        self.total_queries = 0
        self.current_query = ""
        self.execution_times: List[float] = []
        self.cpu_usage: List[float] = []
        self.memory_usage: List[float] = []
        self.timestamps: List[float] = []

    def initialize_dashboard(self, total_queries: int, query_types: List[str]):
        """
        Initialise le dashboard avec les informations du test

        Args:
            total_queries: Nombre total de requêtes à exécuter
            query_types: Types de requêtes sélectionnés
        """
        self.total_queries = total_queries
        self.queries_completed = 0
        self.start_time = time.time()

        st.markdown("## Dashboard Temps Réel")

        # En-tête avec informations
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Requêtes totales", total_queries)

        with col2:
            st.metric("Types sélectionnés", len(query_types))

        with col3:
            st.metric("Démarré à", datetime.now().strftime("%H:%M:%S"))

        st.markdown("---")

    def create_progress_section(self) -> tuple:
        """
        Crée la section de progression

        Returns:
            Tuple (progress_bar, status_text, metrics_container)
        """
        st.subheader("Progression")

        # Barre de progression principale
        progress_bar = st.progress(0.0)

        # Texte de statut
        status_text = st.empty()

        # Métriques en temps réel
        metrics_cols = st.columns(4)

        with metrics_cols[0]:
            completed_metric = st.empty()

        with metrics_cols[1]:
            elapsed_metric = st.empty()

        with metrics_cols[2]:
            eta_metric = st.empty()

        with metrics_cols[3]:
            speed_metric = st.empty()

        metrics_container = {
            "completed": completed_metric,
            "elapsed": elapsed_metric,
            "eta": eta_metric,
            "speed": speed_metric
        }

        return progress_bar, status_text, metrics_container

    def create_live_charts(self) -> Dict[str, Any]:
        """
        Crée les graphiques temps réel

        Returns:
            Dictionnaire des placeholders pour les graphiques
        """
        st.subheader("Métriques Temps Réel")

        # Conteneurs pour les graphiques
        chart_cols = st.columns(2)

        with chart_cols[0]:
            st.markdown("**Temps d'exécution par requête**")
            execution_chart = st.empty()

        with chart_cols[1]:
            st.markdown("**Utilisation des ressources**")
            resources_chart = st.empty()

        return {
            "execution": execution_chart,
            "resources": resources_chart
        }

    def update_progress(
        self,
        query_name: str,
        progress_bar,
        status_text,
        metrics_container
    ):
        """
        Met à jour la section de progression

        Args:
            query_name: Nom de la requête en cours
            progress_bar: Placeholder de la barre de progression
            status_text: Placeholder du texte de statut
            metrics_container: Conteneur des métriques
        """
        self.queries_completed += 1
        self.current_query = query_name

        # Mise à jour de la barre de progression
        progress = self.queries_completed / self.total_queries if self.total_queries > 0 else 0
        progress_bar.progress(min(progress, 1.0))

        # Mise à jour du statut
        status_text.text(
            f"🔄 En cours: {query_name} ({self.queries_completed}/{self.total_queries})"
        )

        # Calcul des métriques
        elapsed_time = time.time() - self.start_time
        queries_per_second = self.queries_completed / elapsed_time if elapsed_time > 0 else 0

        remaining_queries = self.total_queries - self.queries_completed
        eta_seconds = remaining_queries / queries_per_second if queries_per_second > 0 else 0

        # Mise à jour des métriques
        metrics_container["completed"].metric(
            "Complétées",
            f"{self.queries_completed}/{self.total_queries}",
            delta=f"{progress*100:.1f}%"
        )

        metrics_container["elapsed"].metric(
            "Temps écoulé",
            f"{elapsed_time:.1f}s"
        )

        metrics_container["eta"].metric(
            "Temps restant",
            f"{eta_seconds:.1f}s"
        )

        metrics_container["speed"].metric(
            "Vitesse",
            f"{queries_per_second:.2f} req/s"
        )

    def update_execution_chart(self, execution_time: float, query_name: str, charts_container):
        """
        Met à jour le graphique des temps d'exécution

        Args:
            execution_time: Temps d'exécution de la requête
            query_name: Nom de la requête
            charts_container: Conteneur des graphiques
        """
        self.execution_times.append(execution_time)
        self.timestamps.append(time.time() - self.start_time)

        # Créer le graphique
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=list(range(1, len(self.execution_times) + 1)),
            y=self.execution_times,
            mode='lines+markers',
            name='Temps d\'exécution',
            line=dict(color='royalblue', width=2),
            marker=dict(size=8)
        ))

        # Ligne de moyenne
        if self.execution_times:
            avg_time = sum(self.execution_times) / len(self.execution_times)
            fig.add_hline(
                y=avg_time,
                line_dash="dash",
                line_color="green",
                annotation_text=f"Moyenne: {avg_time:.3f}s"
            )

        fig.update_layout(
            xaxis_title="Requête #",
            yaxis_title="Temps (s)",
            height=300,
            margin=dict(l=0, r=0, t=30, b=0),
            showlegend=True
        )

        charts_container["execution"].plotly_chart(fig, use_container_width=True)

    def update_resources_chart(self, cpu_percent: float, memory_mb: float, charts_container):
        """
        Met à jour le graphique des ressources

        Args:
            cpu_percent: Utilisation CPU en pourcentage
            memory_mb: Utilisation mémoire en MB
            charts_container: Conteneur des graphiques
        """
        self.cpu_usage.append(cpu_percent)
        self.memory_usage.append(memory_mb)

        # Créer un graphique avec deux axes Y
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Trace CPU
        fig.add_trace(
            go.Scatter(
                x=list(range(1, len(self.cpu_usage) + 1)),
                y=self.cpu_usage,
                mode='lines',
                name='CPU %',
                line=dict(color='red', width=2)
            ),
            secondary_y=False
        )

        # Trace Mémoire
        fig.add_trace(
            go.Scatter(
                x=list(range(1, len(self.memory_usage) + 1)),
                y=self.memory_usage,
                mode='lines',
                name='Mémoire (MB)',
                line=dict(color='blue', width=2)
            ),
            secondary_y=True
        )

        # Mise à jour des axes
        fig.update_xaxes(title_text="Requête #")
        fig.update_yaxes(title_text="CPU %", secondary_y=False)
        fig.update_yaxes(title_text="Mémoire (MB)", secondary_y=True)

        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=30, b=0),
            showlegend=True,
            legend=dict(x=0, y=1)
        )

        charts_container["resources"].plotly_chart(fig, use_container_width=True)

    def update_all(
        self,
        query_name: str,
        execution_time: float,
        cpu_percent: float,
        memory_mb: float,
        progress_bar,
        status_text,
        metrics_container,
        charts_container
    ):
        """
        Met à jour tout le dashboard en une seule fois

        Args:
            query_name: Nom de la requête
            execution_time: Temps d'exécution
            cpu_percent: Utilisation CPU
            memory_mb: Utilisation mémoire
            progress_bar: Placeholder progression
            status_text: Placeholder statut
            metrics_container: Conteneur métriques
            charts_container: Conteneur graphiques
        """
        self.update_progress(query_name, progress_bar, status_text, metrics_container)
        self.update_execution_chart(execution_time, query_name, charts_container)
        self.update_resources_chart(cpu_percent, memory_mb, charts_container)

    def show_summary(self):
        """Affiche un résumé final des tests"""
        st.markdown("---")
        st.subheader("✅ Tests Terminés")

        total_time = time.time() - self.start_time

        # Statistiques finales
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Requêtes exécutées", self.queries_completed)

        with col2:
            st.metric("Temps total", f"{total_time:.2f}s")

        with col3:
            avg_time = sum(self.execution_times) / len(self.execution_times) if self.execution_times else 0
            st.metric("Temps moyen", f"{avg_time:.3f}s")

        with col4:
            throughput = self.queries_completed / total_time if total_time > 0 else 0
            st.metric("Débit", f"{throughput:.2f} req/s")

        # Statistiques détaillées
        if self.execution_times:
            st.markdown("#### Statistiques Détaillées")

            stats_df = pd.DataFrame({
                "Métrique": ["Min", "Max", "Moyenne", "Médiane", "Écart-type"],
                "Temps d'exécution (s)": [
                    f"{min(self.execution_times):.3f}",
                    f"{max(self.execution_times):.3f}",
                    f"{sum(self.execution_times)/len(self.execution_times):.3f}",
                    f"{sorted(self.execution_times)[len(self.execution_times)//2]:.3f}",
                    f"{pd.Series(self.execution_times).std():.3f}"
                ]
            })

            st.dataframe(stats_df, use_container_width=True, hide_index=True)


def demo_realtime_dashboard():
    """Démonstration du dashboard temps réel"""
    import random

    st.title("Démonstration Dashboard Temps Réel")

    if st.button("Lancer la démonstration"):
        # Initialiser le dashboard
        dashboard = RealtimeDashboard()
        dashboard.initialize_dashboard(
            total_queries=10,
            query_types=["Simple", "Jointure", "Agrégation"]
        )

        # Créer les sections
        progress_bar, status_text, metrics_container = dashboard.create_progress_section()
        charts_container = dashboard.create_live_charts()

        # Simuler des requêtes
        for i in range(10):
            query_name = f"Test Query {i+1}"
            execution_time = random.uniform(0.5, 3.0)
            cpu_percent = random.uniform(20, 80)
            memory_mb = random.uniform(100, 500)

            dashboard.update_all(
                query_name=query_name,
                execution_time=execution_time,
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                progress_bar=progress_bar,
                status_text=status_text,
                metrics_container=metrics_container,
                charts_container=charts_container
            )

            time.sleep(0.5)

        # Afficher le résumé
        dashboard.show_summary()


if __name__ == "__main__":
    demo_realtime_dashboard()
