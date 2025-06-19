#!/usr/bin/env python3
"""
Script de configuration automatique pour la plateforme SPARQL
Crée la structure de dossiers et les fichiers nécessaires
"""

import os
import sys
from pathlib import Path

def create_directory_structure():
    """Crée la structure de dossiers nécessaire"""
    
    # Structure des dossiers à créer
    directories = [
        "config",
        "core", 
        "queries",
        "visualization",
        "ui",
        "ui/tabs",
        "ui/components",
        "utils",
        "tests"
    ]
    
    print("Création de la structure de dossiers...")
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Dossier créé: {directory}")
    
    print("✅ Structure de dossiers créée avec succès!")

def create_init_files():
    """Crée les fichiers __init__.py nécessaires"""
    
    init_files = [
        "config/__init__.py",
        "core/__init__.py", 
        "queries/__init__.py",
        "visualization/__init__.py",
        "ui/__init__.py",
        "ui/tabs/__init__.py",
        "ui/components/__init__.py",
        "utils/__init__.py",
        "tests/__init__.py"
    ]
    
    print("\nCréation des fichiers __init__.py...")
    
    for init_file in init_files:
        with open(init_file, 'w', encoding='utf-8') as f:
            module_name = init_file.split('/')[0]
            f.write(f'"""Module {module_name} de la plateforme SPARQL."""\n')
        print(f"✓ Fichier créé: {init_file}")
    
    print("✅ Fichiers __init__.py créés avec succès!")

def check_dependencies():
    """Vérifie que les dépendances nécessaires sont installées"""
    
    required_packages = [
        'streamlit',
        'pandas', 
        'plotly',
        'SPARQLWrapper',
        'psutil',
        'requests'
    ]
    
    print("\nVérification des dépendances...")
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} installé")
        except ImportError:
            print(f"❌ {package} manquant")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Packages manquants: {', '.join(missing_packages)}")
        print("Installez-les avec: pip install " + " ".join(missing_packages))
        return False
    else:
        print("✅ Toutes les dépendances sont installées!")
        return True

def create_sample_config():
    """Crée un fichier de configuration d'exemple"""
    
    config_content = '''"""
Configuration d'exemple pour la plateforme SPARQL
"""

# Endpoints par défaut
DEFAULT_VIRTUOSO_ENDPOINT = "http://localhost:8890/sparql"
DEFAULT_FUSEKI_ENDPOINT = "http://localhost:3030/dataset/query"

# Paramètres de test par défaut
DEFAULT_NUM_ITERATIONS = 5
DEFAULT_WARMUP_ITERATIONS = 2
DEFAULT_CONCURRENT_QUERIES = 1

# Jeux de données disponibles
AVAILABLE_DATASETS = ["LUBM", "BSBM", "DBpedia", "YAGO", "Personnalisé"]

# Configuration de timeout
QUERY_TIMEOUT = 60
CONNECTIVITY_TIMEOUT = 5
'''
    
    with open('config/settings.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✓ Fichier de configuration créé: config/settings.py")

def create_sample_main():
    """Crée un fichier main.py minimal pour tester"""
    
    main_content = '''"""
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
'''
    
    with open('main_test.py', 'w', encoding='utf-8') as f:
        f.write(main_content)
    
    print("✓ Fichier de test créé: main_test.py")

def main():
    """Fonction principale de configuration"""
    
    print("🚀 Configuration de la plateforme d'évaluation SPARQL")
    print("=" * 60)
    
    # Créer la structure
    create_directory_structure()
    create_init_files() 
    create_sample_config()
    create_sample_main()
    
    # Vérifier les dépendances
    deps_ok = check_dependencies()
    
    print("\n" + "=" * 60)
    print("📋 Résumé de l'installation")
    print("=" * 60)
    
    if deps_ok:
        print("✅ Configuration terminée avec succès!")
        print("\n📖 Prochaines étapes:")
        print("1. Testez l'installation: streamlit run main_test.py")
        print("2. Si le test fonctionne, ajoutez tous les autres fichiers Python")
        print("3. Remplacez main_test.py par le vrai main.py")
        print("4. Lancez l'application: streamlit run main.py")
    else:
        print("⚠️ Installation incomplète!")
        print("Installez d'abord les dépendances manquantes avec pip")
    
    print("\n🔗 Structure créée dans le dossier actuel:")
    print(f"   {os.getcwd()}")

if __name__ == "__main__":
    main()