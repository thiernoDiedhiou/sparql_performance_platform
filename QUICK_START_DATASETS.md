# 🚀 Guide de Démarrage Rapide - Onglet Datasets

## ✅ Félicitations ! L'onglet Datasets est opérationnel

D'après vos logs, l'application fonctionne correctement. Voici comment utiliser l'onglet Datasets.

## 📍 Accès à l'onglet

1. **L'application est lancée** → ✅ (visible dans vos logs)
2. **Cliquez sur "📦 Datasets"** → 2ème onglet dans l'interface
3. **L'interface se charge** → ✅ (logs: "Dossier de datasets validé")

## 🎯 Premier test recommandé

### Test avec Generic 10K (le plus rapide)

1. **Dans l'onglet Datasets, sélectionnez** :
   - Dataset : **Generic** 🟡
   - Taille : **10K** ⚡

2. **Vérifiez les informations affichées** :
   - Taille du fichier : ~400 KB
   - Temps estimé : ~3-5 secondes
   - Mémoire requise : ~50 MB
   - ✅ Devrait afficher "Mémoire suffisante"

3. **Cliquez sur un bouton de chargement** :
   - "📥 Charger dans Virtuoso" (si Virtuoso est démarré)
   - OU "📥 Charger dans Fuseki" (si Fuseki est démarré)
   - OU "📥 Charger dans les deux"

4. **Observez la progression** :
   - Barre de progression s'affiche
   - Message "🔄 Chargement dans..."
   - Validation automatique
   - Message "💾 Sauvegarde des métadonnées..."

5. **Vérifiez le résultat** :
   - ✅ Message de succès "Dataset chargé avec succès"
   - ✅ Nombre de triplets affiché
   - 🎈 Animation de ballons

## 📊 Vérifier les métadonnées créées

Après le chargement, vérifiez les fichiers :

### 1. Fichier `datasets_metadata.json`
```bash
# Dans PowerShell
cat datasets_metadata.json
```

Vous devriez voir quelque chose comme :
```json
{
  "virtuoso": {
    "dataset_name": "Generic",
    "size": "10K",
    "graph_uri": "http://example.org/dataset_Generic_10K_...",
    "triplet_count": 10000,
    "loaded_at": "2025-10-30T15:45:00",
    "file_path": "datasets/Generic/10K.ttl"
  }
}
```

### 2. Fichier `.env` (section ajoutée)
```bash
# Dans PowerShell
tail -20 .env
```

Vous devriez voir une nouvelle section :
```env
# ==============================================================================
# CONFIGURATION DES DATASETS CHARGÉS (Auto-généré)
# ==============================================================================

CURRENT_DATASET_NAME=Generic
CURRENT_DATASET_SIZE=10K
CURRENT_DATASET_TARGET=virtuoso
DATASET_LOADED_AT=2025-10-30 15:45:00
DATASETS_PATH=datasets
```

## 📈 Consulter les statistiques

Après le chargement, **faites défiler vers le bas** de l'onglet Datasets.

Vous verrez la section **"📊 Datasets actuellement chargés"** avec :
- Total de datasets chargés : **1**
- Total de triplets : **10,000**

Et les détails par moteur :
- 🔵 **Virtuoso** (si chargé)
  - Dataset: Generic (10K)
  - Triplets: 10,000
  - Date de chargement
  - Bouton "🗑️ Effacer"

## 🔍 Tester une requête SPARQL

Après avoir chargé le dataset, testez qu'il est accessible :

### Avec Virtuoso
```bash
# Test simple
curl -X POST "http://localhost:8890/sparql" \
  -H "Content-Type: application/sparql-query" \
  -d "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }"
```

### Avec Fuseki
```bash
# Test simple
curl -X POST "http://localhost:3030/dataset/query" \
  -H "Content-Type: application/sparql-query" \
  -d "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }"
```

## 🧪 Tests supplémentaires

### Test 2 : Charger un dataset plus gros
1. Sélectionnez **DBpedia** 🔵 et **10K**
2. Cliquez "Charger dans Virtuoso"
3. Temps estimé : ~5-8 secondes
4. Vérifiez que les métadonnées sont mises à jour

### Test 3 : Charger dans les deux moteurs
1. Sélectionnez **LUBM** 🟢 et **10K**
2. Cliquez "Charger dans les deux"
3. Observez les deux barres de progression
4. Vérifiez que les deux moteurs sont listés dans les statistiques

### Test 4 : Supprimer un dataset
1. Dans la section statistiques, cliquez sur "🗑️ Effacer" (Virtuoso ou Fuseki)
2. Observez le message de confirmation
3. Vérifiez que les statistiques sont mises à jour
4. Vérifiez que `datasets_metadata.json` ne contient plus ce moteur

## 🐛 Si vous rencontrez un problème

### Message : "Aucun dataset trouvé"
**Cause** : Les fichiers .ttl ne sont pas dans les bons dossiers

**Solution** :
```bash
# Vérifiez la structure
ls -R datasets/

# Devrait afficher :
# datasets/DBpedia/10K.ttl
# datasets/LUBM/10K.ttl
# datasets/Generic/10K.ttl
```

### Message : "Erreur de chargement"
**Cause** : Virtuoso ou Fuseki n'est pas démarré

**Solution** :
```bash
# Tester Virtuoso
curl http://localhost:8890/sparql

# Tester Fuseki
curl http://localhost:3030/dataset/query
```

### Message : "Permissions insuffisantes" (Virtuoso)
**Cause** : L'utilisateur SPARQL n'a pas les droits SPARQL_UPDATE

**Solution** :
```bash
# Se connecter à Virtuoso
isql 1111 dba dba

# Donner les permissions
GRANT SPARQL_UPDATE TO "SPARQL";
```

### Le fichier Generic/10K.ttl est vide
**Cause** : Le fichier existe mais est vide (0 octets)

**Solution** :
- Utilisez DBpedia/10K.ttl ou LUBM/10K.ttl à la place
- Ou créez un fichier Generic/10K.ttl avec du contenu valide

## ✨ Workflow recommandé pour vos tests

### Workflow 1 : Tests de performance
```
1. Charger DBpedia 100K dans les deux moteurs
   └─> Onglet Datasets → Sélectionner DBpedia 100K → Charger dans les deux

2. Aller dans l'onglet Configuration
   └─> Lancer les tests de performance

3. Consulter les résultats
   └─> Onglet Résultats

4. Nettoyer après les tests
   └─> Retour dans Datasets → Effacer tous les datasets
```

### Workflow 2 : Tests comparatifs
```
1. Charger le même dataset dans Virtuoso et Fuseki
   └─> Generic 10K dans les deux

2. Exécuter les mêmes requêtes sur les deux
   └─> Onglet Configuration

3. Comparer les résultats
   └─> Onglet Visualisation

4. Exporter les résultats
   └─> Onglet Export
```

### Workflow 3 : Tests itératifs
```
1. Charger Generic 10K → Tester → Analyser
2. Effacer
3. Charger DBpedia 10K → Tester → Comparer
4. Effacer
5. Charger LUBM 100K → Tests finaux
```

## 📊 Comprendre les logs

Dans votre terminal, vous verrez :
```
2025-10-30 15:39:37,542 - INFO - Dossier de datasets validé : datasets
```
✅ Le système trouve vos datasets

```
2025-10-30 15:39:41,157 - INFO - Test de connectivité pour Virtuoso
```
✅ Vérification de Virtuoso

```
2025-10-30 15:39:41,183 - INFO - Test de connectivité pour Jena Fuseki
```
✅ Vérification de Fuseki

## 🎓 Prochaines étapes

1. ✅ **Vous avez testé le chargement de Generic 10K**
2. ⏭️ Testez avec DBpedia ou LUBM
3. ⏭️ Lancez vos premiers tests de performance
4. ⏭️ Consultez les statistiques et comparez
5. ⏭️ Exportez vos résultats

## 📚 Documentation complète

Pour aller plus loin :
- **[README_DATASETS.md](README_DATASETS.md)** - Guide complet
- **[DATASETS_MANAGEMENT.md](DATASETS_MANAGEMENT.md)** - API détaillée
- **[TEST_DATASETS.md](TEST_DATASETS.md)** - Tests détaillés
- **[examples/dataset_management_example.py](examples/dataset_management_example.py)** - Exemples de code

## 💡 Astuces

1. **Commencez petit** : Generic 10K pour vérifier que tout fonctionne
2. **Vérifiez les métadonnées** : Consultez `datasets_metadata.json` après chaque chargement
3. **Nettoyez régulièrement** : Effacez les datasets après vos tests
4. **Surveillez les logs** : Le terminal vous donne des infos utiles
5. **Utilisez les statistiques** : Elles vous montrent exactement ce qui est chargé

## ✅ Checklist de premier usage

- [ ] Application lancée avec `streamlit run main_v2.py`
- [ ] Onglet "📦 Datasets" visible et cliquable
- [ ] Sélection de Generic 10K
- [ ] Informations du dataset affichées (taille, temps, mémoire)
- [ ] Chargement réussi dans Virtuoso ou Fuseki
- [ ] Message de succès avec nombre de triplets
- [ ] Fichier `datasets_metadata.json` créé
- [ ] Fichier `.env` mis à jour
- [ ] Statistiques visibles en bas de page
- [ ] Test de suppression fonctionnel

## 🎉 Félicitations !

Si vous avez coché tous les éléments ci-dessus, votre système de gestion des datasets est **100% opérationnel** ! 🚀

Vous pouvez maintenant l'utiliser pour tous vos tests de performance SPARQL.

---

**Besoin d'aide ?** Consultez les logs dans votre terminal ou le fichier `logs/sparql_platform.log`
