# 🔍 Investigation: Synchronisation Partielle (10% au lieu de 100%)

**Date**: 30 Octobre 2025
**Problème**: Seuls 10,001 triplets sur 100,000 sont synchronisés de Virtuoso vers Fuseki

---

## 📊 Observation Initiale

### État Constaté

```
Virtuoso: 100,000 triplets dans le graphe
Fuseki:   10,001 triplets dans le graphe (après synchronisation)
Taux:     ~10% transféré
```

### Contexte

- **Dataset**: LUBM 100K
- **Graph URI**: `http://example.org/dataset_LUBM_100K_1761863353`
- **Chunk Size**: 100,000 triplets (configuré dans `settings.py`)
- **Méthode**: Synchronisation optimisée par chunking (`ChunkedDataSynchronizer`)

---

## 🔎 Hypothèses à Tester

### Hypothèse 1: Problème d'Export depuis Virtuoso

**Symptômes possibles**:
- La requête CONSTRUCT ne retourne qu'une partie des données
- Timeout pendant l'export
- Virtuoso limite la taille de la réponse

**Tests à effectuer**:
1. Vérifier la taille réelle du résultat CONSTRUCT
2. Tester avec différents LIMIT (10, 100, 1000, 10000, 100000)
3. Compter les triplets dans le résultat Turtle

**Code de test**:
```python
# Voir diagnose_sync_issue.py - TEST 1
```

### Hypothèse 2: Problème d'Upload vers Fuseki

**Symptômes possibles**:
- Fuseki refuse les gros uploads
- Erreur HTTP non détectée
- Timeout côté Fuseki
- Limite de taille de requête POST

**Tests à effectuer**:
1. Upload de tailles croissantes (10, 100, 1000, 10000 triplets)
2. Vérifier les codes de réponse HTTP
3. Inspecter les logs Fuseki

**Code de test**:
```python
# Voir diagnose_sync_issue.py - TEST 2
```

### Hypothèse 3: Problème de Parsing/Conversion

**Symptômes possibles**:
- Erreur silencieuse dans la conversion bytes → string
- Encodage UTF-8 incorrect
- Données corrompues

**Tests à effectuer**:
1. Sauvegarder le chunk exporté dans un fichier
2. Vérifier manuellement le contenu
3. Tenter un upload manuel du fichier

**Code de test**:
```python
# Voir diagnose_sync_issue.py - TEST 4
```

### Hypothèse 4: Configuration de Fuseki

**Symptômes possibles**:
- Limite de taille de transaction
- Limite de mémoire
- Configuration du servlet HTTP

**Vérifications**:
1. Inspecter `fuseki-config.ttl`
2. Vérifier les logs Fuseki (`fuseki.log`)
3. Vérifier la configuration JVM (heap size)

**Fichiers à vérifier**:
```bash
# Logs Fuseki
cat fuseki.log | grep -i error
cat fuseki.log | grep -i "100000"

# Configuration
cat fuseki-config.ttl
```

### Hypothèse 5: Problème dans le Code de Synchronisation

**Symptômes possibles**:
- Boucle qui s'arrête prématurément
- Condition d'erreur non détectée
- Calcul incorrect du nombre de chunks

**Code à vérifier**:
```python
# data_synchronizer_v2.py lignes 191-226
num_chunks = (triplets_to_export + self.chunk_size - 1) // self.chunk_size

# Pour 100,000 triplets avec chunk_size=100,000:
# num_chunks = (100000 + 100000 - 1) // 100000 = 199999 // 100000 = 1 ✅

# Donc un seul chunk devrait être exporté - c'est correct
```

---

## 🧪 Plan d'Investigation

### Étape 1: Diagnostic Initial
```bash
cd c:\Users\hp\Documents\M2\Web Semantique\Mémoire\Code_NV\sparql_v2
python diagnose_sync_issue.py
```

Ce script va:
1. Vérifier l'état actuel du dataset
2. Tester la capacité d'export de Virtuoso
3. Tester la capacité d'upload de Fuseki
4. Identifier où se produit la perte de données

### Étape 2: Analyse des Résultats

Selon les résultats du diagnostic, nous saurons si le problème vient de:
- **Export Virtuoso**: Le chunk exporté contient déjà moins de 100K triplets
- **Upload Fuseki**: Le chunk est complet mais Fuseki ne l'upload que partiellement
- **Autre**: Problème de configuration ou de code

### Étape 3: Solutions Possibles

#### Si le problème vient de l'export:
- Réduire le chunk size (50K, 10K)
- Augmenter les timeouts
- Vérifier les limites Virtuoso

#### Si le problème vient de l'upload:
- Réduire le chunk size
- Upload par batches plus petits
- Modifier la configuration Fuseki
- Augmenter la mémoire JVM de Fuseki

#### Si le problème vient de la configuration:
- Ajuster les paramètres dans `settings.py`
- Modifier `fuseki-config.ttl`
- Augmenter les ressources système

---

## 📋 Checklist de Diagnostic

- [ ] Exécuter `diagnose_sync_issue.py`
- [ ] Vérifier les logs Virtuoso
- [ ] Vérifier les logs Fuseki
- [ ] Tester avec un chunk size réduit (10K)
- [ ] Vérifier l'encodage des données
- [ ] Inspecter le fichier `export_test_100k.ttl`
- [ ] Tester l'upload manuel avec `curl`
- [ ] Vérifier la configuration JVM de Fuseki

---

## 🔧 Configuration Actuelle

### settings.py
```python
SYNC_CHUNK_SIZE = 100000       # Taille des chunks
MAX_SYNC_TRIPLETS = 1000000    # Limite maximale
SYNCHRONIZATION_TIMEOUT = 300  # 5 minutes
```

### data_synchronizer_v2.py
```python
sparql.setTimeout(300)          # Export: 5 minutes
timeout=300                     # Upload: 5 minutes
timeout=120                     # Clear: 2 minutes
```

---

## 📝 Notes

### Observations Importantes

1. **10,001 triplets transférés**: Le nombre exact (+1) suggère peut-être un triplet de métadonnées?
2. **Taux de 10%**: Curieusement proche de 10,000 triplets
3. **Un seul chunk**: Avec 100K triplets et chunk_size=100K, un seul chunk devrait suffire
4. **Pas de message d'erreur**: L'interface affiche "Synchronisation partielle: 10.0%"

### Questions à Résoudre

1. Pourquoi exactement 10,001 et pas 10,000?
2. Y a-t-il un timeout silencieux?
3. Fuseki rejette-t-il une partie des données?
4. Le CONSTRUCT retourne-t-il vraiment 100K triplets?

---

## 🎯 Prochaines Étapes

1. **Exécuter le diagnostic** (`diagnose_sync_issue.py`)
2. **Analyser les résultats** et identifier le point de défaillance
3. **Appliquer la solution** appropriée
4. **Re-tester** avec LUBM 100K
5. **Documenter** la solution finale

---

**Statut**: 🔴 Investigation en cours
**Priorité**: 🔥 Haute - bloque les tests de performance
**Assigné**: En cours d'investigation automatique
