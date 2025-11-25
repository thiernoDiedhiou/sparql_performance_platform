"""
Barre de navigation personnalisée HTML/CSS
Version professionnelle intégrée au design system existant
Respect des normes d'accessibilité (WCAG 2.1 AA)
"""

import streamlit as st
from ui.design_system import Colors, Typography, Spacing, Effects

class CustomNavbar:
    """
    Classe pour gérer la navigation personnalisée
    Intégration complète avec le design system v3.1
    """

    def __init__(self):
        """Initialisation avec les pages disponibles"""
        self.pages = [
            {
                "id": "config",
                "label": "Configuration & Tests",
                "icon": "🚀",
                "description": "Configurer et exécuter les tests SPARQL"
            },
            {
                "id": "datasets",
                "label": "Datasets",
                "icon": "📦",
                "description": "Gérer les datasets RDF"
            },
            {
                "id": "results",
                "label": "Résultats & Analyses",
                "icon": "📊",
                "description": "Visualiser les résultats"
            },
            {
                "id": "export",
                "label": "Export & Sessions",
                "icon": "📤",
                "description": "Exporter les données"
            },
            {
                "id": "docs",
                "label": "Documentation",
                "icon": "📖",
                "description": "Aide et documentation"
            }
        ]

        # Initialiser l'état de navigation
        if 'current_page' not in st.session_state:
            st.session_state['current_page'] = 'config'

    def render(self) -> str:
        """
        Affiche la navbar et retourne la page sélectionnée

        Returns:
            str: ID de la page active
        """

        # CSS complet pour la navbar
        navbar_css = f"""
        <style>
            /* ============================================ */
            /* NAVBAR PROFESSIONNELLE - VERSION CUSTOM     */
            /* ============================================ */

            /* Réinitialiser le padding Streamlit */
            .main .block-container {{
                padding-top: 0rem !important;
                max-width: 100% !important;
            }}

            /* Conteneur principal de la navbar */
            .custom-navbar {{
                position: fixed;
                top: 0;
                left: 250px;  /* Après la sidebar */
                right: 0;
                z-index: 1000;
                background: linear-gradient(135deg, {Colors.PRIMARY} 0%, {Colors.PRIMARY_DARK} 100%);
                box-shadow: {Effects.SHADOW_LG};
                padding: 0;
                margin: 0;
                border-bottom: 2px solid rgba(255, 255, 255, 0.1);
            }}

            /* Ajustement quand sidebar fermée */
            [data-testid="collapsedControl"] ~ section.main .custom-navbar {{
                left: 0px;
            }}

            /* Container intérieur flex */
            .navbar-inner {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 {Spacing.XL};
                height: 70px;
                max-width: 100%;
                margin: 0 auto;
            }}

            /* Logo et titre */
            .navbar-brand {{
                display: flex;
                align-items: center;
                gap: {Spacing.MD};
                flex-shrink: 0;
                padding-right: {Spacing.XL};
            }}

            .navbar-logo {{
                font-size: 2rem;
                line-height: 1;
                filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
            }}

            .navbar-title {{
                display: flex;
                flex-direction: column;
                gap: {Spacing.XS};
            }}

            .navbar-title-main {{
                color: {Colors.TEXT_ON_PRIMARY};
                font-size: {Typography.SIZE_H4};
                font-weight: {Typography.WEIGHT_BOLD};
                margin: 0;
                line-height: 1.2;
                letter-spacing: -0.02em;
            }}

            .navbar-title-sub {{
                color: rgba(255, 255, 255, 0.8);
                font-size: {Typography.SIZE_BODY_SMALL};
                margin: 0;
                line-height: 1;
                font-weight: {Typography.WEIGHT_MEDIUM};
            }}

            /* Menu de navigation */
            .navbar-menu {{
                display: flex;
                align-items: center;
                gap: {Spacing.XS};
                flex: 1;
                justify-content: center;
            }}

            /* Liens de navigation */
            .navbar-link {{
                display: flex;
                align-items: center;
                gap: {Spacing.XS};
                padding: {Spacing.SM} {Spacing.LG};
                border-radius: {Effects.RADIUS_MD};
                background: transparent;
                color: rgba(255, 255, 255, 0.85);
                text-decoration: none;
                font-size: {Typography.SIZE_BODY_SMALL};
                font-weight: {Typography.WEIGHT_MEDIUM};
                transition: all 0.2s ease;
                cursor: pointer;
                border: 2px solid transparent;
                white-space: nowrap;
            }}

            /* Hover sur les liens */
            .navbar-link:hover {{
                background: rgba(255, 255, 255, 0.15);
                color: {Colors.TEXT_ON_PRIMARY};
                transform: translateY(-1px);
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            }}

            /* Focus pour l'accessibilité */
            .navbar-link:focus {{
                outline: 2px solid rgba(255, 255, 255, 0.8);
                outline-offset: 2px;
            }}

            /* Lien actif */
            .navbar-link.active {{
                background: {Colors.BG_CARD};
                color: {Colors.PRIMARY};
                font-weight: {Typography.WEIGHT_SEMIBOLD};
                box-shadow: {Effects.SHADOW_SM};
                border-color: rgba(255, 255, 255, 0.2);
            }}

            .navbar-link.active:hover {{
                background: {Colors.BG_CARD};
                color: {Colors.PRIMARY_DARK};
                transform: none;
            }}

            /* Icône du lien */
            .navbar-link-icon {{
                font-size: 1.1rem;
                line-height: 1;
            }}

            /* Actions à droite */
            .navbar-actions {{
                display: flex;
                align-items: center;
                gap: {Spacing.SM};
                flex-shrink: 0;
                padding-left: {Spacing.XL};
            }}

            /* Bouton d'action */
            .navbar-btn {{
                display: flex;
                align-items: center;
                gap: {Spacing.XS};
                padding: {Spacing.SM} {Spacing.LG};
                background: rgba(255, 255, 255, 0.2);
                color: {Colors.TEXT_ON_PRIMARY};
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: {Effects.RADIUS_MD};
                font-size: {Typography.SIZE_BODY_SMALL};
                font-weight: {Typography.WEIGHT_SEMIBOLD};
                cursor: pointer;
                transition: all 0.2s ease;
                text-decoration: none;
            }}

            .navbar-btn:hover {{
                background: rgba(255, 255, 255, 0.3);
                border-color: rgba(255, 255, 255, 0.5);
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }}

            /* Espaceur pour compenser la navbar fixe */
            .navbar-spacer {{
                height: 90px;
                margin-bottom: {Spacing.MD};
            }}

            /* ============================================ */
            /* RESPONSIVE - MOBILE ET TABLETTE             */
            /* ============================================ */

            /* Tablette (< 1024px) */
            @media (max-width: 1024px) {{
                .navbar-inner {{
                    padding: 0 {Spacing.MD};
                }}

                .navbar-brand {{
                    padding-right: {Spacing.MD};
                }}

                .navbar-title-sub {{
                    display: none;
                }}

                .navbar-link {{
                    padding: {Spacing.SM} {Spacing.MD};
                    font-size: {Typography.SIZE_BODY_SMALL};
                }}

                .navbar-actions {{
                    padding-left: {Spacing.MD};
                }}
            }}

            /* Mobile (< 768px) */
            @media (max-width: 768px) {{
                .navbar-inner {{
                    flex-direction: column;
                    height: auto;
                    padding: {Spacing.MD};
                }}

                .navbar-menu {{
                    flex-direction: column;
                    width: 100%;
                    gap: {Spacing.XS};
                }}

                .navbar-link {{
                    width: 100%;
                    justify-content: flex-start;
                }}

                .navbar-actions {{
                    width: 100%;
                    justify-content: center;
                    padding-left: 0;
                    margin-top: {Spacing.SM};
                }}

                .navbar-spacer {{
                    height: auto;
                }}
            }}

            /* ============================================ */
            /* ACCESSIBILITÉ                               */
            /* ============================================ */

            /* Skip link (invisible mais accessible) */
            .skip-link {{
                position: absolute;
                top: -40px;
                left: 0;
                background: {Colors.PRIMARY};
                color: {Colors.TEXT_ON_PRIMARY};
                padding: {Spacing.SM} {Spacing.MD};
                text-decoration: none;
                border-radius: {Effects.RADIUS_MD};
                z-index: 1001;
            }}

            .skip-link:focus {{
                top: 10px;
                left: 10px;
            }}

            /* Indicateur visuel pour keyboard navigation */
            *:focus-visible {{
                outline: 2px solid rgba(255, 255, 255, 0.8);
                outline-offset: 2px;
            }}
        </style>
        """

        st.markdown(navbar_css, unsafe_allow_html=True)

        # Construction du HTML de la navbar
        navbar_html = self._build_navbar_html()

        # Afficher la navbar
        st.markdown(navbar_html, unsafe_allow_html=True)

        # Espaceur
        st.markdown('<div class="navbar-spacer"></div>', unsafe_allow_html=True)

        # Retourner la page active
        return st.session_state['current_page']

    def _build_navbar_html(self) -> str:
        """Construit le HTML de la navbar"""

        current_page = st.session_state['current_page']

        # Skip link pour accessibilité
        skip_link = '<a href="#main-content" class="skip-link">Aller au contenu principal</a>'

        # Logo et titre
        brand_html = f"""
        <div class="navbar-brand">
            <div class="navbar-logo" role="img" aria-label="Logo SPARQL Performance">⚡</div>
            <div class="navbar-title">
                <div class="navbar-title-main">SPARQL Performance Platform</div>
                <div class="navbar-title-sub">Benchmarking professionnel • v3.1</div>
            </div>
        </div>
        """

        # Menu de navigation
        menu_items = []
        for page in self.pages:
            active_class = "active" if page['id'] == current_page else ""
            aria_current = 'aria-current="page"' if page['id'] == current_page else ""

            menu_items.append(f"""
            <a href="?page={page['id']}"
               class="navbar-link {active_class}"
               role="menuitem"
               {aria_current}
               title="{page['description']}"
               onclick="return false;">
                <span class="navbar-link-icon">{page['icon']}</span>
                <span>{page['label']}</span>
            </a>
            """)

        menu_html = f"""
        <nav class="navbar-menu" role="menubar" aria-label="Navigation principale">
            {''.join(menu_items)}
        </nav>
        """

        # Actions (boutons à droite)
        actions_html = f"""
        <div class="navbar-actions">
            <a href="#deploy" class="navbar-btn" role="button" aria-label="Déployer l'application">
                🚀 Deploy
            </a>
        </div>
        """

        # Navbar complète
        full_navbar = f"""
        {skip_link}
        <header class="custom-navbar" role="banner">
            <div class="navbar-inner">
                {brand_html}
                {menu_html}
                {actions_html}
            </div>
        </header>
        """

        return full_navbar

    def set_page(self, page_id: str):
        """Change la page active"""
        if any(p['id'] == page_id for p in self.pages):
            st.session_state['current_page'] = page_id


def render_custom_navbar() -> str:
    """
    Fonction utilitaire pour afficher la navbar custom

    Returns:
        str: ID de la page active

    Exemple d'utilisation:
        current_page = render_custom_navbar()

        if current_page == 'config':
            # Afficher la page de configuration
            pass
    """
    navbar = CustomNavbar()
    return navbar.render()


# ============================================================================
# EXEMPLE D'UTILISATION COMPLÈTE
# ============================================================================

if __name__ == "__main__":
    st.set_page_config(
        page_title="SPARQL Performance Platform",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Afficher la navbar
    current_page = render_custom_navbar()

    # Conteneur principal avec ID pour accessibilité
    st.markdown('<main id="main-content" role="main">', unsafe_allow_html=True)

    # Router vers les pages
    if current_page == "config":
        st.title("Configuration & Tests")
        st.caption("Configurez les endpoints SPARQL et lancez les benchmarks")

        with st.expander("📝 Exemple de configuration"):
            st.code("""
            endpoint_virtuoso = "http://localhost:8890/sparql"
            endpoint_fuseki = "http://localhost:3030/dataset/query"
            """, language="python")

    elif current_page == "datasets":
        st.title("Datasets")
        st.caption("Gestion des datasets RDF pour les tests")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Datasets chargés", "5", "+2")
        with col2:
            st.metric("Triples totaux", "1.2M", "+100K")
        with col3:
            st.metric("Taille totale", "256 MB", "+50 MB")

    elif current_page == "results":
        st.title("Résultats & Analyses")
        st.caption("Visualisation des résultats de benchmarks")

        # Exemple de graphique
        import pandas as pd
        import plotly.express as px

        df = pd.DataFrame({
            'Engine': ['Virtuoso', 'Fuseki', 'Virtuoso', 'Fuseki'],
            'Query': ['Q1', 'Q1', 'Q2', 'Q2'],
            'Time (ms)': [12.5, 18.3, 25.7, 32.1]
        })

        fig = px.bar(df, x='Query', y='Time (ms)', color='Engine', barmode='group',
                     title="Temps d'exécution par requête")
        st.plotly_chart(fig, use_container_width=True)

    elif current_page == "export":
        st.title("📤 Export & Sessions")
        st.caption("Exportation des données et gestion des sessions")

        col1, col2 = st.columns(2)
        with col1:
            st.button("📥 Exporter en JSON", use_container_width=True)
            st.button("Exporter en CSV", use_container_width=True)
        with col2:
            st.button("💾 Sauvegarder la session", use_container_width=True)
            st.button("📂 Charger une session", use_container_width=True)

    elif current_page == "docs":
        st.title("📖 Documentation")
        st.caption("Guide d'utilisation de la plateforme")

        st.markdown("""
        ### Démarrage Rapide

        1. **Configurer les endpoints** dans l'onglet Configuration
        2. **Charger des datasets** dans l'onglet Datasets
        3. **Lancer les tests** et consulter les résultats
        4. **Exporter** vos analyses

        ### 📚 Ressources

        - [Guide complet](https://example.com)
        - [API Reference](https://example.com)
        - [Exemples de requêtes](https://example.com)
        """)

    st.markdown('</main>', unsafe_allow_html=True)
