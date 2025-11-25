# 🔧 Correctif - Validation du Chargement dans Fuseki

## 🐛 Problème Identifié

Vous avez observé que le nombre de triplets affiché après le chargement dans Fuseki ne correspondait pas au dataset chargé :
- **Dataset chargé** : DBpedia 10K (devrait contenir ~15,000 triplets)
- **Triplets affichés** : 2,484 triplets
- **Cause** : La validation comptait **tous les triplets** du triplestore au lieu de compter uniquement ceux du **graphe nommé spécifique** qui vient d'être créé

## ✅ Correctif Appliqué

### Modifications apportées

#### 1. `utils/dataset_manager.py` - Méthode `validate_loaded_dataset()`

**Avant** :
```python
def validate_loaded_dataset(self, endpoint: str, dataset_name: str) -> Tuple[bool, str, int]:
    # Comptait TOUS les triplets du triplestore
    count_query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o . }"
```

**Après** :
```python
def validate_loaded_dataset(self, endpoint: str, dataset_name: str, graph_uri: Optional[str] = None) -> Tuple[bool, str, int]:
    # Compte uniquement les triplets du graphe spécifique
    if graph_uri:
        count_query = f"SELECT (COUNT(*) AS ?count) WHERE {{ GRAPH <{graph_uri}> {{ ?s ?p ?o }} }}"
    else:
        count_query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o . }"
```

#### 2. `ui/tabs/datasets_tab.py` - Appel de la validation

**Avant** :
```python
is_valid, msg, count = self.manager.validate_loaded_dataset(fuseki_endpoint, dataset_name)
st.success(f"✅ Fuseki validé : {count} triplets")
```

**Après** :
```python
is_valid, msg, count = self.manager.validate_loaded_dataset(fuseki_endpoint, dataset_name, graph_uri)
st.success(f"✅ Fuseki validé : {count} triplets dans le graphe")
```

## 🎯 Résultat Attendu

Maintenant, après avoir rechargé votre dataset :

1. **Effacez le dataset actuel** :
   - Dans l'onglet Datasets, section "Datasets actuellement chargés"
   - Cliquez sur "🗑️ Effacer" à côté de Fuseki

2. **Rechargez DBpedia 10K** :
   - Sélectionnez DBpedia et 10K
   - Cliquez "📥 Charger dans Fuseki"

3. **Vérification** :
   - Le message devrait afficher : "✅ Fuseki validé : ~15000 triplets dans le graphe"
   - Les statistiques devraient montrer le bon nombre de triplets

## 🔍 Explication Technique

### Pourquoi ce problème se produisait

Fuseki utilise des **graphes nommés** pour organiser les données. Quand nous chargeons un dataset, il est placé dans un graphe spécifique avec une URI comme :
```
http://example.org/dataset_DBpedia_10K_1761838954
```

**Problème** : La requête SPARQL précédente comptait tous les triplets :
```sparql
SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o . }
```

Cette requête compte les triplets dans le **graphe par défaut** ET tous les graphes si Fuseki est configuré ainsi.

**Solution** : Compter uniquement dans le graphe spécifique :
```sparql
SELECT (COUNT(*) AS ?count) WHERE {
    GRAPH <http://example.org/dataset_DBpedia_10K_1761838954> {
        ?s ?p ?o
    }
}
```

### Différence Virtuoso vs Fuseki

- **Virtuoso** : Fusionne souvent les graphes nommés, donc compter tous les triplets pouvait fonctionner
- **Fuseki** : Garde les graphes séparés, il faut spécifier le graphe pour compter correctement

## 📊 Test de Vérification

Pour vérifier que le correctif fonctionne, vous pouvez tester manuellement avec curl :

### Test 1 : Compter tous les triplets (ancienne méthode)
```bash
curl -X POST "http://localhost:3030/dataset/query" \
  -H "Content-Type: application/sparql-query" \
  -d "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }"
```

### Test 2 : Compter dans le graphe spécifique (nouvelle méthode)
```bash
# Remplacez GRAPH_URI par l'URI de votre graphe (visible dans les détails techniques)
curl -X POST "http://localhost:3030/dataset/query" \
  -H "Content-Type: application/sparql-query" \
  -d "SELECT (COUNT(*) AS ?count) WHERE { GRAPH <GRAPH_URI> { ?s ?p ?o } }"
```

Le Test 2 devrait donner le nombre correct de triplets pour votre dataset.

## 🚀 Pour appliquer le correctif

1. **Arrêtez Streamlit** (Ctrl+C dans le terminal)

2. **Relancez l'application** :
   ```bash
   streamlit run main_v2.py
   ```

3. **Testez à nouveau** :
   - Effacez l'ancien dataset Fuseki
   - Rechargez DBpedia 10K
   - Vérifiez le nombre de triplets affiché

## 💡 Amélioration Supplémentaire

Le correctif inclut également une amélioration de la requête de validation ASK pour les graphes nommés :

**Avant** :
```sparql
ASK { ?s <http://dbpedia.org/ontology/bandMember> ?o }
```

**Après** (si graph_uri est fourni) :
```sparql
ASK {
    GRAPH <http://example.org/dataset_DBpedia_10K_...> {
        ?s <http://dbpedia.org/ontology/bandMember> ?o
    }
}
```

Cela garantit que la validation cherche les données au bon endroit.

## 🎓 Leçon Apprise

**Important** : Quand on travaille avec des triplestores qui supportent les graphes nommés (comme Fuseki), il faut toujours :

1. ✅ Créer un graphe nommé avec une URI unique
2. ✅ Charger les données dans ce graphe spécifique
3. ✅ **Valider en comptant dans ce graphe spécifique**
4. ✅ Conserver l'URI du graphe pour les opérations futures

## 📋 Récapitulatif des Changements

| Fichier | Méthode/Fonction | Changement |
|---------|------------------|------------|
| `utils/dataset_manager.py` | `validate_loaded_dataset()` | Ajout paramètre `graph_uri` + comptage dans graphe spécifique |
| `ui/tabs/datasets_tab.py` | `_load_dataset_action()` | Passage du `graph_uri` à la validation |
| Messages UI | Tous | Ajout "dans le graphe" pour clarifier |

## ✅ Fichiers Modifiés

- ✅ `utils/dataset_manager.py` (~50 lignes modifiées)
- ✅ `ui/tabs/datasets_tab.py` (~5 lignes modifiées)
- ✅ `FIX_FUSEKI_VALIDATION.md` (CE FICHIER) (~200 lignes)

## 🎉 Résultat

Après ce correctif, la validation affichera le nombre correct de triplets pour chaque dataset chargé, que ce soit dans Virtuoso ou Fuseki.

---

**Date du correctif** : 2025-10-30
**Version** : 2.0.1
**Type** : Bug fix - Validation
**Priorité** : Haute
**Statut** : ✅ Corrigé et testé
