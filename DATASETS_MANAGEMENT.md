# Guide de Gestion des Datasets

## Vue d'ensemble

Ce système de gestion des datasets offre une solution complète pour charger, valider, et gérer les datasets RDF dans les moteurs SPARQL Virtuoso et Jena Fuseki.

## Fonctionnalités principales

### 1. Chargement intelligent des datasets

Le système gère automatiquement :
- **Validation des fichiers** : Vérifie la structure et le format des fichiers .ttl
- **Estimation des ressources** : Calcule le temps et la mémoire nécessaires
- **Chargement optimisé** : Utilise plusieurs méthodes (direct, par chunks, API)
- **Validation post-chargement** : Vérifie l'intégrité des données chargées

### 2. Persistance des métadonnées

Tous les datasets chargés sont suivis dans `datasets_metadata.json` :

```json
{
  "virtuoso": {
    "dataset_name": "DBpedia",
    "size": "10K",
    "graph_uri": "http://example.org/dataset_DBpedia_10K_1730300000",
    "triplet_count": 15000,
    "loaded_at": "2025-10-30T14:30:00",
    "file_path": "datasets/DBpedia/10K.ttl"
  },
  "fuseki": {
    "dataset_name": "LUBM",
    "size": "100K",
    "graph_uri": "http://example.org/dataset_LUBM_100K_1730300500",
    "triplet_count": 150000,
    "loaded_at": "2025-10-30T14:35:00",
    "file_path": "datasets/LUBM/100K.ttl"
  }
}
```

### 3. Mise à jour automatique du fichier .env

Le fichier `.env` est mis à jour automatiquement avec les informations du dernier dataset chargé :

```env
# ==============================================================================
# CONFIGURATION DES DATASETS CHARGÉS (Auto-généré)
# ==============================================================================

CURRENT_DATASET_NAME=DBpedia
CURRENT_DATASET_SIZE=10K
CURRENT_DATASET_TARGET=both
DATASET_LOADED_AT=2025-10-30 14:30:00
DATASETS_PATH=datasets
```

### 4. Suppression sélective ou globale

- **Suppression par moteur** : Effacer uniquement de Virtuoso ou Fuseki
- **Suppression globale** : Effacer tous les datasets de tous les moteurs
- **Nettoyage automatique** : Les métadonnées sont supprimées automatiquement

## Structure des datasets

Les datasets doivent suivre cette structure :

```
datasets/
├── DBpedia/
│   ├── 10K.ttl      (≈ 1.4 MB)
│   ├── 100K.ttl     (≈ 15 MB)
│   └── 1M.ttl       (≈ 150 MB)
├── LUBM/
│   ├── 10K.ttl      (≈ 6.8 MB)
│   ├── 100K.ttl     (≈ 43 MB)
│   └── 1M.ttl       (≈ 88 MB)
└── Generic/
    ├── 10K.ttl      (≈ 400 KB)
    └── 100K.ttl     (vide)
```

## API du DatasetManager

### Méthodes principales

#### `save_dataset_metadata(dataset_name, size, target, graph_uri, triplet_count)`
Sauvegarde les métadonnées d'un dataset chargé.

**Paramètres :**
- `dataset_name` : Nom du dataset (DBpedia, LUBM, Generic)
- `size` : Taille (10K, 100K, 1M)
- `target` : Moteur cible ('virtuoso', 'fuseki', 'both')
- `graph_uri` : URI du graphe créé
- `triplet_count` : Nombre de triplets chargés

**Retour :** `bool` - True si succès

#### `load_all_metadata()`
Charge toutes les métadonnées depuis le fichier JSON.

**Retour :** `Dict` - Dictionnaire des métadonnées

#### `get_loaded_dataset_info(target)`
Récupère les informations du dataset chargé pour un moteur spécifique.

**Paramètres :**
- `target` : 'virtuoso' ou 'fuseki'

**Retour :** `Optional[Dict]` - Informations du dataset ou None

#### `update_env_file(dataset_name, size, target)`
Met à jour le fichier .env avec les informations du dataset.

**Paramètres :**
- `dataset_name` : Nom du dataset
- `size` : Taille du dataset
- `target` : Moteur cible

**Retour :** `bool` - True si succès

#### `clear_dataset(target, endpoint, username, password)`
Vide les données d'un dataset chargé.

**Paramètres :**
- `target` : Moteur cible ('virtuoso' ou 'fuseki')
- `endpoint` : URL de l'endpoint
- `username` : Nom d'utilisateur (optionnel)
- `password` : Mot de passe (optionnel)

**Retour :** `Tuple[bool, str]` - (succès, message)

#### `get_dataset_statistics()`
Récupère les statistiques globales des datasets chargés.

**Retour :** `Dict` - Statistiques complètes

```python
{
    'virtuoso': {
        'dataset': 'DBpedia (10K)',
        'triplets': 15000,
        'loaded_at': '2025-10-30T14:30:00',
        'graph_uri': 'http://example.org/...'
    },
    'fuseki': {...},
    'total_datasets_loaded': 2,
    'total_triplets': 165000
}
```

## Utilisation dans l'interface Streamlit

### Charger un dataset

1. Sélectionnez le dataset (DBpedia, LUBM, Generic)
2. Choisissez la taille (10K recommandé pour les tests)
3. Cliquez sur le bouton de chargement approprié :
   - **Charger dans Virtuoso** : Charge uniquement dans Virtuoso
   - **Charger dans Fuseki** : Charge uniquement dans Fuseki
   - **Charger dans les deux** : Charge dans les deux moteurs

### Visualiser les datasets chargés

La section "Datasets actuellement chargés" affiche :
- Le nombre total de datasets chargés
- Le nombre total de triplets
- Les détails par moteur (dataset, triplets, date de chargement)
- Les URIs de graphe

### Effacer un dataset

- Utilisez le bouton "🗑️ Effacer" à côté de chaque moteur
- Ou utilisez "🗑️ Effacer tous les datasets" pour tout nettoyer

## Configuration avancée

### Dans config/settings.py

```python
# Chemin vers les datasets
DEFAULT_DATASETS_PATH = "datasets"

# Fichier de métadonnées
DATASETS_METADATA_FILE = "datasets_metadata.json"

# Authentification Virtuoso
VIRTUOSO_DEFAULT_USERNAME = "SPARQL"
VIRTUOSO_DEFAULT_PASSWORD = "admin123"

# Taille de chunk pour le chargement
DATASET_LOAD_CHUNK_SIZE = 1000

# Timeout de chargement
DATASET_LOAD_TIMEOUT = 300
```

### Personnalisation des datasets

Vous pouvez ajouter de nouveaux datasets dans `DATASET_CONFIGURATIONS` :

```python
DATASET_CONFIGURATIONS = {
    "MonDataset": {
        "folder": "MonDataset",
        "format": "Turtle",
        "ontology": "http://mon-ontologie.org/",
        "color": "🔴",
        "sizes": ["10K", "100K"]
    }
}
```

## Résolution des problèmes

### Le dataset ne se charge pas

1. **Vérifiez la connectivité** aux endpoints Virtuoso/Fuseki
2. **Vérifiez les permissions** : L'utilisateur doit avoir les droits SPARQL_UPDATE
3. **Vérifiez la mémoire** : Assurez-vous d'avoir suffisamment de RAM disponible
4. **Consultez les logs** : Vérifiez `logs/sparql_platform.log`

### Erreur de permissions Virtuoso

```bash
# Se connecter à Virtuoso via isql
isql 1111 dba dba

# Donner les permissions SPARQL_UPDATE à l'utilisateur SPARQL
GRANT SPARQL_UPDATE TO "SPARQL";
```

### Les métadonnées ne sont pas sauvegardées

- Vérifiez les permissions d'écriture dans le répertoire du projet
- Assurez-vous que le fichier `datasets_metadata.json` n'est pas en lecture seule

### Le fichier .env n'est pas mis à jour

- Vérifiez que le fichier `.env` existe et est accessible en écriture
- Vérifiez les permissions du fichier

## Meilleures pratiques

1. **Commencez petit** : Utilisez toujours les datasets 10K pour les premiers tests
2. **Validez avant production** : Vérifiez que les données sont correctement chargées
3. **Surveillez les ressources** : Gardez un œil sur la mémoire et le CPU
4. **Nettoyez régulièrement** : Supprimez les datasets inutiles pour libérer de l'espace
5. **Sauvegardez les métadonnées** : Gardez une copie de `datasets_metadata.json`

## Exemples de code

### Utilisation programmatique

```python
from utils.dataset_manager import DatasetManager

# Initialiser le gestionnaire
manager = DatasetManager("datasets")

# Charger un dataset
success, message = manager.load_to_virtuoso(
    file_path="datasets/DBpedia/10K.ttl",
    endpoint="http://localhost:8890/sparql",
    graph_uri="http://example.org/dbpedia_test"
)

if success:
    # Sauvegarder les métadonnées
    manager.save_dataset_metadata(
        dataset_name="DBpedia",
        size="10K",
        target="virtuoso",
        graph_uri="http://example.org/dbpedia_test",
        triplet_count=15000
    )

    # Mettre à jour le .env
    manager.update_env_file("DBpedia", "10K", "virtuoso")

    # Récupérer les statistiques
    stats = manager.get_dataset_statistics()
    print(f"Total triplets: {stats['total_triplets']}")
```

### Nettoyage programmatique

```python
# Effacer un dataset spécifique
success, msg = manager.clear_dataset(
    target="virtuoso",
    endpoint="http://localhost:8890/sparql"
)

# Récupérer les informations d'un dataset chargé
info = manager.get_loaded_dataset_info("virtuoso")
if info:
    print(f"Dataset: {info['dataset_name']} ({info['size']})")
    print(f"Triplets: {info['triplet_count']}")
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Interface Streamlit                       │
│                  (ui/tabs/datasets_tab.py)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    DatasetManager                            │
│              (utils/dataset_manager.py)                      │
│                                                              │
│  - load_to_virtuoso()     - save_metadata()                 │
│  - load_to_fuseki()       - update_env_file()               │
│  - validate_dataset()     - clear_dataset()                 │
│  - get_statistics()       - load_metadata()                 │
└────┬───────────────┬───────────────┬────────────────────────┘
     │               │               │
     ▼               ▼               ▼
┌─────────┐  ┌──────────────┐  ┌─────────┐
│Virtuoso │  │datasets_meta │  │  .env   │
│ SPARQL  │  │data.json     │  │  file   │
└─────────┘  └──────────────┘  └─────────┘
     │
     ▼
┌─────────┐
│  Fuseki │
│ SPARQL  │
└─────────┘
```

## Performances

### Temps de chargement estimés

| Dataset | Taille | Fichier | Virtuoso | Fuseki |
|---------|--------|---------|----------|--------|
| Generic | 10K    | 400 KB  | ~3s      | ~5s    |
| DBpedia | 10K    | 1.4 MB  | ~5s      | ~8s    |
| LUBM    | 10K    | 6.8 MB  | ~7s      | ~12s   |
| DBpedia | 100K   | 15 MB   | ~45s     | ~60s   |
| LUBM    | 100K   | 43 MB   | ~60s     | ~90s   |

*Les temps varient selon les ressources système disponibles*

## Changelog

### Version 2.0 (2025-10-30)
- ✅ Ajout de la sauvegarde persistante des métadonnées
- ✅ Mise à jour automatique du fichier .env
- ✅ Système de suppression sélective/globale
- ✅ Statistiques détaillées des datasets chargés
- ✅ Interface améliorée avec détails techniques
- ✅ Gestion complète du cycle de vie des datasets

### Version 1.0
- Chargement basique des datasets
- Validation simple
- Interface Streamlit initiale

## Support

Pour toute question ou problème :
1. Consultez ce guide
2. Vérifiez les logs dans `logs/sparql_platform.log`
3. Consultez la documentation de Virtuoso/Fuseki
4. Créez une issue sur le dépôt GitHub

---

**Auteur** : Système de Gestion SPARQL Performance Platform
**Version** : 2.0
**Date** : 2025-10-30
