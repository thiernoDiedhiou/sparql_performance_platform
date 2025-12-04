# Platforme Test Performance Moteur SPARQL

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.31+-red.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/tests-103%20tests%20%7C%2096%25%20pass-success.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-52%25-yellow.svg)](tests/)
[![License](https://img.shields.io/badge/license-Academic-orange.svg)](LICENSE)

Une plateforme professionnelle d'évaluation comparative des performances des moteurs SPARQL, conçue pour comparer **Virtuoso** et **Jena Fuseki**.

---

## Table des matières

- [Fonctionnalités principales](#-fonctionnalités-principales)
- [Architecture](#-architecture)
- [Installation rapide](#-installation-rapide)
- [Utilisation](#-utilisation)
- [Tests et qualité](#-tests-et-qualité)
- [Configuration avancée](#-configuration-avancée)
- [Documentation complète](#-documentation-complète)
- [Support et contribution](#-support-et-contribution)

---

## Fonctionnalités principales

### Tests de performance automatisés

- Exécution automatique de requêtes SPARQL avec mesures détaillées
- **Dashboard temps réel** avec barres de progression et ETA
- Support multi-moteurs (Virtuoso, Jena Fuseki, et autres endpoints SPARQL)
- Itérations d'échauffement pour des mesures précises
- Gestion robuste des erreurs avec retry automatique

### Métriques scientifiques avancées

- **Temps d'exécution** : P50, P75, P90, P95, P99 (percentiles)
- **CPU** : Monitoring par cœur avec détection de l'hyperthreading
- **Mémoire** : RSS, VMS, disponibilité système
- **Disque I/O** : Octets lus/écrits pendant l'exécution
- **Réseau I/O** : Trafic réseau généré par les requêtes
- **Fiabilité** : Taux de succès, classification des erreurs

### Synchronisation optimisée

- **Exportation par chunks** : Support pour 100K+
- Barres de progression par chunk avec estimation de temps
- Retry automatique par chunk en cas d'erreur
- Validation des données exportées

### 🆕 Gestion  des datasets

- **Chargement intelligent** : Validation automatique et estimation des ressources
- **Persistance des métadonnées** : Sauvegarde dans `datasets_metadata.json`
- **Mise à jour automatique** : Fichier `.env` mis à jour après chaque chargement
- **Suppression sélective** : Nettoyage par moteur ou global
- **Statistiques détaillées** : Vue d'ensemble des datasets chargés par moteur
- **Interface intuitive** : Gestion complète via Streamlit

### Infrastructure production-ready

- **Docker Compose** : Déploiement one-click de Virtuoso + Fuseki + Streamlit
- **Logging professionnel** : Rotation automatique (10MB, 5 backups)
- **Configuration .env** : 38 variables pour personnalisation complète
- **Validation pré-vol** : Vérification endpoints, configuration, permissions
- **Tests unitaires** : 103 tests avec 96% de réussite

### Visualisations interactives

- Graphiques dynamiques avec Plotly
- Comparaisons multi-moteurs
- Heatmaps de performance
- Export vers CSV, Excel, JSON avec rapports détaillés

---

#### Tests unitaires complets

```bash

```

**Exécution :**

```bash
# Tous les tests
pytest tests/

# Tests avec couverture
pytest tests/ --cov=. --cov-report=html

# Tests par catégorie
pytest tests/ -m "unit"
pytest tests/ -m "integration"
```

#### Logging professionnel

```python
from utils.logging_config import setup_logging, log_query, log_sync

# Configuration automatique
logger = setup_logging(
    log_dir="logs",
    log_file="sparql_platform.log",
    log_level="INFO",
    max_bytes=10*1024*1024,  # 10MB
    backup_count=5
)

# Logging spécialisé
log_query(query_name="Q1", engine="Virtuoso", duration=1.23, success=True)
log_sync(operation="export", records=50000, duration=5.67, status="success")

# Context manager pour timing automatique
with log_performance_context("Data export"):
    export_data()  # Timing automatique
```

**Fonctionnalités :**

- Rotation automatique à 10MB
- 5 fichiers de backup conservés
- Console colorée (DEBUG=bleu, INFO=vert, WARNING=jaune, ERROR=rouge)
- Formats structurés pour analyse

#### Docker Compose

```bash
# Démarrage complet (Virtuoso + Fuseki + Streamlit)
docker-compose up -d

# Vérification santé
docker-compose ps

# Logs en temps réel
docker-compose logs -f streamlit_app

# Arrêt propre
docker-compose down
```

**Services orchestrés :**

- **Virtuoso** : Port 8890 (SPARQL) + 1111 (ISQL)
- **Jena Fuseki** : Port 3030 (UI + SPARQL)
- **Streamlit** : Port 8501 (Interface web)

**Health checks :**

- Vérification automatique toutes les 30s
- Retry x3 avant échec
- Démarrage séquentiel avec dépendances

#### Synchronisation par chunks

```python
from utils.data_synchronizer_v2 import DataSynchronizerV2

sync = DataSynchronizerV2(
    virtuoso_endpoint="http://localhost:8890/sparql",
    fuseki_endpoint="http://localhost:3030/dataset/data",
    chunk_size=100000,  # 100K triplets par chunk
    max_triplets=1000000  # Limite totale
)

# Export avec progression
progress_bar = st.progress(0)
status_text = st.empty()

def progress_callback(current, total, message):
    progress = current / total
    progress_bar.progress(progress)
    status_text.text(f"{message} ({current}/{total})")

success = sync.synchronize_data(progress_callback=progress_callback)
```

**Avantages :**

- Support pour **10M+ triplets** (vs 500K avant)
- Pas de timeout sur les gros volumes
- Progression granulaire par chunk
- Retry automatique par chunk

#### Métriques avancées

```python
from core.advanced_metrics import AdvancedMetricsCollector

collector = AdvancedMetricsCollector()

# Calcul des percentiles
percentiles = collector.calculate_percentiles(
    values=[1.2, 1.5, 2.1, 3.4, 5.6],
    percentiles=[50, 75, 90, 95, 99]
)
# Résultat: P50=2.1, P95=5.31, P99=5.55

# Monitoring CPU par cœur
cpu_metrics = collector.collect_cpu_metrics()
# {
#     "total_cores": 8,
#     "physical_cores": 4,
#     "hyperthreading": True,
#     "per_core_usage": [45.2, 67.8, 23.1, ...],
#     "frequencies": {"current": 2400, "min": 800, "max": 3600}
# }

# Rapport de performance complet
report = collector.generate_performance_report(
    engine="Virtuoso",
    execution_times=[1.2, 1.5, 2.1],
    cpu_usage=[45.2, 67.8, 23.1],
    memory_mb=[512, 523, 534]
)
```

**Métriques collectées :**

- **Percentiles** : P50, P75, P90, P95, P99 (standards scientifiques)
- **CPU** : Usage global + par cœur + fréquences
- **Mémoire** : RSS, VMS, disponibilité système
- **Disque I/O** : Octets lus/écrits
- **Réseau I/O** : Envoi/Réception

#### Validation de configuration

```python
from config.config_validator import ConfigValidator

validator = ConfigValidator()

# Validation complète pré-vol
validation_result = validator.validate_all()

if validation_result["is_valid"]:
    print("Configuration valide !")
else:
    print("Erreurs détectées :")
    for error in validation_result["errors"]:
        print(f"  - {error}")

    print("Avertissements :")
    for warning in validation_result["warnings"]:
        print(f"  - {warning}")
```

**Validations effectuées :**

- **URLs** : Format, protocole HTTP/HTTPS
- **Endpoints** : Connectivité, timeout, réponse SPARQL
- **Chemins** : Existence, permissions lecture/écriture
- **Valeurs numériques** : Plages valides (timeouts, itérations, etc.)
- **Dépendances** : Modules Python requis

#### Configuration .env

```bash
# .env.example - 38 variables configurables

# ============================================
# ENDPOINTS SPARQL
# ============================================
VIRTUOSO_ENDPOINT=http://localhost:8890/sparql
VIRTUOSO_UPDATE_ENDPOINT=http://localhost:8890/sparql-auth
FUSEKI_ENDPOINT=http://localhost:3030/dataset/query
FUSEKI_UPDATE_ENDPOINT=http://localhost:3030/dataset/update

# ============================================
# SYNCHRONISATION
# ============================================
SYNC_CHUNK_SIZE=100000
MAX_SYNC_TRIPLETS=1000000
SYNC_RETRY_ATTEMPTS=3
SYNC_RETRY_DELAY=2

# ============================================
# TIMEOUTS ET PERFORMANCE
# ============================================
QUERY_TIMEOUT=60
CONNECTIVITY_TIMEOUT=5
MAX_WORKERS=4

# ============================================
# LOGGING
# ============================================
LOG_LEVEL=INFO
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# ... et 20+ autres variables
```

**Chargement automatique :**

```python
from config.env_loader import load_env_config, get_env

# Chargement avec validation
config = load_env_config(env_file=".env")

# Accès typé
virtuoso_url = get_env("VIRTUOSO_ENDPOINT", "http://localhost:8890/sparql")
chunk_size = get_env("SYNC_CHUNK_SIZE", 100000, cast_type=int)
enable_cache = get_env("ENABLE_QUERY_CACHE", True, cast_type=bool)
```

#### Dashboard temps réel

```python
from ui.components.realtime_dashboard import RealtimeDashboard

dashboard = RealtimeDashboard(total_queries=10)

# Mise à jour pendant l'exécution
for i, query in enumerate(queries):
    result = execute_query(query)

    dashboard.update_all(
        query_name=query.name,
        execution_time=result.duration,
        cpu_percent=result.cpu_usage,
        memory_mb=result.memory_mb,
        progress_bar=progress_bar,
        status_text=status_text,
        metrics_container=metrics_col,
        charts_container=charts_col
    )

# Affichage final
dashboard.display_final_summary(summary_container)
```

**Visualisations temps réel :**

- **Barres de progression** : Requête actuelle + progression globale
- **Graphiques dynamiques** : Temps d'exécution par requête (Plotly)
- **Monitoring ressources** : CPU + Mémoire en temps réel
- **Résumé final** : Statistiques agrégées

---

## Architecture

```
sparql_performance_platform_v2/
├── main.py                           # Point d'entrée Streamlit
│
├── config/                           # Configuration
│
├── core/                             # Logique métier
│
├── queries/                          # Catalogues de requêtes
│
├── visualization/                    # Visualisations
│
├── ui/                               # Interface utilisateur
│   ├── sidebar.py                    # Barre latérale
│   ├── tabs/                         # Onglets
│   └── components/                   # NEW: Composants UI
│
├── utils/                            # Utilitaires
│
├── tests/                            # NEW: Tests unitaires
│  
├── docker-compose.yml                # NEW: Orchestration Docker
├── Dockerfile                        # NEW: Image Streamlit
├── .dockerignore                     # NEW: Exclusions Docker
├── requirements.txt                  # Dépendances Python
```

---

## Installation rapide

### Option 1: Docker Compose (Recommandé)

```bash
# 1. Cloner le repository
git clone https://github.com/thiernoDiedhiou/sparql_performance_platform.git
cd sparql_performance_platform

# 2. Configurer l'environnement (OBLIGATOIRE)
cp .env.example .env
nano .env  # Modifier les mots de passe par défaut !
# ⚠️ IMPORTANT: Changer TOUS les mots de passe en production

# 3. Démarrer tous les services
docker-compose up -d

# 4. Vérifier la santé
docker-compose ps

# 5. Accéder à l'interface
# Streamlit: http://localhost:8501
# Virtuoso: http://localhost:8890/sparql
# Fuseki: http://localhost:3030
```

### Option 2: Installation manuelle

```bash
# 1. Prérequis
# - Python 3.10+
# - Virtuoso et Fuseki installés séparément

# 2. Cloner et installer
git clone https://github.com/thiernoDiedhiou/sparql_performance_platform.git
cd sparql_performance_platform

# 3. Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate  # Windows

# 4. Installer dépendances
pip install --upgrade pip
pip install -r requirements.txt

# 5. Configurer l'environnement
cp .env.example .env
nano .env  # MODIFIER les credentials par défaut
# ⚠️ Ne JAMAIS utiliser les mots de passe par défaut en production

# 6. Valider configuration
python -c "from config.config_validator import ConfigValidator; ConfigValidator().validate_all()"

# 7. Lancer l'application
streamlit run main.py
```

### Vérification installation

```bash
# Tests unitaires
pytest tests/ -v

# Validation configuration
python -c "from config.config_validator import ConfigValidator; print(ConfigValidator().validate_all())"

# Vérification endpoints
curl http://localhost:8890/sparql?query=ASK%20%7B%7D
curl http://localhost:3030/$/ping
```

---

## 🔐 Sécurité et Configuration

### Variables d'environnement (.env)

**⚠️ CRITIQUE : Le fichier `.env` contient des informations sensibles !**

#### Configuration Obligatoire

```bash
# 1. Copier le template
cp .env.example .env

# 2. Éditer avec vos credentials
nano .env  # ou code .env, vim .env, etc.
```

#### Variables Critiques à Modifier

```bash
# AUTHENTIFICATION VIRTUOSO (OBLIGATOIRE)
VIRTUOSO_USERNAME=SPARQL
VIRTUOSO_PASSWORD=changeme_virtuoso_password  # ⚠️ À CHANGER !

# AUTHENTIFICATION FUSEKI (si applicable)
FUSEKI_USERNAME=admin
FUSEKI_PASSWORD=changeme_fuseki_password      # ⚠️ À CHANGER !

# ADMINISTRATION APPLICATION
ENABLE_AUTHENTICATION=true
ADMIN_USERNAME=admin
ADMIN_PASSWORD=changeme_admin_password        # ⚠️ À CHANGER !
```

#### Règles de Sécurité

✅ **À FAIRE :**

- Utiliser des mots de passe forts (≥16 caractères, alphanumériques + symboles)
- Changer TOUS les mots de passe par défaut
- Restreindre les permissions : `chmod 600 .env` (Linux/macOS)
- Vérifier que `.env` est dans `.gitignore`

❌ **NE JAMAIS :**

- Commiter le fichier `.env` dans Git
- Utiliser les mots de passe par défaut en production
- Partager le fichier `.env` publiquement
- Hardcoder des credentials dans le code

### Protection Anti-Injection SPARQL

La plateforme **bloque automatiquement** les requêtes malveillantes :

```sparql
-- ❌ BLOQUÉES (opérations de modification)
INSERT DATA { ... }
DELETE WHERE { ... }
DROP GRAPH <...>

-- ✅ AUTORISÉES (opérations de lecture)
SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 100
CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }
```

**Limites de sécurité :**

- Longueur max : 50,000 caractères
- Niveaux d'imbrication max : 10
- Timeout : 60 secondes

## Utilisation

### 1. Configuration initiale

#### Via interface Streamlit

1. Ouvrir [http://localhost:8501](http://localhost:8501)
2. Barre latérale > Configuration
3. Entrer les URLs des endpoints SPARQL
4. Cliquer sur "Valider la configuration"

#### Via fichier .env

```bash
# Copier le template
cp .env.example .env

# Éditer avec vos paramètres
nano .env

# Valider
python -c "from config.config_validator import ConfigValidator; ConfigValidator().validate_all()"
```

### 2. Synchronisation des données

```python
# Via l'interface
1. Onglet "Configuration"
2. Section "Synchronisation de données"
3. Bouton "Synchroniser Virtuoso → Fuseki"
4. Suivre la progression en temps réel

# Via code
from utils.data_synchronizer_v2 import DataSynchronizerV2

sync = DataSynchronizerV2(
    virtuoso_endpoint="http://localhost:8890/sparql",
    fuseki_endpoint="http://localhost:3030/dataset/data",
    chunk_size=100000
)

sync.synchronize_data()
```

### 3. Exécution des tests

#### Interface graphique

1. Onglet "Exécution"
2. Sélectionner le jeu de données (LUBM, DBpedia, etc.)
3. Choisir les types de requêtes à tester
4. Configurer les paramètres (itérations, warmup, etc.)
5. Cliquer sur "Lancer les tests"
6. Suivre la progression en temps réel avec dashboard

#### API programmatique

```python
from core.tester import SPARQLPerformanceTester
from queries.catalog import SPARQLQueryCatalog

# Initialiser le testeur
tester = SPARQLPerformanceTester(
    virtuoso_endpoint="http://localhost:8890/sparql",
    fuseki_endpoint="http://localhost:3030/dataset/query"
)

# Charger les requêtes
catalog = SPARQLQueryCatalog()
queries = catalog.get_queries_by_type("LUBM")

# Exécuter un benchmark
for query in queries:
    result = tester.run_benchmark(
        query_name=query["name"],
        query_text=query["text"],
        num_iterations=10,
        warmup_iterations=3
    )
    print(f"{query['name']}: {result['avg_time']:.3f}s")
```

### 4. Analyse des résultats

#### Onglet "Résultats"

- Tableau récapitulatif avec métriques clés
- Tri et filtrage par moteur/requête
- Export CSV, Excel, JSON

#### Onglet "Visualisation"

- **Graphiques en barres** : Comparaison temps d'exécution
- **Graphiques de dispersion** : Corrélation Virtuoso vs Fuseki
- **Heatmaps** : Vue d'ensemble des performances
- **Box plots** : Distribution avec percentiles
- **Séries temporelles** : Évolution par itération

#### Métriques avancées

```python
from core.advanced_metrics import AdvancedMetricsCollector

collector = AdvancedMetricsCollector()

# Percentiles
percentiles = collector.calculate_percentiles(execution_times)
print(f"P50 (médiane): {percentiles.p50:.3f}s")
print(f"P95: {percentiles.p95:.3f}s")
print(f"P99: {percentiles.p99:.3f}s")

# Rapport complet
report = collector.generate_performance_report(
    engine="Virtuoso",
    execution_times=times,
    cpu_usage=cpu,
    memory_mb=memory
)
```

### 5. Export et rapports

#### Formats disponibles

- **CSV** : Données brutes pour analyse externe
- **Excel** : Feuilles multiples (résumé + détails + métriques)
- **JSON** : Données structurées avec métadonnées complètes

#### Génération de rapports

```python
from visualization.reports import ReportGenerator

generator = ReportGenerator()

# Rapport complet
report = generator.generate_full_report(
    results=test_results,
    include_percentiles=True,
    include_system_info=True
)

# Export
generator.export_to_excel(report, "rapport_performance.xlsx")
generator.export_to_json(report, "rapport_performance.json")
```

---

## Tests et qualité

### Suite de tests complète

```bash
# Tous les tests (103 tests)
pytest tests/ -v

# Tests avec couverture
pytest tests/ --cov=. --cov-report=html --cov-report=term

# Tests par marqueur
pytest tests/ -m "unit"        # Tests unitaires
pytest tests/ -m "integration" # Tests d'intégration
pytest tests/ -m "slow"        # Tests lents

# Tests par fichier
pytest tests/test_executor.py -v
pytest tests/test_tester.py -v
pytest tests/test_helpers.py -v

# Mode verbose avec détails
pytest tests/ -vv --tb=short

# Arrêt au premier échec
pytest tests/ -x
```

### Statistiques de tests

| Fichier                   | Tests         | Réussite     | Couverture    |
| ------------------------- | ------------- | ------------- | ------------- |
| test_executor.py          | 17            | 100%          | 68%           |
| test_tester.py            | 12            | 100%          | 61%           |
| test_data_synchronizer.py | 22            | 95%           | 54%           |
| test_queries.py           | 23            | 100%          | 72%           |
| test_helpers.py           | 28            | 96%           | 85%           |
| **TOTAL**           | **102** | **96%** | **52%** |

### CI/CD avec GitHub Actions

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest tests/ --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## Configuration avancée

### Profils de test prédéfinis

#### Développement rapide

```python
QUICK_TEST_PROFILE = {
    "num_iterations": 3,
    "warmup_iterations": 1,
    "concurrent_queries": 1,
    "query_types": ["simple"],
    "collect_system_metrics": False
}
```

#### Production complète

```python
PRODUCTION_TEST_PROFILE = {
    "num_iterations": 10,
    "warmup_iterations": 3,
    "concurrent_queries": 1,
    "query_types": ["all"],
    "collect_system_metrics": True,
    "calculate_percentiles": True
}
```

#### Test de stress

```python
STRESS_TEST_PROFILE = {
    "num_iterations": 20,
    "warmup_iterations": 5,
    "concurrent_queries": 5,
    "query_types": ["all"],
    "collect_system_metrics": True,
    "calculate_percentiles": True,
    "enable_retry": True
}
```

### Personnalisation du logging

```python
from utils.logging_config import setup_logging

# Configuration personnalisée
logger = setup_logging(
    log_dir="custom_logs",
    log_file="my_app.log",
    log_level="DEBUG",
    max_bytes=20*1024*1024,  # 20MB
    backup_count=10,
    console_level="INFO",
    file_level="DEBUG"
)

# Utilisation
logger.info("Application démarrée")
logger.debug("Détails de debug")
logger.warning("Avertissement")
logger.error("Erreur détectée")
```

### Ajout de nouveaux moteurs SPARQL

```python
# Dans core/executor.py
class CustomEngineExecutor(QueryExecutor):
    """Support pour un nouveau moteur SPARQL"""

    def setup_endpoint(self, endpoint_url, query):
        """Configuration spécifique au moteur"""
        sparql = SPARQLWrapper(endpoint_url)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)

        # Configuration spécifique
        sparql.addCustomHttpHeader("X-Custom-Header", "value")

        return sparql

    def execute_with_retries(self, sparql, max_retries=3):
        """Exécution avec retry personnalisé"""
        # Implémentation spécifique
        pass
```

### Ajout de nouvelles métriques

```python
# Dans core/advanced_metrics.py
class CustomMetricsCollector(AdvancedMetricsCollector):
    """Collecteur de métriques personnalisées"""

    def collect_network_latency(self):
        """Mesure la latence réseau"""
        import socket
        # Implémentation
        pass

    def collect_cache_hit_ratio(self):
        """Mesure le taux de cache hit"""
        # Implémentation
        pass
```

---

## Dépannage

### Problèmes courants

#### 1. Endpoint non accessible

```bash
# Diagnostic
curl -X GET "http://localhost:8890/sparql?query=ASK%20%7B%7D"

# Solutions
- Vérifier que Virtuoso/Fuseki est démarré
- Tester la connectivité réseau
- Vérifier les pare-feu
- Consulter les logs: docker-compose logs virtuoso
```

#### 2. Tests échouent

```bash
# Diagnostic
pytest tests/ -vv --tb=short

# Solutions courantes
- Installer toutes les dépendances: pip install -r requirements.txt
- Vérifier la version Python: python --version (3.10+ requis)
- Nettoyer les caches: pytest --cache-clear
- Vérifier les mocks dans conftest.py
```

#### 3. Synchronisation échoue

```bash
# Diagnostic
python -c "from utils.data_synchronizer_v2 import DataSynchronizerV2; DataSynchronizerV2().test_connectivity()"

# Solutions
- Réduire chunk_size dans .env: SYNC_CHUNK_SIZE=50000
- Augmenter les timeouts: QUERY_TIMEOUT=120
- Vérifier les permissions d'écriture sur Fuseki
- Consulter logs/sparql_platform.log
```

#### 4. Erreurs de mémoire

```bash
# Solutions
- Réduire le nombre d'itérations simultanées
- Augmenter la mémoire Docker: docker-compose.yml > JVM_ARGS=-Xmx4g
- Utiliser LIMIT dans les requêtes
- Activer le chunking pour la synchronisation
```

#### 5. Dashboard ne s'affiche pas

```bash
# Diagnostic
streamlit --version
curl http://localhost:8501/_stcore/health

# Solutions
- Redémarrer Streamlit: docker-compose restart streamlit_app
- Vider le cache navigateur: Ctrl+Shift+R
- Vérifier les logs: docker-compose logs streamlit_app
- Tester en mode local: streamlit run main.py
```

### Logs et debugging

#### Activation mode debug

```bash
# Via .env
LOG_LEVEL=DEBUG

# Via code
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Consultation des logs

```bash
# Logs rotatifs
tail -f logs/sparql_platform.log

# Logs Docker
docker-compose logs -f --tail=100 streamlit_app
docker-compose logs -f virtuoso
docker-compose logs -f fuseki
```

---

## Support et contribution

### Obtenir de l'aide

- **Email** : githubthierno@gmail.com

### Contribuer au projet

#### 1. Fork et clone

```bash
git clone https://github.com/thiernoDiedhiou/sparql_performance_platform.git
cd sparql_performance_platform
git checkout -b feature/amazing-feature
```

#### 2. Développer

```bash
# Créer environnement virtuel
python -m venv venv
source venv/bin/activate

# Installer dépendances + dev tools
pip install -r requirements.txt
pip install black flake8 mypy pytest

# Développer votre fonctionnalité
# ...

# Formater le code
black .

# Vérifier le style
flake8 .

# Vérifier les types
mypy .

# Lancer les tests
pytest tests/ -v
```

#### 3. Commiter et pousser

```bash
git add .
git commit -m "feat: Add amazing feature"
git push origin feature/amazing-feature
```

#### 4. Créer une Pull Request

- Décrire clairement les changements
- Référencer les issues liées
- S'assurer que tous les tests passent

### Standards de code

- **Formatage** : [Black](https://black.readthedocs.io/) (line length: 100)
- **Linting** : [Flake8](https://flake8.pycqa.org/)
- **Type hints** : [MyPy](http://mypy-lang.org/) pour la vérification statique
- **Documentation** : Docstrings Google style
- **Tests** : Pytest avec >80% de couverture

### Conventions de commit

```
feat: Nouvelle fonctionnalité
fix: Correction de bug
docs: Documentation uniquement
style: Formatage (pas de changement de code)
refactor: Refactoring du code
test: Ajout/modification de tests
chore: Tâches de maintenance
```

---

## Licence

Ce projet est développé dans le cadre d'un **Mémoire de Master 2 en Informatique - Génie Logiciel**.

**Usage académique** : Libre pour la recherche et l'éducation.

---

## Citation

Si vous utilisez cette plateforme dans vos travaux de recherche, veuillez citer :

```bibtex
@mastersthesis{diedhiou2024sparql,
  author  = {Thierno Diedhiou},
  title   = {Évaluation comparative des performances des moteurs SPARQL: Virtuoso vs Jena Fuseki},
  school  = {Université Iba Der Thiam de Thiès, Sénégal},
  year    = {2024},
  type    = {Mémoire de Master 2},
  url     = {https://github.com/thiernoDiedhiou/sparql_performance_platform}
}
```

---

## Remerciements

- **Tenforce** pour l'image Docker Virtuoso
- **Apache Jena** pour Jena Fuseki
- **Streamlit** pour le framework web
- **Plotly** pour les visualisations interactives
- Tous les contributeurs du projet

---

---

**Développé  pour l'évaluation des performances SPARQL**
