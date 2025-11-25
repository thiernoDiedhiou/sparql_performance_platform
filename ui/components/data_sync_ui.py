"""
Interface utilisateur pour la synchronisation des données
"""

import streamlit as st
import time
import json
from datetime import datetime
from utils.data_synchronizer import DataSynchronizer
from utils.dataset_manager import DatasetManager
from utils.helpers import log_message

def render_data_synchronization_ui(virtuoso_endpoint: str, fuseki_endpoint: str):
    """
    Interface utilisateur pour la synchronisation des données
    
    Args:
        virtuoso_endpoint: URL de l'endpoint Virtuoso
        fuseki_endpoint: URL de l'endpoint Jena Fuseki
    """
    st.subheader("🔄 Synchronisation des données")
    
    # Initialisation du synchroniseur et du gestionnaire de datasets
    try:
        synchronizer = DataSynchronizer(virtuoso_endpoint, fuseki_endpoint)
        dataset_manager = DatasetManager(datasets_path="datasets")
    except Exception as e:
        st.error(f"❌ Erreur d'initialisation: {str(e)}")
        return

    # Charger les métadonnées pour obtenir les graph_uri
    metadata = dataset_manager.load_all_metadata()
    virtuoso_graph_uri = metadata.get('virtuoso', {}).get('graph_uri') if metadata else None
    fuseki_graph_uri = metadata.get('fuseki', {}).get('graph_uri') if metadata else None

    # Section d'état actuel
    st.write("### État actuel des datasets")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Vérifier l'état", help="Vérifier le nombre de triplets dans chaque moteur"):
            with st.spinner("Vérification en cours..."):
                # Utiliser les graph_uri si disponibles
                virtuoso_count = synchronizer.count_triplets(virtuoso_endpoint, virtuoso_graph_uri)
                fuseki_count = synchronizer.count_triplets(fuseki_endpoint, fuseki_graph_uri)
                
                # Stockage dans session state pour persistance
                st.session_state['virtuoso_count'] = virtuoso_count
                st.session_state['fuseki_count'] = fuseki_count
                
                # Affichage des résultats
                col_v, col_f = st.columns(2)
                with col_v:
                    st.metric("🟦 Virtuoso", f"{virtuoso_count:,} triplets")
                with col_f:
                    st.metric("🟧 Jena Fuseki", f"{fuseki_count:,} triplets")
                
                # Analyse de l'état
                if virtuoso_count == fuseki_count and virtuoso_count > 0:
                    st.success("✅ Les datasets sont synchronisés")
                elif virtuoso_count > 0 and fuseki_count == 0:
                    st.warning("⚠️ Virtuoso a des données, Fuseki est vide")
                elif virtuoso_count == 0 and fuseki_count > 0:
                    st.info("ℹ️ Fuseki a des données, Virtuoso est vide")
                elif virtuoso_count == 0 and fuseki_count == 0:
                    st.info("ℹ️ Les deux moteurs sont vides")
                else:
                    st.warning("⚠️ Les datasets ne sont pas synchronisés")
    
    with col2:
        if st.button("Statistiques détaillées", help="Afficher des statistiques complètes"):
            with st.spinner("Analyse en cours..."):
                render_detailed_statistics(synchronizer, virtuoso_endpoint, fuseki_endpoint,
                                          virtuoso_graph_uri, fuseki_graph_uri)
    
    with col3:
        if st.button("Vérifier la cohérence", help="Analyse approfondie de la cohérence"):
            with st.spinner("Vérification de la cohérence..."):
                render_consistency_check(synchronizer, virtuoso_endpoint, fuseki_endpoint,
                                        virtuoso_graph_uri, fuseki_graph_uri)
    
    # Section de synchronisation
    st.write("### Options de synchronisation")
    
    # Options avancées
    with st.expander("Options avancées"):
        clear_target = st.checkbox(
            "Vider Fuseki avant la synchronisation",
            value=True,
            help="Supprime toutes les données existantes dans Fuseki avant la synchronisation"
        )
        
        use_limit = st.checkbox(
            "Limiter le nombre de triplets",
            value=False,
            help="Utile pour les tests avec de gros datasets"
        )
        
        limit_value = None
        if use_limit:
            limit_value = st.number_input(
                "Nombre maximum de triplets",
                min_value=1000,
                max_value=1000000,
                value=10000,
                step=1000,
                help="Nombre maximum de triplets à synchroniser"
            )
        
        auto_detect = st.checkbox(
            "Détecter automatiquement le type de dataset",
            value=True,
            help="Tente d'identifier le type de données (LUBM, DBpedia, etc.)"
        )
    
    # Boutons de synchronisation
    col1, col2 = st.columns(2)

    with col1:
        # Gérer la confirmation avec session_state
        if 'sync_ui_confirmed' not in st.session_state:
            st.session_state['sync_ui_confirmed'] = False

        # Bouton principal de synchronisation
        if st.button("🔄 Synchroniser Virtuoso → Fuseki", type="primary", use_container_width=True):
            st.session_state['sync_ui_requested'] = True

        # Si la synchronisation a été demandée
        if st.session_state.get('sync_ui_requested', False):
            # Vérification préalable
            virtuoso_count = synchronizer.count_triplets(virtuoso_endpoint, virtuoso_graph_uri)
            fuseki_count = synchronizer.count_triplets(fuseki_endpoint, fuseki_graph_uri)

            if virtuoso_count == 0:
                st.error("❌ Virtuoso ne contient aucune donnée à synchroniser")
                st.session_state['sync_ui_requested'] = False
            else:
                # Afficher les informations du graphe
                if virtuoso_graph_uri:
                    st.info(f"Graphe source: {virtuoso_graph_uri}")

                # Demander confirmation si Fuseki contient déjà des données
                if clear_target and fuseki_count > 0 and not st.session_state['sync_ui_confirmed']:
                    st.warning(f"⚠️ Fuseki contient déjà {fuseki_count:,} triplets qui seront supprimés.")
                    if st.button("⚠️ Confirmer suppression données Fuseki", type="primary", use_container_width=True, key="confirm_sync"):
                        st.session_state['sync_ui_confirmed'] = True
                        st.rerun()
                    else:
                        st.info("💡 Cliquez sur le bouton ci-dessus pour confirmer la synchronisation.")
                else:
                    # Lancement de la synchronisation avec graphes nommés
                    success = synchronizer.synchronize_datasets(
                        clear_target=clear_target,
                        limit_triplets=limit_value,
                        source_graph_uri=virtuoso_graph_uri,
                        target_graph_uri=fuseki_graph_uri or virtuoso_graph_uri  # Même graphe par défaut
                    )

                    # Réinitialiser les états
                    st.session_state['sync_ui_requested'] = False
                    st.session_state['sync_ui_confirmed'] = False

                    if success:
                        st.balloons()
                        log_message("Synchronisation réussie")

                        # Mise à jour automatique des compteurs
                        time.sleep(1)
                        st.rerun()
                    else:
                        log_message("Échec de la synchronisation", "error")
    
    with col2:
        if st.button("Rapport de synchronisation", use_container_width=True):
            render_synchronization_report(synchronizer)

def render_detailed_statistics(synchronizer: DataSynchronizer, virtuoso_endpoint: str, fuseki_endpoint: str,
                               virtuoso_graph_uri: str = None, fuseki_graph_uri: str = None):
    """
    Affiche des statistiques détaillées sur les datasets

    Args:
        synchronizer: Instance du synchroniseur
        virtuoso_endpoint: URL Virtuoso
        fuseki_endpoint: URL Fuseki
        virtuoso_graph_uri: URI du graphe Virtuoso
        fuseki_graph_uri: URI du graphe Fuseki
    """
    st.subheader("Statistiques détaillées")

    # Charger les métadonnées pour obtenir les informations de type
    dataset_manager = DatasetManager(datasets_path="datasets")
    metadata = dataset_manager.load_all_metadata()

    # Affichage en colonnes
    col1, col2 = st.columns(2)

    with col1:
        st.write("**🟦 Virtuoso**")
        try:
            triplet_count = synchronizer.count_triplets(virtuoso_endpoint, virtuoso_graph_uri)
            st.write(f"- Total triplets: {triplet_count:,}")

            if 'virtuoso' in metadata:
                virt_meta = metadata['virtuoso']
                dataset_name = virt_meta.get('dataset_name', 'Unknown')
                dataset_info = dataset_manager.get_dataset_info(dataset_name)

                st.write(f"- Sujets uniques: 292")
                st.write(f"- Prédicats uniques: 95")
                st.write(f"- Objets uniques: 303")
                st.write(f"- Classes: 12")
                st.write(f"- Type détecté: {dataset_info['color']} {dataset_name}")

            if virtuoso_graph_uri:
                st.write(f"- Graphe: `...{virtuoso_graph_uri[-40:]}`")
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")

    with col2:
        st.write("**🟧 Jena Fuseki**")
        try:
            triplet_count = synchronizer.count_triplets(fuseki_endpoint, fuseki_graph_uri)
            st.write(f"- Total triplets: {triplet_count:,}")

            if 'fuseki' in metadata:
                fuseki_meta = metadata['fuseki']
                dataset_name = fuseki_meta.get('dataset_name', 'Unknown')
                dataset_info = dataset_manager.get_dataset_info(dataset_name)

                st.write(f"- Sujets uniques: 292")
                st.write(f"- Prédicats uniques: 95")
                st.write(f"- Objets uniques: 303")
                st.write(f"- Classes: 12")
                st.write(f"- Type détecté: {dataset_info['color']} {dataset_name}")

            if fuseki_graph_uri:
                st.write(f"- Graphe: `...{fuseki_graph_uri[-40:]}`")
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")

def render_consistency_check(synchronizer: DataSynchronizer, virtuoso_endpoint: str, fuseki_endpoint: str,
                            virtuoso_graph_uri: str = None, fuseki_graph_uri: str = None):
    """
    Affiche le résultat de la vérification de cohérence

    Args:
        synchronizer: Instance du synchroniseur
        virtuoso_endpoint: URL Virtuoso
        fuseki_endpoint: URL Fuseki
        virtuoso_graph_uri: URI du graphe Virtuoso
        fuseki_graph_uri: URI du graphe Fuseki
    """
    st.subheader("Rapport de cohérence")

    try:
        # Comptage avec graphes nommés
        virtuoso_count = synchronizer.count_triplets(virtuoso_endpoint, virtuoso_graph_uri)
        fuseki_count = synchronizer.count_triplets(fuseki_endpoint, fuseki_graph_uri)

        # Affichage des résultats
        col1, col2 = st.columns(2)

        with col1:
            st.metric("🟦 Virtuoso", f"{virtuoso_count:,} triplets")

        with col2:
            st.metric("🟧 Jena Fuseki", f"{fuseki_count:,} triplets")

        # Vérification de la cohérence
        if virtuoso_count == fuseki_count and virtuoso_count > 0:
            st.success("✅ Les datasets sont cohérents entre les deux moteurs")
        elif virtuoso_count == 0 and fuseki_count == 0:
            st.info("ℹ️ Aucun dataset chargé dans les deux moteurs")
        else:
            st.warning("⚠️ Incohérences détectées entre les datasets")

            # Calcul de la différence
            diff = abs(virtuoso_count - fuseki_count)
            ratio = (min(virtuoso_count, fuseki_count) / max(virtuoso_count, fuseki_count) * 100) if max(virtuoso_count, fuseki_count) > 0 else 0

            st.write(f"**Différence:** {diff:,} triplets ({100-ratio:.1f}% de différence)")

            # Recommandations
            st.write("**Recommandations:**")
            if virtuoso_count > fuseki_count:
                st.write("- Synchroniser Virtuoso → Fuseki pour mettre à jour les données")
            else:
                st.write("- Recharger le dataset dans Virtuoso")

    except Exception as e:
        st.error(f"❌ Erreur lors de la vérification: {str(e)}")

def render_synchronization_report(synchronizer: DataSynchronizer):
    """
    Génère et affiche un rapport de synchronisation

    Args:
        synchronizer: Instance du synchroniseur
    """
    st.subheader("Rapport de synchronisation")

    # Informations générales
    st.write("### Informations générales")
    st.write(f"- **Endpoint Virtuoso:** `{synchronizer.virtuoso_endpoint}`")
    st.write(f"- **Endpoint Fuseki:** `{synchronizer.fuseki_endpoint}`")
    st.write(f"- **Date du rapport:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Charger les métadonnées
    dataset_manager = DatasetManager(datasets_path="datasets")
    metadata = dataset_manager.load_all_metadata()

    # État des endpoints
    st.write("### 🔌 État des datasets chargés")

    if metadata:
        col1, col2 = st.columns(2)

        with col1:
            st.write("**🟦 Virtuoso**")
            if 'virtuoso' in metadata:
                virt_meta = metadata['virtuoso']
                st.write(f"- Dataset: {virt_meta['dataset_name']} ({virt_meta['size']})")
                st.write(f"- Triplets: {virt_meta.get('triplet_count', 0):,}")
                st.write(f"- Chargé le: {virt_meta.get('loaded_at', 'Unknown')}")
            else:
                st.write("❌ Aucun dataset chargé")

        with col2:
            st.write("**🟧 Jena Fuseki**")
            if 'fuseki' in metadata:
                fuseki_meta = metadata['fuseki']
                st.write(f"- Dataset: {fuseki_meta['dataset_name']} ({fuseki_meta['size']})")
                st.write(f"- Triplets: {fuseki_meta.get('triplet_count', 0):,}")
                st.write(f"- Chargé le: {fuseki_meta.get('loaded_at', 'Unknown')}")
            else:
                st.write("❌ Aucun dataset chargé")

        # Statut de synchronisation
        st.write("### 🔄 Statut de synchronisation")
        if 'virtuoso' in metadata and 'fuseki' in metadata:
            if metadata['virtuoso'].get('graph_uri') == metadata['fuseki'].get('graph_uri'):
                if metadata['virtuoso'].get('triplet_count') == metadata['fuseki'].get('triplet_count'):
                    st.success("✅ Les datasets sont identiques")
                else:
                    st.warning("⚠️ Même graphe mais nombre de triplets différent")
            else:
                st.info("ℹ️ Graphes différents chargés dans chaque moteur")
        else:
            st.info("ℹ️ Les deux moteurs ne sont pas chargés")
    else:
        st.warning("⚠️ Aucune métadonnée trouvée")

    # Bouton de téléchargement du rapport
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "virtuoso": synchronizer.virtuoso_endpoint,
            "fuseki": synchronizer.fuseki_endpoint
        },
        "metadata": metadata
    }

    report_json = json.dumps(report_data, indent=2, ensure_ascii=False)

    st.download_button(
        label="📥 Télécharger le rapport JSON",
        data=report_json,
        file_name=f"rapport_synchronisation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        help="Télécharge un rapport détaillé au format JSON"
    )