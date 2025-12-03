# Guide d'Installation - Plateforme d'Évaluation SPARQL

**Master 2 Informatique - Génie Logiciel**

---

## Table des matières

1. [Prérequis système](#prérequis-système)
2. [Installation automatique](#installation-automatique)
3. [Installation manuelle](#installation-manuelle)
4. [Vérification de l&#39;installation](#vérification-de-linstallation)
5. [Dépannage](#dépannage)
6. [Utilisation](#utilisation)

---

## Prérequis système

### Système d'exploitation

- **Windows** : Windows 10/11 (64-bit)
- **Linux** : Ubuntu 20.04+ / Debian 11+ / Fedora 35+
- **macOS** : macOS 11+ (Big Sur ou supérieur)

### Logiciels requis

| Logiciel             | Version minimale         | Recommandé | Installation                                 |
| -------------------- | ------------------------ | ----------- | -------------------------------------------- |
| **Python**     | 3.8                      | 3.10+       | [python.org](https://www.python.org/downloads/) |
| **pip**        | 21.0+                    | Latest      | Inclus avec Python                           |
| **Git**        | 2.30+                    | Latest      | [git-scm.com](https://git-scm.com/)             |
| **Navigateur** | Chrome 90+ / Firefox 88+ | Latest      | -                                            |

### Ressources matérielles

| Composant                   | Minimum   | Recommandé |
| --------------------------- | --------- | ----------- |
| **RAM**               | 4 GB      | 8 GB+       |
| **CPU**               | Dual-core | Quad-core+  |
| **Espace disque**     | 500 MB    | 2 GB+       |
| **Connexion réseau** | 1 Mbps    | 10 Mbps+    |

### Moteurs SPARQL (optionnels pour tests complets)

#### OpenLink Virtuoso

**Installation via Docker (recommandé) :**

```bash
docker pull openlink/virtuoso-opensource-7
docker run -d \
  --name virtuoso \
  -p 8890:8890 \
  -p 1111:1111 \
  -e DBA_PASSWORD=dba \
  -v $(pwd)/virtuoso-data:/database \
  openlink/virtuoso-opensource-7
```

**Installation native :**

- **Windows** : [Télécharger](https://virtuoso.openlinksw.com/download/)
- **Linux** : `sudo apt-get install virtuoso-opensource`
- **macOS** : `brew install virtuoso`

**Vérification :**

```bash
# Interface web : http://localhost:8890
# SPARQL endpoint : http://localhost:8890/sparql
```

#### Apache Jena Fuseki

**Installation via Docker (recommandé) :**

```bash
docker pull stain/jena-fuseki
docker run -d \
  --name fuseki \
  -p 3030:3030 \
  -e ADMIN_PASSWORD=admin \
  -v $(pwd)/fuseki-data:/fuseki \
  stain/jena-fuseki
```

**Installation native :**

```bash
# Télécharger depuis https://jena.apache.org/download/
wget https://dlcdn.apache.org/jena/binaries/apache-jena-fuseki-4.9.0.tar.gz
tar -xzf apache-jena-fuseki-4.9.0.tar.gz
cd apache-jena-fuseki-4.9.0
./fuseki-server --port=3030
```

**Vérification :**

```bash
# Interface web : http://localhost:3030
# SPARQL endpoint : http://localhost:3030/dataset/query
```

---

## Installation automatique

### Étape 1 : Cloner le dépôt

```bash
# Via HTTPS
git clone https://github.com/thiernoDiedhiou/sparql_performance_platform.git
cd sparql_performance_platform

# Via SSH
git clone git@github.com:thiernoDiedhiou/sparql_performance_platform.git
cd sparql_performance_platform
```

### Étape 2 : Créer un environnement virtuel

**Windows :**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS :**

```bash
python3 -m venv venv
source venv/bin/activate
```

### Étape 3 : Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Contenu de `requirements.txt` :**

```txt
streamlit==1.28.0
pandas==2.1.0
numpy==1.24.3
plotly==5.17.0
SPARQLWrapper==2.0.0
psutil==5.9.5
requests==2.31.0
openpyxl==3.1.2
Pillow==10.0.0
```

### Étape 4 : Exécuter le script d'installation

```bash
python setup.py
```

**Sortie attendue :**

```
Configuration de la plateforme d'évaluation SPARQL
============================================================
Création de la structure de dossiers...
✓ Dossier créé: config
✓ Dossier créé: core
...
✓ streamlit installé
✓ pandas installé
...
✓ Configuration terminée avec succès!

Prochaines étapes:
1. Configurez les endpoints SPARQL dans config/settings.py
2. Lancez l'application: streamlit run main.py
```

---

## Installation manuelle

### Étape 1 : Structure des dossiers

```bash
mkdir -p config core queries visualization ui/tabs ui/components utils tests images/images_memoire
```

### Étape 2 : Fichiers `__init__.py`

```bash
touch config/__init__.py
touch core/__init__.py
touch queries/__init__.py
touch visualization/__init__.py
touch ui/__init__.py
touch ui/tabs/__init__.py
touch ui/components/__init__.py
touch utils/__init__.py
touch tests/__init__.py
```

### Étape 3 : Fichiers de configuration

Créez `config/settings.py` :

```python
"""Configuration de la plateforme SPARQL"""

# Endpoints SPARQL
DEFAULT_VIRTUOSO_ENDPOINT = "http://localhost:8890/sparql"
DEFAULT_FUSEKI_ENDPOINT = "http://localhost:3030/dataset/query"

# Paramètres de test
DEFAULT_NUM_ITERATIONS = 20
DEFAULT_WARMUP_ITERATIONS = 2
DEFAULT_CONCURRENT_QUERIES = 5

# Datasets
AVAILABLE_DATASETS = ["LUBM", "DBpedia", "Personnalisé"]

# Timeouts
QUERY_TIMEOUT = 60  # secondes
CONNECTIVITY_TIMEOUT = 5  # secondes

# Métriques
ENABLE_CPU_MONITORING = True
ENABLE_MEMORY_MONITORING = True
METRICS_INTERVAL = 0.1  # secondes
```

## Vérification de l'installation

### Test automatique

```bash
python setup.py --verify
```

### Test manuel

**
    Vérifier les imports Python :**

```python
python -c "import streamlit, pandas, plotly, SPARQLWrapper, psutil; print('OK')"
```

### Checklist de vérification

- [ ] Python 3.8+ installé et accessible
- [ ] Environnement virtuel créé et activé
- [ ] Toutes les dépendances installées sans erreur
- [ ] Structure de dossiers conforme
- [ ] Fichiers `__init__.py` présents
- [ ] Virtuoso accessible sur port 8890 (si utilisé)
- [ ] Fuseki accessible sur port 3030 (si utilisé)
- [ ] Dataset chargé
- [ ] Interface Streamlit démarre sans erreur
- [ ] Connexion aux endpoints réussie

---

## Dépannage

### Problème 1 : Erreur d'import Streamlit

**Symptôme :**

```
ModuleNotFoundError: No module named 'streamlit'
```

**Solution :**

```bash
# Vérifier l'environnement virtuel
which python  # Linux/macOS
where python  # Windows

# Réinstaller
pip install --upgrade streamlit
```

### Problème 2 : Port déjà utilisé

**Symptôme :**

```
OSError: [Errno 48] Address already in use
```

**Solution :**

```bash
# Trouver le processus
lsof -i :8501  # Linux/macOS
netstat -ano | findstr :8501  # Windows

# Tuer le processus
kill -9 <PID>  # Linux/macOS
taskkill /F /PID <PID>  # Windows

# Ou changer le port
streamlit run main.py --server.port 8502
```

---

## Utilisation

### Lancement de l'application

```bash
# Activer l'environnement virtuel
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows

# Lancer Streamlit
streamlit run main.py
```

**Options avancées :**

```bash
# Changer le port
streamlit run main.py --server.port 8080

# Désactiver le file watcher
streamlit run main.py --server.fileWatcherType none

# Mode production
streamlit run main.py --server.headless true
```

### Workflow typique

**1. Configuration (Onglet Configuration) :**

- Sélectionner les endpoints Virtuoso et Fuseki
- Choisir un dataset
- Définir le nombre d'itérations
- Activer/désactiver le mode concurrent

**2. Tests (Onglet Tests) :**

- Cliquer sur "Lancer les tests"
- Attendre la fin de l'exécution
- Observer les métriques en temps réel

**3. Visualisation (Onglet Visualisations) :**

- Explorer les graphiques interactifs
- Comparer les performances Virtuoso vs Fuseki
- Analyser les distributions (Box Plot, Violin Plot)

**4. Export (Onglet Exportation) :**

- Générer les rapports statistiques
- Exporter en CSV/JSON/Excel
- Télécharger les graphiques haute résolution

---
