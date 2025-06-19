"""
Gestionnaire de données et état de session pour l'application
"""

import streamlit as st
import pandas as pd
from typing import Any, Dict, Optional
from datetime import datetime
import json
from utils.helpers import log_message

class DataManager:
    """Classe pour gérer les données et l'état de session"""
    
    def __init__(self):
        """Initialise le gestionnaire de données"""
        self.session_key_results = 'results_df'
        self.session_key_config = 'test_config'
        self.session_key_completed = 'test_completed'
        self.session_key_history = 'test_history'
    
    def initialize_session_state(self):
        """Initialise l'état de session avec les valeurs par défaut"""
        if self.session_key_results not in st.session_state:
            st.session_state[self.session_key_results] = pd.DataFrame()
        
        if self.session_key_config not in st.session_state:
            st.session_state[self.session_key_config] = {}
        
        if self.session_key_completed not in st.session_state:
            st.session_state[self.session_key_completed] = False
        
        if self.session_key_history not in st.session_state:
            st.session_state[self.session_key_history] = []
        
        log_message("État de session initialisé")
    
    def save_results(self, results_df: pd.DataFrame, config: Dict[str, Any]):
        """
        Sauvegarde les résultats dans l'état de session
        
        Args:
            results_df: DataFrame des résultats
            config: Configuration utilisée pour les tests
        """
        try:
            st.session_state[self.session_key_results] = results_df
            st.session_state[self.session_key_config] = config
            st.session_state[self.session_key_completed] = True
            
            # Ajouter à l'historique
            test_entry = {
                "timestamp": datetime.now().isoformat(),
                "config": config,
                "results_count": len(results_df),
                "success_rate": results_df['success'].mean() if 'success' in results_df.columns else 0
            }
            
            history = st.session_state[self.session_key_history]
            history.append(test_entry)
            
            # Limiter l'historique aux 50 derniers tests
            if len(history) > 50:
                history = history[-50:]
            
            st.session_state[self.session_key_history] = history
            
            log_message(f"Résultats sauvegardés: {len(results_df)} enregistrements")
            
        except Exception as e:
            log_message(f"Erreur lors de la sauvegarde: {str(e)}", "error")
    
    def get_results(self) -> Optional[pd.DataFrame]:
        """
        Récupère les résultats de l'état de session
        
        Returns:
            DataFrame des résultats ou None si aucun résultat
        """
        if self.session_key_results in st.session_state:
            results = st.session_state[self.session_key_results]
            if not results.empty:
                return results
        return None
    
    def get_config(self) -> Dict[str, Any]:
        """
        Récupère la configuration de l'état de session
        
        Returns:
            Dictionnaire de configuration
        """
        return st.session_state.get(self.session_key_config, {})
    
    def is_test_completed(self) -> bool:
        """
        Vérifie si un test a été complété
        
        Returns:
            True si un test a été complété
        """
        return st.session_state.get(self.session_key_completed, False)
    
    def get_test_history(self) -> list:
        """
        Récupère l'historique des tests
        
        Returns:
            Liste de l'historique des tests
        """
        return st.session_state.get(self.session_key_history, [])
    
    def clear_results(self):
        """Efface les résultats de l'état de session"""
        st.session_state[self.session_key_results] = pd.DataFrame()
        st.session_state[self.session_key_completed] = False
        log_message("Résultats effacés")
    
    def clear_history(self):
        """Efface l'historique des tests"""
        st.session_state[self.session_key_history] = []
        log_message("Historique effacé")
    
    def export_session_data(self) -> Dict[str, Any]:
        """
        Exporte toutes les données de session
        
        Returns:
            Dictionnaire contenant toutes les données de session
        """
        try:
            results_df = self.get_results()
            
            export_data = {
                "export_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0"
                },
                "current_config": self.get_config(),
                "test_completed": self.is_test_completed(),
                "test_history": self.get_test_history(),
                "current_results": results_df.to_dict('records') if results_df is not None else []
            }
            
            return export_data
            
        except Exception as e:
            log_message(f"Erreur lors de l'export des données de session: {str(e)}", "error")
            return {"error": "Erreur lors de l'export"}
    
    def import_session_data(self, data: Dict[str, Any]) -> bool:
        """
        Importe des données de session
        
        Args:
            data: Dictionnaire contenant les données à importer
            
        Returns:
            True si l'import a réussi
        """
        try:
            if "current_config" in data:
                st.session_state[self.session_key_config] = data["current_config"]
            
            if "test_completed" in data:
                st.session_state[self.session_key_completed] = data["test_completed"]
            
            if "test_history" in data:
                st.session_state[self.session_key_history] = data["test_history"]
            
            if "current_results" in data and data["current_results"]:
                results_df = pd.DataFrame(data["current_results"])
                st.session_state[self.session_key_results] = results_df
            
            log_message("Données de session importées avec succès")
            return True
            
        except Exception as e:
            log_message(f"Erreur lors de l'import des données de session: {str(e)}", "error")
            return False
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """
        Récupère les statistiques de la session actuelle
        
        Returns:
            Dictionnaire contenant les statistiques
        """
        try:
            results_df = self.get_results()
            history = self.get_test_history()
            
            stats = {
                "session_info": {
                    "has_current_results": results_df is not None and not results_df.empty,
                    "current_results_count": len(results_df) if results_df is not None else 0,
                    "test_completed": self.is_test_completed(),
                    "history_count": len(history)
                },
                "performance_summary": {}
            }
            
            if results_df is not None and not results_df.empty:
                stats["performance_summary"] = {
                    "avg_execution_time": results_df['execution_time'].mean() if 'execution_time' in results_df.columns else 0,
                    "success_rate": results_df['success'].mean() * 100 if 'success' in results_df.columns else 0,
                    "unique_queries": results_df['query_name'].nunique() if 'query_name' in results_df.columns else 0,
                    "engines_tested": results_df['engine'].nunique() if 'engine' in results_df.columns else 0
                }
            
            if history:
                recent_tests = history[-10:]  # 10 derniers tests
                stats["recent_activity"] = {
                    "last_test_timestamp": recent_tests[-1]["timestamp"],
                    "avg_success_rate": sum(test["success_rate"] for test in recent_tests) / len(recent_tests) * 100,
                    "total_executions": sum(test["results_count"] for test in recent_tests)
                }
            
            return stats
            
        except Exception as e:
            log_message(f"Erreur lors du calcul des statistiques: {str(e)}", "error")
            return {"error": "Impossible de calculer les statistiques"}

# Instance globale du gestionnaire de données
data_manager = DataManager()

def initialize_session_state():
    """Fonction utilitaire pour initialiser l'état de session"""
    data_manager.initialize_session_state()

def save_test_results(results_df: pd.DataFrame, config: Dict[str, Any]):
    """
    Fonction utilitaire pour sauvegarder les résultats de test
    
    Args:
        results_df: DataFrame des résultats
        config: Configuration utilisée
    """
    data_manager.save_results(results_df, config)

def get_test_results() -> Optional[pd.DataFrame]:
    """
    Fonction utilitaire pour récupérer les résultats de test
    
    Returns:
        DataFrame des résultats ou None
    """
    return data_manager.get_results()

def is_test_completed() -> bool:
    """
    Fonction utilitaire pour vérifier si un test est complété
    
    Returns:
        True si un test a été complété
    """
    return data_manager.is_test_completed()

def clear_test_results():
    """Fonction utilitaire pour effacer les résultats de test"""
    data_manager.clear_results()

def get_session_stats() -> Dict[str, Any]:
    """
    Fonction utilitaire pour récupérer les statistiques de session
    
    Returns:
        Dictionnaire des statistiques
    """
    return data_manager.get_session_statistics()