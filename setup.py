"""
Script d'installation automatique - Plateforme d'Évaluation SPARQL
Version 3.2.2 | Master 2 Informatique - Génie Logiciel

Ce script automatise l'installation complète de la plateforme :
- Vérification des prérequis système
- Création de la structure de dossiers
- Installation des dépendances Python
- Configuration des paramètres par défaut
- Vérification des endpoints SPARQL (optionnel)
- Tests de connectivité

Usage:
    python setup.py              # Installation standard
    python setup.py --verify     # Vérification uniquement
    python setup.py --full       # Installation + vérification endpoints
"""

import sys
import os
import subprocess
import platform
import shutil
from pathlib import Path

# Couleurs pour l'affichage terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(message):
    """Affiche un en-tête formaté"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_success(message):
    """Affiche un message de succès"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """Affiche un message d'erreur"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_warning(message):
    """Affiche un avertissement"""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_info(message):
    """Affiche une information"""
    print(f"{Colors.OKBLUE}ℹ {message}{Colors.ENDC}")

def check_python_version():
    """Vérifie la version de Python"""
    print_info("Vérification de la version Python...")
    version = sys.version_info

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8+ requis. Version actuelle: {version.major}.{version.minor}.{version.micro}")
        print_info("Téléchargez Python depuis https://www.python.org/downloads/")
        return False

    print_success(f"Python {version.major}.{version.minor}.{version.micro} détecté")
    return True

def check_pip():
    """Vérifie que pip est installé"""
    print_info("Vérification de pip...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"],
                              capture_output=True, text=True, check=True)
        print_success(f"pip installé: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print_error("pip n'est pas installé ou inaccessible")
        return False

def check_git():
    """Vérifie que git est installé (optionnel)"""
    print_info("Vérification de git (optionnel)...")
    try:
        result = subprocess.run(["git", "--version"],
                              capture_output=True, text=True, check=True)
        print_success(f"git installé: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_warning("git non détecté (optionnel pour mise à jour)")
        return False

def create_directory_structure():
    """Crée la structure de dossiers du projet"""
    print_info("Création de la structure de dossiers...")

    directories = [
        "config",
        "core",
        "queries",
        "visualization",
        "ui",
        "ui/tabs",
        "ui/components",
        "utils",
        "tests",
        "images/images_memoire",
        "datasets"
    ]

    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print_success(f"Dossier créé: {directory}")
        else:
            print_info(f"Dossier existant: {directory}")

    return True

def create_init_files():
    """Crée les fichiers __init__.py pour les packages Python"""
    print_info("Création des fichiers __init__.py...")

    packages = [
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

    for package in packages:
        init_file = Path(package) / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            print_success(f"Créé: {init_file}")
        else:
            print_info(f"Existant: {init_file}")

    return True

def create_requirements_txt():
    """Crée le fichier requirements.txt avec les dépendances"""
    print_info("Création de requirements.txt...")

    requirements = """streamlit==1.28.0
pandas==2.1.0
numpy==1.24.3
plotly==5.17.0
SPARQLWrapper==2.0.0
psutil==5.9.5
requests==2.31.0
openpyxl==3.1.2
Pillow==10.0.0
"""

    req_file = Path("requirements.txt")
    if not req_file.exists():
        req_file.write_text(requirements)
        print_success("requirements.txt créé")
    else:
        print_info("requirements.txt existant (non écrasé)")

    return True

def install_dependencies():
    """Installe les dépendances Python"""
    print_info("Installation des dépendances Python...")
    print_warning("Cela peut prendre plusieurs minutes...")

    try:
        # Mise à jour de pip
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                      check=True, capture_output=True)
        print_success("pip mis à jour")

        # Installation des dépendances
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                      check=True, capture_output=True)
        print_success("Toutes les dépendances installées avec succès")
        return True

    except subprocess.CalledProcessError as e:
        print_error(f"Erreur lors de l'installation des dépendances: {e}")
        return False

def create_config_file():
    """Crée le fichier de configuration par défaut"""
    print_info("Création du fichier config/settings.py...")

    config_content = '''"""Configuration de la plateforme SPARQL"""

# Endpoints SPARQL
DEFAULT_VIRTUOSO_ENDPOINT = "http://localhost:8890/sparql"
DEFAULT_FUSEKI_ENDPOINT = "http://localhost:3030/dataset/query"

# Paramètres de test
DEFAULT_NUM_ITERATIONS = 20
DEFAULT_WARMUP_ITERATIONS = 2
DEFAULT_CONCURRENT_QUERIES = 5

# Datasets disponibles
AVAILABLE_DATASETS = ["LUBM", "BSBM", "DBpedia", "YAGO", "Personnalisé"]

# Timeouts (en secondes)
QUERY_TIMEOUT = 60
CONNECTIVITY_TIMEOUT = 5

# Monitoring système
ENABLE_CPU_MONITORING = True
ENABLE_MEMORY_MONITORING = True
METRICS_INTERVAL = 0.1  # secondes

# Export
DEFAULT_EXPORT_FORMAT = "csv"
EXPORT_FORMATS = ["csv", "json", "excel"]

# Interface utilisateur
APP_TITLE = "Plateforme d'Évaluation SPARQL"
APP_VERSION = "3.2.2"
APP_AUTHOR = "Master 2 Informatique - Génie Logiciel"

# Chemins
RESULTS_DIR = "results"
IMAGES_DIR = "images/images_memoire"
DATASETS_DIR = "datasets"
'''

    config_file = Path("config/settings.py")
    if not config_file.exists():
        config_file.write_text(config_content)
        print_success("config/settings.py créé")
    else:
        print_info("config/settings.py existant (non écrasé)")

    return True

def verify_installation():
    """Vérifie que tous les modules requis sont importables"""
    print_info("Vérification de l'installation des modules Python...")

    required_modules = [
        "streamlit",
        "pandas",
        "numpy",
        "plotly",
        "SPARQLWrapper",
        "psutil",
        "requests",
        "openpyxl",
        "PIL"
    ]

    all_ok = True
    for module in required_modules:
        try:
            __import__(module)
            print_success(f"{module} importé avec succès")
        except ImportError:
            print_error(f"Échec de l'import de {module}")
            all_ok = False

    return all_ok

def check_docker():
    """Vérifie si Docker est installé (pour les moteurs SPARQL)"""
    print_info("Vérification de Docker (optionnel)...")
    try:
        result = subprocess.run(["docker", "--version"],
                              capture_output=True, text=True, check=True)
        print_success(f"Docker installé: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_warning("Docker non détecté (requis pour Virtuoso/Fuseki via Docker)")
        return False

def check_sparql_endpoints(check_full=False):
    """Vérifie la connectivité aux endpoints SPARQL"""
    if not check_full:
        print_info("Vérification des endpoints SPARQL ignorée (utilisez --full pour activer)")
        return True

    print_info("Vérification de la connectivité aux endpoints SPARQL...")

    try:
        import requests

        endpoints = {
            "Virtuoso": "http://localhost:8890/sparql",
            "Fuseki": "http://localhost:3030/dataset/query"
        }

        for name, url in endpoints.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code in [200, 400]:  # 400 est OK pour SPARQL sans query
                    print_success(f"{name} accessible sur {url}")
                else:
                    print_warning(f"{name} répond avec code {response.status_code}")
            except requests.exceptions.RequestException:
                print_warning(f"{name} non accessible sur {url} (moteur peut-être arrêté)")

        return True

    except ImportError:
        print_error("Module requests non installé")
        return False

def set_encoding_windows():
    """Configure l'encodage UTF-8 pour Windows"""
    if platform.system() == "Windows":
        print_info("Configuration de l'encodage UTF-8 pour Windows...")
        try:
            os.environ['PYTHONIOENCODING'] = 'utf-8'
            print_success("Encodage UTF-8 configuré")
            print_info("Pour rendre permanent, ajoutez cette variable d'environnement système")
            return True
        except Exception as e:
            print_warning(f"Impossible de configurer l'encodage: {e}")
            return False
    return True

def display_system_info():
    """Affiche les informations système"""
    print_info("Informations système:")
    print(f"  - OS: {platform.system()} {platform.release()}")
    print(f"  - Architecture: {platform.machine()}")
    print(f"  - Python: {sys.version.split()[0]}")
    print(f"  - Répertoire de travail: {os.getcwd()}")

def display_next_steps():
    """Affiche les prochaines étapes"""
    print_header("Installation terminée avec succès!")

    print(f"{Colors.BOLD}Prochaines étapes:{Colors.ENDC}\n")

    print("1. Configurer les endpoints SPARQL:")
    print(f"   - Éditez {Colors.OKCYAN}config/settings.py{Colors.ENDC}")
    print("   - Démarrez Virtuoso: docker run -d --name virtuoso -p 8890:8890 openlink/virtuoso-opensource-7")
    print("   - Démarrez Fuseki: docker run -d --name fuseki -p 3030:3030 stain/jena-fuseki")

    print("\n2. Charger un dataset LUBM:")
    print("   - Suivez les instructions dans INSTALLATION.md section 'Configuration des moteurs SPARQL'")

    print("\n3. Lancer l'application:")
    print(f"   {Colors.OKCYAN}streamlit run main.py{Colors.ENDC}")

    print("\n4. Scripts d'extraction (si nécessaire):")
    print("   - Statistiques: python _archive/_test/extract_stats_simple.py")

    print("\n5. Documentation:")
    print("   - Guide d'installation: INSTALLATION.md")
    print("   - Vue d'ensemble: README.md")
    print("   - Métriques disponibles: _archive/STATISTIQUES_DISPONIBLES.md")
    print("   - Méthodes statistiques: _archive/METHODES_STATISTIQUES.md")

    print(f"\n{Colors.OKGREEN}Pour toute question, consultez la documentation ou ouvrez une issue sur GitHub.{Colors.ENDC}\n")

def main():
    """Fonction principale d'installation"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Installation automatique de la plateforme SPARQL"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Vérifier l'installation existante uniquement"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Installation complète + vérification des endpoints SPARQL"
    )

    args = parser.parse_args()

    print_header("Configuration de la plateforme d'évaluation SPARQL")
    print_info(f"Version 3.2.2 | Master 2 Informatique - Génie Logiciel")

    display_system_info()

    # Mode vérification uniquement
    if args.verify:
        print_header("Mode vérification")
        success = (
            check_python_version() and
            check_pip() and
            verify_installation() and
            check_sparql_endpoints(check_full=True)
        )

        if success:
            print_success("\n✓ Toutes les vérifications sont passées!")
            return 0
        else:
            print_error("\n✗ Certaines vérifications ont échoué")
            return 1

    # Installation complète
    print_header("Démarrage de l'installation")

    steps = [
        ("Vérification Python", check_python_version),
        ("Vérification pip", check_pip),
        ("Vérification git", check_git),
        ("Structure de dossiers", create_directory_structure),
        ("Fichiers __init__.py", create_init_files),
        ("Fichier requirements.txt", create_requirements_txt),
        ("Installation dépendances", install_dependencies),
        ("Fichier de configuration", create_config_file),
        ("Vérification imports", verify_installation),
        ("Configuration encodage", set_encoding_windows),
        ("Vérification Docker", check_docker),
    ]

    # Ajouter la vérification des endpoints si --full
    if args.full:
        steps.append(("Vérification endpoints SPARQL", lambda: check_sparql_endpoints(True)))

    failed_steps = []

    for step_name, step_func in steps:
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print_error(f"Erreur lors de '{step_name}': {e}")
            failed_steps.append(step_name)

    # Résumé
    if failed_steps:
        print_header("Installation terminée avec avertissements")
        print_warning("Étapes avec problèmes:")
        for step in failed_steps:
            print(f"  - {step}")
        print_info("\nL'application peut toujours fonctionner. Consultez INSTALLATION.md pour le dépannage.")
        return 1
    else:
        display_next_steps()
        return 0

if __name__ == "__main__":
    sys.exit(main())
