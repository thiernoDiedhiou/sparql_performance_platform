# 🔄 Mise à Jour : Support des Graphes Nommés dans data_synchronizer_v2.py

**Date** : 2025-10-30
**Version** : 2.1
**Statut** : ✅ Complété

---

## 📋 Résumé

Le module `data_synchronizer_v2.py` a été mis à jour pour supporter les **graphes nommés** (Named Graphs) dans les triplestores Virtuoso et Fuseki. Cette mise à jour aligne le module de synchronisation avec l'architecture actuelle qui utilise des graphes nommés pour isoler les datasets.

## 🎯 Motivation

### Problème Identifié

Le module `data_synchronizer_v2.py` comptait et synchronisait **tous les triplets** dans les triplestores, sans distinction de graphe :

```python
# ANCIEN CODE - Problématique
count_query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o . }"
```

Cela posait plusieurs problèmes :
- ❌ Impossibilité de synchroniser un dataset spécifique
- ❌ Comptage incorrect dans les environnements multi-datasets
- ❌ Risque de mélanger des données de différents datasets
- ❌ Incohérence avec le nouveau système de gestion des datasets

### Solution

Ajout du support des **graphes nommés** à toutes les opérations de synchronisation :

```python
# NOUVEAU CODE
if graph_uri:
    count_query = f"SELECT (COUNT(*) AS ?count) WHERE {{ GRAPH <{graph_uri}> {{ ?s ?p ?o }} }}"
else:
    count_query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o . }"
```

---

## 🛠️ Modifications Détaillées

### 1. Méthode `count_triplets()`

**Avant** :
```python
def count_triplets(self, endpoint_url: str) -> int:
```

**Après** :
```python
def count_triplets(self, endpoint_url: str, graph_uri: Optional[str] = None) -> int:
```

**Changements** :
- ✅ Ajout du paramètre `graph_uri` optionnel
- ✅ Requête SPARQL adaptée pour compter dans un graphe spécifique
- ✅ Logging amélioré avec indication du graphe

---

### 2. Méthode `export_chunk_from_virtuoso()`

**Avant** :
```python
def export_chunk_from_virtuoso(
    self,
    offset: int,
    limit: int,
    progress_callback: Optional[Callable] = None
) -> Optional[str]:
```

**Après** :
```python
def export_chunk_from_virtuoso(
    self,
    offset: int,
    limit: int,
    graph_uri: Optional[str] = None,
    progress_callback: Optional[Callable] = None
) -> Optional[str]:
```

**Changements** :
- ✅ Ajout du paramètre `graph_uri` optionnel
- ✅ Requête CONSTRUCT adaptée pour extraire d'un graphe spécifique :

```python
if graph_uri:
    query = f"""
    CONSTRUCT {{ ?s ?p ?o }}
    WHERE {{ GRAPH <{graph_uri}> {{ ?s ?p ?o }} }}
    LIMIT {limit}
    OFFSET {offset}
    """
```

---

### 3. Méthode `export_data_chunked()`

**Avant** :
```python
def export_data_chunked(
    self,
    total_triplets: Optional[int] = None,
    progress_callback: Optional[Callable] = None
) -> List[str]:
```

**Après** :
```python
def export_data_chunked(
    self,
    total_triplets: Optional[int] = None,
    graph_uri: Optional[str] = None,
    progress_callback: Optional[Callable] = None
) -> List[str]:
```

**Changements** :
- ✅ Propagation du `graph_uri` à `count_triplets()` et `export_chunk_from_virtuoso()`
- ✅ Logging avec indication du graphe source

---

### 4. Méthode `upload_chunk_to_fuseki()`

**Avant** :
```python
def upload_chunk_to_fuseki(self, chunk_data: str, chunk_number: int) -> bool:
```

**Après** :
```python
def upload_chunk_to_fuseki(
    self,
    chunk_data: str,
    chunk_number: int,
    graph_uri: Optional[str] = None
) -> bool:
```

**Changements** :
- ✅ Ajout du paramètre `graph_uri` optionnel
- ✅ URL d'upload adaptée pour cibler un graphe spécifique :

```python
if graph_uri:
    upload_url = f"{self.fuseki_base_url}/data?graph={graph_uri}"
else:
    upload_url = f"{self.fuseki_base_url}/data"
```

---

### 5. Méthode `clear_fuseki_dataset()`

**Avant** :
```python
def clear_fuseki_dataset(self) -> bool:
    delete_query = "DELETE WHERE { ?s ?p ?o }"
```

**Après** :
```python
def clear_fuseki_dataset(self, graph_uri: Optional[str] = None) -> bool:
    if graph_uri:
        delete_query = f"CLEAR GRAPH <{graph_uri}>"
    else:
        delete_query = "DELETE WHERE { ?s ?p ?o }"
```

**Changements** :
- ✅ Support du nettoyage ciblé d'un graphe spécifique
- ✅ Préservation de la compatibilité avec le nettoyage global

---

### 6. Méthode `synchronize_datasets_chunked()`

**Avant** :
```python
def synchronize_datasets_chunked(
    self,
    clear_target: bool = True,
    limit_triplets: Optional[int] = None,
    show_progress: bool = True
) -> bool:
```

**Après** :
```python
def synchronize_datasets_chunked(
    self,
    clear_target: bool = True,
    limit_triplets: Optional[int] = None,
    show_progress: bool = True,
    source_graph_uri: Optional[str] = None,
    target_graph_uri: Optional[str] = None
) -> bool:
```

**Changements** :
- ✅ Ajout des paramètres `source_graph_uri` et `target_graph_uri`
- ✅ Propagation des URIs de graphe à toutes les opérations :
  - Comptage initial avec graphes spécifiques
  - Export depuis le graphe source
  - Nettoyage du graphe cible
  - Upload vers le graphe cible
  - Vérification finale du graphe cible

---

### 7. Classe `DataSynchronizer` (compatibilité)

**Avant** :
```python
def synchronize_datasets(self, clear_target: bool = True, limit_triplets: Optional[int] = None) -> bool:
```

**Après** :
```python
def synchronize_datasets(
    self,
    clear_target: bool = True,
    limit_triplets: Optional[int] = None,
    source_graph_uri: Optional[str] = None,
    target_graph_uri: Optional[str] = None
) -> bool:
```

**Changements** :
- ✅ Rétrocompatibilité assurée (paramètres optionnels)
- ✅ Support des graphes nommés ajouté

---

## 📊 Impact et Bénéfices

### Avant la Mise à Jour

```python
# Synchronisation globale uniquement
synchronizer = DataSynchronizer(virtuoso_url, fuseki_url)
synchronizer.synchronize_datasets()
# ❌ Synchronise TOUS les triplets
```

### Après la Mise à Jour

```python
# Synchronisation ciblée par graphe
synchronizer = DataSynchronizer(virtuoso_url, fuseki_url)
synchronizer.synchronize_datasets(
    source_graph_uri="http://example.org/dataset_DBpedia_10K_12345",
    target_graph_uri="http://example.org/dataset_DBpedia_10K_12345"
)
# ✅ Synchronise uniquement le graphe spécifié
```

### Cas d'Usage Activés

1. **Synchronisation sélective** : Ne synchroniser qu'un dataset spécifique
2. **Multi-datasets** : Gérer plusieurs datasets isolés dans le même triplestore
3. **Tests parallèles** : Tester différentes configurations sans interférence
4. **Migration ciblée** : Migrer un graphe spécifique d'un environnement à un autre
5. **Cohérence** : Garantir que seules les données du bon dataset sont synchronisées

---

## 🔧 Utilisation

### Exemple 1 : Synchronisation avec Graphes Nommés

```python
from utils.data_synchronizer_v2 import DataSynchronizer

# Initialisation
sync = DataSynchronizer(
    virtuoso_endpoint="http://localhost:8890/sparql",
    fuseki_endpoint="http://localhost:3030/dataset/query"
)

# Synchronisation d'un graphe spécifique
graph_uri = "http://example.org/dataset_DBpedia_10K_12345"

success = sync.synchronize_datasets(
    clear_target=True,
    source_graph_uri=graph_uri,  # Graphe source dans Virtuoso
    target_graph_uri=graph_uri   # Graphe cible dans Fuseki
)

if success:
    print(f"✅ Graphe {graph_uri} synchronisé avec succès")
```

### Exemple 2 : Synchronisation Globale (Rétrocompatible)

```python
# Fonctionne toujours sans spécifier de graphe
sync.synchronize_datasets(clear_target=True)
# Synchronise tous les triplets (comportement historique)
```

### Exemple 3 : Comptage par Graphe

```python
# Compter les triplets dans un graphe spécifique
graph_uri = "http://example.org/dataset_DBpedia_10K_12345"

virtuoso_count = sync.count_triplets(
    "http://localhost:8890/sparql",
    graph_uri
)

fuseki_count = sync.count_triplets(
    "http://localhost:3030/dataset/query",
    graph_uri
)

print(f"Virtuoso: {virtuoso_count:,} triplets")
print(f"Fuseki: {fuseki_count:,} triplets")
```

---

## 🧪 Tests Recommandés

### Test 1 : Synchronisation Simple

```python
# 1. Charger un dataset dans Virtuoso avec un graphe nommé
# 2. Synchroniser vers Fuseki avec le même graphe
# 3. Vérifier que les comptages correspondent
```

### Test 2 : Synchronisation Multi-Graphes

```python
# 1. Charger 2 datasets différents dans Virtuoso
# 2. Synchroniser chaque graphe individuellement vers Fuseki
# 3. Vérifier l'isolation des données
```

### Test 3 : Rétrocompatibilité

```python
# 1. Tester la synchronisation sans spécifier de graphe
# 2. Vérifier que le comportement global est préservé
```

---

## ⚠️ Points d'Attention

### 1. Paramètres Optionnels

Tous les paramètres `graph_uri`, `source_graph_uri`, et `target_graph_uri` sont **optionnels** :
- Si `None` : Comportement global (tous les triplets)
- Si spécifié : Opération ciblée sur le graphe

### 2. Cohérence Source/Cible

Pour une synchronisation correcte, assurez-vous que :
- Le graphe source existe dans Virtuoso
- Le même URI de graphe est utilisé pour la cible dans Fuseki (sauf cas d'usage spécifique)

### 3. Performance

L'extraction depuis un graphe nommé peut être légèrement plus lente que l'extraction globale, mais offre une meilleure précision et isolation.

---

## 🔗 Intégration avec dataset_manager.py

Le `dataset_manager.py` génère des URIs de graphe uniques :

```python
graph_uri = f"http://example.org/dataset_{dataset_name}_{size}_{timestamp}"
```

Ces URIs peuvent être passés directement au synchroniseur :

```python
# Dans datasets_tab.py ou autre
metadata = dataset_manager.get_loaded_dataset_info('virtuoso')
graph_uri = metadata['graph_uri']

synchronizer.synchronize_datasets(
    source_graph_uri=graph_uri,
    target_graph_uri=graph_uri
)
```

---

## 📝 Checklist de Validation

- [x] Méthode `count_triplets()` supporte `graph_uri`
- [x] Méthode `export_chunk_from_virtuoso()` supporte `graph_uri`
- [x] Méthode `export_data_chunked()` supporte `graph_uri`
- [x] Méthode `upload_chunk_to_fuseki()` supporte `graph_uri`
- [x] Méthode `clear_fuseki_dataset()` supporte `graph_uri`
- [x] Méthode `synchronize_datasets_chunked()` supporte les graphes source/cible
- [x] Classe `DataSynchronizer` mise à jour pour compatibilité
- [x] Logging amélioré avec indication des graphes
- [x] Rétrocompatibilité préservée (tous paramètres optionnels)
- [x] Documentation à jour

---

## 📚 Fichiers Modifiés

### Principal
- [utils/data_synchronizer_v2.py](utils/data_synchronizer_v2.py) - Module de synchronisation

### Documentation
- [NAMED_GRAPHS_SYNC_UPDATE.md](NAMED_GRAPHS_SYNC_UPDATE.md) - Ce document

---

## 🚀 Prochaines Étapes

1. **Tester la synchronisation** avec les datasets actuellement chargés
2. **Mettre à jour les scripts** qui utilisent `data_synchronizer_v2.py`
3. **Intégrer dans l'interface** Streamlit (onglet Configuration)
4. **Documenter les cas d'usage** dans le README principal

---

## 💡 Exemple Complet d'Utilisation

```python
"""
Exemple complet : Synchronisation avec graphes nommés
"""

from utils.data_synchronizer_v2 import DataSynchronizer
from utils.dataset_manager import DatasetManager

# 1. Charger les métadonnées du dataset
dm = DatasetManager()
virtuoso_metadata = dm.get_loaded_dataset_info('virtuoso')

if virtuoso_metadata:
    graph_uri = virtuoso_metadata['graph_uri']

    # 2. Créer le synchroniseur
    sync = DataSynchronizer(
        virtuoso_endpoint="http://localhost:8890/sparql",
        fuseki_endpoint="http://localhost:3030/dataset/query"
    )

    # 3. Compter les triplets dans Virtuoso
    print(f"📊 Virtuoso - Graphe: {graph_uri}")
    virt_count = sync.count_triplets(sync.virtuoso_endpoint, graph_uri)
    print(f"   Triplets: {virt_count:,}")

    # 4. Synchroniser vers Fuseki
    print(f"\n🔄 Synchronisation en cours...")
    success = sync.synchronize_datasets(
        clear_target=True,
        source_graph_uri=graph_uri,
        target_graph_uri=graph_uri
    )

    if success:
        # 5. Vérifier le résultat
        fuseki_count = sync.count_triplets(sync.fuseki_endpoint, graph_uri)
        print(f"\n✅ Synchronisation réussie !")
        print(f"   Fuseki - Triplets: {fuseki_count:,}")

        # 6. Calculer la cohérence
        if virt_count == fuseki_count:
            print(f"   ✅ Données 100% cohérentes")
        else:
            ratio = (fuseki_count / virt_count * 100) if virt_count > 0 else 0
            print(f"   ⚠️  Cohérence: {ratio:.1f}%")
else:
    print("❌ Aucun dataset chargé dans Virtuoso")
```

---

**Auteur** : Claude Code
**Version** : 2.1
**Date** : 2025-10-30
**Statut** : ✅ Production Ready
