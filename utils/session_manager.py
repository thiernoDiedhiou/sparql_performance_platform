"""
Gestionnaire de sessions pour sauvegarder et charger les configurations
Permet de comparer plusieurs exécutions de tests (sessions A vs B)
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import streamlit as st
import pandas as pd


class SessionManager:
    """
    Gestionnaire de sessions pour sauvegarder et restaurer les configurations et résultats
    """

    def __init__(self, sessions_dir: str = "sessions"):
        """
        Initialise le gestionnaire de sessions

        Args:
            sessions_dir: Répertoire de sauvegarde des sessions
        """
        self.sessions_dir = sessions_dir
        self._ensure_sessions_dir()

    def _ensure_sessions_dir(self):
        """Crée le répertoire des sessions s'il n'existe pas"""
        if not os.path.exists(self.sessions_dir):
            os.makedirs(self.sessions_dir)

    def save_session(
        self,
        session_name: str,
        config: Dict[str, Any],
        results_df: Optional[pd.DataFrame] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Sauvegarde une session complète (config + résultats)

        Args:
            session_name: Nom de la session
            config: Configuration utilisée
            results_df: DataFrame des résultats (optionnel)
            metadata: Métadonnées supplémentaires (optionnel)

        Returns:
            True si sauvegarde réussie
        """
        try:
            timestamp = datetime.now().isoformat()
            # Remplacer tous les caractères invalides pour les noms de fichiers Windows
            session_id = f"{timestamp}_{session_name}".replace(":", "-").replace(" ", "_").replace(".", "-")

            session_data = {
                "session_name": session_name,
                "session_id": session_id,
                "timestamp": timestamp,
                "config": self._serialize_config(config),
                "metadata": metadata or {},
                "has_results": results_df is not None
            }

            # Sauvegarde de la configuration
            config_path = os.path.join(self.sessions_dir, f"{session_id}_config.json")
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

            # Sauvegarde des résultats si présents
            if results_df is not None:
                results_path = os.path.join(self.sessions_dir, f"{session_id}_results.csv")
                results_df.to_csv(results_path, index=False, encoding='utf-8')

                # Sauvegarde aussi en pickle pour préserver les types
                results_pickle_path = os.path.join(self.sessions_dir, f"{session_id}_results.pkl")
                results_df.to_pickle(results_pickle_path)

            return True

        except Exception as e:
            st.error(f"Erreur lors de la sauvegarde de la session: {str(e)}")
            return False

    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Charge une session sauvegardée

        Args:
            session_id: Identifiant de la session

        Returns:
            Dictionnaire avec config et résultats, ou None
        """
        try:
            # Chargement de la configuration
            config_path = os.path.join(self.sessions_dir, f"{session_id}_config.json")

            if not os.path.exists(config_path):
                return None

            with open(config_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            # Chargement des résultats si disponibles
            results_df = None
            if session_data.get("has_results", False):
                results_pickle_path = os.path.join(self.sessions_dir, f"{session_id}_results.pkl")
                results_csv_path = os.path.join(self.sessions_dir, f"{session_id}_results.csv")

                if os.path.exists(results_pickle_path):
                    results_df = pd.read_pickle(results_pickle_path)
                elif os.path.exists(results_csv_path):
                    results_df = pd.read_csv(results_csv_path)

            return {
                "config": session_data["config"],
                "results": results_df,
                "metadata": session_data.get("metadata", {}),
                "timestamp": session_data["timestamp"],
                "session_name": session_data["session_name"],
                "session_id": session_data["session_id"]
            }

        except Exception as e:
            st.error(f"Erreur lors du chargement de la session: {str(e)}")
            return None

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        Liste toutes les sessions sauvegardées

        Returns:
            Liste des sessions avec métadonnées
        """
        sessions = []

        try:
            # Recherche de tous les fichiers de configuration
            for filename in os.listdir(self.sessions_dir):
                if filename.endswith("_config.json"):
                    config_path = os.path.join(self.sessions_dir, filename)

                    with open(config_path, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)

                    sessions.append({
                        "session_id": session_data["session_id"],
                        "session_name": session_data["session_name"],
                        "timestamp": session_data["timestamp"],
                        "has_results": session_data.get("has_results", False),
                        "metadata": session_data.get("metadata", {})
                    })

            # Tri par timestamp décroissant (plus récents en premier)
            sessions.sort(key=lambda x: x["timestamp"], reverse=True)

        except Exception as e:
            st.error(f"Erreur lors du listage des sessions: {str(e)}")

        return sessions

    def delete_session(self, session_id: str) -> bool:
        """
        Supprime une session sauvegardée

        Args:
            session_id: Identifiant de la session

        Returns:
            True si suppression réussie
        """
        try:
            # Suppression des fichiers associés
            files_to_delete = [
                f"{session_id}_config.json",
                f"{session_id}_results.csv",
                f"{session_id}_results.pkl"
            ]

            for filename in files_to_delete:
                filepath = os.path.join(self.sessions_dir, filename)
                if os.path.exists(filepath):
                    os.remove(filepath)

            return True

        except Exception as e:
            st.error(f"Erreur lors de la suppression de la session: {str(e)}")
            return False

    def export_session(self, session_id: str, export_path: str) -> bool:
        """
        Exporte une session vers un fichier JSON complet

        Args:
            session_id: Identifiant de la session
            export_path: Chemin du fichier d'export

        Returns:
            True si export réussi
        """
        try:
            session = self.load_session(session_id)

            if session is None:
                return False

            # Conversion du DataFrame en dict pour la sérialisation JSON
            export_data = {
                "session_name": session["session_name"],
                "session_id": session["session_id"],
                "timestamp": session["timestamp"],
                "config": session["config"],
                "metadata": session["metadata"],
                "results": session["results"].to_dict(orient="records") if session["results"] is not None else None
            }

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            st.error(f"Erreur lors de l'export de la session: {str(e)}")
            return False

    def import_session(self, import_path: str) -> Optional[str]:
        """
        Importe une session depuis un fichier JSON

        Args:
            import_path: Chemin du fichier à importer

        Returns:
            session_id de la session importée, ou None
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)

            # Conversion des résultats en DataFrame
            results_df = None
            if import_data.get("results"):
                results_df = pd.DataFrame(import_data["results"])

            # Sauvegarde comme nouvelle session
            session_name = f"{import_data['session_name']}_imported"

            success = self.save_session(
                session_name=session_name,
                config=import_data["config"],
                results_df=results_df,
                metadata=import_data.get("metadata", {})
            )

            if success:
                # Récupération du dernier session_id créé
                sessions = self.list_sessions()
                if sessions:
                    return sessions[0]["session_id"]

            return None

        except Exception as e:
            st.error(f"Erreur lors de l'import de la session: {str(e)}")
            return None

    def compare_sessions(self, session_id_a: str, session_id_b: str) -> Optional[Dict[str, Any]]:
        """
        Compare deux sessions et retourne les différences

        Args:
            session_id_a: Première session
            session_id_b: Deuxième session

        Returns:
            Dictionnaire avec les comparaisons
        """
        try:
            session_a = self.load_session(session_id_a)
            session_b = self.load_session(session_id_b)

            if not session_a or not session_b:
                return None

            comparison = {
                "session_a": {
                    "name": session_a["session_name"],
                    "timestamp": session_a["timestamp"]
                },
                "session_b": {
                    "name": session_b["session_name"],
                    "timestamp": session_b["timestamp"]
                },
                "config_diff": self._compare_configs(
                    session_a["config"],
                    session_b["config"]
                )
            }

            # Comparaison des résultats si disponibles
            if session_a["results"] is not None and session_b["results"] is not None:
                comparison["results_comparison"] = self._compare_results(
                    session_a["results"],
                    session_b["results"]
                )

            return comparison

        except Exception as e:
            st.error(f"Erreur lors de la comparaison des sessions: {str(e)}")
            return None

    def _serialize_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sérialise une configuration pour sauvegarde JSON

        Args:
            config: Configuration à sérialiser

        Returns:
            Configuration sérialisée
        """
        serialized = {}

        for key, value in config.items():
            # Conversion des types non-sérialisables
            if isinstance(value, (str, int, float, bool, type(None))):
                serialized[key] = value
            elif isinstance(value, dict):
                serialized[key] = self._serialize_config(value)
            elif isinstance(value, list):
                serialized[key] = [
                    self._serialize_config(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                # Conversion en string pour les types complexes
                serialized[key] = str(value)

        return serialized

    def _compare_configs(self, config_a: Dict[str, Any], config_b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare deux configurations

        Returns:
            Différences détectées
        """
        differences = {}

        all_keys = set(config_a.keys()) | set(config_b.keys())

        for key in all_keys:
            val_a = config_a.get(key)
            val_b = config_b.get(key)

            if val_a != val_b:
                differences[key] = {
                    "session_a": val_a,
                    "session_b": val_b
                }

        return differences

    def _compare_results(self, results_a: pd.DataFrame, results_b: pd.DataFrame) -> Dict[str, Any]:
        """
        Compare deux DataFrames de résultats

        Returns:
            Statistiques comparatives
        """
        comparison = {}

        # Comparaison des temps moyens
        if 'execution_time' in results_a.columns and 'execution_time' in results_b.columns:
            comparison["avg_execution_time"] = {
                "session_a": results_a['execution_time'].mean(),
                "session_b": results_b['execution_time'].mean(),
                "difference": results_b['execution_time'].mean() - results_a['execution_time'].mean()
            }

        # Comparaison des taux de succès
        if 'success' in results_a.columns and 'success' in results_b.columns:
            comparison["success_rate"] = {
                "session_a": results_a['success'].mean() * 100,
                "session_b": results_b['success'].mean() * 100,
                "difference": (results_b['success'].mean() - results_a['success'].mean()) * 100
            }

        # Comparaison du nombre d'exécutions
        comparison["num_executions"] = {
            "session_a": len(results_a),
            "session_b": len(results_b),
            "difference": len(results_b) - len(results_a)
        }

        return comparison


# ============================================================================
# COMPOSANT UI POUR STREAMLIT
# ============================================================================

def render_session_manager_ui():
    """
    Interface utilisateur Streamlit pour le gestionnaire de sessions
    """
    st.subheader("💾 Gestionnaire de sessions")

    manager = SessionManager()

    # Onglets pour les différentes actions
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Sessions sauvegardées",
        "💾 Sauvegarder",
        "⚖️ Comparer",
        "📤 Import/Export"
    ])

    # ========================================================================
    # TAB 1: LISTE DES SESSIONS
    # ========================================================================
    with tab1:
        st.markdown("#### 📋 Sessions sauvegardées")

        sessions = manager.list_sessions()

        if not sessions:
            st.info("Aucune session sauvegardée pour le moment.")
        else:
            for session in sessions:
                with st.expander(
                    f"📦 {session['session_name']} - {session['timestamp'][:19]}",
                    expanded=False
                ):
                    col1, col2, col3 = st.columns([3, 1.5, 1.5])

                    with col1:
                        st.write(f"**ID:** `{session['session_id'][:30]}...`")
                        st.write(f"**Résultats:** {'✅ Oui' if session['has_results'] else '❌ Non'}")

                    with col2:
                        if st.button("📥 Charger", key=f"load_{session['session_id']}", use_container_width=True):
                            loaded = manager.load_session(session['session_id'])

                            if loaded:
                                # Restauration dans session_state
                                # Filtrer les clés qui correspondent à des widgets avant de les restaurer
                                widget_key_patterns = ['clear_', 'load_', 'delete_', 'save_', 'export_', 'import_']
                                skipped_keys = []

                                for key, value in loaded['config'].items():
                                    # Ignorer les clés de widgets
                                    if any(key.startswith(pattern) for pattern in widget_key_patterns):
                                        skipped_keys.append(key)
                                        continue

                                    # Tenter de restaurer les autres clés avec try-except pour plus de sécurité
                                    try:
                                        st.session_state[key] = value
                                    except Exception as e:
                                        # Ignorer les clés qui causent des conflits avec des widgets
                                        if "cannot be modified after the widget" in str(e) or "cannot be set using" in str(e):
                                            skipped_keys.append(key)
                                        else:
                                            # Re-lever les autres erreurs
                                            raise

                                # Restaurer les résultats dans la clé attendue par l'application
                                if loaded['results'] is not None:
                                    st.session_state['results_df'] = loaded['results']
                                    st.session_state['loaded_session_results'] = loaded['results']

                                st.success(f"✅ Session chargée! ({len(skipped_keys)} clés de widgets ignorées)")
                                st.rerun()

                    with col3:
                        if st.button("🗑️ Supprimer", key=f"delete_{session['session_id']}", use_container_width=True):
                            if manager.delete_session(session['session_id']):
                                st.success("✅ Session supprimée!")
                                st.rerun()

    # ========================================================================
    # TAB 2: SAUVEGARDER UNE NOUVELLE SESSION
    # ========================================================================
    with tab2:
        st.markdown("#### 💾 Sauvegarder la configuration actuelle")

        session_name = st.text_input(
            "Nom de la session",
            value=f"Test_{datetime.now().strftime('%Y%m%d_%H%M')}",
            help="Donnez un nom descriptif à votre session"
        )

        session_description = st.text_area(
            "Description (optionnel)",
            help="Décrivez le contexte de ce test"
        )

        include_results = st.checkbox(
            "Inclure les résultats des tests",
            value=True,
            help="Sauvegarder aussi les résultats si disponibles"
        )

        if st.button("💾 Sauvegarder la session", type="primary"):
            # Collecte de la configuration actuelle
            config = {k: v for k, v in st.session_state.items() if not k.startswith('_')}

            # Résultats si demandés
            results_df = None
            if include_results:
                from utils.data_manager import get_test_results
                results_df = get_test_results()

            # Métadonnées
            metadata = {
                "description": session_description,
                "saved_by": "user",
                "app_version": "2.0"
            }

            success = manager.save_session(
                session_name=session_name,
                config=config,
                results_df=results_df,
                metadata=metadata
            )

            if success:
                st.success("✅ Session sauvegardée avec succès!")
                st.balloons()
            else:
                st.error("❌ Échec de la sauvegarde")

    # ========================================================================
    # TAB 3: COMPARAISON DE SESSIONS
    # ========================================================================
    with tab3:
        st.markdown("#### ⚖️ Comparer deux sessions")

        sessions = manager.list_sessions()

        if len(sessions) < 2:
            st.warning("⚠️ Vous devez avoir au moins 2 sessions sauvegardées pour les comparer.")
        else:
            col1, col2 = st.columns(2)

            with col1:
                session_a = st.selectbox(
                    "Session A",
                    options=[s['session_id'] for s in sessions],
                    format_func=lambda x: next(s['session_name'] for s in sessions if s['session_id'] == x)
                )

            with col2:
                session_b = st.selectbox(
                    "Session B",
                    options=[s['session_id'] for s in sessions],
                    format_func=lambda x: next(s['session_name'] for s in sessions if s['session_id'] == x),
                    index=1 if len(sessions) > 1 else 0
                )

            if st.button("⚖️ Comparer", type="primary"):
                comparison = manager.compare_sessions(session_a, session_b)

                if comparison:
                    st.success("✅ Comparaison effectuée!")

                    # Affichage des différences de configuration
                    if comparison['config_diff']:
                        st.markdown("#### 🔧 Différences de configuration")

                        diff_df = pd.DataFrame([
                            {
                                "Paramètre": key,
                                "Session A": diff["session_a"],
                                "Session B": diff["session_b"]
                            }
                            for key, diff in comparison['config_diff'].items()
                        ])

                        st.dataframe(diff_df, use_container_width=True)

                    # Affichage de la comparaison des résultats
                    if 'results_comparison' in comparison:
                        st.markdown("#### 📊 Comparaison des résultats")

                        results_comp = comparison['results_comparison']

                        col1, col2 = st.columns(2)

                        with col1:
                            st.metric(
                                "Temps moyen Session A",
                                f"{results_comp['avg_execution_time']['session_a']:.3f}s"
                            )

                        with col2:
                            st.metric(
                                "Temps moyen Session B",
                                f"{results_comp['avg_execution_time']['session_b']:.3f}s",
                                delta=f"{results_comp['avg_execution_time']['difference']:.3f}s"
                            )

    # ========================================================================
    # TAB 4: IMPORT/EXPORT
    # ========================================================================
    with tab4:
        st.markdown("#### 📤 Import / Export")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 📤 Exporter une session")

            sessions = manager.list_sessions()

            if sessions:
                session_to_export = st.selectbox(
                    "Choisir une session",
                    options=[s['session_id'] for s in sessions],
                    format_func=lambda x: next(s['session_name'] for s in sessions if s['session_id'] == x)
                )

                export_filename = st.text_input(
                    "Nom du fichier d'export",
                    value=f"session_export_{datetime.now().strftime('%Y%m%d')}.json"
                )

                if st.button("📤 Exporter"):
                    export_path = os.path.join("exports", export_filename)
                    os.makedirs("exports", exist_ok=True)

                    if manager.export_session(session_to_export, export_path):
                        st.success(f"✅ Session exportée vers: {export_path}")

                        # Bouton de téléchargement
                        with open(export_path, 'r') as f:
                            st.download_button(
                                label="📥 Télécharger le fichier",
                                data=f.read(),
                                file_name=export_filename,
                                mime="application/json"
                            )

        with col2:
            st.markdown("##### 📥 Importer une session")

            uploaded_file = st.file_uploader(
                "Choisir un fichier JSON",
                type=["json"],
                help="Fichier de session exporté précédemment"
            )

            if uploaded_file:
                if st.button("📥 Importer"):
                    # Sauvegarde temporaire du fichier
                    temp_path = os.path.join("temp", uploaded_file.name)
                    os.makedirs("temp", exist_ok=True)

                    with open(temp_path, 'wb') as f:
                        f.write(uploaded_file.getvalue())

                    session_id = manager.import_session(temp_path)

                    if session_id:
                        st.success(f"✅ Session importée avec succès!")
                        st.info(f"ID: {session_id}")
                        st.rerun()
                    else:
                        st.error("❌ Échec de l'import")

                    # Nettoyage
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
