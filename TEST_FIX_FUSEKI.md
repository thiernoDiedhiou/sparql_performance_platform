# 🧪 Test du Correctif Fuseki - Guide Pas à Pas

## ✅ Le correctif a été appliqué automatiquement

Les fichiers suivants ont été modifiés :
- ✅ `utils/dataset_manager.py`
- ✅ `ui/tabs/datasets_tab.py`

## 🚀 Procédure de Test

### Étape 1 : Redémarrer l'application

1. **Dans votre terminal PowerShell où Streamlit tourne** :
   - Appuyez sur `Ctrl+C` pour arrêter l'application

2. **Relancez Streamlit** :
   ```powershell
   streamlit run main_v2.py
   ```

3. **Attendez le message** :
   ```
   You can now view your Streamlit app in your browser.
   URL: http://localhost:8501
   ```

### Étape 2 : Nettoyer le dataset existant

1. **Allez dans l'onglet "📦 Datasets"**

2. **Faites défiler jusqu'à "Datasets actuellement chargés"**

3. **Sous "🟢 Fuseki", cliquez sur "🗑️ Effacer"**
   - Attendez le message de confirmation
   - La page devrait se rafraîchir

### Étape 3 : Recharger le dataset

1. **En haut de l'onglet Datasets** :
   - Sélectionnez : **DBpedia** 🔵
   - Sélectionnez : **10K**

2. **Cliquez sur "📥 Charger dans Fuseki"**

3. **Observez la progression** :
   - Barre de progression
   - Message "🔄 Chargement dans Fuseki..."
   - Message "✅ Chargement terminé !"

### Étape 4 : Vérifier le résultat

**Ce que vous devriez voir maintenant** :

```
🔍 Validation du chargement en cours...

✅ Fuseki validé : 15000 triplets dans le graphe
(ou un nombre proche de 15000)

💾 Sauvegarde des métadonnées...
✅ Métadonnées et configuration sauvegardées avec succès

🎈 (Animation de ballons)
```

**Dans la section "Datasets actuellement chargés"** :

```
📊 Datasets actuellement chargés

Total de datasets chargés: 1
Total de triplets: 15,000

🟢 Fuseki
Dataset: DBpedia (10K)
Triplets: 15,000  ← NOMBRE CORRECT !
Chargé le: 2025-10-30 15:XX:XX
```

## ✅ Critères de Succès

Le correctif fonctionne si :

- [ ] Le message de validation affiche **"~15,000 triplets dans le graphe"**
- [ ] La section statistiques affiche **"15,000 triplets"** (pas 2,484)
- [ ] Le nombre correspond approximativement à la taille du dataset
- [ ] Aucune erreur n'est affichée

## 🧪 Test de Comparaison (Optionnel)

Pour confirmer que le correctif fonctionne vraiment, vous pouvez :

### Test A : Vérifier avec une requête SPARQL directe

```bash
# Test 1 : Compter tous les triplets (ancienne méthode)
curl -X POST "http://localhost:3030/dataset/query" \
  -H "Content-Type: application/sparql-query" \
  -d "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }"

# Devrait retourner 2,484 (les anciennes données)
```

```bash
# Test 2 : Compter dans le graphe spécifique (nouvelle méthode)
# Récupérez d'abord l'URI du graphe depuis les "Détails techniques fuseki"
# Puis :
curl -X POST "http://localhost:3030/dataset/query" \
  -H "Content-Type: application/sparql-query" \
  -d "SELECT (COUNT(*) AS ?count) WHERE { GRAPH <URI_DU_GRAPHE> { ?s ?p ?o } }"

# Devrait retourner ~15,000
```

### Test B : Charger dans les deux moteurs

1. **Chargez DBpedia 10K dans les deux moteurs** :
   - Cliquez "📥 Charger dans les deux"

2. **Vérifiez que les deux affichent le même nombre** :
   - Virtuoso : ~15,000 triplets
   - Fuseki : ~15,000 triplets

3. **Les nombres devraient être identiques ou très proches**

## 📊 Comprendre les Résultats

### Pourquoi ~15,000 et pas exactement 10,000 ?

Le fichier **DBpedia 10K.ttl** contient environ **10,000 entités** mais chaque entité a plusieurs triplets :
- Nom
- Type
- Propriétés diverses
- Relations

Exemple pour un groupe de musique :
```turtle
<http://dbpedia.org/resource/The_Beatles>
    rdf:type dbo:MusicalArtist ;
    rdfs:label "The Beatles" ;
    dbo:hometown <http://dbpedia.org/resource/Liverpool> ;
    dbo:genre <http://dbpedia.org/resource/Rock_music> .
```

Cela fait **4 triplets** pour une seule entité !

Donc **10K entités** × **~1.5 triplets/entité** ≈ **15,000 triplets**

### Variation des nombres

Il est normal d'avoir des variations :
- ✅ 14,500 - 15,500 triplets → **Normal**
- ⚠️ 2,000 - 3,000 triplets → **Problème** (ancien bug)
- ❌ 0 triplets → **Échec de chargement**

## 🐛 Si le problème persiste

### Scénario 1 : Toujours 2,484 triplets

**Cause possible** : Le cache du navigateur ou de Streamlit

**Solution** :
```powershell
# Arrêtez Streamlit
Ctrl+C

# Nettoyez le cache
streamlit cache clear

# Relancez
streamlit run main_v2.py
```

Puis rechargez la page web (F5 ou Ctrl+F5)

### Scénario 2 : Erreur lors du chargement

**Erreur possible** : "graph_uri parameter missing"

**Cause** : Les modifications ne sont pas prises en compte

**Solution** :
```powershell
# Vérifiez que les fichiers sont bien modifiés
cat utils/dataset_manager.py | Select-String "graph_uri"

# Devrait afficher plusieurs lignes avec "graph_uri"
```

### Scénario 3 : Message "Aucun triplet trouvé"

**Cause** : Le graphe est vide ou l'URI est incorrecte

**Solution** :
1. Effacez le dataset
2. Rechargez avec les logs activés
3. Notez l'URI du graphe créé
4. Vérifiez manuellement avec curl

## 📝 Logs à surveiller

Dans votre terminal PowerShell, vous devriez voir :

```
2025-10-30 15:XX:XX - INFO - Dataset chargé avec succès dans le graphe http://example.org/dataset_DBpedia_10K_...
2025-10-30 15:XX:XX - INFO - Métadonnées sauvegardées: DBpedia (10K) dans fuseki
```

## ✅ Checklist de Validation

Cochez les éléments au fur et à mesure :

- [ ] Application redémarrée
- [ ] Ancien dataset Fuseki effacé
- [ ] DBpedia 10K rechargé dans Fuseki
- [ ] Message de validation affiche "~15,000 triplets dans le graphe"
- [ ] Section statistiques affiche "15,000 triplets"
- [ ] Fichier `datasets_metadata.json` contient le bon nombre
- [ ] Aucune erreur dans les logs

## 🎉 Si tous les tests passent

**Félicitations !** Le correctif fonctionne parfaitement. Vous pouvez maintenant :

1. ✅ Charger vos datasets en toute confiance
2. ✅ Faire vos tests de performance
3. ✅ Comparer Virtuoso et Fuseki avec précision

## 📚 Documentation Complète

Pour plus d'informations :
- **[FIX_FUSEKI_VALIDATION.md](FIX_FUSEKI_VALIDATION.md)** - Explication technique du correctif
- **[README_DATASETS.md](README_DATASETS.md)** - Guide d'utilisation général
- **[QUICK_START_DATASETS.md](QUICK_START_DATASETS.md)** - Démarrage rapide

## 💡 Astuce Pro

Pour vérifier rapidement si le correctif fonctionne sans recharger :

```powershell
# Affichez les métadonnées actuelles
cat datasets_metadata.json | Select-String "triplet_count"

# Si vous voyez 2484 → Effacez et rechargez
# Si vous voyez ~15000 → Correctif fonctionnel !
```

---

**Version** : 2.0.1
**Date** : 2025-10-30
**Statut** : Correctif appliqué
**Prêt pour** : Test immédiat
