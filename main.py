"""
Point d'entrée principal de la plateforme d'évaluation SPARQL
"""

import streamlit as st

def main():
    """Fonction principale de l'application Streamlit"""
    
    # Configuration de la page (doit être en premier)
    try:
        from config.settings import configure_page
        configure_page()
    except ImportError:
        st.set_page_config(
            page_title="Comparaison des performances de requêtes SPARQL",
            page_icon="📊",
            layout="wide"
        )
    
    # Initialisation de l'état de session
    try:
        from utils.data_manager import initialize_session_state
        initialize_session_state()
    except ImportError:
        if 'initialized' not in st.session_state:
            st.session_state['initialized'] = True
    
    # Titre principal
    st.title("Plateforme d'évaluation de performance des moteurs SPARQL")
    st.markdown("### Étude comparative entre Virtuoso et Jena Fuseki")
    
    # Interface de la barre latérale
    try:
        from ui.sidebar import render_sidebar
        sidebar_config = render_sidebar()
    except ImportError as e:
        st.error(f"Erreur lors du chargement de la barre latérale: {str(e)}")
        sidebar_config = {}
    
    # Onglets principaux
    tabs = st.tabs(["Configuration et tests", "Résultats", "Visualisation", "Exportation"])
    
    # Onglet Configuration
    with tabs[0]:
        try:
            from ui.tabs.configuration_tab import render_configuration_tab
            render_configuration_tab(sidebar_config)
        except ImportError as e:
            st.error(f"Erreur lors du chargement de l'onglet Configuration: {str(e)}")
            st.info("Module configuration_tab non disponible")
    
    # Onglet Résultats
    with tabs[1]:
        try:
            from ui.tabs.results_tab import render_results_tab
            render_results_tab()
        except ImportError as e:
            st.error(f"Erreur lors du chargement de l'onglet Résultats: {str(e)}")
            st.info("Module results_tab non disponible")
    
    # Onglet Visualisation
    with tabs[2]:
        try:
            from ui.tabs.visualization_tab import render_visualization_tab
            render_visualization_tab()
        except ImportError as e:
            st.error(f"Erreur lors du chargement de l'onglet Visualisation: {str(e)}")
            st.info("Module visualization_tab non disponible")
    
    # Onglet Exportation
    with tabs[3]:
        try:
            from ui.tabs.export_tab import render_export_tab
            render_export_tab()
        except ImportError as e:
            st.error(f"Erreur lors du chargement de l'onglet Exportation: {str(e)}")
            st.info("Module export_tab non disponible")
    
    # Pied de page
    st.markdown("---")
    st.markdown(
        "Application développée pour l'évaluation des performances de requêtes SPARQL "
        "dans le cadre d'un mémoire de Master 2 en Informatique - Génie Logiciel."
    )

if __name__ == "__main__":
    main()