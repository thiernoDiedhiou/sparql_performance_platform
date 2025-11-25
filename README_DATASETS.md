# 📦 Système de Gestion des Datasets - Guide Rapide

## 🎯 Vue d'ensemble

Système complet de gestion des datasets RDF pour la plateforme SPARQL Performance Testing. Permet de charger, valider, gérer et supprimer des datasets dans Virtuoso et Jena Fuseki avec persistance des métadonnées et mise à jour automatique de la configuration.

## ✨ Fonctionnalités principales

- ✅ **Chargement intelligent** avec validation et estimation des ressources
- ✅ **Persistance des métadonnées** dans `datasets_metadata.json`
- ✅ **Mise à jour automatique** du fichier `.env`
- ✅ **Suppression sélective ou globale** avec nettoyage complet
- ✅ **Statistiques détaillées** par moteur et globales
- ✅ **Interface Streamlit intuitive** avec feedback en temps réel

## 🚀 Démarrage rapide

### 1. Structure des datasets

Assurez-vous que vos datasets suivent cette structure :

```
datasets/
├── DBpedia/
│   ├── 10K.ttl
│   ├── 100K.ttl
│   └── 1M.ttl
├── LUBM/
│   ├── 10K.ttl
│   ├── 100K.ttl
│   └── 1M.ttl
└── Generic/
    ├── 10K.ttl
    └── 100K.ttl
```

### 2. Utilisation via l'interface Streamlit

1. **Lancez l'application** :
   ```bash
   streamlit run main_v2.py
   ```

2. **Allez dans l'onglet "Datasets"**

3. **Sélectionnez un dataset** (ex: Generic 10K pour un test rapide)

4. **Cliquez sur "Charger dans Virtuoso"** ou "Charger dans Fuseki"

5. **Consultez les statistiques** dans la section du bas

### 3. Utilisation programmatique

```python
from utils.dataset_manager import DatasetManager

# Initialiser le gestionnaire
manager = DatasetManager("datasets")

# Charger un dataset
success, message = manager.load_to_virtuoso(
    file_path="datasets/Generic/10K.ttl",
    endpoint="http://localhost:8890/sparql",
    graph_uri="http://example.org/generic_test"
)

if success:
    # Sauvegarder les métadonnées
    manager.save_dataset_metadata(
        dataset_name="Generic",
        size="10K",
        target="virtuoso",
        graph_uri="http://example.org/generic_test",
        triplet_count=10000
    )

    # Mettre à jour le .env
    manager.update_env_file("Generic", "10K", "virtuoso")
```

### 4. Exemples interactifs

Lancez les exemples interactifs :

```bash
# Menu interactif
python examples/dataset_management_example.py

# Exemple spécifique
python examples/dataset_management_example.py 2  # Lister les datasets
python examples/dataset_management_example.py 3  # Voir les statistiques
```

## 📚 Documentation complète

- **[DATASETS_MANAGEMENT.md](DATASETS_MANAGEMENT.md)** - Guide complet avec API détaillée
- **[CHANGELOG_DATASETS.md](CHANGELOG_DATASETS.md)** - Liste des changements et nouveautés
- **[examples/dataset_management_example.py](examples/dataset_management_example.py)** - 7 exemples pratiques

## 🗂️ Fichiers générés

### 1. `datasets_metadata.json`
```json
{
  "virtuoso": {
    "dataset_name": "DBpedia",
    "size": "10K",
    "graph_uri": "http://example.org/dataset_DBpedia_10K_1730300000",
    "triplet_count": 15000,
    "loaded_at": "2025-10-30T14:30:00",
    "file_path": "datasets/DBpedia/10K.ttl"
  }
}
```

### 2. `.env` (section auto-générée)
```env
CURRENT_DATASET_NAME=DBpedia
CURRENT_DATASET_SIZE=10K
CURRENT_DATASET_TARGET=virtuoso
DATASET_LOADED_AT=2025-10-30 14:30:00
DATASETS_PATH=datasets
```

## 🔑 Datasets disponibles

| Dataset | Description | Format | Tailles |
|---------|-------------|--------|---------|
| 🔵 DBpedia | Données structurées de Wikipedia | N-Triples | 10K, 100K, 1M |
| 🟢 LUBM | Benchmark académique | Turtle | 10K, 100K, 1M |
| 🟡 Generic | Dataset de test synthétique | Turtle | 10K, 100K |

## 📊 Performances

| Dataset | Taille | Fichier | Temps de chargement |
|---------|--------|---------|---------------------|
| Generic | 10K | 400 KB | ~3-5s |
| DBpedia | 10K | 1.4 MB | ~5-8s |
| LUBM | 10K | 6.8 MB | ~7-12s |
| DBpedia | 100K | 15 MB | ~45-60s |
| LUBM | 100K | 43 MB | ~60-90s |

*Les temps varient selon les ressources système*

## 🛠️ API principale

### DatasetManager

#### Méthodes de chargement
```python
load_to_virtuoso(file_path, endpoint, graph_uri) -> Tuple[bool, str]
load_to_fuseki(file_path, endpoint, graph_uri) -> Tuple[bool, str]
```

#### Métadonnées
```python
save_dataset_metadata(dataset_name, size, target, graph_uri, triplet_count) -> bool
load_all_metadata() -> Dict
get_loaded_dataset_info(target) -> Optional[Dict]
```

#### Configuration
```python
update_env_file(dataset_name, size, target) -> bool
```

#### Suppression
```python
clear_dataset(target, endpoint, username, password) -> Tuple[bool, str]
```

#### Statistiques
```python
get_dataset_statistics() -> Dict
get_loading_recommendations(dataset_name, size) -> Dict
```

#### Validation
```python
validate_dataset_coherence(dataset_name, size) -> Tuple[bool, str, Dict]
validate_loaded_dataset(endpoint, dataset_name) -> Tuple[bool, str, int]
check_virtuoso_permissions(endpoint, username, password) -> Tuple[bool, str, dict]
```

## 🔧 Configuration

### Dans `config/settings.py`

```python
# Chemin des datasets
DEFAULT_DATASETS_PATH = "datasets"

# Authentification Virtuoso
VIRTUOSO_DEFAULT_USERNAME = "SPARQL"
VIRTUOSO_DEFAULT_PASSWORD = "admin123"

# Configuration de chargement
DATASET_LOAD_CHUNK_SIZE = 1000
DATASET_LOAD_TIMEOUT = 300

# Obtenir toute la configuration
config = get_datasets_config()
```

## 🐛 Résolution des problèmes

### Le dataset ne se charge pas

**Problème** : Erreur lors du chargement

**Solutions** :
1. Vérifier que Virtuoso/Fuseki est démarré
2. Tester la connectivité : `curl http://localhost:8890/sparql`
3. Vérifier les permissions de l'utilisateur SPARQL
4. Consulter les logs : `logs/sparql_platform.log`

### Erreur de permissions Virtuoso

**Problème** : "Pas de permissions SPARQL_UPDATE"

**Solution** :
```sql
-- Se connecter via isql
isql 1111 dba dba

-- Donner les permissions
GRANT SPARQL_UPDATE TO "SPARQL";
```

### Métadonnées non sauvegardées

**Problème** : Le fichier `datasets_metadata.json` n'est pas créé

**Solutions** :
1. Vérifier les permissions d'écriture dans le répertoire
2. Vérifier que le chemin est correct
3. Relancer avec les droits administrateur

### Le .env n'est pas mis à jour

**Problème** : Les variables ne sont pas ajoutées au .env

**Solutions** :
1. Vérifier que le fichier `.env` existe
2. Vérifier les permissions d'écriture
3. Vérifier qu'il n'est pas ouvert dans un autre programme

## 📈 Workflow recommandé

### Pour les tests rapides
```
1. Charger Generic 10K (≈3s)
2. Tester rapidement
3. Effacer si besoin
```

### Pour les benchmarks
```
1. Charger DBpedia ou LUBM 100K (≈60s)
2. Lancer les tests de performance
3. Consulter les statistiques
4. Exporter les résultats
```

### Pour la production
```
1. Valider le dataset avec validate_dataset_coherence()
2. Vérifier les ressources avec get_loading_recommendations()
3. Charger avec validation complète
4. Vérifier les métadonnées
5. Tester avec quelques requêtes
```

## 🎓 Exemples de cas d'usage

### Cas 1: Test rapide de connectivité
```python
manager = DatasetManager("datasets")

# Charger Generic 10K (très rapide)
success, msg = manager.load_to_virtuoso(
    "datasets/Generic/10K.ttl",
    "http://localhost:8890/sparql"
)

if success:
    print("✅ Virtuoso opérationnel!")
```

### Cas 2: Benchmark comparatif
```python
manager = DatasetManager("datasets")

# Charger le même dataset dans les deux moteurs
dataset = "DBpedia"
size = "100K"
graph_uri = f"http://example.org/{dataset}_{size}"

# Virtuoso
manager.load_to_virtuoso(
    f"datasets/{dataset}/{size}.ttl",
    "http://localhost:8890/sparql",
    graph_uri
)

# Fuseki
manager.load_to_fuseki(
    f"datasets/{dataset}/{size}.ttl",
    "http://localhost:3030/dataset/query",
    graph_uri
)

# Maintenant vous pouvez comparer les performances
```

### Cas 3: Nettoyage et rechargement
```python
manager = DatasetManager("datasets")

# Effacer l'ancien dataset
manager.clear_dataset("virtuoso", "http://localhost:8890/sparql")

# Charger un nouveau dataset
manager.load_to_virtuoso(
    "datasets/LUBM/10K.ttl",
    "http://localhost:8890/sparql"
)

# Sauvegarder les métadonnées
manager.save_dataset_metadata("LUBM", "10K", "virtuoso", "...", 10000)
```

## 🔗 Intégration avec d'autres composants

### Avec les tests de performance
```python
# 1. Charger le dataset
manager.load_to_virtuoso(...)

# 2. Obtenir les infos pour les tests
info = manager.get_loaded_dataset_info("virtuoso")
dataset_name = info['dataset_name']

# 3. Lancer les tests avec le bon dataset
from core.executor import QueryExecutor
executor = QueryExecutor(dataset_type=dataset_name)
```

### Avec la synchronisation
```python
# Vérifier si les datasets sont identiques
stats = manager.get_dataset_statistics()

if stats['virtuoso'] and stats['fuseki']:
    v_triplets = stats['virtuoso']['triplets']
    f_triplets = stats['fuseki']['triplets']

    if v_triplets != f_triplets:
        print("⚠️ Les datasets ne sont pas synchronisés!")
```

## 📞 Support

- **Documentation** : [DATASETS_MANAGEMENT.md](DATASETS_MANAGEMENT.md)
- **Changelog** : [CHANGELOG_DATASETS.md](CHANGELOG_DATASETS.md)
- **Exemples** : [examples/dataset_management_example.py](examples/dataset_management_example.py)
- **Logs** : `logs/sparql_platform.log`

## 🎉 Contribution

Ce système fait partie de la plateforme SPARQL Performance Testing pour un mémoire de Master 2.

### Structure du code

```
sparql_v2/
├── utils/
│   └── dataset_manager.py      # Gestionnaire principal
├── ui/
│   └── tabs/
│       └── datasets_tab.py     # Interface Streamlit
├── config/
│   └── settings.py             # Configuration
├── examples/
│   └── dataset_management_example.py  # Exemples
├── datasets/                   # Vos datasets
├── datasets_metadata.json      # Métadonnées (auto-généré)
└── .env                        # Configuration (auto-mis à jour)
```

## ✅ Checklist de démarrage

- [ ] Créer le dossier `datasets/` avec les sous-dossiers
- [ ] Placer les fichiers .ttl dans les bons dossiers
- [ ] Démarrer Virtuoso et/ou Fuseki
- [ ] Tester la connectivité
- [ ] Vérifier les permissions SPARQL_UPDATE
- [ ] Charger un dataset de test (Generic 10K)
- [ ] Consulter les métadonnées générées
- [ ] Vérifier la mise à jour du .env
- [ ] Essayer de supprimer le dataset
- [ ] Consulter la documentation complète

---

**Version** : 2.0
**Date** : 2025-10-30
**Statut** : Production ready
**Licence** : Projet académique - Master 2

🚀 **Prêt à gérer vos datasets comme un pro !**
