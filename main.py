"""
Point d'entrée principal de la plateforme d'évaluation SPARQL
Utilise Streamlit avec un design professionnel et un système de composants réutilisables.
"""

import streamlit as st
import psutil
import json
from datetime import datetime
from config.settings import (
    APP_VERSION, APP_VERSION_FULL, APP_NAME, APP_DESCRIPTION,
    APP_AUTHOR, APP_GITHUB
)
from ui.design_system import (
    Colors, Typography, Spacing, Effects, Layout,
    apply_custom_css, create_card, create_metric_card,
    create_alert, create_divider, create_status_badge,
    get_usage_color, get_navbar_logo_css
)


def render_sidebar():
    """Sidebar améliorée avec actions rapides et informations système"""

    with st.sidebar:
        # ====================================================================
        # LOGO ET VERSION
        # ====================================================================
        # Logo de la plateforme (remplace le titre textuel)
        from pathlib import Path

        # Utiliser chemin absolu pour portabilité
        BASE_DIR = Path(__file__).parent.resolve()
        logo_path = BASE_DIR / "images" / "logo" / "logo.png"

        if logo_path.exists():
            _, col_logo, _ = st.columns([1, 3, 1])
            with col_logo:
                st.image(str(logo_path), use_container_width=True)
            st.caption("Plateforme de benchmarking SPARQL")
        else:
            st.markdown(f"""
            <div style="text-align: center; padding: {Spacing.LG} 0;">
                <div style="font-size: 3rem; margin-bottom: {Spacing.SM};">⚡</div>
                <div style="
                    color: {Colors.PRIMARY};
                    font-size: {Typography.SIZE_H3};
                    font-weight: {Typography.WEIGHT_BOLD};
                ">SPARQL Performance</div>
                <div style="
                    color: {Colors.TEXT_SECONDARY};
                    font-size: {Typography.SIZE_BODY_SMALL};
                    margin-top: {Spacing.XS};
                ">Version {APP_VERSION_FULL}</div>
            </div>
            """, unsafe_allow_html=True)

        create_divider()

        # ====================================================================
        # ACTIONS RAPIDES
        # ====================================================================
        st.markdown("### ⚡ Actions Rapides")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🧭 Guide", use_container_width=True, type="secondary"):
                st.session_state['show_guide'] = True
                st.rerun()

        with col2:
            if st.button("🔄 Rafraîchir", use_container_width=True, type="secondary"):
                st.rerun()

        # Dashboard système
        if st.button("📊 État Système", use_container_width=True, type="secondary"):
            st.session_state['show_system_dashboard'] = True
            st.rerun()

        create_divider()

        # ====================================================================
        # MÉTRIQUES SYSTÈME COMPACTES
        # ====================================================================
        st.markdown("### 💻 Monitoring")

        try:
            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory().percent

            # CPU - Utilisation du helper get_usage_color()
            cpu_color = get_usage_color(cpu)
            st.markdown(f"""
            <div style="
                padding: {Spacing.SM};
                background: {Colors.GRAY_50};
                border-radius: {Effects.RADIUS_MD};
                margin-bottom: {Spacing.SM};
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: {Colors.TEXT_SECONDARY};">💻 CPU</span>
                    <span style="
                        color: {cpu_color};
                        font-weight: {Typography.WEIGHT_BOLD};
                    ">{cpu:.1f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Mémoire - Utilisation du helper get_usage_color()
            mem_color = get_usage_color(mem)
            st.markdown(f"""
            <div style="
                padding: {Spacing.SM};
                background: {Colors.GRAY_50};
                border-radius: {Effects.RADIUS_MD};
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: {Colors.TEXT_SECONDARY};">🧠 RAM</span>
                    <span style="
                        color: {mem_color};
                        font-weight: {Typography.WEIGHT_BOLD};
                    ">{mem:.1f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        except Exception:
            st.caption("Monitoring non disponible")

        create_divider()

        # ====================================================================
        # CONFIGURATION DES ENDPOINTS
        # ====================================================================
        try:
            from ui.sidebar_v2 import render_sidebar_v2
            sidebar_config = render_sidebar_v2()
            return sidebar_config
        except ImportError:
            st.warning("Module sidebar non disponible")
            return {}


def render_system_dashboard():
    """Dashboard système détaillé (modal/overlay)"""

    st.markdown("## Dashboard Système")
    create_divider()

    try:
        import psutil

        # Métriques principales en grille
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_color = get_usage_color(cpu_percent)
            create_metric_card(
                label="CPU",
                value=f"{cpu_percent:.1f}%",
                icon="💻",
                color=cpu_color
            )

        with col2:
            memory = psutil.virtual_memory()
            mem_color = get_usage_color(memory.percent)
            create_metric_card(
                label="Mémoire",
                value=f"{memory.percent:.1f}%",
                delta=f"{memory.used / (1024**3):.1f} GB / {memory.total / (1024**3):.1f} GB",
                icon="🧠",
                color=mem_color
            )

        with col3:
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_color = get_usage_color(disk_percent)
            create_metric_card(
                label="Disque",
                value=f"{disk_percent:.1f}%",
                delta=f"{disk.used / (1024**3):.0f} GB / {disk.total / (1024**3):.0f} GB",
                icon="💾",
                color=disk_color
            )

        with col4:
            cpu_count = psutil.cpu_count()
            create_metric_card(
                label="Cœurs CPU",
                value=str(cpu_count),
                delta=f"{psutil.cpu_count(logical=False)} physiques",
                icon="⚙️",
                color=Colors.PRIMARY
            )

        # Alertes si critique
        if cpu_percent > 85 or memory.percent > 85 or disk_percent > 85:
            create_alert(
                "⚠️ Attention : Utilisation des ressources système élevée. "
                "Envisagez de fermer des applications pour améliorer les performances.",
                alert_type="warning"
            )

        create_divider()

        # Bouton de retour
        if st.button("← Retour à la plateforme", use_container_width=True):
            st.session_state['show_system_dashboard'] = False
            st.rerun()

    except ImportError:
        create_alert(
            "Module psutil non disponible. Installez-le avec: pip install psutil",
            alert_type="error"
        )


def render_guide(show_back_button: bool = True):
    """
    Guide de démarrage rapide - VERSION STREAMLIT NATIF + DESIGN SYSTEM
    Utilise les composants natifs Streamlit avec couleurs du design system via CSS

    Args:
        show_back_button: Si True, affiche le bouton "Retour à la plateforme" (défaut: True)
    """
    # Note: Colors, Spacing, Effects déjà importés en haut du fichier
    # st.markdown("## Guide de Démarrage Rapide")
    st.markdown("---")

    # CSS personnalisé pour styler les st.info/success/warning avec les couleurs du design system
    guide_css = f"""
    <style>
        /* Surcharge des couleurs Streamlit avec notre design system */
        .element-container .stAlert {{
            border-radius: {Effects.RADIUS_LG};
            padding: {Spacing.LG};
            margin-bottom: {Spacing.MD};
            box-shadow: {Effects.SHADOW_SM};
        }}

        /* Info - Bleu */
        [data-testid="stAlert"] [data-baseweb="notification"][kind="info"] {{
            background-color: {Colors.INFO_PALE};
            border-left: {Effects.BORDER_THICK} solid {Colors.INFO};
        }}

        /* Success - Vert */
        [data-testid="stAlert"] [data-baseweb="notification"][kind="success"] {{
            background-color: {Colors.SUCCESS_PALE};
            border-left: {Effects.BORDER_THICK} solid {Colors.SUCCESS};
        }}

        /* Warning - Orange */
        [data-testid="stAlert"] [data-baseweb="notification"][kind="warning"] {{
            background-color: {Colors.WARNING_PALE};
            border-left: {Effects.BORDER_THICK} solid {Colors.WARNING};
        }}

        /* Gestion du débordement pour les URLs longues */
        .stMarkdown p, .stMarkdown li {{
            word-wrap: break-word;
            word-break: break-word;
            overflow-wrap: break-word;
        }}

        .stMarkdown code {{
            word-break: break-all;
        }}
    </style>
    """
    st.markdown(guide_css, unsafe_allow_html=True)

    # Première ligne: Configuration + Datasets
    col1, col2 = st.columns(2)

    with col1:
        st.info("⚙️ **1. Configuration**")
        st.markdown("""
**Vérifiez la connectivité des endpoints SPARQL**

- **Virtuoso:** `http://localhost:8890/sparql`
- **Fuseki:** `http://localhost:3030/dataset/query`
- Testez les connexions avant de continuer
        """)

    with col2:
        st.success("📦 **2. Gestion des Datasets**")
        st.markdown("""
**Chargez et validez vos données RDF**

- Chargez un dataset (DBpedia, LUBM, Generic)
- Vérifiez le nombre de triplets chargés
- Synchronisez entre Virtuoso et Fuseki
- Validez la cohérence des données
        """)

    # Deuxième ligne: Tests + Résultats
    col3, col4 = st.columns(2)

    with col3:
        st.warning("🧪 **3. Tests de Performance**")
        st.markdown("""
**Lancez les benchmarks SPARQL**

- Sélectionnez les requêtes à tester
- Configurez les paramètres (itérations, warmup)
- Lancez l'exécution des benchmarks
- Surveillez la progression en temps réel
        """)

    with col4:
        st.info("📊 **4. Résultats & Export**")
        st.markdown("""
**Analysez et exportez vos données**

- Consultez les temps d'exécution détaillés
- Comparez Virtuoso vs Fuseki (graphiques)
- Analysez les performances par requête
- Exportez en CSV, Excel ou JSON
        """)

    st.markdown("---")

    # Bouton de retour (conditionnel)
    if show_back_button:
        if st.button("← Retour à la plateforme", use_container_width=True):
            st.session_state['show_guide'] = False
            st.rerun()


def main():
    """Fonction principale de l'application Streamlit avec design professionnel"""

    # ========================================================================
    # CONFIGURATION DE LA PAGE (doit être en premier)
    # ========================================================================
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': APP_GITHUB,
            'Report a bug': f'{APP_GITHUB}/issues',
            'About': f"# {APP_NAME} {APP_VERSION_FULL}\n\n{APP_DESCRIPTION}\n\n**{APP_AUTHOR}**"
        }
    )

    # ========================================================================
    # APPLICATION DU DESIGN SYSTEM
    # ========================================================================
    apply_custom_css()

    # ========================================================================
    # INITIALISATION DE L'ÉTAT DE SESSION
    # ========================================================================
    try:
        from utils.data_manager import initialize_session_state
        initialize_session_state()
    except ImportError:
        if 'initialized' not in st.session_state:
            st.session_state['initialized'] = True

    # Initialisation spécifique version
    if 'ui_version' not in st.session_state:
        st.session_state['ui_version'] = APP_VERSION

    if 'show_guide' not in st.session_state:
        st.session_state['show_guide'] = False

    if 'show_system_dashboard' not in st.session_state:
        st.session_state['show_system_dashboard'] = False

    # ========================================================================
    # SIDEBAR AVEC ACTIONS RAPIDES
    # ========================================================================
    sidebar_config = render_sidebar()

    # ========================================================================
    # GESTION DES OVERLAYS (GUIDE ET DASHBOARD)
    # ========================================================================
    if st.session_state.get('show_guide', False):
        render_guide()
        return

    if st.session_state.get('show_system_dashboard', False):
        render_system_dashboard()
        return

    # ========================================================================
    # NAVBAR AVEC LOGO - CSS CENTRALISÉ
    # ========================================================================

    # Encoder le logo en base64 pour CSS
    from utils.logo_encoder import get_logo_base64
    logo_base64 = get_logo_base64()

    # Injecter le CSS du logo dans la navbar (fonction centralisée)
    if logo_base64:
        st.markdown(get_navbar_logo_css(logo_base64), unsafe_allow_html=True)

    # Tabs Streamlit avec icônes professionnelles sobres
    # Le logo est intégré via CSS dans la navbar
    tabs = st.tabs([
        "⌂ Accueil",
        "⚙ Configuration & Tests",
        "⊞ Datasets",
        "▣ Résultats & Analyses",
        "⇪ Export & Sessions",
        "◉ Documentation"
    ])

    # ========================================================================
    # CONTENU DES ONGLETS
    # ========================================================================

    with tabs[0]:
        # ====================================================================
        # ONGLET 0: ACCUEIL
        # ====================================================================
        try:
            from ui.tabs.home_tab import render_home_tab
            render_home_tab()
        except ImportError as e:
            create_alert(
                f"Module home_tab non disponible : {str(e)}",
                alert_type="error"
            )

    with tabs[1]:
        # ====================================================================
        # ONGLET 1: CONFIGURATION & TESTS
        # ====================================================================
        # st.markdown("### ⚙ Configuration & Exécution des Tests")
        # st.caption("Configurez les endpoints SPARQL et lancez les benchmarks")

        # create_divider()

        try:
            from ui.tabs.configuration_tab import render_configuration_tab
            render_configuration_tab(sidebar_config)
        except ImportError as e:
            create_alert(
                f"Module configuration_tab non disponible : {str(e)}",
                alert_type="warning"
            )

            # Interface de remplacement élégante
            col1, col2 = st.columns(2)

            with col1:
                create_card(
                    title="Vérification de la connectivité",
                    icon="🔍",
                    content="""
                    <p>Testez la connexion aux endpoints SPARQL :</p>
                    <ul>
                        <li><strong>Virtuoso</strong>: Port 8890</li>
                        <li><strong>Fuseki</strong>: Port 3030</li>
                    </ul>
                    """,
                    border_color=Colors.PRIMARY
                )

            with col2:
                create_card(
                    title="Paramètres de test",
                    icon="⚙️",
                    content="""
                    <p>Configurez les paramètres d'exécution :</p>
                    <ul>
                        <li>Nombre d'itérations</li>
                        <li>Itérations de warmup</li>
                        <li>Requêtes concurrentes</li>
                    </ul>
                    """,
                    border_color=Colors.SECONDARY
                )

    with tabs[2]:
        # ====================================================================
        # ONGLET 2: GESTION DES DATASETS
        # ====================================================================
        # st.markdown("### ⊞ Gestion des Datasets")
        # st.caption("Chargez, validez et synchronisez vos datasets de test")

        # create_divider()

        try:
            from ui.tabs.datasets_tab import render_datasets_tab
            render_datasets_tab()
        except ImportError as e:
            create_alert(
                f"Module datasets_tab non disponible : {str(e)}",
                alert_type="warning"
            )

            # Interface de remplacement
            col1, col2, col3 = st.columns(3)

            with col1:
                create_card(
                    title="DBpedia",
                    icon="🌐",
                    content="""
                    <ul style="margin: 0; padding-left: 1.5rem;">
                        <li>10K triplets</li>
                        <li>100K triplets</li>
                        <li>1M triplets</li>
                    </ul>
                    """,
                    border_color=Colors.PRIMARY
                )

            with col2:
                create_card(
                    title="LUBM",
                    icon="🎓",
                    content="""
                    <ul style="margin: 0; padding-left: 1.5rem;">
                        <li>10K triplets</li>
                        <li>100K triplets</li>
                        <li>1M triplets</li>
                    </ul>
                    """,
                    border_color=Colors.SECONDARY
                )

            with col3:
                create_card(
                    title="Generic",
                    icon="📄",
                    content="""
                    <ul style="margin: 0; padding-left: 1.5rem;">
                        <li>10K triplets</li>
                        <li>100K triplets</li>
                        <li>Custom dataset</li>
                    </ul>
                    """,
                    border_color=Colors.SUCCESS
                )

    with tabs[3]:
        # ====================================================================
        # ONGLET 3: RÉSULTATS & ANALYSES (FUSION DE 3 ONGLETS)
        # ====================================================================
        st.markdown("### ▣ Résultats & Analyses Visuelles")
        st.caption("Consultez les performances et comparez les résultats")

        create_divider()

        # Sous-onglets pour organiser
        sub_tabs = st.tabs(["◫ Résultats Bruts", "◨ Visualisations", "◉ Analyses Détaillées"])

        with sub_tabs[0]:
            try:
                from ui.tabs.results_tab import render_results_tab
                render_results_tab()
            except ImportError:
                st.info("Module results_tab non disponible")

        with sub_tabs[1]:
            try:
                from ui.tabs.visualization_tab import render_visualization_tab
                render_visualization_tab()
            except ImportError:
                st.info("Module visualization_tab non disponible")

        with sub_tabs[2]:
            try:
                from ui.tabs.analysis_tab import render_analysis_tab
                render_analysis_tab()
            except ImportError as e:
                create_alert(
                    f"Module analysis_tab non disponible : {str(e)}",
                    alert_type="warning"
                )
                st.info("📊 Module d'analyses détaillées en cours de chargement...")

    with tabs[4]:
        # ====================================================================
        # ONGLET 4: EXPORT & SESSIONS (FUSION DE 2 ONGLETS)
        # ====================================================================
        st.markdown("### ⇪ Export & Gestion des Sessions")
        st.caption("Exportez vos résultats et gérez vos configurations")

        create_divider()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### ⇪ Export des Résultats")

            st.info("💾 **Formats disponibles**")
            st.markdown("""
- **CSV**: Compatible Excel, R, Python
- **Excel**: Feuilles multiples avec formatage
- **JSON**: Données structurées complètes
            """)

            try:
                from ui.tabs.export_tab import render_export_tab
                render_export_tab()
            except ImportError:
                st.info("Module export_tab non disponible")

        with col2:
            st.markdown("#### ⊙ Gestion des Sessions")

            # Sauvegarde rapide
            if st.button("⊙ Sauvegarder la session actuelle", use_container_width=True, type="primary"):
                session_data = {
                    "timestamp": datetime.now().isoformat(),
                    "version": APP_VERSION,
                    "config": {
                        "virtuoso_endpoint": st.session_state.get('virtuoso_endpoint', 'http://localhost:8890/sparql'),
                        "fuseki_endpoint": st.session_state.get('fuseki_endpoint', 'http://localhost:3030/dataset/query'),
                        "num_iterations": st.session_state.get('num_iterations', 5),
                        "warmup_iterations": st.session_state.get('warmup_iterations', 2),
                        "concurrent_queries": st.session_state.get('concurrent_queries', 1),
                        "dataset_type": st.session_state.get('dataset_type', 'LUBM'),
                    },
                    "selected_queries": st.session_state.get('selected_queries', []),
                }

                filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

                st.download_button(
                    label="📥 Télécharger la session",
                    data=json.dumps(session_data, indent=2, ensure_ascii=False),
                    file_name=filename,
                    mime="application/json",
                    use_container_width=True
                )

                st.success(f"✅ Session prête : {filename}")

            try:
                from utils.session_manager import render_session_manager_ui
                render_session_manager_ui()
            except ImportError:
                create_card(
                    title="Sessions sauvegardées",
                    icon="📂",
                    content="""
                    <p>Chargez une session précédente pour restaurer votre configuration.</p>
                    <p style="color: #6B7280; margin-top: 0.5rem;">Module session_manager à venir</p>
                    """,
                    border_color=Colors.SECONDARY
                )

    with tabs[5]:
        # ====================================================================
        # ONGLET 5: DOCUMENTATION
        # ====================================================================
        st.markdown("### ◉ Documentation & Aide")
        st.caption("Guides complets et documentation du mémoire")

        create_divider()

        try:
            from ui.tabs.chapters_tab import show_chapters_tab
            show_chapters_tab()
        except Exception as e:
            create_alert(
                f"Module documentation non disponible : {str(e)}",
                alert_type="warning"
            )

            # Documentation de remplacement
            col1, col2 = st.columns(2)

            with col1:
                create_card(
                    title="Guides Utilisateur",
                    icon="📘",
                    content="""
                    <ul style="margin: 0; padding-left: 1.5rem;">
                        <li><strong>Guide de démarrage rapide</strong> (cliquer sur 🧭 Guide)</li>
                        <li>Configuration des endpoints</li>
                        <li>Gestion des datasets</li>
                        <li>Interprétation des résultats</li>
                    </ul>
                    """,
                    border_color=Colors.PRIMARY
                )

            with col2:
                create_card(
                    title="Documentation Technique",
                    icon="📗",
                    content="""
                    <ul style="margin: 0; padding-left: 1.5rem;">
                        <li>Architecture de la plateforme</li>
                        <li>Design system v3.1</li>
                        <li>API et composants</li>
                        <li>FAQ et dépannage</li>
                    </ul>
                    """,
                    border_color=Colors.SECONDARY
                )

    # ========================================================================
    # PIED DE PAGE PROFESSIONNEL
    # ========================================================================
    create_divider()

    footer_html = f"""
    <div style="
        background: {Colors.GRAY_50};
        padding: {Spacing.LG};
        border-radius: {Effects.RADIUS_MD};
        margin-top: {Spacing.XL};
        border-top: 2px solid {Colors.GRAY_200};
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="
                    color: {Colors.TEXT_PRIMARY};
                    font-size: {Typography.SIZE_BODY};
                    font-weight: {Typography.WEIGHT_SEMIBOLD};
                    margin-bottom: {Spacing.XS};
                ">
                    🎓 {APP_NAME} {APP_VERSION_FULL}
                </div>
                <div style="
                    color: {Colors.TEXT_SECONDARY};
                    font-size: {Typography.SIZE_BODY_SMALL};
                ">
                    {APP_AUTHOR}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="
                    color: {Colors.TEXT_SECONDARY};
                    font-size: {Typography.SIZE_BODY_SMALL};
                ">
                    <a href="{APP_GITHUB}"
                       style="color: {Colors.PRIMARY}; text-decoration: none; margin-right: {Spacing.MD};">
                        📖 Documentation
                    </a>
                    <a href="{APP_GITHUB}/issues"
                       style="color: {Colors.PRIMARY}; text-decoration: none;">
                        🐛 Support
                    </a>
                </div>
                <div style="
                    color: {Colors.TEXT_DISABLED};
                    font-size: {Typography.SIZE_CAPTION};
                    margin-top: {Spacing.XS};
                ">
                    Propulsé par Streamlit • Design System {APP_VERSION_FULL}
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

    # Fermer le conteneur main pour l'accessibilité
    st.markdown('</main>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
