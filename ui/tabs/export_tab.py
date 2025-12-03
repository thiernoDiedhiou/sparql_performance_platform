"""
Onglet d'exportation des résultats
"""

import streamlit as st
import pandas as pd
import numpy as np
import io
import json
from datetime import datetime
from utils.data_manager import get_test_results, is_test_completed
from utils.helpers import create_benchmark_summary, export_results_to_json, format_test_results_summary

# Import conditionnel pour la visualisation
try:
    from visualization.visualizer import ResultVisualizer
    VISUALIZER_AVAILABLE = True
except ImportError:
    VISUALIZER_AVAILABLE = False

def render_export_tab():
    """Affiche l'onglet d'exportation"""
    st.header("📤 Exportation des résultats")
    
    if not is_test_completed():
        st.info("ℹ️ Aucun test n'a encore été exécuté. Allez dans l'onglet 'Configuration et tests' pour lancer les tests.")
        
        # Afficher un guide d'utilisation
        with st.expander("📖 Guide pour commencer"):
            st.markdown("""
            ### Comment effectuer vos premiers tests
            
            1. **Aller dans l'onglet 'Configuration et tests'**
            2. **Configurer les endpoints** dans la barre latérale (ou utiliser les endpoints de test)
            3. **Sélectionner les types de requêtes** à tester
            4. **Cliquer sur 'Exécuter les tests'**
            5. **Revenir ici** pour exporter les résultats
            
            ### Endpoints de test recommandés
            
            Si vous n'avez pas encore configuré vos moteurs SPARQL locaux, vous pouvez utiliser :
            - **DBpedia public** : `https://dbpedia.org/sparql`
            - **Wikidata public** : `https://query.wikidata.org/sparql`
            
            ⚠️ *Note: Les endpoints publics peuvent être plus lents et avoir des limitations*
            """)
        
        return
    
    results_df = get_test_results()
    
    if results_df is None or results_df.empty:
        st.warning("⚠️ Aucun résultat disponible pour l'exportation.")
        st.info("Les tests semblent avoir été exécutés mais aucune donnée n'a été sauvegardée.")
        return
    
    # Vérifier la validité des données
    if not _validate_results_data(results_df):
        st.error("❌ Les données de résultats sont incomplètes ou corrompues.")
        st.info("Veuillez relancer les tests pour obtenir des données valides.")
        return
    
    # Section d'exportation des données brutes
    render_data_export_section(results_df)
    
    # Section de génération de rapports
    render_report_generation_section(results_df)
    
    # Section d'exportation de visualisations
    render_visualization_export_section(results_df)

def _validate_results_data(results_df: pd.DataFrame) -> bool:
    """
    Valide que les données de résultats contiennent les colonnes nécessaires
    
    Args:
        results_df: DataFrame des résultats
        
    Returns:
        True si les données sont valides
    """
    required_columns = ['execution_time', 'success', 'engine']
    missing_columns = [col for col in required_columns if col not in results_df.columns]
    
    if missing_columns:
        st.warning(f"⚠️ Colonnes manquantes dans les données: {', '.join(missing_columns)}")
        st.write("**Colonnes disponibles:**", list(results_df.columns))
        return False
    
    return True

def render_data_export_section(results_df: pd.DataFrame):
    """
    Affiche la section d'exportation des données brutes
    
    Args:
        results_df: DataFrame des résultats
    """
    st.subheader("Exportation des données brutes")
    
    # Aperçu des données
    with st.expander("👀 Aperçu des données à exporter"):
        st.write(f"**Nombre total d'enregistrements:** {len(results_df)}")
        st.write(f"**Colonnes disponibles:** {', '.join(results_df.columns)}")
        st.dataframe(results_df.head(10), use_container_width=True)
    
    # Options d'exportation
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.radio(
            "📁 Format d'exportation",
            options=["CSV", "Excel", "JSON"],
            help="Choisissez le format pour exporter les données"
        )
    
    with col2:
        include_metadata = st.checkbox(
            "Inclure les métadonnées",
            value=True,
            help="Ajouter des informations sur l'export (date, configuration, etc.)"
        )
    
    # Génération et téléchargement
    try:
        if export_format == "CSV":
            render_csv_export(results_df, include_metadata)
        elif export_format == "Excel":
            render_excel_export(results_df, include_metadata)
        elif export_format == "JSON":
            render_json_export(results_df, include_metadata)
    except Exception as e:
        st.error(f"Erreur lors de l'export {export_format}: {str(e)}")

def render_csv_export(results_df: pd.DataFrame, include_metadata: bool):
    """
    Gère l'export CSV
    
    Args:
        results_df: DataFrame des résultats
        include_metadata: Inclure les métadonnées
    """
    try:
        csv_data = results_df.to_csv(index=False)
        
        if include_metadata:
            metadata = f"""# Résultats de performance SPARQL
# Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Nombre d'enregistrements: {len(results_df)}
# Colonnes: {', '.join(results_df.columns)}

"""
            csv_data = metadata + csv_data
        
        st.download_button(
            label="📥 Télécharger en CSV",
            data=csv_data,
            file_name=f"sparql_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            help="Télécharge les résultats au format CSV"
        )
        
    except Exception as e:
        st.error(f"Erreur lors de la génération du CSV: {str(e)}")

def render_excel_export(results_df: pd.DataFrame, include_metadata: bool):
    """
    Gère l'export Excel
    
    Args:
        results_df: DataFrame des résultats
        include_metadata: Inclure les métadonnées
    """
    try:
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Feuille principale avec les résultats
            results_df.to_excel(writer, sheet_name='Résultats', index=False)
            
            # Feuille résumé si le visualiseur est disponible
            if VISUALIZER_AVAILABLE and _validate_results_data(results_df):
                try:
                    from visualization.visualizer import ResultVisualizer
                    visualizer = ResultVisualizer()
                    summary_table = visualizer.create_summary_table(results_df)
                    summary_table.to_excel(writer, sheet_name='Résumé', index=False)
                except Exception:
                    pass  # Ignorer si le résumé ne peut pas être créé
            
            # Feuille statistiques
            if 'execution_time' in results_df.columns and 'query_name' in results_df.columns and 'engine' in results_df.columns:
                try:
                    stats_df = results_df.groupby(['query_name', 'engine']).agg({
                        'execution_time': ['mean', 'min', 'max', 'std', 'count'],
                        'success': 'mean'
                    }).round(4)
                    stats_df.to_excel(writer, sheet_name='Statistiques')
                except Exception:
                    pass  # Ignorer si les statistiques ne peuvent pas être créées
            
            # Métadonnées si demandées
            if include_metadata:
                metadata_df = pd.DataFrame({
                    'Paramètre': [
                        'Date de génération',
                        'Nombre d\'enregistrements',
                        'Nombre de requêtes uniques',
                        'Nombre de moteurs testés',
                        'Taux de succès global (%)'
                    ],
                    'Valeur': [
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        len(results_df),
                        results_df['query_name'].nunique() if 'query_name' in results_df.columns else 'N/A',
                        results_df['engine'].nunique() if 'engine' in results_df.columns else 'N/A',
                        f"{results_df['success'].mean() * 100:.2f}" if 'success' in results_df.columns else 'N/A'
                    ]
                })
                metadata_df.to_excel(writer, sheet_name='Métadonnées', index=False)
        
        buffer.seek(0)
        
        st.download_button(
            label="📥 Télécharger en Excel",
            data=buffer,
            file_name=f"sparql_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Télécharge les résultats au format Excel avec feuilles multiples"
        )
        
    except Exception as e:
        st.error(f"Erreur lors de la génération du fichier Excel: {str(e)}")

def render_json_export(results_df: pd.DataFrame, include_metadata: bool):
    """
    Gère l'export JSON
    
    Args:
        results_df: DataFrame des résultats
        include_metadata: Inclure les métadonnées
    """
    try:
        json_data = export_results_to_json(results_df)
        
        st.download_button(
            label="📥 Télécharger en JSON",
            data=json_data,
            file_name=f"sparql_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            help="Télécharge les résultats au format JSON avec métadonnées"
        )
        
    except Exception as e:
        st.error(f"Erreur lors de la génération du JSON: {str(e)}")

def render_report_generation_section(results_df: pd.DataFrame):
    """
    Affiche la section de génération de rapports

    Args:
        results_df: DataFrame des résultats
    """
    st.subheader("📝 Génération de rapports")

    # Vérifier si les données sont suffisantes pour un rapport
    if not _validate_results_data(results_df):
        st.warning("⚠️ Données insuffisantes pour générer un rapport complet.")
        return

    report_type = st.selectbox(
        "📋 Type de rapport",
        options=[
            "Rapport complet",
            "Résumé exécutif",
            "Rapport technique",
            "Comparaison des moteurs",
            "Analyse de performance",
            "Rapport avancé avec percentiles (P50/P95/P99)"  # ⭐ NOUVEAU
        ],
        help="Choisissez le type de rapport à générer"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        include_charts_desc = st.checkbox(
            "Inclure les descriptions de graphiques",
            value=True,
            help="Ajouter des descriptions détaillées des visualisations"
        )
    
    with col2:
        include_recommendations = st.checkbox(
            "Inclure les recommandations",
            value=True,
            help="Ajouter des recommandations basées sur l'analyse"
        )
    
    if st.button("📄 Générer le rapport", type="primary"):
        with st.spinner("Génération du rapport en cours..."):
            try:
                report_content = generate_report_safe(
                    results_df, 
                    report_type, 
                    include_charts_desc, 
                    include_recommendations
                )
                
                # Aperçu du rapport
                st.subheader("👀 Aperçu du rapport")
                with st.expander("Voir le contenu du rapport", expanded=True):
                    st.markdown(report_content)
                
                # Téléchargement du rapport
                st.download_button(
                    label="📥 Télécharger le rapport",
                    data=report_content,
                    file_name=f"rapport_sparql_{report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    help="Télécharge le rapport au format Markdown"
                )
                
            except Exception as e:
                st.error(f"Erreur lors de la génération du rapport: {str(e)}")
                st.info("Vérifiez que les données de test sont complètes et valides.")
                
                # Rapport d'erreur détaillé
                error_report = f"""# Erreur lors de la génération du rapport

**Erreur rencontrée:** {str(e)}

**Informations de débogage:**
- Nombre d'enregistrements: {len(results_df)}
- Colonnes disponibles: {', '.join(results_df.columns)}
- Types de données: {dict(results_df.dtypes)}

**Suggestions:**
1. Vérifiez que les tests ont été exécutés correctement
2. Assurez-vous que les colonnes requises sont présentes
3. Contactez le support technique si le problème persiste

---
*Rapport d'erreur généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
                
                st.download_button(
                    label="📥 Télécharger le rapport d'erreur",
                    data=error_report,
                    file_name=f"erreur_rapport_sparql_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    help="Télécharge un rapport d'erreur pour diagnostic"
                )

def generate_advanced_percentile_report(results_df: pd.DataFrame, include_recommendations: bool) -> str:
    """
    Génère un rapport avancé avec analyse des percentiles (P50/P95/P99)

    Args:
        results_df: DataFrame des résultats
        include_recommendations: Inclure les recommandations

    Returns:
        Contenu du rapport en Markdown avec percentiles
    """
    try:
        # En-tête du rapport
        report = f"""# Rapport avancé de performance SPARQL - Analyse par percentiles

**Date de génération:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Introduction

Ce rapport présente une **analyse statistique avancée** des performances SPARQL en utilisant les percentiles.
Les percentiles permettent d'identifier les valeurs typiques (P50), les seuils de SLA (P95), et les valeurs aberrantes (P99).

### Méthodologie

- **P50 (Médiane):** Temps d'exécution typique - 50% des requêtes sont plus rapides
- **P75:** 75% des requêtes sont plus rapides que cette valeur
- **P90:** 90% des requêtes sont plus rapides que cette valeur
- **P95 (SLA):** Seuil de qualité de service - 95% des requêtes respectent ce temps
- **P99 (Outliers):** Détection des cas extrêmes - 99% des requêtes sont plus rapides

### Données analysées

- **Nombre d'exécutions:** {len(results_df)}
- **Colonnes disponibles:** {', '.join(results_df.columns)}
- **Période d'analyse:** {datetime.now().strftime('%Y-%m-%d')}

---

"""

        # Validation des colonnes nécessaires
        if 'execution_time' not in results_df.columns:
            report += """
## ⚠️ Données insuffisantes

Les données d'exécution ne sont pas disponibles pour calculer les percentiles.

**Colonnes requises manquantes:** execution_time
"""
            return report

        # Calcul des percentiles globaux
        exec_times = results_df['execution_time'].dropna()

        if len(exec_times) == 0:
            report += """
## ⚠️ Aucune donnée d'exécution

Aucune mesure de temps d'exécution n'est disponible.
"""
            return report

        # Calcul des percentiles avec numpy
        percentiles = {
            'p50': float(np.percentile(exec_times, 50)),
            'p75': float(np.percentile(exec_times, 75)),
            'p90': float(np.percentile(exec_times, 90)),
            'p95': float(np.percentile(exec_times, 95)),
            'p99': float(np.percentile(exec_times, 99)),
            'min': float(exec_times.min()),
            'max': float(exec_times.max()),
            'mean': float(exec_times.mean()),
            'std': float(exec_times.std())
        }

        # Section: Percentiles globaux
        report += f"""
## 📊 Percentiles globaux - Temps d'exécution

| Métrique | Temps (secondes) | Description |
|----------|------------------|-------------|
| **Minimum** | {percentiles['min']:.6f} | Temps le plus rapide observé |
| **P50 (Médiane)** | {percentiles['p50']:.6f} | Performance typique |
| **P75** | {percentiles['p75']:.6f} | 75% des requêtes plus rapides |
| **P90** | {percentiles['p90']:.6f} | 90% des requêtes plus rapides |
| **P95 (SLA)** | {percentiles['p95']:.6f} | Seuil de qualité de service |
| **P99 (Outliers)** | {percentiles['p99']:.6f} | Détection des valeurs extrêmes |
| **Maximum** | {percentiles['max']:.6f} | Temps le plus lent observé |
| **Moyenne** | {percentiles['mean']:.6f} | Moyenne arithmétique |
| **Écart-type** | {percentiles['std']:.6f} | Variation des performances |

### Interprétation

"""

        # Ajout d'interprétations automatiques
        if percentiles['p95'] < 1.0:
            report += "- ✅ **Excellente performance:** 95% des requêtes s'exécutent en moins d'1 seconde\n"
        elif percentiles['p95'] < 5.0:
            report += "- ✅ **Bonne performance:** 95% des requêtes s'exécutent en moins de 5 secondes\n"
        elif percentiles['p95'] < 10.0:
            report += "- ⚠️ **Performance acceptable:** 95% des requêtes s'exécutent en moins de 10 secondes\n"
        else:
            report += "- ⚠️ **Performance à améliorer:** Le P95 dépasse 10 secondes\n"

        if percentiles['p99'] > percentiles['p95'] * 3:
            report += "- ⚠️ **Présence d'outliers significatifs:** Le P99 est 3× plus lent que le P95\n"

        if percentiles['std'] > percentiles['mean']:
            report += "- ⚠️ **Forte variabilité:** L'écart-type dépasse la moyenne (performances instables)\n"

        report += "\n---\n\n"

        # Section: Percentiles par requête (si disponible)
        if 'query_name' in results_df.columns:
            report += "## 📈 Percentiles par requête\n\n"

            query_stats = []
            for query_name in results_df['query_name'].unique():
                query_data = results_df[results_df['query_name'] == query_name]['execution_time'].dropna()

                if len(query_data) > 0:
                    query_stats.append({
                        'Requête': query_name,
                        'P50': np.percentile(query_data, 50),
                        'P95': np.percentile(query_data, 95),
                        'P99': np.percentile(query_data, 99),
                        'Moyenne': query_data.mean(),
                        'Min': query_data.min(),
                        'Max': query_data.max(),
                        'Exécutions': len(query_data)
                    })

            if query_stats:
                query_df = pd.DataFrame(query_stats)
                query_df = query_df.sort_values('P95', ascending=False)

                report += query_df.to_markdown(index=False, floatfmt=".6f")
                report += "\n\n"

                # Top 5 requêtes les plus lentes (P95)
                report += "### 🐌 Top 5 requêtes les plus lentes (P95)\n\n"
                top_slowest = query_df.head(5)
                for idx, row in top_slowest.iterrows():
                    report += f"{idx+1}. **{row['Requête']}** - P95: {row['P95']:.6f}s (Moyenne: {row['Moyenne']:.6f}s)\n"

                report += "\n"

                # Top 5 requêtes les plus rapides (P50)
                report += "### ⚡ Top 5 requêtes les plus rapides (P50)\n\n"
                top_fastest = query_df.sort_values('P50').head(5)
                for idx, row in top_fastest.iterrows():
                    report += f"{idx+1}. **{row['Requête']}** - P50: {row['P50']:.6f}s (Moyenne: {row['Moyenne']:.6f}s)\n"

                report += "\n---\n\n"

        # Section: Percentiles par moteur (si disponible)
        if 'engine' in results_df.columns:
            report += "## 🔧 Percentiles par moteur SPARQL\n\n"

            engine_stats = []
            for engine_name in results_df['engine'].unique():
                engine_data = results_df[results_df['engine'] == engine_name]['execution_time'].dropna()

                if len(engine_data) > 0:
                    engine_stats.append({
                        'Moteur': engine_name,
                        'P50': np.percentile(engine_data, 50),
                        'P95': np.percentile(engine_data, 95),
                        'P99': np.percentile(engine_data, 99),
                        'Moyenne': engine_data.mean(),
                        'Min': engine_data.min(),
                        'Max': engine_data.max(),
                        'Exécutions': len(engine_data)
                    })

            if engine_stats:
                engine_df = pd.DataFrame(engine_stats)
                report += engine_df.to_markdown(index=False, floatfmt=".6f")
                report += "\n\n"

                # Comparaison des moteurs
                report += "### Comparaison des performances\n\n"
                best_p50 = engine_df.loc[engine_df['P50'].idxmin()]
                best_p95 = engine_df.loc[engine_df['P95'].idxmin()]

                report += f"- **Meilleur P50 (performance typique):** {best_p50['Moteur']} ({best_p50['P50']:.6f}s)\n"
                report += f"- **Meilleur P95 (SLA):** {best_p95['Moteur']} ({best_p95['P95']:.6f}s)\n"

                report += "\n---\n\n"

        # Section: Recommandations
        if include_recommendations:
            report += """
## 💡 Recommandations basées sur les percentiles

### Optimisation des performances

1. **Concentrez-vous sur le P95:** C'est le seuil de qualité de service
   - Identifiez les requêtes avec P95 > 5 secondes
   - Optimisez ces requêtes en priorité

2. **Analysez le P99 pour les outliers:**
   - Si P99 >> P95 → présence de valeurs aberrantes
   - Vérifiez la stabilité du système lors de ces pics

3. **Stabilité (écart-type):**
   - Un écart-type élevé indique des performances variables
   - Vérifiez la charge système et la configuration

### Utilisation pour les SLA

- **SLA "Excellente performance":** P95 < 1 seconde
- **SLA "Bonne performance":** P95 < 5 secondes
- **SLA "Performance acceptable":** P95 < 10 secondes

### Métriques à surveiller

- **P50:** Performance quotidienne typique
- **P95:** Seuil pour définir vos SLA
- **P99:** Détection précoce de problèmes de performance

"""

        # Pied de page
        report += f"""
---

**Rapport avancé généré par la Plateforme d'évaluation SPARQL**
*Développé dans le cadre d'un mémoire de Master 2 en Informatique - Génie Logiciel*

*Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return report

    except Exception as e:
        # Rapport d'erreur en cas d'échec
        return f"""# Erreur lors de la génération du rapport avancé

**Erreur rencontrée:** {str(e)}

**Type d'erreur:** {type(e).__name__}

**Informations disponibles:**
- Nombre d'enregistrements: {len(results_df) if results_df is not None else 0}
- Colonnes: {', '.join(results_df.columns) if results_df is not None and not results_df.empty else 'Aucune'}

---
*Rapport d'erreur généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

def generate_report_safe(results_df: pd.DataFrame, report_type: str, 
                        include_charts: bool, include_recommendations: bool) -> str:
    """
    Génère un rapport de manière sécurisée avec gestion d'erreurs
    
    Args:
        results_df: DataFrame des résultats
        report_type: Type de rapport à générer
        include_charts: Inclure les descriptions de graphiques
        include_recommendations: Inclure les recommandations
        
    Returns:
        Contenu du rapport en Markdown
    """
    try:
        # Si c'est un rapport avancé avec percentiles, utiliser une fonction dédiée
        if report_type == "Rapport avancé avec percentiles (P50/P95/P99)":
            return generate_advanced_percentile_report(results_df, include_recommendations)

        # En-tête du rapport standard
        report = f"""# {report_type} - Performance SPARQL

**Date de génération:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Résumé exécutif

"""

        # Informations de base sur les données
        report += f"""
### Données analysées

- **Nombre d'enregistrements:** {len(results_df)}
- **Colonnes disponibles:** {', '.join(results_df.columns)}
- **Période d'analyse:** {datetime.now().strftime('%Y-%m-%d')}

"""
        
        # Tentative de génération du résumé avec gestion d'erreur
        try:
            summary = create_benchmark_summary(results_df)
            
            # Vérifier si le résumé contient une erreur
            if "error" in summary:
                report += f"""
### ⚠️ Limitation de l'analyse

Les métriques avancées ne peuvent pas être calculées : {summary['error']}

**Analyse basique disponible:**
- Nombre total d'enregistrements: {len(results_df)}
- Colonnes présentes: {', '.join(results_df.columns)}

"""
            else:
                # Résumé complet disponible
                report += f"""
### Aperçu général

- **Nombre total d'exécutions:** {summary['overview']['total_executions']}
- **Requêtes uniques testées:** {summary['overview']['unique_queries']}
- **Moteurs évalués:** {summary['overview']['engines_tested']}
- **Taux de succès global:** {summary['overview']['success_rate']:.2f}%

### Performance globale

- **Temps d'exécution moyen:** {summary['performance']['avg_execution_time']:.4f} secondes
- **Temps minimum observé:** {summary['performance']['min_execution_time']:.4f} secondes
- **Temps maximum observé:** {summary['performance']['max_execution_time']:.4f} secondes
- **Écart-type:** {summary['performance']['std_execution_time']:.4f} secondes

### Utilisation des ressources

- **CPU moyen:** {summary['resources']['avg_cpu_usage']:.2f}%
- **Mémoire moyenne:** {summary['resources']['avg_memory_usage']:.2f} MB
- **CPU maximum:** {summary['resources']['max_cpu_usage']:.2f}%
- **Mémoire maximum:** {summary['resources']['max_memory_usage']:.2f} MB

"""
        except Exception as e:
            # Fallback si le résumé échoue
            report += f"""
### ⚠️ Analyse limitée

Impossible de générer un résumé complet des performances.

**Raison:** {str(e)}

**Données brutes disponibles:**
- {len(results_df)} enregistrements au total
- Colonnes: {', '.join(results_df.columns)}

"""
        
        # Ajouter une analyse basique des données
        try:
            if 'execution_time' in results_df.columns:
                avg_time = results_df['execution_time'].mean()
                min_time = results_df['execution_time'].min()
                max_time = results_df['execution_time'].max()
                
                report += f"""
### Analyse basique des temps d'exécution

- **Temps moyen:** {avg_time:.4f} secondes
- **Temps minimum:** {min_time:.4f} secondes
- **Temps maximum:** {max_time:.4f} secondes
- **Écart:** {max_time - min_time:.4f} secondes

"""
            
            if 'engine' in results_df.columns:
                engine_counts = results_df['engine'].value_counts()
                report += "**Répartition par moteur:**\n"
                for engine, count in engine_counts.items():
                    report += f"- {engine}: {count} exécutions\n"
                
        except Exception as e:
            report += f"Erreur lors de l'analyse basique: {str(e)}\n"
        
        # Ajout des recommandations générales si demandé
        if include_recommendations:
            report += """
## Recommandations générales

1. **Validation des données:** Assurez-vous que tous les tests se sont déroulés correctement
2. **Analyse plus poussée:** Consultez les données brutes pour une analyse détaillée
3. **Tests supplémentaires:** Considérez l'exécution de tests avec plus d'itérations
4. **Documentation:** Conservez ce rapport pour référence future

"""
        
        # Pied de page
        report += f"""
---

**Rapport généré par la Plateforme d'évaluation SPARQL**  
*Développé dans le cadre d'un mémoire de Master 2 en Informatique - Génie Logiciel*

*Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report
        
    except Exception as e:
        # Rapport d'erreur minimal en cas d'échec complet
        return f"""# Erreur lors de la génération du rapport

**Type de rapport demandé:** {report_type}
**Erreur rencontrée:** {str(e)}

**Informations disponibles:**
- Nombre d'enregistrements: {len(results_df) if results_df is not None else 0}
- Colonnes: {', '.join(results_df.columns) if results_df is not None and not results_df.empty else 'Aucune'}

**Suggestion:** Vérifiez que les tests ont été exécutés et que les données sont valides.

---
*Rapport d'erreur généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

def render_visualization_export_section(results_df: pd.DataFrame):
    """
    Affiche la section d'export des visualisations
    
    Args:
        results_df: DataFrame des résultats
    """
    st.subheader("Exportation des visualisations")
    
    st.info("""
    **Note:** Les graphiques interactifs Plotly peuvent être sauvegardés directement depuis l'onglet 'Visualisation' 
    en utilisant les options d'export intégrées (icône de l'appareil photo dans chaque graphique).
    """)
    
    # Guide pour l'export des visualisations
    with st.expander("📖 Guide d'exportation des graphiques"):
        st.markdown("""
        ### Comment exporter les graphiques
        
        1. **Depuis l'onglet Visualisation:**
           - Allez dans l'onglet 'Visualisation'
           - Survolez un graphique avec votre souris
           - Cliquez sur l'icône de l'appareil photo (📷) en haut à droite
           - Choisissez le format (PNG, SVG, PDF)
        
        2. **Formats disponibles:**
           - **PNG:** Image haute qualité pour les présentations
           - **SVG:** Format vectoriel pour l'édition
           - **PDF:** Pour l'inclusion dans des documents
        
        3. **Qualité recommandée:**
           - Résolution: 1200x800 pour les présentations
           - Format SVG pour les publications académiques
        """)
    
    # Génération d'un package complet
    if st.button("Générer un package d'export complet"):
        with st.spinner("Préparation du package d'export..."):
            package_info = create_export_package_info(results_df)
            
            st.success("✅ Package d'export préparé!")
            st.json(package_info)

def create_export_package_info(results_df: pd.DataFrame) -> dict:
    """
    Crée les informations du package d'export
    
    Args:
        results_df: DataFrame des résultats
        
    Returns:
        Dictionnaire d'informations du package
    """
    return {
        "package_info": {
            "creation_date": datetime.now().isoformat(),
            "total_records": len(results_df),
            "data_columns": list(results_df.columns),
            "export_formats": ["CSV", "Excel", "JSON", "Markdown Report"]
        },
        "contents": {
            "raw_data": "Données complètes de performance",
            "summary_tables": "Tableaux récapitulatifs et statistiques",
            "detailed_report": "Rapport d'analyse détaillé",
            "visualization_guide": "Guide pour exporter les graphiques"
        },
        "recommendations": {
            "academic_use": "Utilisez les formats Excel + SVG pour les publications",
            "business_use": "Privilégiez CSV + PNG pour les présentations",
            "technical_use": "JSON + Markdown pour l'intégration technique"
        }
    }