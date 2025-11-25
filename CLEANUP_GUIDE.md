# 🧹 Guide de Nettoyage des Graphes Résiduels

## 📊 Situation Actuelle

D'après le diagnostic, vos triplestores contiennent plusieurs graphes résiduels d'anciens chargements :

### Virtuoso (32,484 triplets au total)
- ✅ **1 graphe actif** : `http://example.org/dataset_DBpedia_10K_1761840524` (10,000 triplets)
- ❌ **2 graphes résiduels** à supprimer (~20,000 triplets)
- ⚙️ **3 graphes système** à conserver

### Fuseki (60,000 triplets au total)
- ✅ **1 graphe actif** : `http://example.org/dataset_DBpedia_10K_1761840524` (10,000 triplets)
- ❌ **5 graphes résiduels** à supprimer (~50,000 triplets)

## 🎯 Objectif

Nettoyer les graphes résiduels pour ne garder que le graphe actif dans chaque triplestore.

## 🚀 Solution : Script de Nettoyage Interactif

J'ai créé `clean_graphs_interactive.py` qui vous permet de :
- ✅ Voir tous les graphes avec leur nombre de triplets
- ✅ Sélectionner manuellement les graphes à supprimer
- ✅ Ou supprimer automatiquement tous les graphes de dataset (sauf les systèmes)
- ✅ Protection contre la suppression accidentelle des graphes système

## 📝 Instructions

### Étape 1 : Exécuter le script

```powershell
python clean_graphs_interactive.py
```

### Étape 2 : Choisir le triplestore

```
Quel triplestore voulez-vous nettoyer ?
  1. Virtuoso
  2. Fuseki
  3. Les deux
  4. Quitter
```

**Recommandation** : Commencez par nettoyer un seul triplestore (option 1 ou 2) pour tester.

### Étape 3 : Voir la liste des graphes

Le script affichera tous les graphes trouvés avec leur nombre de triplets :

```
1. [SYSTEME] http://www.openlinksw.com/schemas/virtrdf#
2. http://example.org/dataset_DBpedia_10K_old_1
   -> 10,000 triplets
3. http://example.org/dataset_DBpedia_10K_old_2
   -> 10,000 triplets
4. http://example.org/dataset_DBpedia_10K_1761840524
   -> 10,000 triplets (← GRAPHE ACTIF À CONSERVER)
```

### Étape 4 : Choisir l'option de suppression

```
Options :
  1. Supprimer TOUS les graphes de dataset (conserve les systèmes)
  2. Sélectionner manuellement les graphes à supprimer
  3. Annuler et quitter
```

**Option recommandée** : **Option 2** (sélection manuelle) pour plus de contrôle

### Étape 5 : Sélectionner les graphes à supprimer

Si vous choisissez l'option 2, identifiez le graphe actif à **CONSERVER** :

Le graphe actif est : `http://example.org/dataset_DBpedia_10K_1761840524`

Donc si vos graphes sont numérotés :
- 1. Graphe système → **NE PAS supprimer**
- 2. Old graph 1 → **Supprimer**
- 3. Old graph 2 → **Supprimer**
- 4. `...1761840524` → **NE PAS supprimer (graphe actif)**
- 5. Old graph 3 → **Supprimer**

Entrez : `2,3,5` (tous les numéros SAUF le graphe actif et les systèmes)

### Étape 6 : Confirmer

Le script affichera un récapitulatif et demandera confirmation :

```
3 graphe(s) sera/seront supprimé(s) :
   - http://example.org/dataset_DBpedia_10K_old_1
   - http://example.org/dataset_DBpedia_10K_old_2
   - http://example.org/dataset_DBpedia_10K_old_3

Confirmez la suppression (oui/non) :
```

Tapez `oui` pour confirmer.

### Étape 7 : Vérifier le résultat

Une fois le nettoyage terminé, relancez le diagnostic :

```powershell
python diagnostic_datasets.py
```

**Résultat attendu** :
- **Virtuoso** : 1 graphe actif (10,000 triplets) + graphes système
- **Fuseki** : 1 graphe actif (10,000 triplets)

## ⚠️ Points d'Attention

### Graphes à TOUJOURS Conserver

1. **Graphe actif actuel** : `http://example.org/dataset_DBpedia_10K_1761840524`
2. **Graphes système Virtuoso** :
   - `http://www.openlinksw.com/schemas/virtrdf#`
   - `http://www.w3.org/ns/ldp#`
   - `urn:activitystreams-owl:map`

Le script protège automatiquement les graphes système, mais faites attention à ne pas supprimer le graphe actif !

### Comment Identifier le Graphe Actif

Le graphe actif contient généralement :
- Le timestamp le plus récent dans son URI
- Dans votre cas : `1761840524` (= 30 octobre 2025, 15:52)

Si vous avez un doute, référez-vous au diagnostic qui montre le graphe correspondant aux métadonnées.

## 🔄 Workflow Complet Recommandé

### 1. Vérifier l'état initial
```powershell
python diagnostic_datasets.py
```

### 2. Nettoyer Virtuoso
```powershell
python clean_graphs_interactive.py
# Choisir option 1 (Virtuoso)
# Sélection manuelle des graphes
```

### 3. Vérifier après Virtuoso
```powershell
python diagnostic_datasets.py
```

### 4. Nettoyer Fuseki
```powershell
python clean_graphs_interactive.py
# Choisir option 2 (Fuseki)
# Sélection manuelle des graphes
```

### 5. Vérification finale
```powershell
python diagnostic_datasets.py
```

## 📊 Résultat Final Attendu

Après le nettoyage complet, votre diagnostic devrait afficher :

```
╔══════════════════════════════════════════════════════════════╗
║  ÉTAT DES TRIPLESTORES                                       ║
╚══════════════════════════════════════════════════════════════╝

┌────────────────────────────────────────────────────────────┐
│ VIRTUOSO                                                     │
│ http://localhost:8890/sparql                                │
└────────────────────────────────────────────────────────────┘

Graphes trouvés : 4 (1 dataset + 3 système)

📊 Résumé VIRTUOSO
   • Graphes de dataset : 1
   • Triplets de dataset : 10,000
   • Graphes système : 3
   ✅ Propre : 1 seul graphe de dataset

┌────────────────────────────────────────────────────────────┐
│ FUSEKI                                                       │
│ http://localhost:3030/dataset/query                         │
└────────────────────────────────────────────────────────────┘

Graphes trouvés : 1

📊 Résumé FUSEKI
   • Graphes de dataset : 1
   • Triplets dans le graphe actif : 10,000
   ✅ Propre : 1 seul graphe de dataset
```

## 🆘 En Cas de Problème

### Erreur de connexion
```
[ERREUR] Impossible de lister les graphes
```
**Solution** : Vérifiez que Virtuoso/Fuseki est démarré

### Erreur de permissions
```
[ECHEC] lors de la suppression
```
**Solution** : Vérifiez les permissions SPARQL_UPDATE :
```sql
isql 1111 dba dba
GRANT SPARQL_UPDATE TO "SPARQL";
```

### Suppression accidentelle du mauvais graphe
Si vous supprimez accidentellement le graphe actif :
1. Rechargez le dataset via l'interface Streamlit (onglet Datasets)
2. Ou relancez le chargement programmatique

## 💡 Conseil Pro

**Après le nettoyage**, rechargez votre dataset via l'interface pour recréer les métadonnées propres :

1. Lancez `streamlit run main_v2.py`
2. Allez dans l'onglet "📦 Datasets"
3. Sélectionnez votre dataset (ex: DBpedia 10K)
4. Cliquez sur "Charger dans Virtuoso" ou "Charger dans Fuseki"

Cela garantira que :
- ✅ Le fichier `datasets_metadata.json` est mis à jour
- ✅ Le fichier `.env` contient les bonnes informations
- ✅ L'application connaît l'état actuel des triplestores

---

## 📚 Documentation Associée

- [diagnostic_datasets.py](diagnostic_datasets.py) - Script de diagnostic
- [clean_graphs_interactive.py](clean_graphs_interactive.py) - Script de nettoyage
- [RESOLUTION_INCOHERENCES.md](RESOLUTION_INCOHERENCES.md) - Guide complet de résolution
- [README_DATASETS.md](README_DATASETS.md) - Guide d'utilisation des datasets

---

**Date** : 2025-10-30
**Version** : 1.0
**Statut** : Prêt à utiliser

🧹 **Bon nettoyage !**
