"""
Onglet d'analyses détaillées avec insights avancés et recommandations
Module pour analyser les résultats de benchmarks SPARQL
"""

import streamlit as st
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Import du design system
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from ui.design_system import (
    Colors, Typography, Spacing, Effects,
    create_card, create_metric_card, create_alert, create_divider,
    create_status_badge
)


class PerformanceAnalyzer:
    """Analyseur de performances avec statistiques et détection d'anomalies"""

    def __init__(self, results: Dict):
        """
        Initialise l'analyseur avec les résultats de tests

        Args:
            results: Dictionnaire contenant les résultats des benchmarks
                    Format attendu: {
                        'virtuoso': {'times': [...], 'queries': [...]},
                        'fuseki': {'times': [...], 'queries': [...]}
                    }
        """
        self.results = results
        self.stats = {}
        self.anomalies = []
        self.recommendations = []

        if results:
            self._compute_statistics()
            self._detect_anomalies()
            self._generate_recommendations()

    def _compute_statistics(self):
        """Calcule les statistiques pour chaque triplestore"""
        for engine in ['virtuoso', 'fuseki']:
            if engine in self.results and 'times' in self.results[engine]:
                times = np.array(self.results[engine]['times'])

                self.stats[engine] = {
                    'mean': np.mean(times),
                    'median': np.median(times),
                    'std': np.std(times),
                    'min': np.min(times),
                    'max': np.max(times),
                    'p25': np.percentile(times, 25),
                    'p75': np.percentile(times, 75),
                    'p95': np.percentile(times, 95),
                    'p99': np.percentile(times, 99),
                    'count': len(times)
                }

    def _detect_anomalies(self):
        """Détecte les anomalies (outliers) dans les résultats"""
        for engine in ['virtuoso', 'fuseki']:
            if engine not in self.stats:
                continue

            times = np.array(self.results[engine]['times'])
            mean = self.stats[engine]['mean']
            std = self.stats[engine]['std']

            # Détection des outliers (> 2.5 écart-types)
            threshold = mean + 2.5 * std

            for idx, time in enumerate(times):
                if time > threshold:
                    query_id = idx + 1
                    deviation = ((time - mean) / mean) * 100

                    self.anomalies.append({
                        'engine': engine,
                        'query_id': query_id,
                        'time': time,
                        'mean': mean,
                        'deviation': deviation,
                        'severity': 'critical' if deviation > 200 else 'warning',
                        'reason': f"Temps {deviation:.0f}% supérieur à la moyenne"
                    })

    def _generate_recommendations(self):
        """Génère des recommandations basées sur les analyses"""
        if not self.stats:
            return

        # Recommandation 1: Comparaison globale
        if 'virtuoso' in self.stats and 'fuseki' in self.stats:
            v_mean = self.stats['virtuoso']['mean']
            f_mean = self.stats['fuseki']['mean']

            diff_pct = abs((v_mean - f_mean) / max(v_mean, f_mean)) * 100

            if diff_pct > 30:
                winner = 'Virtuoso' if v_mean < f_mean else 'Fuseki'
                loser = 'Fuseki' if winner == 'Virtuoso' else 'Virtuoso'

                self.recommendations.append({
                    'level': 'important',
                    'title': f"Performance globale : {winner} est +{diff_pct:.0f}% plus rapide",
                    'icon': '⚡',
                    'color': Colors.PRIMARY,
                    'content': f"""**{winner}** performe significativement mieux que {loser} sur l'ensemble des requêtes testées.

**Recommandation** : Privilégier {winner} pour ce type de workload."""
                })

        # Recommandation 2: Variabilité haute
        for engine in ['virtuoso', 'fuseki']:
            if engine not in self.stats:
                continue

            cv = (self.stats[engine]['std'] / self.stats[engine]['mean']) * 100

            if cv > 80:
                self.recommendations.append({
                    'level': 'warning',
                    'title': f"Variabilité élevée détectée sur {engine.capitalize()}",
                    'icon': '⚠️',
                    'color': Colors.WARNING,
                    'content': f"""Le coefficient de variation est de **{cv:.0f}%**, indiquant une forte variabilité dans les temps de réponse.

**Causes possibles** :
- Cache non optimal
- Requêtes de complexité très variable
- Ressources système fluctuantes

**Action** : Analyser les requêtes individuellement."""
                })

        # Recommandation 3: Anomalies critiques
        critical_anomalies = [a for a in self.anomalies if a['severity'] == 'critical']

        if len(critical_anomalies) > 0:
            self.recommendations.append({
                'level': 'critical',
                'title': f"{len(critical_anomalies)} anomalie(s) critique(s) détectée(s)",
                'icon': '🔴',
                'color': Colors.ERROR,
                'content': f"""**{len(critical_anomalies)} requête(s)** présentent des temps d'exécution anormalement élevés (>200% de la moyenne).

**Recommandations** :
- Vérifier les index sur les prédicats utilisés
- Optimiser les clauses JOIN et FILTER
- Augmenter les ressources allouées
- Analyser les plans d'exécution"""
            })

        # Recommandation 4: Optimisation générale
        if 'virtuoso' in self.stats or 'fuseki' in self.stats:
            self.recommendations.append({
                'level': 'info',
                'title': "Optimisations générales recommandées",
                'icon': '💡',
                'color': Colors.INFO,
                'content': """**Pour améliorer les performances globales** :

- **Cache** : Augmenter la taille du cache de requêtes
- **Warmup** : Augmenter les itérations de préchauffage
- **Index** : Créer des index sur les prédicats fréquents
- **Dataset** : Tester avec des tailles variées
- **Concurrent** : Tester avec plusieurs requêtes simultanées"""
            })

    def get_comparison_metrics(self) -> Dict:
        """Retourne les métriques de comparaison entre les deux engines"""
        if 'virtuoso' not in self.stats or 'fuseki' not in self.stats:
            return {}

        v = self.stats['virtuoso']
        f = self.stats['fuseki']

        return {
            'mean_diff': ((v['mean'] - f['mean']) / f['mean']) * 100,
            'median_diff': ((v['median'] - f['median']) / f['median']) * 100,
            'winner': 'virtuoso' if v['mean'] < f['mean'] else 'fuseki',
            'winner_advantage': abs(((v['mean'] - f['mean']) / max(v['mean'], f['mean'])) * 100)
        }


def create_statistics_table(analyzer: PerformanceAnalyzer) -> pd.DataFrame:
    """Crée un DataFrame des statistiques pour affichage Streamlit natif"""

    stats = analyzer.stats

    if not stats:
        return None

    metrics = [
        ('Moyenne', 'mean', 'ms'),
        ('Médiane', 'median', 'ms'),
        ('Minimum', 'min', 'ms'),
        ('Maximum', 'max', 'ms'),
        ('Écart-type', 'std', 'ms'),
        ('P95', 'p95', 'ms'),
        ('P99', 'p99', 'ms'),
        ('Nombre', 'count', '')
    ]

    # Créer les données du DataFrame
    data = {'Métrique': []}

    if 'virtuoso' in stats:
        data['Virtuoso'] = []

    if 'fuseki' in stats:
        data['Fuseki'] = []

    for label, key, unit in metrics:
        data['Métrique'].append(label)

        if 'virtuoso' in stats:
            value = stats['virtuoso'][key]
            formatted = f"{value:.1f} {unit}" if isinstance(value, float) else f"{value} {unit}"
            data['Virtuoso'].append(formatted.strip())

        if 'fuseki' in stats:
            value = stats['fuseki'][key]
            formatted = f"{value:.1f} {unit}" if isinstance(value, float) else f"{value} {unit}"
            data['Fuseki'].append(formatted.strip())

    return pd.DataFrame(data)


def create_box_plot(analyzer: PerformanceAnalyzer):
    """Crée un box plot comparatif"""

    fig = go.Figure()

    if 'virtuoso' in analyzer.results:
        fig.add_trace(go.Box(
            y=analyzer.results['virtuoso']['times'],
            name='Virtuoso',
            marker_color=Colors.VIRTUOSO,
            boxmean='sd'
        ))

    if 'fuseki' in analyzer.results:
        fig.add_trace(go.Box(
            y=analyzer.results['fuseki']['times'],
            name='Fuseki',
            marker_color=Colors.FUSEKI,
            boxmean='sd'
        ))

    fig.update_layout(
        title='Distribution des Temps de Réponse',
        yaxis_title='Temps (ms)',
        height=400,
        showlegend=True,
        template='plotly_white'
    )

    return fig


def create_comparison_bar_chart(analyzer: PerformanceAnalyzer):
    """Crée un graphique à barres comparatif"""

    if not analyzer.stats:
        return None

    metrics = ['mean', 'median', 'p95', 'p99']
    metric_labels = ['Moyenne', 'Médiane', 'P95', 'P99']

    data = []

    for engine in ['virtuoso', 'fuseki']:
        if engine in analyzer.stats:
            values = [analyzer.stats[engine][m] for m in metrics]
            data.append({
                'engine': engine.capitalize(),
                'values': values,
                'color': Colors.VIRTUOSO if engine == 'virtuoso' else Colors.FUSEKI
            })

    fig = go.Figure()

    for d in data:
        fig.add_trace(go.Bar(
            x=metric_labels,
            y=d['values'],
            name=d['engine'],
            marker_color=d['color']
        ))

    fig.update_layout(
        title='Comparaison des Métriques Clés',
        yaxis_title='Temps (ms)',
        barmode='group',
        height=400,
        template='plotly_white'
    )

    return fig


def create_violin_plot(analyzer: PerformanceAnalyzer):
    """Crée un violin plot pour montrer la distribution"""

    fig = go.Figure()

    if 'virtuoso' in analyzer.results:
        fig.add_trace(go.Violin(
            y=analyzer.results['virtuoso']['times'],
            name='Virtuoso',
            box_visible=True,
            meanline_visible=True,
            fillcolor=Colors.VIRTUOSO,
            opacity=0.6,
            x0='Virtuoso'
        ))

    if 'fuseki' in analyzer.results:
        fig.add_trace(go.Violin(
            y=analyzer.results['fuseki']['times'],
            name='Fuseki',
            box_visible=True,
            meanline_visible=True,
            fillcolor=Colors.FUSEKI,
            opacity=0.6,
            x0='Fuseki'
        ))

    fig.update_layout(
        title='Distribution Détaillée (Violin Plot)',
        yaxis_title='Temps (ms)',
        height=400,
        showlegend=False,
        template='plotly_white'
    )

    return fig


def render_detailed_analysis_tab():
    """Fonction principale pour afficher l'onglet d'analyses détaillées"""

    st.markdown("## 🔬 Analyses Détaillées")
    st.caption("Insights avancés, statistiques et recommandations automatiques")

    create_divider()

    # Charger les résultats depuis session_state
    # Vérifier d'abord results_df (format actuel de l'application)
    results_df = st.session_state.get('results_df', None)

    # Convertir results_df au format attendu par l'analyseur
    results = None
    if results_df is not None and not results_df.empty:
        try:
            # Convertir execution_time de secondes en millisecondes et extraire par moteur
            results = {}

            # Filtrer Virtuoso (excluant les variantes "Concurrent")
            virtuoso_df = results_df[results_df['engine'] == 'Virtuoso']
            if not virtuoso_df.empty:
                results['virtuoso'] = {
                    'times': (virtuoso_df['execution_time'] * 1000).tolist(),  # Convertir s → ms
                    'queries': list(range(1, len(virtuoso_df) + 1))
                }

            # Filtrer Jena Fuseki (excluant les variantes "Concurrent")
            fuseki_df = results_df[results_df['engine'] == 'Jena Fuseki']
            if not fuseki_df.empty:
                results['fuseki'] = {
                    'times': (fuseki_df['execution_time'] * 1000).tolist(),  # Convertir s → ms
                    'queries': list(range(1, len(fuseki_df) + 1))
                }

            # Vérifier que nous avons des résultats pour au moins un moteur
            if not results.get('virtuoso') and not results.get('fuseki'):
                results = None

        except Exception as e:
            st.error(f"❌ Erreur lors de la conversion des résultats: {str(e)}")
            results = None

    # Vérifier aussi l'ancien format 'benchmark_results' (pour compatibilité)
    if not results:
        results = st.session_state.get('benchmark_results', None)

    if not results or not results.get('virtuoso') and not results.get('fuseki'):
        create_alert(
            "Aucun résultat disponible pour l'analyse. "
            "Veuillez d'abord exécuter des tests dans l'onglet 'Configuration & Tests'.",
            alert_type="info"
        )

        # Guide visuel avec Streamlit natif
        col1, col2 = st.columns(2)

        with col1:
            st.info("🚀 **Comment obtenir des résultats ?**")
            st.markdown("""
1. Allez dans l'onglet **Configuration & Tests**
2. Sélectionnez les requêtes à tester
3. Cliquez sur **Exécuter les tests**
4. Revenez ici pour voir les analyses
            """)

        with col2:
            st.success("ℹ️ **Ce que vous verrez**")
            st.markdown("""
- **Statistiques avancées** (moyenne, P95, P99)
- **Détection d'anomalies** automatique
- **Recommandations** personnalisées
- **Visualisations** interactives
            """)

        return

    # Créer l'analyseur
    analyzer = PerformanceAnalyzer(results)

    # ==========================================================================
    # 1. VUE D'ENSEMBLE
    # ==========================================================================
    st.markdown("### Vue d'Ensemble")

    col1, col2, col3, col4 = st.columns(4)

    if 'virtuoso' in analyzer.stats:
        with col1:
            create_metric_card(
                label="Moyenne Virtuoso",
                value=f"{analyzer.stats['virtuoso']['mean']:.1f} ms",
                delta=f"±{analyzer.stats['virtuoso']['std']:.1f}",
                icon="🔴",
                color=Colors.VIRTUOSO
            )

        with col2:
            create_metric_card(
                label="P95 Virtuoso",
                value=f"{analyzer.stats['virtuoso']['p95']:.1f} ms",
                icon="ℹ️",
                color=Colors.VIRTUOSO
            )

    if 'fuseki' in analyzer.stats:
        with col3:
            create_metric_card(
                label="Moyenne Fuseki",
                value=f"{analyzer.stats['fuseki']['mean']:.1f} ms",
                delta=f"±{analyzer.stats['fuseki']['std']:.1f}",
                icon="🔵",
                color=Colors.FUSEKI
            )

        with col4:
            create_metric_card(
                label="P95 Fuseki",
                value=f"{analyzer.stats['fuseki']['p95']:.1f} ms",
                icon="ℹ️",
                color=Colors.FUSEKI
            )

    # Comparaison globale
    if 'virtuoso' in analyzer.stats and 'fuseki' in analyzer.stats:
        comparison = analyzer.get_comparison_metrics()

        winner_name = comparison['winner'].capitalize()
        advantage = comparison['winner_advantage']

        if advantage > 10:
            icon = "✅" if advantage > 30 else "ℹ️"
            st.markdown(f"""
            <div style="
                background: {Colors.PRIMARY_PALE};
                border-left: 4px solid {Colors.PRIMARY};
                padding: {Spacing.LG};
                border-radius: {Effects.RADIUS_MD};
                margin-top: {Spacing.MD};
            ">
                <div style="
                    font-size: {Typography.SIZE_H3};
                    font-weight: {Typography.WEIGHT_BOLD};
                    color: {Colors.PRIMARY};
                    margin-bottom: {Spacing.SM};
                ">
                    {icon} Gagnant : {winner_name}
                </div>
                <div style="color: {Colors.TEXT_PRIMARY};">
                    <strong>{winner_name}</strong> est <strong>{advantage:.1f}%</strong> plus rapide en moyenne
                </div>
            </div>
            """, unsafe_allow_html=True)

    create_divider()

    # ==========================================================================
    # 2. STATISTIQUES DÉTAILLÉES
    # ==========================================================================
    st.markdown("### Statistiques Détaillées")

    stats_df = create_statistics_table(analyzer)

    if stats_df is not None:
        st.markdown("**Métriques Statistiques Complètes**")
        st.dataframe(
            stats_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Métrique": st.column_config.TextColumn("Métrique", width="medium"),
                "Virtuoso": st.column_config.TextColumn("Virtuoso", width="medium"),
                "Fuseki": st.column_config.TextColumn("Fuseki", width="medium")
            }
        )
    else:
        st.info("Aucune statistique disponible")

    create_divider()

    # ==========================================================================
    # 3. DÉTECTION D'ANOMALIES
    # ==========================================================================
    st.markdown("### ⚠️ Détection d'Anomalies")

    if analyzer.anomalies:
        # Séparer par sévérité
        critical = [a for a in analyzer.anomalies if a['severity'] == 'critical']
        warnings = [a for a in analyzer.anomalies if a['severity'] == 'warning']

        if critical:
            create_alert(
                f"🔴 {len(critical)} anomalie(s) critique(s) détectée(s) - Action requise",
                alert_type="error"
            )

            for anomaly in critical[:5]:  # Limiter à 5
                st.markdown(f"""
                **Requête #{anomaly['query_id']}** ({anomaly['engine'].capitalize()})
                - Temps : **{anomaly['time']:.1f} ms** (moyenne: {anomaly['mean']:.1f} ms)
                - Écart : **+{anomaly['deviation']:.0f}%** par rapport à la moyenne
                - Raison : {anomaly['reason']}
                """)

        if warnings:
            create_alert(
                f"🟡 {len(warnings)} avertissement(s) détecté(s)",
                alert_type="warning"
            )
    else:
        create_alert(
            "✅ Aucune anomalie détectée - Les performances sont stables",
            alert_type="success"
        )

    create_divider()

    # ==========================================================================
    # 4. RECOMMANDATIONS
    # ==========================================================================
    st.markdown("### Recommandations Personnalisées")

    if analyzer.recommendations:
        for rec in analyzer.recommendations:
            # Déterminer le type d'expander selon la couleur
            if rec['color'] == Colors.WARNING:
                st.warning(f"**{rec['icon']} {rec['title']}**")
                st.markdown(rec['content'])
            elif rec['color'] == Colors.PRIMARY:
                st.info(f"**{rec['icon']} {rec['title']}**")
                st.markdown(rec['content'])
            else:
                st.markdown(f"**{rec['icon']} {rec['title']}**")
                st.markdown(rec['content'])
            st.markdown("---")  # Séparateur
    else:
        st.info("Aucune recommandation spécifique pour le moment.")

    create_divider()

    # ==========================================================================
    # 5. VISUALISATIONS AVANCÉES
    # ==========================================================================
    st.markdown("### Visualisations Avancées")

    # Box plot
    fig_box = create_box_plot(analyzer)
    st.plotly_chart(fig_box, use_container_width=True)

    # Graphique à barres comparatif
    fig_bar = create_comparison_bar_chart(analyzer)
    if fig_bar:
        st.plotly_chart(fig_bar, use_container_width=True)

    # Violin plot
    fig_violin = create_violin_plot(analyzer)
    st.plotly_chart(fig_violin, use_container_width=True)

    create_divider()

    # ==========================================================================
    # 6. EXPORT DES ANALYSES
    # ==========================================================================
    st.markdown("### 📥 Export des Analyses")

    col1, col2 = st.columns(2)

    with col1:
        # Export JSON
        if st.button("📄 Exporter en JSON", use_container_width=True):
            import json

            export_data = {
                'timestamp': datetime.now().isoformat(),
                'statistics': analyzer.stats,
                'anomalies': analyzer.anomalies,
                'recommendations': [
                    {'title': r['title'], 'level': r['level']}
                    for r in analyzer.recommendations
                ]
            }

            filename = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            st.download_button(
                label="💾 Télécharger",
                data=json.dumps(export_data, indent=2, ensure_ascii=False),
                file_name=filename,
                mime="application/json",
                use_container_width=True
            )

    with col2:
        # Export CSV
        if st.button("Exporter en CSV", use_container_width=True):
            # Créer un DataFrame avec les stats
            df_data = []
            for engine, stats in analyzer.stats.items():
                for metric, value in stats.items():
                    df_data.append({
                        'Engine': engine.capitalize(),
                        'Metric': metric,
                        'Value': value
                    })

            df = pd.DataFrame(df_data)
            csv = df.to_csv(index=False)

            filename = f"statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            st.download_button(
                label="💾 Télécharger",
                data=csv,
                file_name=filename,
                mime="text/csv",
                use_container_width=True
            )


# Fonction principale d'export
def render_analysis_tab():
    """Point d'entrée principal pour l'onglet d'analyse"""
    render_detailed_analysis_tab()


if __name__ == "__main__":
    # Test avec données simulées
    test_results = {
        'virtuoso': {
            'times': [12, 15, 18, 145, 11, 16, 1250, 14, 19, 13],
            'queries': list(range(1, 11))
        },
        'fuseki': {
            'times': [15, 18, 22, 189, 14, 19, 245, 17, 23, 16],
            'queries': list(range(1, 11))
        }
    }

    st.session_state['benchmark_results'] = test_results
    render_analysis_tab()
