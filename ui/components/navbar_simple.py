"""
Barre de navigation simple avec streamlit-option-menu
Version facile à implémenter, responsive et accessible
"""

import streamlit as st
from streamlit_option_menu import option_menu

def render_simple_navbar():
    """
    Barre de navigation horizontale avec streamlit-option-menu

    Avantages:
    - Installation simple: pip install streamlit-option-menu
    - Responsive par défaut
    - Icons intégrés
    - Gestion automatique de l'état

    Inconvénients:
    - Moins de contrôle sur le design
    - Dépendance externe
    """

    # Configuration du menu horizontal
    selected = option_menu(
        menu_title=None,  # Pas de titre (le logo sera à gauche)
        options=["Configuration", "Datasets", "Résultats", "Export", "Documentation"],
        icons=["gear", "database", "bar-chart", "download", "book"],  # Bootstrap icons
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {
                "padding": "0!important",
                "background-color": "#1f77b4",  # Bleu professionnel
                "margin": "0",
            },
            "icon": {
                "color": "rgba(255, 255, 255, 0.8)",
                "font-size": "18px"
            },
            "nav-link": {
                "font-size": "14px",
                "font-weight": "500",
                "text-align": "center",
                "margin": "0px",
                "padding": "12px 20px",
                "color": "rgba(255, 255, 255, 0.8)",
                "border-radius": "0px",
                "--hover-color": "rgba(255, 255, 255, 0.1)",
            },
            "nav-link-selected": {
                "background-color": "rgba(255, 255, 255, 0.2)",
                "color": "#ffffff",
                "font-weight": "600",
            },
        }
    )

    return selected


def render_simple_navbar_with_logo():
    """
    Version améliorée avec logo à gauche et bouton Deploy à droite
    """

    # Layout en 3 colonnes
    col_logo, col_menu, col_actions = st.columns([1, 6, 1])

    with col_logo:
        st.markdown("""
        <div style="display: flex; align-items: center; padding: 10px 0;">
            <span style="font-size: 2rem;">⚡</span>
        </div>
        """, unsafe_allow_html=True)

    with col_menu:
        selected = option_menu(
            menu_title=None,
            options=["Configuration & Tests", "Datasets", "Résultats & Analyses", "Export", "Docs"],
            icons=["rocket", "database", "graph-up", "download", "book"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {
                    "padding": "0!important",
                    "background-color": "transparent",
                },
                "icon": {
                    "color": "rgba(255, 255, 255, 0.8)",
                    "font-size": "16px"
                },
                "nav-link": {
                    "font-size": "13px",
                    "font-weight": "500",
                    "text-align": "center",
                    "margin": "0px 4px",
                    "padding": "10px 16px",
                    "color": "rgba(255, 255, 255, 0.8)",
                    "border-radius": "8px",
                    "transition": "all 0.2s",
                },
                "nav-link-selected": {
                    "background-color": "#ffffff",
                    "color": "#1f77b4",
                    "font-weight": "600",
                    "box-shadow": "0 2px 4px rgba(0,0,0,0.1)",
                },
            }
        )

    with col_actions:
        if st.button("Deploy", key="deploy_btn"):
            st.info("Deploy clicked!")

    return selected


# Exemple d'utilisation
if __name__ == "__main__":
    st.set_page_config(
        page_title="SPARQL Performance Platform",
        page_icon="⚡",
        layout="wide"
    )

    # Styling global pour la navbar
    st.markdown("""
    <style>
        /* Supprimer le padding par défaut de Streamlit */
        .main .block-container {
            padding-top: 0rem;
        }

        /* Conteneur navbar avec gradient */
        div[data-testid="stHorizontalBlock"]:first-of-type {
            background: linear-gradient(135deg, #1f77b4 0%, #154360 100%);
            padding: 1rem 2rem;
            margin: -1rem -1rem 2rem -1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
    </style>
    """, unsafe_allow_html=True)

    # Afficher la navbar
    selected_page = render_simple_navbar_with_logo()

    st.markdown("---")

    # Router vers les pages
    if selected_page == "Configuration & Tests":
        st.title("Configuration & Tests")
        st.write("Page de configuration des endpoints SPARQL")

    elif selected_page == "Datasets":
        st.title("Datasets")
        st.write("Gestion des datasets RDF")

    elif selected_page == "Résultats & Analyses":
        st.title("Résultats & Analyses")
        st.write("Visualisation des résultats de benchmarks")

    elif selected_page == "Export":
        st.title("📤 Export")
        st.write("Exportation des données et rapports")

    elif selected_page == "Docs":
        st.title("📖 Documentation")
        st.write("Guide d'utilisation de la plateforme")
