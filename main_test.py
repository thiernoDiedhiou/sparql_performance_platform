"""
Point d'entrée de test pour la plateforme SPARQL
Version simplifiée pour vérifier l'installation
"""

import streamlit as st
import sys
import os

# Configuration de base
st.set_page_config(
    page_title="Plateforme SPARQL - Test",
    page_icon="📊",
    layout="wide"
)

st.title("🧪 Test d'installation - Plateforme SPARQL")

# Vérification des modules
st.subheader("Vérification des modules")

modules_to_check = [
    'config.settings',
    'core.tester', 
    'queries.catalog',
    'visualization.visualizer',
    'ui.sidebar',
    'utils.helpers'
]

for module in modules_to_check:
    try:
        __import__(module)
        st.success(f"✅ Module {module} importé avec succès")
    except ImportError as e:
        st.error(f"❌ Erreur d'import pour {module}: {str(e)}")
        st.write("💡 Conseil: Vérifiez que tous les fichiers sont créés dans la bonne structure")

st.subheader("Prochaines étapes")
st.info("""
Si tous les modules s'importent correctement:
1. Remplacez ce fichier main.py par le fichier main.py complet
2. Assurez-vous que tous les autres fichiers Python sont en place
3. Lancez l'application avec: streamlit run main.py
""")

st.subheader("Structure attendue")
st.code("""
sparql_performance_platform/
├── main.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── core/
│   ├── __init__.py
│   ├── tester.py
│   ├── executor.py
│   └── metrics.py
├── queries/
│   ├── __init__.py
│   ├── catalog.py
│   ├── lubm_queries.py
│   ├── dbpedia_queries.py
│   └── generic_queries.py
├── visualization/
│   ├── __init__.py
│   └── visualizer.py
├── ui/
│   ├── __init__.py
│   ├── sidebar.py
│   └── tabs/
│       ├── __init__.py
│       ├── configuration_tab.py
│       ├── results_tab.py
│       ├── visualization_tab.py
│       └── export_tab.py
└── utils/
    ├── __init__.py
    ├── data_manager.py
    └── helpers.py
""")
