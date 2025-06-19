"""
Version de débogage du main.py pour identifier les modules manquants
"""

import streamlit as st

def test_imports():
    """Teste les imports un par un"""
    
    st.title("🔍 Test des imports - Débogage")
    
    imports_to_test = [
        ("config.settings", "configure_page"),
        ("ui.sidebar", "render_sidebar"),
        ("ui.tabs.configuration_tab", "render_configuration_tab"),
        ("ui.tabs.results_tab", "render_results_tab"),
        ("ui.tabs.visualization_tab", "render_visualization_tab"),
        ("ui.tabs.export_tab", "render_export_tab"),
        ("utils.data_manager", "initialize_session_state"),
    ]
    
    success_count = 0
    
    for module_name, function_name in imports_to_test:
        try:
            module = __import__(module_name, fromlist=[function_name])
            getattr(module, function_name)
            st.success(f"✅ {module_name}.{function_name} - OK")
            success_count += 1
        except ImportError as e:
            st.error(f"❌ Erreur d'import pour {module_name}: {str(e)}")
        except AttributeError as e:
            st.warning(f"⚠️ Module {module_name} trouvé mais fonction {function_name} manquante: {str(e)}")
        except Exception as e:
            st.error(f"❌ Erreur inattendue pour {module_name}: {str(e)}")
    
    st.write(f"**Résultat: {success_count}/{len(imports_to_test)} modules OK**")
    
    if success_count == len(imports_to_test):
        st.success("🎉 Tous les modules sont prêts ! Vous pouvez utiliser le main.py complet.")
    else:
        st.warning("⚠️ Certains modules sont manquants. Créez-les avant d'utiliser main.py")
        
        st.subheader("📝 Modules à créer en priorité:")
        
        # Liste des fichiers à créer
        files_to_create = {
            "ui.sidebar": "ui/sidebar.py",
            "ui.tabs.configuration_tab": "ui/tabs/configuration_tab.py", 
            "ui.tabs.results_tab": "ui/tabs/results_tab.py",
            "ui.tabs.visualization_tab": "ui/tabs/visualization_tab.py",
            "ui.tabs.export_tab": "ui/tabs/export_tab.py",
            "utils.data_manager": "utils/data_manager.py",
            "utils.helpers": "utils/helpers.py",
            "core.tester": "core/tester.py",
            "core.executor": "core/executor.py",
            "core.metrics": "core/metrics.py",
            "queries.catalog": "queries/catalog.py",
            "queries.generic_queries": "queries/generic_queries.py",
            "queries.lubm_queries": "queries/lubm_queries.py",
            "queries.dbpedia_queries": "queries/dbpedia_queries.py",
            "visualization.visualizer": "visualization/visualizer.py",
            "ui.components.connectivity_checker": "ui/components/connectivity_checker.py",
            "ui.components.system_info": "ui/components/system_info.py"
        }
        
        for module, filepath in files_to_create.items():
            st.write(f"- `{filepath}` pour le module `{module}`")

def main():
    """Fonction principale de débogage"""
    
    # Configuration de base
    st.set_page_config(
        page_title="SPARQL Platform - Debug",
        page_icon="🔍",
        layout="wide"
    )
    
    # Test des imports
    test_imports()
    
    st.subheader("📋 Instructions")
    st.info("""
    **Prochaines étapes:**
    
    1. **Si tous les modules sont OK:** Remplacez ce fichier par le main.py complet
    2. **Si des modules manquent:** Créez les fichiers indiqués ci-dessus
    3. **Ordre recommandé de création:**
       - utils/helpers.py (fonctions utilitaires)
       - core/metrics.py (métriques système)
       - core/executor.py (exécution requêtes)
       - core/tester.py (testeur principal)
       - queries/ (tous les fichiers de requêtes)
       - visualization/visualizer.py
       - ui/components/ (composants UI)
       - utils/data_manager.py
       - ui/tabs/ (tous les onglets)
       - ui/sidebar.py
    
    4. **Tester à chaque étape** avec cette page de débogage
    """)
    
    # Informations sur la structure attendue
    with st.expander("📁 Structure de fichiers attendue"):
        st.code("""
sparql_performance_platform/
├── main.py (ou main_debug.py temporairement)
├── requirements.txt
├── config/
│   ├── __init__.py ✅
│   └── settings.py ✅
├── core/
│   ├── __init__.py ✅
│   ├── tester.py ❓
│   ├── executor.py ❓
│   └── metrics.py ❓
├── queries/
│   ├── __init__.py ✅
│   ├── catalog.py ❓
│   ├── lubm_queries.py ❓
│   ├── dbpedia_queries.py ❓
│   └── generic_queries.py ❓
├── visualization/
│   ├── __init__.py ✅
│   └── visualizer.py ❓
├── ui/
│   ├── __init__.py ✅
│   ├── sidebar.py ❓
│   ├── tabs/
│   │   ├── __init__.py ✅
│   │   ├── configuration_tab.py ❓
│   │   ├── results_tab.py ❓
│   │   ├── visualization_tab.py ❓
│   │   └── export_tab.py ❓
│   └── components/
│       ├── __init__.py ✅
│       ├── connectivity_checker.py ❓
│       └── system_info.py ❓
└── utils/
    ├── __init__.py ✅
    ├── data_manager.py ❓
    └── helpers.py ❓

Légende: ✅ = Créé, ❓ = À créer
        """)

if __name__ == "__main__":
    main()