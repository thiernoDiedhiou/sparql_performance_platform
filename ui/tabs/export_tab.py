"""
Onglet d'exportation des résultats
"""

import streamlit as st
import pandas as pd
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
    st.subheader("📊 Exportation des données brutes")
    
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
            "Analyse de performance"
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
        # En-tête du rapport
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
    st.subheader("📊 Exportation des visualisations")
    
    st.info("""
    💡 **Note:** Les graphiques interactifs Plotly peuvent être sauvegardés directement depuis l'onglet 'Visualisation' 
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
    if st.button("📦 Générer un package d'export complet"):
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