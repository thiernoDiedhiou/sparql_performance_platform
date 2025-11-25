# 🚀 Prochaines Étapes - Guide Rapide

## 📍 Où en êtes-vous ?

Vous avez maintenant :
- ✅ Un système de gestion de datasets complet avec graphes nommés
- ✅ Un module de synchronisation adapté pour les graphes nommés
- ✅ Des outils de diagnostic et de nettoyage
- ✅ Documentation complète

**Mais** : Vos triplestores contiennent encore des graphes résiduels à nettoyer

---

## 🎯 Étape Suivante Immédiate : Nettoyage

### Pourquoi nettoyer ?

Actuellement, vous avez :
- **Virtuoso** : 32,484 triplets (10,000 utiles + 22,484 résiduels)
- **Fuseki** : 60,000 triplets (10,000 utiles + 50,000 résiduels)

Après le nettoyage :
- **Virtuoso** : 10,000 triplets (+ graphes système)
- **Fuseki** : 10,000 triplets

### Comment nettoyer ?

**Option 1 : Nettoyage Interactif (Recommandé)**

```powershell
python clean_graphs_interactive.py
```

**Workflow** :
1. Choisissez le triplestore (commencez par Virtuoso)
2. Le script liste tous les graphes avec leurs triplets
3. Identifiez le graphe actif : `http://example.org/dataset_DBpedia_10K_1761840524`
4. Sélectionnez manuellement les graphes à supprimer (tous sauf l'actif)
5. Confirmez la suppression
6. Vérifiez avec `python diagnostic_datasets.py`
7. Répétez pour Fuseki

**Graphe à CONSERVER** :
```
http://example.org/dataset_DBpedia_10K_1761840524
```
Ce graphe contient `1761840524` dans son URI (= timestamp du chargement)

**Option 2 : Nettoyage via l'Interface**

Dans Streamlit (onglet Datasets), vous pouvez :
- Voir les statistiques actuelles
- Utiliser le bouton "Nettoyer" pour chaque triplestore

---

## 🧪 Étape 2 : Tester la Synchronisation

Après le nettoyage, testez le nouveau système :

```powershell
python test_named_graphs_sync.py
```

Ce script va :
- ✅ Vérifier le comptage par graphe
- ✅ Comparer Virtuoso et Fuseki
- ✅ Valider la rétrocompatibilité

**Résultat attendu** : 3/3 tests réussis

---

## 🔄 Étape 3 : Synchroniser (Optionnel)

Si vous voulez que Fuseki ait les mêmes données que Virtuoso avec les graphes nommés :

```python
from utils.data_synchronizer_v2 import DataSynchronizer
from utils.dataset_manager import DatasetManager

# 1. Récupérer le graph_uri du dataset Virtuoso
dm = DatasetManager()
virt_meta = dm.get_loaded_dataset_info('virtuoso')
graph_uri = virt_meta['graph_uri']

# 2. Synchroniser
sync = DataSynchronizer(
    "http://localhost:8890/sparql",
    "http://localhost:3030/dataset/query"
)

success = sync.synchronize_datasets(
    source_graph_uri=graph_uri,
    target_graph_uri=graph_uri
)

print(f"✅ Synchronisation réussie" if success else "❌ Échec")
```

---

## 📊 Étape 4 : Vérification Finale

```powershell
python diagnostic_datasets.py
```

**État final attendu** :

```
VIRTUOSO
  • Graphes de dataset : 1
  • Triplets de dataset : 10,000
  • Graphes système : 3
  ✅ Propre

FUSEKI
  • Graphes de dataset : 1
  • Triplets de dataset : 10,000
  ✅ Propre
```

---

## 💡 Utilisation Quotidienne

### Charger un Nouveau Dataset

1. **Via l'interface Streamlit** (Recommandé)
   ```powershell
   streamlit run main_v2.py
   ```
   - Onglet "📦 Datasets"
   - Sélectionner dataset et taille
   - Choisir le triplestore cible
   - Cliquer sur "Charger"

2. **Via Python**
   ```python
   from utils.dataset_manager import DatasetManager

   dm = DatasetManager()
   success, msg, graph_uri, count = dm.load_dataset(
       dataset_file="datasets/DBpedia/10K.ttl",
       dataset_name="DBpedia",
       size="10K",
       target="virtuoso"
   )
   ```

### Synchroniser les Triplestores

```python
from utils.data_synchronizer_v2 import DataSynchronizer

sync = DataSynchronizer(virtuoso_url, fuseki_url)

# Avec graphes nommés (nouveau)
sync.synchronize_datasets(
    source_graph_uri=graph_uri,
    target_graph_uri=graph_uri
)

# Sans graphes (ancien comportement)
sync.synchronize_datasets()
```

### Nettoyer un Dataset

```python
dm = DatasetManager()

# Nettoyer Virtuoso
success, msg = dm.clear_dataset(
    target="virtuoso",
    endpoint="http://localhost:8890/sparql",
    username="SPARQL",
    password="admin123"
)

# Nettoyer Fuseki
success, msg = dm.clear_dataset(
    target="fuseki",
    endpoint="http://localhost:3030/dataset"
)
```

---

## 🔧 Commandes Utiles

### Diagnostic
```powershell
# État complet des triplestores
python diagnostic_datasets.py

# Tests de synchronisation
python test_named_graphs_sync.py
```

### Nettoyage
```powershell
# Interactif (recommandé)
python clean_graphs_interactive.py

# Automatique (nécessite métadonnées)
python clean_old_graphs.py
```

### Interface
```powershell
# Lancer l'application
streamlit run main_v2.py
```

---

## 📚 Documentation

### Guides Principaux
- [SESSION_SUMMARY_2025-10-30.md](SESSION_SUMMARY_2025-10-30.md) - Résumé complet de ce qui a été fait
- [CLEANUP_GUIDE.md](CLEANUP_GUIDE.md) - Guide détaillé de nettoyage
- [NAMED_GRAPHS_SYNC_UPDATE.md](NAMED_GRAPHS_SYNC_UPDATE.md) - Détails techniques de la synchronisation

### Guides Précédents
- [README_DATASETS.md](README_DATASETS.md) - Guide d'utilisation des datasets
- [DATASETS_MANAGEMENT.md](DATASETS_MANAGEMENT.md) - Documentation API complète
- [RESOLUTION_INCOHERENCES.md](RESOLUTION_INCOHERENCES.md) - Troubleshooting

---

## ⚠️ Points d'Attention

### Graphes à Ne JAMAIS Supprimer

**Virtuoso** :
- `http://www.openlinksw.com/schemas/virtrdf#` (système)
- `http://www.w3.org/ns/ldp#` (système)
- `urn:activitystreams-owl:map` (système)
- Votre graphe actif (avec le timestamp récent)

**Fuseki** :
- Votre graphe actif uniquement

### En Cas de Problème

1. **Les services ne répondent pas**
   ```powershell
   # Vérifier Virtuoso
   curl http://localhost:8890/sparql?query=SELECT%20(COUNT(*)%20AS%20?count)%20WHERE%20{%20?s%20?p%20?o%20}

   # Vérifier Fuseki
   curl http://localhost:3030/dataset/query?query=SELECT%20(COUNT(*)%20AS%20?count)%20WHERE%20{%20?s%20?p%20?o%20}
   ```

2. **Erreurs de permissions Virtuoso**
   ```sql
   isql 1111 dba dba
   GRANT SPARQL_UPDATE TO "SPARQL";
   ```

3. **Métadonnées incohérentes**
   - Supprimer `datasets_metadata.json`
   - Recharger le dataset via l'interface
   - Les métadonnées seront recréées automatiquement

---

## 🎯 Checklist Rapide

Avant de commencer à utiliser le système en production :

- [ ] Nettoyer les graphes résiduels (Virtuoso)
- [ ] Nettoyer les graphes résiduels (Fuseki)
- [ ] Vérifier avec `diagnostic_datasets.py`
- [ ] Tester avec `test_named_graphs_sync.py`
- [ ] Charger un dataset de test via l'interface
- [ ] Vérifier que les métadonnées sont créées
- [ ] Tester la synchronisation
- [ ] Vérifier le `.env` mis à jour

---

## 🚀 Démarrage Rapide

**Si vous voulez juste commencer maintenant** :

```powershell
# 1. Nettoyer
python clean_graphs_interactive.py

# 2. Vérifier
python diagnostic_datasets.py

# 3. Lancer l'interface
streamlit run main_v2.py
```

C'est parti ! 🎉

---

**Date** : 30 Octobre 2025
**Statut** : Prêt à utiliser
**Version** : 2.1

💡 **Conseil** : Commencez par le nettoyage, c'est la base pour un système propre !
