# 🔧 Correction des Problèmes de Synchronisation

**Date**: 30 Octobre 2025
**Problèmes identifiés**:
1. Avertissement "datasets non synchronisés" incorrect
2. Synchronisation partielle (10% au lieu de 100%)

---

## 📋 Résumé des Problèmes

### Problème 1: Vérification de Synchronisation Incorrecte ✅ CORRIGÉ

**Symptôme**: L'interface affiche "Les datasets ne sont pas synchronisés" même quand ils le sont

**Cause**: La fonction `get_sync_status_summary()` dans [utils/helpers.py](utils/helpers.py) ne utilisait PAS les graphes nommés pour vérifier la synchronisation

**Code problématique**:
```python
# Ligne 666-667 (ancien code)
v_count = synchronizer.count_triplets(st.session_state['virtuoso_endpoint'])
f_count = synchronizer.count_triplets(st.session_state['fuseki_endpoint'])
```

Cela comptait les triplets **globalement** au lieu de compter dans les graphes nommés spécifiques.

**Résultat**:
- Virtuoso: 12,484 triplets (2,484 système + 10,000 dataset)
- Fuseki: 2,484 triplets (graphe par défaut seulement)
- Conclusion erronée: "Non synchronisés" ❌

**Solution**: Utiliser les `graph_uri` depuis les métadonnées

**Nouveau code** (lignes 667-675):
```python
# Charger les métadonnées pour obtenir les graph_uri
dataset_manager = DatasetManager(datasets_path="datasets")
metadata = dataset_manager.load_all_metadata()
virtuoso_graph_uri = metadata.get('virtuoso', {}).get('graph_uri') if metadata else None
fuseki_graph_uri = metadata.get('fuseki', {}).get('graph_uri') if metadata else None

# Compter les triplets dans les graphes nommés
v_count = synchronizer.count_triplets(st.session_state['virtuoso_endpoint'], virtuoso_graph_uri)
f_count = synchronizer.count_triplets(st.session_state['fuseki_endpoint'], fuseki_graph_uri)
```

**Impact**: ✅ La vérification fonctionne maintenant correctement avec les graphes nommés

---

### Problème 2: Synchronisation Partielle (10%) 🔍 EN INVESTIGATION

**Symptôme**: Seuls 10,001 triplets sur 100,000 sont synchronisés de Virtuoso vers Fuseki

**Observation**:
```
État initial:
  Virtuoso: 100,000 triplets dans le graphe
  Fuseki:   0 triplets dans le graphe

État final après synchronisation:
  Virtuoso: 100,000 triplets
  Fuseki:   10,001 triplets ⚠️
  Taux:     ~10%
```

**Contexte**:
- Dataset: LUBM 100K
- Graph URI: Utilisé correctement dans les deux sens
- Chunk size: 100,000 triplets (1 seul chunk devrait suffire)
- Méthode: `ChunkedDataSynchronizer`

**Hypothèses possibles**:
1. Export incomplet depuis Virtuoso (CONSTRUCT retourne moins de 100K)
2. Upload partiel vers Fuseki (données rejetées/tronquées)
3. Timeout silencieux pendant le transfert
4. Limite de taille dans Fuseki
5. Erreur de parsing/conversion des données

---

## 🔧 Corrections Appliquées

### 1. Fonction `get_sync_status_summary()` - ✅ CORRIGÉ

**Fichier**: [utils/helpers.py](utils/helpers.py)
**Lignes**: 643-694

**Changements**:
- Ajout de l'import `DatasetManager`
- Chargement des métadonnées pour obtenir les `graph_uri`
- Utilisation des `graph_uri` dans les comptages

**Avant**:
```python
v_count = synchronizer.count_triplets(st.session_state['virtuoso_endpoint'])
f_count = synchronizer.count_triplets(st.session_state['fuseki_endpoint'])
```

**Après**:
```python
dataset_manager = DatasetManager(datasets_path="datasets")
metadata = dataset_manager.load_all_metadata()
virtuoso_graph_uri = metadata.get('virtuoso', {}).get('graph_uri') if metadata else None
fuseki_graph_uri = metadata.get('fuseki', {}).get('graph_uri') if metadata else None

v_count = synchronizer.count_triplets(st.session_state['virtuoso_endpoint'], virtuoso_graph_uri)
f_count = synchronizer.count_triplets(st.session_state['fuseki_endpoint'], fuseki_graph_uri)
```

---

## 🧪 Outils de Diagnostic Créés

### 1. `diagnose_sync_issue.py` - Script de Diagnostic Complet

**Objectif**: Identifier où se produit la perte de données (export vs upload)

**Tests effectués**:
1. **TEST 1**: Taille du résultat CONSTRUCT depuis Virtuoso
   - Teste avec LIMIT croissants (10, 100, 1K, 10K, 100K)
   - Compte les lignes et la taille du résultat
   - Estime le nombre de triplets dans le Turtle
   - Sauvegarde le chunk 100K pour inspection manuelle

2. **TEST 2**: Capacité d'upload de Fuseki
   - Upload de tailles croissantes (10, 100, 1K, 10K)
   - Vérifie les codes HTTP
   - Compte les triplets après upload
   - Identifie les limites de Fuseki

3. **TEST 3**: État actuel du dataset
   - Compte les triplets dans les deux graphes
   - Calcule le pourcentage transféré
   - Identifie les triplets manquants

4. **TEST 4**: Export d'un chunk complet de 100K
   - Exporte un chunk de 100,000 triplets
   - Mesure la durée et la taille
   - Vérifie si le chunk est complet

**Utilisation**:
```bash
cd c:\Users\hp\Documents\M2\Web Semantique\Mémoire\Code_NV\sparql_v2
python diagnose_sync_issue.py
```

**Sortie attendue**: Identification du point de défaillance (export ou upload)

---

### 2. `test_sync_with_small_chunks.py` - Test avec Différentes Tailles de Chunk

**Objectif**: Trouver la taille de chunk optimale qui permet une synchronisation à 100%

**Tests effectués**:
- Teste avec chunk sizes: 10K, 25K, 50K, 100K
- Pour chaque taille:
  - Nettoie Fuseki
  - Exporte les chunks
  - Upload vers Fuseki
  - Vérifie le taux de réussite
- Compare les résultats et recommande le meilleur chunk size

**Utilisation**:
```bash
python test_sync_with_small_chunks.py
```

**Sortie attendue**: Recommandation du chunk size optimal

**Exemple de sortie**:
```
RÉSUMÉ COMPARATIF
================================================================================

Chunk Size      Chunks     Uploads    Taux       Durée
--------------------------------------------------------------------------------
    10,000          10          10      100.0%      45.2s
    25,000           4           4       99.8%      38.1s
    50,000           2           2       99.9%      35.5s
   100,000           1           1       10.0%      32.1s  ⚠️

RECOMMANDATION
================================================================================

✅ Meilleur chunk size: 10,000 triplets
   Taux de réussite: 100.0%
   Nombre de chunks: 10
   Durée: 45.2s

💡 Suggestion: Modifier SYNC_CHUNK_SIZE dans config/settings.py:
   SYNC_CHUNK_SIZE = 10000
```

---

## 📝 Prochaines Étapes

### Étape 1: Diagnostic Initial

Exécutez le script de diagnostic pour identifier le problème:

```bash
python diagnose_sync_issue.py
```

**Que chercher**:
- Le chunk exporté contient-il vraiment 100K triplets?
- Fuseki peut-il recevoir de gros uploads?
- À quel moment se produit la perte?

### Étape 2: Test avec Chunks Plus Petits

Si le diagnostic montre un problème avec les gros chunks:

```bash
python test_sync_with_small_chunks.py
```

**Que chercher**:
- Quelle taille de chunk donne 100% de réussite?
- Y a-t-il un seuil au-delà duquel ça échoue?

### Étape 3: Appliquer la Solution

Selon les résultats:

#### Solution A: Réduire le Chunk Size

Si les petits chunks fonctionnent mais pas les gros:

1. Modifiez [config/settings.py](config/settings.py) ligne 65:
   ```python
   # Avant
   SYNC_CHUNK_SIZE = 100000

   # Après (exemple avec 10K)
   SYNC_CHUNK_SIZE = 10000
   ```

2. Relancez la synchronisation dans l'interface

#### Solution B: Augmenter les Limites de Fuseki

Si le problème vient de Fuseki:

1. Éditez la configuration JVM de Fuseki:
   ```bash
   # Dans fuseki-server.bat ou fuseki-server
   set JAVA_OPTIONS=-Xmx4g -Xms2g
   ```

2. Redémarrez Fuseki

3. Relancez la synchronisation

#### Solution C: Export/Import Manuel

En dernier recours:

1. Exportez depuis Virtuoso:
   ```bash
   python -c "from diagnose_sync_issue import test_chunk_export; test_chunk_export()"
   ```

2. Uploadez manuellement vers Fuseki:
   ```bash
   curl -X POST http://localhost:3030/dataset/data?graph=<GRAPH_URI> \
     -H "Content-Type: text/turtle" \
     --data-binary @export_test_100k.ttl
   ```

---

## 🎯 Vérification Finale

Après avoir appliqué une solution, vérifiez que tout fonctionne:

### Test 1: Vérification de Synchronisation

1. Allez dans l'onglet "Configuration"
2. Cliquez sur "Tester la connectivité"
3. Vérifiez que les comptages sont corrects dans les graphes nommés
4. L'avertissement "datasets non synchronisés" ne devrait PLUS apparaître ✅

### Test 2: Synchronisation Complète

1. Allez dans la section "Synchronisation des données"
2. Cliquez sur "Synchroniser Virtuoso → Fuseki"
3. Vérifiez que:
   - Export réussi: X chunks
   - Upload réussi: X/X chunks
   - État final: 100,000 = 100,000 ✅
   - Taux: 100% ✅

### Test 3: Tests de Performance

1. Allez dans l'onglet "Configuration"
2. Sélectionnez quelques requêtes
3. Cliquez sur "Exécuter les tests"
4. Vérifiez que:
   - Pas d'avertissement de synchronisation ✅
   - Les tests s'exécutent correctement ✅
   - Les résultats sont cohérents ✅

---

## 📚 Documentation Associée

- [TRIPLESTORE_COUNTING_BEHAVIOR.md](TRIPLESTORE_COUNTING_BEHAVIOR.md) - Comportement des comptages
- [SYNC_ISSUE_INVESTIGATION.md](SYNC_ISSUE_INVESTIGATION.md) - Investigation détaillée
- [FIX_DATA_SYNC_UI.md](FIX_DATA_SYNC_UI.md) - Corrections de l'UI de synchronisation
- [FIX_CONNECTIVITY_TEST.md](FIX_CONNECTIVITY_TEST.md) - Corrections du test de connectivité

---

## ✅ Checklist de Résolution

### Problème 1: Vérification Incorrecte
- [x] Identifier la cause (comptage global au lieu de graphe nommé)
- [x] Corriger `get_sync_status_summary()` dans [utils/helpers.py](utils/helpers.py)
- [x] Tester la correction
- [ ] Valider avec l'utilisateur

### Problème 2: Synchronisation Partielle
- [x] Créer les scripts de diagnostic
- [x] Documenter le problème
- [ ] Exécuter les diagnostics
- [ ] Identifier la cause exacte
- [ ] Appliquer la solution
- [ ] Valider avec l'utilisateur

---

**Dernière mise à jour**: 30 Octobre 2025
**Statut Problème 1**: ✅ Corrigé
**Statut Problème 2**: 🔍 Scripts de diagnostic prêts - En attente d'exécution
