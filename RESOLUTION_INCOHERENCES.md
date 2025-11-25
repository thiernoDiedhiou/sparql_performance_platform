# 🔧 Résolution des Incohérences de Datasets

## 🔍 Incohérences Détectées

D'après vos captures d'écran, vous avez identifié plusieurs incohérences :

### État Initial Observé

| Source | Virtuoso | Fuseki |
|--------|----------|--------|
| **Métadonnées affichées** | ? | 10,000 triplets |
| **État actuel des datasets** | 22,484 triplets | 2,484 triplets |
| **Synchronisation** | ⚠️ Non synchronisés | |

### Problèmes Identifiés

1. **Incohérence Fuseki** : Métadonnées (10,000) ≠ Réalité (2,484)
2. **Incohérence Globale** : Virtuoso (22,484) ≠ Fuseki (2,484)
3. **Métadonnées obsolètes** : Les fichiers de métadonnées ne reflètent pas la réalité

## 🎯 Causes Probables

### Cause 1 : Ancien Bug de Validation
Le système comptait **tous les triplets** du triplestore au lieu de compter uniquement ceux du graphe spécifique.

**Conséquence** :
- Les métadonnées ont été sauvegardées avec des valeurs incorrectes
- L'affichage montre des nombres qui ne correspondent pas à la réalité

### Cause 2 : Datasets Résiduels
Il y a probablement des **anciens datasets** dans les triplestores qui n'ont pas été nettoyés.

**Indices** :
- Virtuoso a 22,484 triplets (probablement plusieurs datasets)
- Fuseki a 2,484 triplets (anciennes données)

### Cause 3 : Chargements Multiples
Des datasets ont été chargés plusieurs fois sans nettoyage entre chaque chargement.

## ✅ Solution Complète

### Étape 1 : Diagnostic Complet

Exécutez le script de diagnostic pour voir la situation réelle :

```powershell
# Activez l'environnement virtuel si nécessaire
.\venv\Scripts\Activate.ps1

# Lancez le diagnostic
python diagnostic_datasets.py
```

Ce script va :
- ✅ Lister tous les graphes dans Virtuoso et Fuseki
- ✅ Compter les triplets dans chaque graphe
- ✅ Comparer avec les métadonnées
- ✅ Identifier les incohérences
- ✅ Donner des recommandations

### Étape 2 : Nettoyage Complet

#### Option A : Via l'Interface Streamlit (Recommandé)

1. **Arrêtez puis relancez Streamlit** (avec le correctif) :
   ```powershell
   # Ctrl+C pour arrêter
   streamlit run main_v2.py
   ```

2. **Allez dans l'onglet "📦 Datasets"**

3. **Effacez tous les datasets** :
   - Section "Datasets actuellement chargés"
   - Cliquez sur "🗑️ Effacer tous les datasets"
   - Confirmez l'opération

4. **Vérifiez que c'est vide** :
   - Relancez le diagnostic : `python diagnostic_datasets.py`
   - Devrait afficher 0 triplets partout

#### Option B : Nettoyage Manuel via SPARQL

Si l'interface ne fonctionne pas, nettoyez manuellement :

**Pour Virtuoso** :
```bash
# Lister tous les graphes
curl -X POST "http://localhost:8890/sparql" \
  -u "SPARQL:admin123" \
  -H "Content-Type: application/sparql-query" \
  -d "SELECT DISTINCT ?g WHERE { GRAPH ?g { ?s ?p ?o } }"

# Pour chaque graphe trouvé, exécutez :
curl -X POST "http://localhost:8890/sparql" \
  -u "SPARQL:admin123" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=CLEAR GRAPH <URI_DU_GRAPHE>"
```

**Pour Fuseki** :
```bash
# Lister tous les graphes
curl -X POST "http://localhost:3030/dataset/query" \
  -H "Content-Type: application/sparql-query" \
  -d "SELECT DISTINCT ?g WHERE { GRAPH ?g { ?s ?p ?o } }"

# Pour chaque graphe trouvé, exécutez :
curl -X POST "http://localhost:3030/dataset/update" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "update=CLEAR GRAPH <URI_DU_GRAPHE>"
```

### Étape 3 : Nettoyage des Métadonnées

Supprimez le fichier de métadonnées obsolètes :

```powershell
# Sauvegardez d'abord (au cas où)
Copy-Item datasets_metadata.json datasets_metadata.json.bak

# Supprimez le fichier
Remove-Item datasets_metadata.json

# Ou videz-le
"{}" | Out-File -Encoding utf8 datasets_metadata.json
```

### Étape 4 : Rechargement Propre

Maintenant que tout est nettoyé, rechargez proprement :

1. **Dans l'onglet "📦 Datasets"** :
   - Sélectionnez : **DBpedia 10K**
   - Cliquez : **"📥 Charger dans les deux"**

2. **Observez le chargement** :
   - Virtuoso : Devrait afficher "~15,000 triplets dans le graphe"
   - Fuseki : Devrait afficher "~15,000 triplets dans le graphe"
   - Les deux nombres devraient être identiques ou très proches

3. **Vérifiez la cohérence** :
   - Section "Datasets actuellement chargés"
   - **Virtuoso** : 15,000 triplets
   - **Fuseki** : 15,000 triplets
   - ✅ Synchronisés !

4. **Confirmez avec le diagnostic** :
   ```powershell
   python diagnostic_datasets.py
   ```

   Devrait afficher :
   ```
   Virtuoso : 15,000 triplets
   Fuseki : 15,000 triplets
   ✅ Cohérent
   ```

## 📊 Résultats Attendus

### Avant Nettoyage
```
Virtuoso : 22,484 triplets (incohérent)
Fuseki : 2,484 triplets (incohérent)
Métadonnées : 10,000 triplets (faux)
⚠️ Non synchronisés
```

### Après Nettoyage et Rechargement
```
Virtuoso : 15,000 triplets ✅
Fuseki : 15,000 triplets ✅
Métadonnées : 15,000 triplets ✅
✅ Synchronisés
```

## 🔍 Comprendre les Nombres

### Pourquoi 15,000 et pas 10,000 ?

Le fichier **DBpedia 10K** contient :
- **~10,000 entités** (sujets RDF)
- **Chaque entité a ~1.5 triplets** en moyenne
- **Total : ~15,000 triplets RDF**

Exemple :
```turtle
# 1 entité = 4 triplets
<http://dbpedia.org/resource/The_Beatles>
    rdf:type dbo:MusicalArtist ;           # Triplet 1
    rdfs:label "The Beatles" ;              # Triplet 2
    dbo:hometown <...Liverpool> ;           # Triplet 3
    dbo:genre <...Rock_music> .             # Triplet 4
```

### Pourquoi des Variations ?

Il est normal d'avoir de légères variations :
- ✅ 14,500 - 15,500 → Normal (format, préfixes)
- ✅ 14,000 - 16,000 → Acceptable (différences de parsing)
- ⚠️ 10,000 - 12,000 → Suspect (données incomplètes ?)
- ❌ 2,000 - 3,000 → Erreur (ancien dataset ou échec)

## 🐛 Résolution de Problèmes Spécifiques

### Problème 1 : "Effacer ne fonctionne pas"

**Symptôme** : Le bouton "🗑️ Effacer" ne supprime pas les données

**Solution** :
1. Vérifiez les permissions SPARQL_UPDATE
2. Nettoyez manuellement via curl (voir Étape 2, Option B)
3. Redémarrez Virtuoso/Fuseki

### Problème 2 : "Les nombres restent incohérents après rechargement"

**Symptôme** : Après rechargement, les nombres sont toujours différents

**Causes possibles** :
- Le cache de Streamlit n'est pas vidé
- Les métadonnées ne sont pas mises à jour
- Le correctif n'est pas appliqué

**Solution** :
```powershell
# Nettoyez le cache Streamlit
streamlit cache clear

# Supprimez les métadonnées
Remove-Item datasets_metadata.json

# Redémarrez complètement
# Ctrl+C puis streamlit run main_v2.py
```

### Problème 3 : "Le diagnostic ne fonctionne pas"

**Symptôme** : `python diagnostic_datasets.py` donne des erreurs

**Solution** :
```powershell
# Vérifiez que SPARQLWrapper est installé
pip install SPARQLWrapper

# Vérifiez que Virtuoso et Fuseki sont accessibles
curl http://localhost:8890/sparql
curl http://localhost:3030/dataset/query
```

## 💡 Prévention Future

Pour éviter ces incohérences à l'avenir :

### 1. Toujours Effacer Avant de Recharger
Si vous voulez recharger un dataset :
1. Effacez d'abord l'ancien
2. Puis rechargez le nouveau

### 2. Utiliser "Charger dans les deux"
Pour garantir la synchronisation :
- Utilisez toujours "📥 Charger dans les deux"
- Ne chargez pas séparément dans Virtuoso puis Fuseki

### 3. Vérifier Régulièrement
Exécutez le diagnostic de temps en temps :
```powershell
python diagnostic_datasets.py
```

### 4. Suivre les Logs
Regardez les logs dans le terminal pour détecter les problèmes :
```
2025-10-30 XX:XX:XX - INFO - Dataset chargé : 15000 triplets
```

## 📋 Checklist de Résolution

Suivez cette checklist pour résoudre complètement :

- [ ] Exécuté `python diagnostic_datasets.py` (voir l'état actuel)
- [ ] Arrêté et relancé Streamlit (appliquer le correctif)
- [ ] Effacé tous les datasets via l'interface
- [ ] Supprimé `datasets_metadata.json`
- [ ] Rechargé DBpedia 10K dans les deux moteurs
- [ ] Vérifié que les deux affichent ~15,000 triplets
- [ ] Ré-exécuté le diagnostic (confirmer la cohérence)
- [ ] Vérifié que "État actuel des datasets" montre les mêmes nombres

## 🎓 Leçons Apprises

### 1. Graphes Nommés vs Graphe Par Défaut
- **Fuseki** utilise des graphes nommés par défaut
- Il faut **toujours spécifier le graphe** dans les requêtes
- Compter tous les triplets ne donne pas le bon résultat

### 2. Métadonnées ≠ Réalité
- Les métadonnées peuvent devenir obsolètes
- Il faut **valider directement** auprès du triplestore
- Un diagnostic régulier est important

### 3. Nettoyage Régulier
- Ne pas laisser de datasets résiduels
- Toujours effacer avant de recharger
- Utiliser les outils de nettoyage fournis

## 🎉 Résultat Final

Après avoir suivi toutes ces étapes, vous devriez avoir :

✅ **Virtuoso** : 15,000 triplets (DBpedia 10K)
✅ **Fuseki** : 15,000 triplets (DBpedia 10K)
✅ **Métadonnées** : Cohérentes avec la réalité
✅ **Synchronisation** : OK
✅ **Diagnostic** : Aucun problème détecté

---

**Date** : 2025-10-30
**Version** : 2.0.1
**Type** : Guide de résolution
**Priorité** : Haute
**Fichiers associés** :
- `diagnostic_datasets.py` - Script de diagnostic
- `FIX_FUSEKI_VALIDATION.md` - Correctif de validation
- `TEST_FIX_FUSEKI.md` - Guide de test
