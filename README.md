# Plateforme d'évaluation de performance des moteurs SPARQL

Une application Streamlit complète pour l'évaluation comparative des performances des moteurs SPARQL, spécialement conçue pour comparer Virtuoso et Jena Fuseki.

## 🚀 Fonctionnalités principales

- **Tests de performance automatisés** : Exécution automatique de requêtes SPARQL avec mesures détaillées
- **Comparaison multi-moteurs** : Support pour Virtuoso, Jena Fuseki et autres endpoints SPARQL
- **Métriques complètes** : Temps d'exécution, utilisation CPU/mémoire, taux de succès
- **Visualisations interactives** : Graphiques dynamiques avec Plotly
- **Catalogues de requêtes** : Requêtes pré-définies pour LUBM, DBpedia et jeux de données génériques
- **Export des résultats** : Export vers CSV, Excel, JSON avec génération de rapports
- **Interface intuitive** : Interface web moderne avec Streamlit

## 📁 Structure du projet

```
sparql_performance_platform/
├── main.py                          # Point d'entrée principal
├── config/                          # Configuration
│   ├── settings.py                  # Paramètres globaux
│   └── endpoints.py                 # Configuration endpoints
├── core/                            # Logique métier
│   ├── tester.py                    # Testeur de performance
│   ├── executor.py                  # Exécuteur de requêtes
│   └── metrics.py                   # Collecteur de métriques
├── queries/                         # Catalogues de requêtes
│   ├── catalog.py                   # Catalogue principal
│   ├── lubm_queries.py              # Requêtes LUBM
│   ├── dbpedia_queries.py           # Requêtes DBpedia
│   └── generic_queries.py           # Requêtes génériques
├── visualization/                   # Visualisations
│   ├── visualizer.py                # Visualiseur principal
│   ├── charts.py                    # Graphiques spécialisés
│   └── reports.py                   # Génération rapports
├── ui/                              # Interface utilisateur
│   ├── sidebar.py                   # Barre latérale
│   └── tabs/                        # Onglets de l'interface
├── utils/                           # Utilitaires
│   ├── data_manager.py              # Gestion des données
│   ├── export_manager.py            # Gestion exports
│   └── helpers.py                   # Fonctions utilitaires
└── tests/                           # Tests unitaires
```

## 🛠️ Installation

### Prérequis

- Python 3.8+
- Moteurs SPARQL (Virtuoso et/ou Jena Fuseki) installés et configurés

### Installation des dépendances

```bash
# Cloner le repository
git clone <repository-url>
cd sparql_performance_platform

# Installer les dépendances
pip install -r requirements.txt
```

### Configuration des moteurs SPARQL

#### Virtuoso

```bash
# Installation via Docker (recommandé)
docker run -d \
  --name virtuoso \
  -p 8890:8890 \
  -e DBA_PASSWORD=dba \
  tenforce/virtuoso:1.3.2-virtuoso7.2.5
```

#### Jena Fuseki

```bash
# Installation via Docker
docker run -d \
  --name fuseki \
  -p 3030:3030 \
  stain/jena-fuseki:latest
```

## 🚀 Utilisation

### Lancement de l'application

```bash
streamlit run main.py
```

L'application sera accessible à l'adresse : `http://localhost:8501`

### Configuration initiale

1. **Endpoints SPARQL** : Configurez les URLs de vos endpoints dans la barre latérale
2. **Jeu de données** : Sélectionnez le type de jeu de données (LUBM, DBpedia, etc.)
3. **Paramètres de test** : Ajustez le nombre d'itérations, niveau de concurrence, etc.

### Exécution des tests

1. **Sélection des requêtes** : Choisissez les types de requêtes à tester
2. **Lancement** : Cliquez sur "Exécuter les tests"
3. **Analyse** : Explorez les résultats dans les onglets Résultats et Visualisation
4. **Export** : Téléchargez les résultats ou générez un rapport

## 📊 Types de tests supportés

### Par complexité

- **Requêtes simples** : Pattern matching basique
- **Requêtes de jointure** : Jointures entre entités
- **Requêtes d'agrégation** : GROUP BY, COUNT, SUM, etc.
- **Requêtes avec filtres** : Conditions FILTER
- **Requêtes avancées** : OPTIONAL, UNION, MINUS
- **Sous-requêtes** : Requêtes imbriquées complexes

### Par jeu de données

- **LUBM** : Lehigh University Benchmark (domaine universitaire)
- **DBpedia** : Données encyclopédiques structurées
- **BSBM** : Berlin SPARQL Benchmark (e-commerce)
- **YAGO** : Base de connaissances géographique
- **Personnalisé** : Vos propres jeux de données RDF

## 📈 Métriques collectées

### Performance

- **Temps d'exécution** : Durée totale de chaque requête
- **Débit** : Requêtes par seconde
- **Latence** : Temps de première réponse

### Ressources système

- **CPU** : Utilisation processeur pendant l'exécution
- **Mémoire** : Consommation RAM
- **Réseau** : Trafic généré (optionnel)

### Fiabilité

- **Taux de succès** : Pourcentage de requêtes réussies
- **Gestion d'erreurs** : Classification des erreurs
- **Stabilité** : Variation des performances

## 🎨 Visualisations disponibles

- **Graphiques en barres** : Comparaison des temps d'exécution
- **Graphiques de dispersion** : Corrélation entre moteurs
- **Heatmaps** : Vue d'ensemble des performances
- **Graphiques de tendance** : Évolution par itération
- **Tableaux récapitulatifs** : Statistiques détaillées

## 📤 Export et rapports

### Formats d'export

- **CSV** : Données brutes pour analyse externe
- **Excel** : Feuilles multiples avec résumés
- **JSON** : Données structurées avec métadonnées

### Types de rapports

- **Rapport complet** : Analyse détaillée de tous les aspects
- **Résumé exécutif** : Vue d'ensemble pour les décideurs
- **Rapport technique** : Détails d'implémentation
- **Comparaison moteurs** : Focus sur les différences

## 🔧 Configuration avancée

### Profils de test prédéfinis

```python
# Test rapide (développement)
{
    "num_iterations": 3,
    "warmup_iterations": 1,
    "concurrent_queries": 1,
    "query_types": ["simple"]
}

# Test complet (production)
{
    "num_iterations": 10,
    "warmup_iterations": 3,
    "concurrent_queries": 1,
    "query_types": ["all"]
}

# Test de stress
{
    "num_iterations": 20,
    "warmup_iterations": 5,
    "concurrent_queries": 5,
    "query_types": ["all"]
}
```

### Variables d'environnement

```bash
# Configuration des endpoints par défaut
export VIRTUOSO_ENDPOINT="http://localhost:8890/sparql"
export FUSEKI_ENDPOINT="http://localhost:3030/dataset/query"

# Configuration des timeouts
export QUERY_TIMEOUT=60
export CONNECTIVITY_TIMEOUT=5

# Mode debug
export DEBUG_MODE=true
```

## 🧪 Développement

### Structure modulaire

Le projet suit une architecture modulaire pour faciliter :

- **Maintenabilité** : Code organisé par responsabilité
- **Réutilisabilité** : Composants indépendants
- **Extensibilité** : Ajout facile de nouveaux moteurs/métriques
- **Testabilité** : Tests unitaires par module

### Ajout de nouveaux moteurs

```python
# Dans core/executor.py
class CustomEngineExecutor(QueryExecutor):
    def setup_endpoint(self, endpoint_url, query):
        # Implémentation spécifique au moteur
        pass
```

### Ajout de nouvelles métriques

```python
# Dans core/metrics.py
class CustomMetricsCollector(MetricsCollector):
    def collect_custom_metrics(self):
        # Collecte de métriques spécialisées
        pass
```

### Tests unitaires

```bash
# Exécution des tests
python -m pytest tests/

# Tests avec couverture
python -m pytest tests/ --cov=. --cov-report=html
```

## 📚 API et extensibilité

### Interface de programmation

```python
from core.tester import SPARQLPerformanceTester
from queries.catalog import SPARQLQueryCatalog

# Utilisation programmatique
tester = SPARQLPerformanceTester(
    virtuoso_endpoint="http://localhost:8890/sparql",
    fuseki_endpoint="http://localhost:3030/dataset/query"
)

catalog = SPARQLQueryCatalog()
queries = catalog.get_queries_by_type("LUBM")

results = tester.run_benchmark("test_query", query, 5, 2)
```

### Hooks et callbacks

```python
# Callback de progression
def progress_callback(current, total, message):
    print(f"Progress: {current}/{total} - {message}")

tester.set_progress_callback(progress_callback)
```

## 🔍 Dépannage

### Problèmes courants

#### Endpoint non accessible

```bash
# Vérification de connectivité
curl -X GET "http://localhost:8890/sparql?query=SELECT%20?s%20WHERE%20{%20?s%20?p%20?o%20}%20LIMIT%201"
```

#### Erreurs de mémoire

- Réduire le nombre d'itérations simultanées
- Augmenter la mémoire allouée aux moteurs SPARQL
- Utiliser des requêtes avec LIMIT

#### Performance dégradée

- Vérifier la charge système
- Redémarrer les moteurs SPARQL
- Utiliser les itérations d'échauffement

### Logs et debug

```python
# Activation du mode debug
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📄 Licence

Ce projet est développé dans le cadre d'un mémoire de Master 2 en Informatique - Génie Logiciel.

## 🤝 Contribution

### Guide de contribution

1. Fork du projet
2. Création d'une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit des changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouverture d'une Pull Request

### Standards de code

- **Formatage** : Black pour le formatage automatique
- **Linting** : Flake8 pour la vérification du style
- **Type hints** : MyPy pour la vérification des types
- **Documentation** : Docstrings Google style

## 📞 Support

Pour toute question ou problème :

- Créez une issue sur GitHub
- Consultez la documentation dans le dossier `docs/`
- Référez-vous aux exemples dans `examples/`

## 🔮 Roadmap

### Version 2.0

- [ ] Support pour GraphDB et autres moteurs
- [ ] Interface REST API
- [ ] Tableau de bord en temps réel
- [ ] Intégration CI/CD pour tests automatiques

### Version 2.1

- [ ] Machine learning pour prédiction de performance
- [ ] Optimisation automatique de requêtes
- [ ] Support pour SPARQL 1.1 Update
- [ ] Clustering et distribution des tests

---

**Développé avec ❤️ pour l'évaluation des performances SPARQL**
