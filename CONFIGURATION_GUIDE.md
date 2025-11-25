# 📘 Guide de Configuration

**Version** : 2.0
**Date** : 31 Octobre 2025
**Pour** : Utilisateurs et Développeurs

---

## 🎯 Configuration Rapide (Quick Start)

### Étape 1 : Copier le Fichier d'Exemple

```bash
cp .env.example .env
```

### Étape 2 : Ajuster les Endpoints

Éditez `.env` et modifiez les URLs si nécessaire :

```bash
# Si Virtuoso est sur un autre port
VIRTUOSO_ENDPOINT=http://localhost:8890/sparql

# Si Fuseki est sur un autre port ou serveur
FUSEKI_ENDPOINT=http://localhost:3030/dataset/query
FUSEKI_UPDATE_ENDPOINT=http://localhost:3030/dataset/update
```

### Étape 3 : Lancer l'Application

```bash
streamlit run main.py
```

✅ **C'est tout !** L'application est prête à l'emploi.

---

## 📁 Fichiers de Configuration

### `.env` - Configuration Utilisateur

**Rôle** : Configuration spécifique à votre environnement

**Priorité** : ⭐⭐⭐ Haute (écrase les valeurs de `settings.py`)

**Versionné** : ❌ Non (ajouté au `.gitignore`)

**Utilisation** :
- URLs des endpoints SPARQL
- Timeouts personnalisés
- Paramètres de logging
- Credentials (si authentification activée)

**Modification** : Éditez directement ce fichier

---

### `config/settings.py` - Configuration Application

**Rôle** : Valeurs par défaut et structures de données Python

**Priorité** : ⭐⭐ Moyenne (si `.env` absent)

**Versionné** : ✅ Oui (partagé avec l'équipe)

**Utilisation** :
- Constantes Python
- Dictionnaires de configuration
- Fonctions de configuration
- Datasets disponibles

**Modification** : Réservé aux développeurs

---

### `.env.example` - Template de Configuration

**Rôle** : Exemple de configuration pour les nouveaux utilisateurs

**Contenu** : Toutes les variables avec valeurs par défaut

**Usage** : `cp .env.example .env`

**Modification** : Lors de l'ajout de nouvelles variables

---

## ⚙️ Paramètres Importants

### 🔗 Endpoints SPARQL

```bash
# Virtuoso
VIRTUOSO_ENDPOINT=http://localhost:8890/sparql

# Jena Fuseki (Query)
FUSEKI_ENDPOINT=http://localhost:3030/dataset/query

# Jena Fuseki (Update)
FUSEKI_UPDATE_ENDPOINT=http://localhost:3030/dataset/update
```

**Note** : Les endpoints doivent être accessibles avant de lancer l'application.

---

### 🔄 Synchronisation des Données

```bash
# Taille optimale des chunks (triplets)
# ⚠️ IMPORTANT: Ne pas augmenter au-delà de 10,000
SYNC_CHUNK_SIZE=10000
```

**Pourquoi 10,000 ?**
- Virtuoso a une limite de ~10,000 lignes pour les requêtes CONSTRUCT
- Valeurs > 10K causent une synchronisation partielle
- Cette valeur assure 100% de réussite

**Si vous voulez augmenter** :
1. Modifiez `virtuoso.ini` : `ResultSetMaxRows = 100000`
2. Redémarrez Virtuoso
3. Testez avec `test_sync_with_small_chunks.py`
4. Ajustez `SYNC_CHUNK_SIZE` selon les résultats

---

### ⏱️ Timeouts

```bash
# Timeout requêtes SPARQL (secondes)
QUERY_TIMEOUT=60

# Timeout connectivité (secondes)
CONNECTIVITY_TIMEOUT=5

# Timeout synchronisation (secondes)
SYNCHRONIZATION_TIMEOUT=300
```

**Recommandations** :
- `QUERY_TIMEOUT` : Augmenter pour les requêtes complexes
- `CONNECTIVITY_TIMEOUT` : Laisser à 5s (test rapide)
- `SYNCHRONIZATION_TIMEOUT` : Augmenter pour les gros datasets (> 1M triplets)

---

### 📊 Tests de Performance

```bash
# Nombre d'itérations par requête
DEFAULT_NUM_ITERATIONS=5

# Échauffement (warmup)
DEFAULT_WARMUP_ITERATIONS=2

# Concurrence (requêtes simultanées)
DEFAULT_CONCURRENT_QUERIES=1
```

**Ajustements selon vos besoins** :
- **Tests rapides** : `DEFAULT_NUM_ITERATIONS=3`
- **Tests précis** : `DEFAULT_NUM_ITERATIONS=10`
- **Charge élevée** : `DEFAULT_CONCURRENT_QUERIES=5` ou plus

---

### 📝 Logging

```bash
# Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Niveau console
CONSOLE_LOG_LEVEL=INFO

# Répertoire des logs
LOG_DIR=logs

# Nom du fichier de log
LOG_FILE=sparql_platform.log
```

**Pour debugging** :
```bash
LOG_LEVEL=DEBUG
CONSOLE_LOG_LEVEL=DEBUG
```

**Pour production** :
```bash
LOG_LEVEL=WARNING
CONSOLE_LOG_LEVEL=INFO
```

---

## 🔧 Configuration Avancée

### Métriques Système

```bash
# Activer la collecte de métriques
ENABLE_SYSTEM_METRICS=true

# Intervalle de collecte (secondes)
METRICS_COLLECTION_INTERVAL=1.0
```

**Impact** :
- Collecte CPU, mémoire, disque pendant les tests
- Légèrement plus lourd (quelques %)
- Utile pour l'analyse de performance détaillée

---

### Alertes

```bash
# Seuil pour gros datasets (triplets)
LARGE_DATASET_THRESHOLD=500000

# Seuil alerte mémoire (MB)
MEMORY_WARNING_THRESHOLD=1024
```

**Personnalisation** :
- Augmentez les seuils si votre machine a beaucoup de RAM
- Diminuez si vous travaillez sur une machine limitée

---

### Export des Résultats

```bash
# Répertoire des résultats
RESULTS_DIR=results

# Format par défaut (csv, excel, json)
DEFAULT_EXPORT_FORMAT=excel
```

**Formats disponibles** :
- `csv` : Léger, compatible tous outils
- `excel` : Formatage, graphiques intégrés
- `json` : Pour traitement programmatique

---

## 🛡️ Sécurité (Optionnel)

### Authentification

```bash
# Activer l'authentification
ENABLE_AUTHENTICATION=false

# Credentials admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=changeme
```

**⚠️ IMPORTANT** :
- Changez `ADMIN_PASSWORD` en production !
- `.env` ne doit **jamais** être versionné
- Utilisez un gestionnaire de secrets pour la production

---

## 📚 Cas d'Usage

### Développement Local

```bash
# .env pour développement
DEV_MODE=true
AUTO_RELOAD=true
SHOW_PYTHON_WARNINGS=true
LOG_LEVEL=DEBUG
STREAMLIT_DEBUG=true
```

---

### Tests Automatisés

```bash
# .env pour CI/CD
ENABLE_SYSTEM_METRICS=false
LOG_LEVEL=WARNING
CONSOLE_LOG_LEVEL=ERROR
DEFAULT_NUM_ITERATIONS=3
QUERY_TIMEOUT=30
```

---

### Production

```bash
# .env pour production
DEV_MODE=false
AUTO_RELOAD=false
SHOW_PYTHON_WARNINGS=false
LOG_LEVEL=WARNING
CONSOLE_LOG_LEVEL=INFO
ENABLE_AUTHENTICATION=true
STREAMLIT_ADDRESS=0.0.0.0
```

---

## 🔍 Vérification de Configuration

### Script de Vérification

Créez un fichier `check_config.py` :

```python
import os
from dotenv import load_dotenv

# Charger .env
load_dotenv()

# Variables critiques
critical_vars = [
    "VIRTUOSO_ENDPOINT",
    "FUSEKI_ENDPOINT",
    "SYNC_CHUNK_SIZE"
]

print("Vérification de la configuration")
print("=" * 50)

for var in critical_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: {value}")
    else:
        print(f"❌ {var}: NON DÉFINI")

# Vérifications spécifiques
chunk_size = int(os.getenv("SYNC_CHUNK_SIZE", 0))
if chunk_size == 10000:
    print("\n✅ SYNC_CHUNK_SIZE optimal (10,000)")
elif chunk_size > 10000:
    print(f"\n⚠️  SYNC_CHUNK_SIZE trop élevé ({chunk_size:,})")
    print("   Recommandation: 10,000 maximum")
```

**Exécution** :
```bash
python check_config.py
```

---

## 🐛 Résolution de Problèmes

### Problème : "Endpoints non configurés"

**Cause** : `.env` absent ou mal configuré

**Solution** :
```bash
cp .env.example .env
# Éditez les endpoints si nécessaire
```

---

### Problème : "Synchronisation partielle"

**Symptôme** : Seulement 10% des données transférées

**Cause** : `SYNC_CHUNK_SIZE` trop élevé

**Solution** :
```bash
# Dans .env
SYNC_CHUNK_SIZE=10000
```

---

### Problème : "Timeout lors de la synchronisation"

**Symptôme** : Erreurs de timeout pendant l'upload

**Solution** :
```bash
# Augmenter le timeout
SYNCHRONIZATION_TIMEOUT=600  # 10 minutes

# OU réduire la taille des chunks
SYNC_CHUNK_SIZE=5000
```

---

### Problème : "Avertissement datasets non synchronisés"

**Cause** : Aucun dataset chargé (seulement les triplets système)

**Solution** :
1. Aller dans l'onglet "Datasets"
2. Charger un dataset (DBpedia 100K par exemple)
3. Synchroniser vers Fuseki

---

## 📖 Documentation Complémentaire

### Pour Aller Plus Loin

- **[SYNC_PROBLEM_SOLVED.md](SYNC_PROBLEM_SOLVED.md)** - Résolution des problèmes de synchronisation
- **[TRIPLESTORE_COUNTING_BEHAVIOR.md](TRIPLESTORE_COUNTING_BEHAVIOR.md)** - Comportement des comptages
- **[SESSION_COMPLETE_2025-10-31.md](SESSION_COMPLETE_2025-10-31.md)** - Récapitulatif complet

### Scripts Utiles

- **`debug_sync_status.py`** - Vérifier le statut de synchronisation
- **`test_sync_with_small_chunks.py`** - Tester différentes tailles de chunk
- **`quick_load_dataset.py`** - Charger rapidement un dataset

---

## ✅ Checklist de Configuration

Avant de lancer l'application :

- [ ] `.env` créé à partir de `.env.example`
- [ ] Endpoints SPARQL configurés et accessibles
- [ ] `SYNC_CHUNK_SIZE=10000` (ne pas modifier sauf besoin spécifique)
- [ ] Timeouts adaptés à vos besoins
- [ ] Logging configuré
- [ ] Virtuoso et Fuseki démarrés
- [ ] Test de connectivité réussi

---

## 🎓 Best Practices

### Configuration

1. ✅ Ne jamais versionner `.env`
2. ✅ Garder `.env.example` à jour avec toutes les variables
3. ✅ Documenter les valeurs non évidentes
4. ✅ Utiliser des valeurs sensées par défaut

### Sécurité

1. ✅ Changer les mots de passe par défaut
2. ✅ Limiter l'accès aux endpoints en production
3. ✅ Activer l'authentification si exposition publique
4. ✅ Utiliser HTTPS en production

### Performance

1. ✅ Ajuster les timeouts selon la taille des datasets
2. ✅ Limiter la concurrence sur les machines modestes
3. ✅ Désactiver les métriques si non nécessaires
4. ✅ Ne pas dépasser `SYNC_CHUNK_SIZE=10000`

---

## 📞 Support

### En Cas de Problème

1. **Vérifier** : La configuration avec `check_config.py`
2. **Diagnostiquer** : Avec `debug_sync_status.py`
3. **Consulter** : La documentation dans le dossier racine
4. **Rapporter** : Sur le repository GitHub (Issues)

---

**Dernière mise à jour** : 31 Octobre 2025
**Version** : 2.0
**Statut** : ✅ Production Ready
