"""
Wizard d'onboarding pour les nouveaux utilisateurs
Guide pas à pas pour la première utilisation de la plateforme
"""

import streamlit as st
from typing import Dict, Any, Optional


class OnboardingWizard:
    """
    Wizard interactif pour guider les nouveaux utilisateurs
    """

    def __init__(self):
        self.total_steps = 5
        self._initialize_state()

    def _initialize_state(self):
        """Initialise l'état du wizard dans session_state"""
        if 'onboarding_completed' not in st.session_state:
            st.session_state['onboarding_completed'] = False

        if 'onboarding_current_step' not in st.session_state:
            st.session_state['onboarding_current_step'] = 1

        if 'onboarding_skipped' not in st.session_state:
            st.session_state['onboarding_skipped'] = False

    def should_show(self) -> bool:
        """
        Détermine si le wizard doit être affiché

        Returns:
            True si le wizard doit être affiché
        """
        return (
            not st.session_state.get('onboarding_completed', False) and
            not st.session_state.get('onboarding_skipped', False)
        )

    def render(self) -> Optional[Dict[str, Any]]:
        """
        Affiche le wizard d'onboarding

        Returns:
            Configuration générée par le wizard, ou None
        """
        if not self.should_show():
            return None

        current_step = st.session_state.get('onboarding_current_step', 1)

        # Conteneur principal avec style
        with st.container():
            # En-tête du wizard
            self._render_header(current_step)

            st.markdown("---")

            # Contenu de l'étape actuelle
            config = self._render_step_content(current_step)

            st.markdown("---")

            # Navigation
            self._render_navigation(current_step)

            return config

    def _render_header(self, current_step: int):
        """
        Affiche l'en-tête du wizard avec progression

        Args:
            current_step: Étape actuelle
        """
        col1, col2, col3 = st.columns([2, 6, 2])

        with col1:
            st.markdown("### 🧭 Guide")

        with col2:
            # Barre de progression
            progress = current_step / self.total_steps
            st.progress(progress)
            st.caption(f"Étape {current_step} sur {self.total_steps}")

        with col3:
            if st.button("✕ Ignorer", key="skip_onboarding"):
                st.session_state['onboarding_skipped'] = True
                st.rerun()

    def _render_step_content(self, step: int) -> Dict[str, Any]:
        """
        Affiche le contenu de l'étape actuelle

        Args:
            step: Numéro de l'étape

        Returns:
            Configuration collectée à cette étape
        """
        if step == 1:
            return self._step_1_welcome()
        elif step == 2:
            return self._step_2_endpoints()
        elif step == 3:
            return self._step_3_dataset()
        elif step == 4:
            return self._step_4_test_profile()
        elif step == 5:
            return self._step_5_ready()
        else:
            return {}

    def _step_1_welcome(self) -> Dict[str, Any]:
        """Étape 1: Bienvenue et présentation"""
        st.markdown("## 👋 Bienvenue sur SPARQL Performance Platform!")

        st.markdown("""
        Cette plateforme vous permet de **comparer les performances** de deux moteurs SPARQL:
        - **Virtuoso** (OpenLink)
        - **Jena Fuseki** (Apache)

        ### Ce que vous pouvez faire:

        ✅ Exécuter des tests de performance automatisés
        ✅ Comparer les temps d'exécution entre moteurs
        ✅ Analyser l'utilisation CPU/mémoire
        ✅ Visualiser les résultats avec des graphiques interactifs
        ✅ Exporter les rapports en CSV/Excel/JSON

        ### Durée estimée du guide: **2 minutes**
        """)

        # Vidéo ou image de démonstration (optionnel)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("https://via.placeholder.com/400x200?text=Demo+Screenshot",
                     caption="Interface de la plateforme", use_container_width=True)

        st.info("**Astuce:** Vous pouvez toujours revenir à ce guide via le menu Aide")

        return {}

    def _step_2_endpoints(self) -> Dict[str, Any]:
        """Étape 2: Configuration des endpoints SPARQL"""
        st.markdown("## 🔗 Étape 1/4: Configurer les endpoints SPARQL")

        st.markdown("""
        Les **endpoints SPARQL** sont les URLs où vos moteurs Virtuoso et Fuseki sont accessibles.

        ### 📍 Exemples d'URLs:
        - `http://localhost:8890/sparql` (Virtuoso local)
        - `http://localhost:3030/dataset/query` (Fuseki local)
        - `http://votreserveur.com:8890/sparql` (Virtuoso distant)
        """)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Virtuoso")
            virtuoso_endpoint = st.text_input(
                "Endpoint Virtuoso",
                value="http://localhost:8890/sparql",
                key="wizard_virtuoso_endpoint",
                help="URL de votre endpoint Virtuoso"
            )

            # Bouton de test
            if st.button("🧪 Tester Virtuoso", key="test_virtuoso"):
                with st.spinner("Test en cours..."):
                    try:
                        from ui.components.connectivity_checker import ConnectivityChecker
                        checker = ConnectivityChecker()
                        result = checker.test_endpoint(virtuoso_endpoint, "Virtuoso")

                        if result['status'] == 'online':
                            st.success(f"✅ {result['message']}")
                            st.session_state['wizard_virtuoso_ok'] = True
                        else:
                            st.error(f"❌ {result['message']}")
                            st.session_state['wizard_virtuoso_ok'] = False
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")
                        st.session_state['wizard_virtuoso_ok'] = False

        with col2:
            st.markdown("#### Jena Fuseki")
            fuseki_endpoint = st.text_input(
                "Endpoint Fuseki",
                value="http://localhost:3030/dataset/query",
                key="wizard_fuseki_endpoint",
                help="URL de votre endpoint Fuseki"
            )

            # Bouton de test
            if st.button("🧪 Tester Fuseki", key="test_fuseki"):
                with st.spinner("Test en cours..."):
                    try:
                        from ui.components.connectivity_checker import ConnectivityChecker
                        checker = ConnectivityChecker()
                        result = checker.test_endpoint(fuseki_endpoint, "Fuseki")

                        if result['status'] == 'online':
                            st.success(f"✅ {result['message']}")
                            st.session_state['wizard_fuseki_ok'] = True
                        else:
                            st.error(f"❌ {result['message']}")
                            st.session_state['wizard_fuseki_ok'] = False
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")
                        st.session_state['wizard_fuseki_ok'] = False

        # Statut de validation
        virtuoso_ok = st.session_state.get('wizard_virtuoso_ok', False)
        fuseki_ok = st.session_state.get('wizard_fuseki_ok', False)

        if virtuoso_ok and fuseki_ok:
            st.success("🎉 Les deux endpoints sont accessibles ! Vous pouvez continuer.")
        elif virtuoso_ok or fuseki_ok:
            st.warning("⚠️ Un seul endpoint est accessible. Vous pouvez continuer, mais les comparaisons seront limitées.")
        else:
            st.info("Testez au moins un endpoint pour continuer")

        # Aide pour les erreurs communes
        with st.expander("❓ Problèmes de connexion ?"):
            st.markdown("""
            **Erreurs courantes:**

            1. **Connection refused:**
               - Vérifiez que Virtuoso/Fuseki est démarré
               - Commande: `docker ps` ou `service status`

            2. **Timeout:**
               - Vérifiez l'URL (http vs https)
               - Vérifiez le port (8890 pour Virtuoso, 3030 pour Fuseki)

            3. **404 Not Found:**
               - Vérifiez le chemin de l'endpoint (/sparql, /query, etc.)

            4. **Pare-feu:**
               - Autorisez les ports 8890 et 3030

            **Démarrage rapide avec Docker:**
            ```bash
            docker-compose up -d
            ```
            """)

        return {
            'virtuoso_endpoint': virtuoso_endpoint,
            'fuseki_endpoint': fuseki_endpoint,
            'endpoints_validated': virtuoso_ok and fuseki_ok
        }

    def _step_3_dataset(self) -> Dict[str, Any]:
        """Étape 3: Choix du jeu de données"""
        st.markdown("## Étape 2/4: Choisir le jeu de données")

        st.markdown("""
        La plateforme propose des **requêtes prédéfinies** adaptées à différents jeux de données.

        ### 📚 Jeux de données disponibles:
        """)

        datasets_info = {
            "LUBM": {
                "icon": "🎓",
                "name": "Lehigh University Benchmark",
                "description": "Benchmark académique pour les systèmes universitaires",
                "queries": 14,
                "complexity": "Moyenne",
                "use_case": "Comparaison standard, données structurées"
            },
            "DBpedia": {
                "icon": "📖",
                "name": "DBpedia",
                "description": "Extraction structurée de Wikipedia",
                "queries": 10,
                "complexity": "Élevée",
                "use_case": "Données encyclopédiques, requêtes complexes"
            },
            "BSBM": {
                "icon": "🛒",
                "name": "Berlin SPARQL Benchmark",
                "description": "Benchmark e-commerce",
                "queries": 12,
                "complexity": "Élevée",
                "use_case": "Simulation d'applications e-commerce"
            },
            "YAGO": {
                "icon": "🌍",
                "name": "Yet Another Great Ontology",
                "description": "Base de connaissances géographique",
                "queries": 8,
                "complexity": "Moyenne",
                "use_case": "Données géographiques et temporelles"
            },
            "Personnalisé": {
                "icon": "⚙️",
                "name": "Jeu de données personnalisé",
                "description": "Utilisez vos propres requêtes",
                "queries": "Variable",
                "complexity": "Variable",
                "use_case": "Vos propres données RDF"
            }
        }

        # Affichage des options sous forme de cartes
        dataset_choice = st.radio(
            "Sélectionnez un jeu de données:",
            options=list(datasets_info.keys()),
            index=0,
            format_func=lambda x: f"{datasets_info[x]['icon']} {datasets_info[x]['name']}",
            key="wizard_dataset_choice"
        )

        # Détails du dataset choisi
        selected_info = datasets_info[dataset_choice]

        col1, col2 = st.columns([2, 1])

        with col1:
            st.info(f"""
            **{selected_info['icon']} {selected_info['name']}**

            {selected_info['description']}

            - **Nombre de requêtes:** {selected_info['queries']}
            - **Complexité:** {selected_info['complexity']}
            - **Cas d'usage:** {selected_info['use_case']}
            """)

        with col2:
            if dataset_choice == "LUBM":
                st.success("✅ Recommandé pour débuter")
            elif dataset_choice == "Personnalisé":
                st.warning("⚠️ Requiert des requêtes SPARQL")

        # Upload de fichier si personnalisé
        dataset_file = None
        if dataset_choice == "Personnalisé":
            st.markdown("---")
            st.markdown("#### 📁 Charger votre jeu de données")

            dataset_file = st.file_uploader(
                "Fichier RDF (optionnel pour les requêtes)",
                type=["rdf", "ttl", "nt", "n3", "owl"],
                key="wizard_dataset_file",
                help="Vous pourrez également entrer des requêtes personnalisées plus tard"
            )

        # Recommandation
        if dataset_choice in ["LUBM", "BSBM"]:
            st.success("**Recommandé:** Ces jeux de données sont parfaits pour des benchmarks standardisés")
        elif dataset_choice == "DBpedia":
            st.info("**Note:** DBpedia nécessite un endpoint avec des données DBpedia chargées")

        return {
            'dataset_choice': dataset_choice,
            'dataset_file': dataset_file
        }

    def _step_4_test_profile(self) -> Dict[str, Any]:
        """Étape 4: Configuration du profil de test"""
        st.markdown("## Étape 3/4: Configurer le profil de test")

        st.markdown("""
        Choisissez un **profil de test** selon vos besoins:
        """)

        # Profils visuels
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            ### ⚡ Rapide
            **Durée:** ~3 minutes

            - 3 itérations
            - 1 échauffement
            - Concurrence: 1

            ✅ **Idéal pour:**
            - Tests rapides
            - Développement
            - Première découverte
            """)

            if st.button("Choisir Rapide", key="profile_quick", width='stretch'):
                st.session_state['wizard_profile'] = 'quick'
                st.rerun()

        with col2:
            st.markdown("""
            ### Standard
            **Durée:** ~10 minutes

            - 5 itérations
            - 2 échauffements
            - Concurrence: 1

            ✅ **Idéal pour:**
            - Usage général
            - Résultats fiables
            - **Recommandé**
            """)

            if st.button("Choisir Standard", key="profile_standard", width='stretch', type="primary"):
                st.session_state['wizard_profile'] = 'standard'
                st.rerun()

        with col3:
            st.markdown("""
            ### 💪 Complet
            **Durée:** ~30 minutes

            - 10 itérations
            - 3 échauffements
            - Concurrence: 2

            ✅ **Idéal pour:**
            - Tests exhaustifs
            - Résultats scientifiques
            - Benchmarks officiels
            """)

            if st.button("Choisir Complet", key="profile_complete", width='stretch'):
                st.session_state['wizard_profile'] = 'complete'
                st.rerun()

        # Affichage du profil choisi
        selected_profile = st.session_state.get('wizard_profile', 'standard')

        profile_configs = {
            'quick': {
                'num_iterations': 3,
                'warmup_iterations': 1,
                'concurrent_queries': 1,
                'query_timeout': 30
            },
            'standard': {
                'num_iterations': 5,
                'warmup_iterations': 2,
                'concurrent_queries': 1,
                'query_timeout': 60
            },
            'complete': {
                'num_iterations': 10,
                'warmup_iterations': 3,
                'concurrent_queries': 2,
                'query_timeout': 120
            }
        }

        config = profile_configs[selected_profile]

        st.success(f"✅ Profil **{selected_profile.capitalize()}** sélectionné")

        # Option avancée
        with st.expander("Personnaliser les paramètres (avancé)"):
            config['num_iterations'] = st.slider(
                "Nombre d'itérations",
                min_value=1,
                max_value=20,
                value=config['num_iterations'],
                key="wizard_iterations"
            )

            config['warmup_iterations'] = st.slider(
                "Itérations d'échauffement",
                min_value=0,
                max_value=5,
                value=config['warmup_iterations'],
                key="wizard_warmup"
            )

            config['concurrent_queries'] = st.slider(
                "Niveau de concurrence",
                min_value=1,
                max_value=10,
                value=config['concurrent_queries'],
                key="wizard_concurrency"
            )

            config['query_timeout'] = st.slider(
                "Timeout par requête (secondes)",
                min_value=10,
                max_value=300,
                value=config['query_timeout'],
                key="wizard_timeout"
            )

        st.info("""
        **Explications:**

        - **Itérations:** Nombre de fois que chaque requête sera exécutée (plus = résultats plus précis)
        - **Échauffement:** Exécutions préalables pour stabiliser les caches (non comptées dans les résultats)
        - **Concurrence:** Nombre de requêtes exécutées simultanément (teste la charge)
        - **Timeout:** Temps maximum d'attente avant abandon d'une requête
        """)

        config['profile_name'] = selected_profile

        return config

    def _step_5_ready(self) -> Dict[str, Any]:
        """Étape 5: Prêt à démarrer"""
        st.markdown("## 🎉 Étape 4/4: Tout est prêt !")

        # Récapitulatif de la configuration
        st.markdown("### 📋 Récapitulatif de votre configuration:")

        # Collecte des données des étapes précédentes
        virtuoso_endpoint = st.session_state.get('wizard_virtuoso_endpoint', 'http://localhost:8890/sparql')
        fuseki_endpoint = st.session_state.get('wizard_fuseki_endpoint', 'http://localhost:3030/dataset/query')
        dataset_choice = st.session_state.get('wizard_dataset_choice', 'LUBM')
        profile = st.session_state.get('wizard_profile', 'standard')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            #### 🔗 Endpoints
            """)
            st.code(f"Virtuoso:\n{virtuoso_endpoint}", language="text")
            st.code(f"Fuseki:\n{fuseki_endpoint}", language="text")

            st.markdown("""
            #### Dataset
            """)
            st.info(f"**{dataset_choice}**")

        with col2:
            st.markdown("""
            #### Profil de test
            """)
            st.info(f"**{profile.capitalize()}**")

            profile_details = {
                'quick': "3 itérations | 1 échauffement | ~3 min",
                'standard': "5 itérations | 2 échauffements | ~10 min",
                'complete': "10 itérations | 3 échauffements | ~30 min"
            }

            st.caption(profile_details.get(profile, ""))

        st.markdown("---")

        # Prochaines étapes
        st.markdown("### Prochaines étapes:")

        st.markdown("""
        1. **Lancer les tests** depuis l'onglet "Configuration et tests"
        2. **Analyser les résultats** dans l'onglet "Résultats"
        3. **Visualiser les graphiques** dans l'onglet "Visualisation"
        4. **Exporter les rapports** dans l'onglet "Exportation"
        """)

        # Bouton de finalisation
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            if st.button("✅ Terminer le guide et commencer",
                        type="primary",
                        width='stretch',
                        key="finish_wizard"):
                # Sauvegarder la configuration dans session_state
                st.session_state['onboarding_completed'] = True
                st.session_state['configuration_from_wizard'] = {
                    'virtuoso_endpoint': virtuoso_endpoint,
                    'fuseki_endpoint': fuseki_endpoint,
                    'dataset_choice': dataset_choice,
                    'profile': profile
                }
                st.success("🎉 Configuration sauvegardée !")
                st.balloons()
                st.rerun()

        st.markdown("---")

        # Ressources supplémentaires
        with st.expander("📚 Ressources supplémentaires"):
            st.markdown("""
            **Documentation:**
            - [Guide d'utilisation complet](docs/README.md)
            - [FAQ](docs/FAQ.md)
            - [Exemples de requêtes](docs/EXAMPLES.md)

            **Support:**
            - [Créer une issue GitHub](https://github.com/thiernoDiedhiou/sparql_performance_platform_v2/issues)
            - Email: support@example.com

            **Tutoriels vidéo:**
            - [Démarrage rapide (5 min)](https://youtube.com/...)
            - [Analyse avancée (15 min)](https://youtube.com/...)
            """)

        return {}

    def _render_navigation(self, current_step: int):
        """
        Affiche les boutons de navigation

        Args:
            current_step: Étape actuelle
        """
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if current_step > 1:
                if st.button("← Précédent", key="prev_step", width='stretch'):
                    st.session_state['onboarding_current_step'] = current_step - 1
                    st.rerun()

        with col3:
            if current_step < self.total_steps:
                if st.button("Suivant →", key="next_step", width='stretch', type="primary"):
                    st.session_state['onboarding_current_step'] = current_step + 1
                    st.rerun()

    def reset(self):
        """Réinitialise le wizard"""
        st.session_state['onboarding_completed'] = False
        st.session_state['onboarding_current_step'] = 1
        st.session_state['onboarding_skipped'] = False

        # Nettoyage des données du wizard
        wizard_keys = [k for k in st.session_state.keys() if k.startswith('wizard_')]
        for key in wizard_keys:
            del st.session_state[key]

    def get_collected_config(self) -> Dict[str, Any]:
        """
        Récupère la configuration collectée par le wizard

        Returns:
            Configuration complète
        """
        return st.session_state.get('configuration_from_wizard', {})


# ============================================================
# FONCTION D'ASSISTANCE
# ============================================================
def show_onboarding_if_needed() -> bool:
    """
    Affiche le wizard d'onboarding si nécessaire

    Returns:
        True si le wizard a été affiché
    """
    wizard = OnboardingWizard()

    if wizard.should_show():
        wizard.render()
        return True

    return False


def force_show_onboarding():
    """Force l'affichage du wizard d'onboarding"""
    wizard = OnboardingWizard()
    wizard.reset()
    st.rerun()
