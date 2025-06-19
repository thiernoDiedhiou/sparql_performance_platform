"""
Gestionnaire d'exportation des résultats et rapports
"""

import pandas as pd
import json
import io
from datetime import datetime
from typing import Dict, Any, Optional
from utils.helpers import create_benchmark_summary, format_test_results_summary, log_message

class ExportManager:
    """Classe pour gérer toutes les exportations de données et rapports"""
    
    def __init__(self):
        """Initialise le gestionnaire d'exportation"""
        self.export_formats = {
            "csv": self._export_csv,
            "excel": self._export_excel,
            "json": self._export_json,
            "markdown": self._export_markdown
        }
    
    def export_data(self, results_df: pd.DataFrame, format_type: str, 
                   include_metadata: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Exporte les données dans le format spécifié
        
        Args:
            results_df: DataFrame des résultats
            format_type: Format d'export (csv, excel, json, markdown)
            include_metadata: Inclure les métadonnées
            **kwargs: Arguments supplémentaires pour l'export
            
        Returns:
            Dictionnaire contenant les données exportées et les métadonnées
        """
        if results_df is None or results_df.empty:
            return {
                "success": False,
                "error": "Aucune donnée à exporter",
                "data": None
            }
        
        if format_type not in self.export_formats:
            return {
                "success": False,
                "error": f"Format '{format_type}' non supporté. Formats disponibles: {list(self.export_formats.keys())}",
                "data": None
            }
        
        try:
            export_function = self.export_formats[format_type]
            result = export_function(results_df, include_metadata, **kwargs)
            
            return {
                "success": True,
                "error": None,
                "data": result["data"],
                "filename": result["filename"],
                "mime_type": result["mime_type"],
                "metadata": result.get("metadata", {})
            }
            
        except Exception as e:
            log_message(f"Erreur lors de l'export {format_type}: {str(e)}", "error")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    def _export_csv(self, results_df: pd.DataFrame, include_metadata: bool, **kwargs) -> Dict[str, Any]:
        """Exporte vers CSV"""
        
        csv_data = results_df.to_csv(index=False)
        
        if include_metadata:
            metadata_header = f"""# Résultats de performance SPARQL
# Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Nombre d'enregistrements: {len(results_df)}
# Colonnes: {', '.join(results_df.columns)}

"""
            csv_data = metadata_header + csv_data
        
        return {
            "data": csv_data,
            "filename": f"sparql_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "mime_type": "text/csv",
            "metadata": {
                "records_count": len(results_df),
                "columns": list(results_df.columns),
                "export_timestamp": datetime.now().isoformat()
            }
        }
    
    def _export_excel(self, results_df: pd.DataFrame, include_metadata: bool, **kwargs) -> Dict[str, Any]:
        """Exporte vers Excel"""
        
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Feuille principale
            results_df.to_excel(writer, sheet_name='Résultats', index=False)
            
            # Feuille statistiques si possible
            if self._has_required_columns(results_df, ['execution_time', 'engine']):
                try:
                    stats_df = results_df.groupby(['query_name', 'engine']).agg({
                        'execution_time': ['mean', 'min', 'max', 'std', 'count'],
                        'success': 'mean' if 'success' in results_df.columns else 'count'
                    }).round(4)
                    stats_df.to_excel(writer, sheet_name='Statistiques')
                except Exception as e:
                    log_message(f"Impossible de créer la feuille statistiques: {str(e)}", "warning")
            
            # Feuille métadonnées
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
        
        return {
            "data": buffer.getvalue(),
            "filename": f"sparql_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "metadata": {
                "sheets": ["Résultats", "Statistiques", "Métadonnées"],
                "records_count": len(results_df),
                "export_timestamp": datetime.now().isoformat()
            }
        }
    
    def _export_json(self, results_df: pd.DataFrame, include_metadata: bool, **kwargs) -> Dict[str, Any]:
        """Exporte vers JSON"""
        
        # Conversion des types pandas vers des types JSON compatibles
        export_df = results_df.copy()
        
        # Conversion des colonnes datetime
        for col in export_df.columns:
            if export_df[col].dtype == 'datetime64[ns]':
                export_df[col] = export_df[col].dt.isoformat()
        
        export_data = {
            "results": export_df.to_dict('records')
        }
        
        if include_metadata:
            export_data["metadata"] = {
                "export_timestamp": datetime.now().isoformat(),
                "total_records": len(export_df),
                "columns": list(export_df.columns),
                "data_types": {col: str(dtype) for col, dtype in export_df.dtypes.items()}
            }
            
            # Ajouter un résumé si possible
            try:
                summary = create_benchmark_summary(results_df)
                if "error" not in summary:
                    export_data["summary"] = summary
            except Exception as e:
                log_message(f"Impossible de créer le résumé pour JSON: {str(e)}", "warning")
        
        json_string = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        return {
            "data": json_string,
            "filename": f"sparql_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "mime_type": "application/json",
            "metadata": export_data.get("metadata", {})
        }
    
    def _export_markdown(self, results_df: pd.DataFrame, include_metadata: bool, **kwargs) -> Dict[str, Any]:
        """Exporte vers Markdown"""
        
        report_type = kwargs.get("report_type", "Rapport complet")
        include_charts = kwargs.get("include_charts", True)
        include_recommendations = kwargs.get("include_recommendations", True)
        
        # Génération du rapport Markdown
        markdown_content = f"""# {report_type} - Performance SPARQL

**Date de génération:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Résumé des données

- **Nombre d'enregistrements:** {len(results_df)}
- **Colonnes disponibles:** {', '.join(results_df.columns)}

"""
        
        # Ajouter le résumé statistique si possible
        try:
            summary = create_benchmark_summary(results_df)
            if "error" not in summary:
                markdown_content += f"""
## Résumé des performances

### Aperçu général
- **Exécutions totales:** {summary['overview']['total_executions']}
- **Requêtes uniques:** {summary['overview']['unique_queries']}
- **Moteurs testés:** {summary['overview']['engines_tested']}
- **Taux de succès:** {summary['overview']['success_rate']:.2f}%

### Performance
- **Temps moyen:** {summary['performance']['avg_execution_time']:.4f}s
- **Temps minimum:** {summary['performance']['min_execution_time']:.4f}s
- **Temps maximum:** {summary['performance']['max_execution_time']:.4f}s

"""
        except Exception as e:
            markdown_content += f"""
## Résumé des performances

*Impossible de générer le résumé automatique: {str(e)}*

"""
        
        # Ajouter les données sous forme de tableau
        if len(results_df) <= 100:  # Limiter la taille pour éviter des fichiers trop volumineux
            markdown_content += """
## Données détaillées

"""
            markdown_content += results_df.to_markdown(index=False)
        else:
            markdown_content += f"""
## Aperçu des données (100 premiers enregistrements)

"""
            markdown_content += results_df.head(100).to_markdown(index=False)
            markdown_content += f"\n\n*Note: Seuls les 100 premiers enregistrements sont affichés. Total: {len(results_df)} enregistrements.*\n"
        
        if include_recommendations:
            markdown_content += """

## Recommandations

1. **Analyses supplémentaires:** Examinez les requêtes les plus lentes pour optimiser les performances
2. **Tests de charge:** Considérez des tests avec plus de concurrence pour valider la scalabilité
3. **Environnement:** Vérifiez que les conditions de test sont représentatives de la production

"""
        
        markdown_content += """
---

*Rapport généré par la Plateforme d'évaluation SPARQL*
"""
        
        return {
            "data": markdown_content,
            "filename": f"rapport_sparql_{report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            "mime_type": "text/markdown",
            "metadata": {
                "report_type": report_type,
                "records_count": len(results_df),
                "export_timestamp": datetime.now().isoformat()
            }
        }
    
    def _has_required_columns(self, df: pd.DataFrame, required_columns: list) -> bool:
        """Vérifie si le DataFrame contient les colonnes requises"""
        return all(col in df.columns for col in required_columns)
    
    def create_export_package(self, results_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Crée un package complet d'export avec plusieurs formats
        
        Args:
            results_df: DataFrame des résultats
            
        Returns:
            Dictionnaire contenant tous les exports
        """
        package = {
            "created_at": datetime.now().isoformat(),
            "total_records": len(results_df),
            "exports": {},
            "errors": []
        }
        
        # Export dans tous les formats
        for format_name in self.export_formats.keys():
            try:
                export_result = self.export_data(results_df, format_name, include_metadata=True)
                if export_result["success"]:
                    package["exports"][format_name] = {
                        "filename": export_result["filename"],
                        "mime_type": export_result["mime_type"],
                        "size_bytes": len(export_result["data"]) if isinstance(export_result["data"], (str, bytes)) else 0
                    }
                else:
                    package["errors"].append(f"Erreur export {format_name}: {export_result['error']}")
            except Exception as e:
                package["errors"].append(f"Erreur critique export {format_name}: {str(e)}")
        
        return package
    
    def get_supported_formats(self) -> Dict[str, str]:
        """
        Retourne les formats d'export supportés
        
        Returns:
            Dictionnaire des formats avec descriptions
        """
        return {
            "csv": "Comma Separated Values - Compatible avec Excel et autres outils",
            "excel": "Microsoft Excel - Feuilles multiples avec statistiques",
            "json": "JavaScript Object Notation - Format structuré avec métadonnées",
            "markdown": "Markdown - Rapport lisible pour documentation"
        }

# Instance globale du gestionnaire d'export
export_manager = ExportManager()

def export_results(results_df: pd.DataFrame, format_type: str, **kwargs) -> Dict[str, Any]:
    """
    Fonction utilitaire pour exporter des résultats
    
    Args:
        results_df: DataFrame des résultats
        format_type: Format d'export
        **kwargs: Arguments supplémentaires
        
    Returns:
        Résultat de l'export
    """
    return export_manager.export_data(results_df, format_type, **kwargs)

def create_export_package(results_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Fonction utilitaire pour créer un package complet d'export
    
    Args:
        results_df: DataFrame des résultats
        
    Returns:
        Package d'export complet
    """
    return export_manager.create_export_package(results_df)

def get_export_formats() -> Dict[str, str]:
    """
    Fonction utilitaire pour récupérer les formats supportés
    
    Returns:
        Dictionnaire des formats supportés
    """
    return export_manager.get_supported_formats()