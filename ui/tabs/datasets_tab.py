"""
Onglet de gestion des datasets locaux
Permet de charger, valider et gérer les datasets DBpedia, LUBM et Generic
"""

import streamlit as st
import time
from pathlib import Path
from typing import Optional
from utils.dataset_manager import DatasetManager
from utils.helpers import log_message
from config.settings import get_default_config


class DatasetsTab:
    """Onglet de gestion des datasets"""

    def __init__(self, datasets_path: str):
        """
        Initialise l'onglet des datasets

        Args:
            datasets_path: Chemin vers le dossier contenant les datasets
        """
        try:
            self.manager = DatasetManager(datasets_path)
            self.available_datasets = self.manager.get_available_datasets()
        except FileNotFoundError as e:
            st.error(f"❌ Erreur d'initialisation : {str(e)}")
            self.manager = None
            self.available_datasets = {}

    def render(self):
        """Affiche l'onglet de gestion des datasets"""

        st.title("Gestion des Datasets")

        if not self.manager:
            st.error("❌ Gestionnaire de datasets non disponible. Vérifiez la configuration.")
            return

        # En-tête avec informations
        st.markdown("""
        Cette section permet de charger des datasets pré-configurés dans les moteurs SPARQL.
        Les datasets sont optimisés pour des tests de performance rapides et fiables.
        """)

        st.markdown("---")

        # Afficher la structure des datasets disponibles
        self._render_datasets_overview()

        st.markdown("---")

        # Vérifier si des datasets sont disponibles
        if not self.available_datasets:
            st.warning("""
           ⚠️ **Aucun dataset trouvé !**

            Veuillez placer vos fichiers de datasets dans :
            `C:\\Users\\hp\\Documents\\memoire\\datasets\\`

            Structure attendue :
            ```
            datasets/
            ├── DBpedia/
            │   ├── 10K.ttl
            │   └── 100K.ttl
            ├── LUBM/
            │   ├── 10K.ttl
            │   └── 100K.ttl
            └── Generic/
                └── 10K.ttl
            ```
            """)
            return

        # Sélection du dataset et de la taille
        col1, col2 = st.columns(2)

        with col1:
            dataset_options = list(self.available_datasets.keys())
            selected_dataset = st.selectbox(
                "Sélectionner un dataset",
                options=dataset_options,
                format_func=lambda x: f"{self.manager.DATASET_INFO[x]['color']} {x}",
                help="Choisissez le type de dataset à charger"
            )

        with col2:
            available_sizes = self.available_datasets[selected_dataset]
            selected_size = st.selectbox(
                "Sélectionner la taille",
                options=available_sizes,
                format_func=lambda x: self.manager.ALLOWED_SIZES[x]["label"],
                help="Choisissez la taille du dataset"
            )

        st.markdown("---")

        # Afficher les informations détaillées
        self._render_dataset_info(selected_dataset, selected_size)

        st.markdown("---")

        # Section de chargement
        self._render_loading_section(selected_dataset, selected_size)

        st.markdown("---")

        # Section de statistiques (si datasets déjà chargés)
        self._render_statistics_section()

    def _render_datasets_overview(self):
        """Affiche une vue d'ensemble des datasets disponibles"""
        st.subheader("Datasets Disponibles")

        if not self.available_datasets:
            return

        # Créer une visualisation en colonnes pour chaque dataset
        cols = st.columns(len(self.available_datasets))

        for idx, (dataset_name, sizes) in enumerate(self.available_datasets.items()):
            with cols[idx]:
                color = self.manager.DATASET_INFO[dataset_name]['color']
                description = self.manager.DATASET_INFO[dataset_name]['description']

                st.markdown(f"### {color} {dataset_name}")
                st.caption(description)

                # Afficher les tailles disponibles
                for size in sizes:
                    info = self.manager.get_dataset_file_info(dataset_name, size)
                    time_estimate = self.manager.estimate_load_time(dataset_name, size)

                    # Emoji selon la vitesse
                    if time_estimate < 10:
                        speed_icon = "⚡"
                        speed_label = "Ultra-rapide"
                    elif time_estimate < 30:
                        speed_icon = ""
                        speed_label = "Rapide"
                    else:
                        speed_icon = ""
                        speed_label = "Recommandé"

                    st.markdown(f"""
                    **{size}.ttl** {speed_icon}
                    - Taille : {info['size_mb']} MB
                    - Temps : ~{time_estimate}s
                    - {speed_label}
                    """)

                st.markdown("---")

        # Afficher un résumé global
        with st.expander("📋 Résumé et Recommandations", expanded=False):
            st.markdown("""
            ### Recommandations par Usage

            **🎭 Pour les démonstrations :**
            - **Generic 10K** ou **DBpedia 10K**
            - Chargement < 5 secondes
            - Parfait pour découverte rapide

            **🔬 Pour les tests de performance :**
            - **LUBM 100K** ou **DBpedia 100K**
            - Résultats représentatifs
            - Comparaisons Virtuoso vs Fuseki

            **Pour le développement :**
            - **Generic 10K**
            - Très léger (< 2 sec)
            - Rechargement rapide

            ### ⚠️ Limitations

            - ✅ **10K** : Tous usages, ultra-rapide
            - ✅ **100K** : Tests réalistes, rapide
            - ❌ **1M** : Non activé (> 2 minutes de chargement)

            ### Conseil

            Commencez toujours avec **Generic 10K** pour tester la connectivité,
            puis passez à **100K** pour des tests significatifs.
            """)

    def _render_dataset_info(self, dataset_name: str, size: str):
        """
        Affiche les informations détaillées sur le dataset sélectionné

        Args:
            dataset_name: Nom du dataset
            size: Taille du dataset
        """
        st.subheader("ℹ️ Informations sur le dataset")

        recommendations = self.manager.get_loading_recommendations(dataset_name, size)

        if "error" in recommendations:
            st.error(f"❌ {recommendations['error']}")
            return

        # Créer un affichage en colonnes
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="💾 Taille du fichier",
                value=f"{recommendations['file_size_mb']} MB"
            )

        with col2:
            st.metric(
                label="Temps estimé",
                value=f"~{recommendations['estimated_time_seconds']}s"
            )

        with col3:
            st.metric(
                label="Mémoire requise",
                value=f"~{recommendations['memory_required_mb']} MB"
            )

        # Informations détaillées
        with st.expander("📋 Détails du dataset", expanded=False):
            st.markdown(f"""
            **Description :** {recommendations['description']}

            **Format :** {recommendations['format']}

            **Recommandé pour :** {recommendations['recommended_for']}

            **Ontologie :** `{self.manager.DATASET_INFO[dataset_name]['ontology']}`
            """)

        # Alerte mémoire
        if not recommendations['memory_available']:
            st.error(f"""
            ⚠️ **ALERTE MÉMOIRE**

            {recommendations['memory_message']}

            **Recommandations :**
            - Fermez les applications non essentielles
            - Choisissez un dataset plus petit (10K)
            - Redémarrez votre navigateur
            """)
        else:
            st.success(f"✅ {recommendations['memory_message']}")

    def _render_loading_section(self, dataset_name: str, size: str):
        """
        Affiche la section de chargement des datasets

        Args:
            dataset_name: Nom du dataset
            size: Taille du dataset
        """
        st.subheader("Chargement du dataset")

        # Récupérer les endpoints de la configuration
        config = get_default_config()
        virtuoso_endpoint = st.session_state.get('virtuoso_endpoint', config['virtuoso_endpoint'])
        fuseki_endpoint = st.session_state.get('fuseki_endpoint', config['fuseki_endpoint'])

        # Afficher les endpoints
        col1, col2 = st.columns(2)

        with col1:
            st.text_input(
                "Virtuoso Endpoint",
                value=virtuoso_endpoint,
                key="dataset_virtuoso_endpoint",
                disabled=True
            )

        with col2:
            st.text_input(
                "Fuseki Endpoint",
                value=fuseki_endpoint,
                key="dataset_fuseki_endpoint",
                disabled=True
            )

        st.markdown("###")

        # Vérifier les recommandations
        recommendations = self.manager.get_loading_recommendations(dataset_name, size)

        # Boutons de chargement
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            load_virtuoso = st.button(
                "📥 Charger dans Virtuoso",
                use_container_width=True,
                type="primary",
                disabled=not recommendations.get('can_load', False),
                help="Charge le dataset dans Virtuoso"
            )

        with col2:
            load_fuseki = st.button(
                "📥 Charger dans Fuseki",
                use_container_width=True,
                type="primary",
                disabled=not recommendations.get('can_load', False),
                help="Charge le dataset dans Fuseki"
            )

        with col3:
            load_both = st.button(
                "📥 Charger dans les deux",
                use_container_width=True,
                disabled=not recommendations.get('can_load', False),
                help="Charge le dataset dans Virtuoso ET Fuseki"
            )

        # Traiter les actions de chargement
        if load_virtuoso:
            self._load_dataset_action(dataset_name, size, "virtuoso", virtuoso_endpoint=virtuoso_endpoint)

        if load_fuseki:
            self._load_dataset_action(dataset_name, size, "fuseki", fuseki_endpoint=fuseki_endpoint)

        if load_both:
            self._load_dataset_action(dataset_name, size, "both", virtuoso_endpoint=virtuoso_endpoint, fuseki_endpoint=fuseki_endpoint)

    def _load_dataset_action(
        self,
        dataset_name: str,
        size: str,
        target: str,
        virtuoso_endpoint: Optional[str] = None,
        fuseki_endpoint: Optional[str] = None
    ):
        """
        Effectue le chargement d'un dataset avec barre de progression

        Args:
            dataset_name: Nom du dataset
            size: Taille du dataset
            target: Cible ('virtuoso', 'fuseki', ou 'both')
            virtuoso_endpoint: Endpoint Virtuoso
            fuseki_endpoint: Endpoint Fuseki
        """
        file_info = self.manager.get_dataset_file_info(dataset_name, size)

        if not file_info.get("exists"):
            st.error(f"❌ Fichier introuvable : {file_info.get('error')}")
            return

        file_path = file_info["path"]
        estimated_time = self.manager.estimate_load_time(dataset_name, size)

        # Barre de progression
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Variables pour stocker les résultats
        graph_uri = f"http://example.org/dataset_{dataset_name}_{size}_{int(time.time())}"
        total_triplets = 0

        try:
            if target == "virtuoso" or target == "both":
                status_text.text("🔄 Chargement dans Virtuoso...")
                progress_bar.progress(25)

                success, message = self.manager.load_to_virtuoso(file_path, virtuoso_endpoint, graph_uri=graph_uri)

                if not success:
                    st.error(f"❌ Virtuoso: {message}")
                    return

                st.success(f"✅ Virtuoso: {message}")
                progress_bar.progress(50)

            if target == "fuseki" or target == "both":
                status_text.text("🔄 Chargement dans Fuseki...")
                progress_bar.progress(50 if target == "fuseki" else 75)

                success, message = self.manager.load_to_fuseki(file_path, fuseki_endpoint, graph_uri=graph_uri)

                if not success:
                    st.error(f"❌ Fuseki: {message}")
                    return

                st.success(f"✅ Fuseki: {message}")

            progress_bar.progress(100)
            status_text.text("✅ Chargement terminé !")

            # Validation
            st.info("Validation du chargement en cours...")
            time.sleep(1)

            if target == "virtuoso" or target == "both":
                is_valid, msg, count = self.manager.validate_loaded_dataset(virtuoso_endpoint, dataset_name, graph_uri)
                if is_valid:
                    st.success(f"✅ Virtuoso validé : {count} triplets dans le graphe")
                    total_triplets = count
                else:
                    st.warning(f"⚠️ Virtuoso : {msg}")

            if target == "fuseki" or target == "both":
                is_valid, msg, count = self.manager.validate_loaded_dataset(fuseki_endpoint, dataset_name, graph_uri)
                if is_valid:
                    st.success(f"✅ Fuseki validé : {count} triplets dans le graphe")
                    if total_triplets == 0:
                        total_triplets = count
                else:
                    st.warning(f"⚠️ Fuseki : {msg}")

            # ======= NOUVEAUTÉ: Sauvegarde des métadonnées et mise à jour du .env =======
            status_text.text("💾 Sauvegarde des métadonnées...")

            # Sauvegarder les métadonnées
            metadata_saved = self.manager.save_dataset_metadata(
                dataset_name=dataset_name,
                size=size,
                target=target,
                graph_uri=graph_uri,
                triplet_count=total_triplets
            )

            # Mettre à jour le fichier .env
            env_updated = self.manager.update_env_file(
                dataset_name=dataset_name,
                size=size,
                target=target
            )

            if metadata_saved and env_updated:
                st.success("✅ Métadonnées et configuration sauvegardées avec succès")
            elif metadata_saved:
                st.warning("⚠️ Métadonnées sauvegardées mais échec de mise à jour du .env")
            elif env_updated:
                st.warning("⚠️ Configuration .env mise à jour mais échec de sauvegarde des métadonnées")
            else:
                st.warning("⚠️ Échec de sauvegarde des métadonnées et de la configuration")

            # Mémoriser le dataset chargé dans la session
            st.session_state['loaded_dataset'] = {
                'name': dataset_name,
                'size': size,
                'target': target,
                'graph_uri': graph_uri,
                'triplet_count': total_triplets,
                'timestamp': time.time()
            }

            st.balloons()
            log_message(f"Dataset {dataset_name} ({size}) chargé avec succès dans {target}")

        except Exception as e:
            st.error(f"❌ Erreur lors du chargement : {str(e)}")
            log_message(f"Erreur chargement dataset: {str(e)}", "error")

        finally:
            progress_bar.empty()
            status_text.empty()

    def _render_statistics_section(self):
        """Affiche les statistiques des datasets chargés"""

        # Charger les statistiques depuis les métadonnées persistantes
        stats = self.manager.get_dataset_statistics()

        if stats['total_datasets_loaded'] == 0:
            st.info("Aucun dataset chargé pour le moment. Utilisez les boutons ci-dessus pour charger un dataset.")
            return

        st.subheader("Datasets actuellement chargés")

        # Afficher un résumé global
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                label="Total de datasets chargés",
                value=stats['total_datasets_loaded']
            )

        with col2:
            st.metric(
                label="Total de triplets",
                value=f"{stats['total_triplets']:,}"
            )

        st.markdown("---")

        # Afficher les détails pour chaque moteur
        for target in ['virtuoso', 'fuseki']:
            if stats[target]:
                info = stats[target]

                st.markdown(f"### {'🔵 Virtuoso' if target == 'virtuoso' else '🟢 Fuseki'}")

                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.markdown(f"**Dataset:** {info['dataset']}")
                    st.caption(f"Chargé le: {info['loaded_at'][:19]}")

                with col2:
                    st.metric("Triplets", f"{info['triplets']:,}")

                with col3:
                    # Bouton pour effacer ce dataset
                    if st.button(
                        f"Effacer",
                        key=f"clear_{target}",
                        use_container_width=True,
                        type="secondary"
                    ):
                        self._clear_dataset_action(target)

                # Afficher le graph URI
                with st.expander(f"ℹ️ Détails techniques {target}", expanded=False):
                    st.code(f"Graph URI: {info['graph_uri']}", language="text")

                st.markdown("---")

        # Bouton pour tout effacer
        if stats['total_datasets_loaded'] > 1:
            if st.button(
                "Effacer tous les datasets",
                use_container_width=True,
                type="primary",
                help="Supprime tous les datasets chargés dans Virtuoso et Fuseki"
            ):
                self._clear_all_datasets_action()

    def _clear_dataset_action(self, target: str):
        """
        Efface un dataset d'un moteur spécifique

        Args:
            target: Moteur cible ('virtuoso' ou 'fuseki')
        """
        config = get_default_config()

        # Obtenir l'endpoint approprié
        endpoint = config['virtuoso_endpoint'] if target == 'virtuoso' else config['fuseki_endpoint']
        endpoint = st.session_state.get(f'{target}_endpoint', endpoint)

        # Afficher une confirmation
        with st.spinner(f"🔄 Suppression du dataset de {target}..."):
            success, message = self.manager.clear_dataset(target, endpoint)

            if success:
                st.success(f"✅ {message}")
                # Mettre à jour la session state si nécessaire
                if 'loaded_dataset' in st.session_state:
                    loaded = st.session_state['loaded_dataset']
                    if loaded.get('target') == target or loaded.get('target') == 'both':
                        del st.session_state['loaded_dataset']
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ {message}")

    def _clear_all_datasets_action(self):
        """Efface tous les datasets de tous les moteurs"""
        config = get_default_config()

        with st.spinner("🔄 Suppression de tous les datasets..."):
            results = []

            # Effacer Virtuoso
            virtuoso_endpoint = st.session_state.get('virtuoso_endpoint', config['virtuoso_endpoint'])
            success_v, msg_v = self.manager.clear_dataset('virtuoso', virtuoso_endpoint)
            results.append(('Virtuoso', success_v, msg_v))

            # Effacer Fuseki
            fuseki_endpoint = st.session_state.get('fuseki_endpoint', config['fuseki_endpoint'])
            success_f, msg_f = self.manager.clear_dataset('fuseki', fuseki_endpoint)
            results.append(('Fuseki', success_f, msg_f))

            # Afficher les résultats
            all_success = True
            for name, success, msg in results:
                if success:
                    st.success(f"✅ {name}: {msg}")
                else:
                    st.warning(f"⚠️ {name}: {msg}")
                    all_success = False

            if all_success:
                st.success("✅ Tous les datasets ont été supprimés avec succès")

            # Nettoyer la session state
            if 'loaded_dataset' in st.session_state:
                del st.session_state['loaded_dataset']

            time.sleep(1)
            st.rerun()


def render_datasets_tab():
    """Fonction de rendu pour l'onglet datasets"""

    # Chemin par défaut des datasets
    datasets_path = st.session_state.get(
        'datasets_path',
        r"datasets"
    )

    # Créer et afficher l'onglet
    tab = DatasetsTab(datasets_path)
    tab.render()

