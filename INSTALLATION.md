# 🚀 Guide d'installation - Plateforme SPARQL

Ce guide vous aide à installer et configurer la plateforme d'évaluation de performance SPARQL étape par étape.

## 📋 Prérequis

- **Python 3.8+** (testé avec Python 3.10.2)
- **pip** (gestionnaire de packages Python)
- **Moteurs SPARQL** : Virtuoso et/ou Jena Fuseki (optionnel pour commencer)

## 🛠️ Installation automatique (Recommandée)

### Étape 1: Télécharger le script de configuration

Créez un nouveau dossier et copiez le fichier `setup.py` fourni.

```bash
# Créer un nouveau dossier pour le projet
mkdir sparql_performance_platform
cd sparql_performance_platform

# Copier le script setup.py dans ce dossier
```

### Étape 2: Exécuter la configuration automatique

```bash
python setup.py
```

Ce script va :

- ✅ Créer la structure de dossiers nécessaire
- ✅ Générer les fichiers `__init__.py`
- ✅ Créer un fichier de configuration de base
- ✅ Vérifier les dépendances Python
- ✅ Créer un fichier de test

### Étape 3: Installer les dépendances

```bash
pip install -r requirements.txt
```

Si le fichier `requirements.txt` n'existe pas encore, installez manuellement :

```bash
pip install streamlit pandas plotly SPARQLWrapper psutil requests openpyxl
```

### Étape 4: Tester l'installation

```bash
streamlit run main_test.py
```

Si cette commande fonctionne et affiche une page web, votre installation de base est correcte !

## 📁 Installation manuelle (Alternative)

Si le script automatique ne fonctionne pas, suivez ces étapes :

### Étape 1: Créer la structure de dossiers

```bash
mkdir -p sparql_performance_platform/{config,core,queries,visualization,ui/tabs,ui/components,utils,tests}
cd sparql_performance_platform
```

### Étape 2: Créer les fichiers __init__.py

```bash
# Créer tous les fichiers __init__.py nécessaires
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

### Étape 3: Ajouter les fichiers Python

Copiez chacun des fichiers Python dans sa structure correspondante :

```
sparql_performance_platform/
├── main.py                          # Point d'entrée principal
├── requirements.txt                 # Dépendances
├── config/
│   └── settings.py                  # Configuration
├── core/
│   ├── tester.py                    # Testeur principal
│   ├── executor.py                  # Exécuteur de requêtes
│   └── metrics.py                   # Collecteur de métriques
├── queries/
│   ├── catalog.py                   # Catalogue principal
│   ├── lubm_queries.py              # Requêtes LUBM
│   ├── dbpedia_queries.py           # Requêtes DBpedia
│   └── generic_queries.py           # Requêtes génériques
├── visualization/
│   └── visualizer.py                # Visualiseur
├── ui/
│   ├── sidebar.py                   # Barre latérale
│   ├── tabs/
│   │   ├── configuration_tab.py     # Onglet configuration
│   │   ├── results_tab.py           # Onglet résultats
│   │   ├── visualization_tab.py     # Onglet visualisation
│   │   └── export_tab.py            # Onglet exportation
│   └── components/
│       ├── connectivity_checker.py  # Vérificateur connectivité
│       └── system_info.py           # Informations système
└── utils/
    ├── data_manager.py              # Gestionnaire de données
    └── helpers.py                   # Fonctions utilitaires
```

## 🔧 Configuration des moteurs SPARQL

### Option 1: Docker (Recommandée)

#### Virtuoso

```bash
docker run -d \
  --name virtuoso \
  -p 8890:8890 \
  -e DBA_PASSWORD=dba \
  tenforce/virtuoso:1.3.2-virtuoso7.2.5
```

#### Jena Fuseki

```bash
docker run -d \
  --name fuseki \
  -p 3030:3030 \
  stain/jena-fuseki:latest
```

### Option 2: Installation native

Consultez la documentation officielle :

- [Virtuoso](https://github.com/openlink/virtuoso-opensource)
- [Jena Fuseki](https://jena.apache.org/documentation/fuseki2/)

## 🚦 Vérification de l'installation

### Étape 1: Test des dépendances

```bash
python -c "import streamlit, pandas, plotly, SPARQLWrapper, psutil; print('✅ Toutes les dépendances sont installées')"
```

### Étape 2: Test de l'application

```bash
streamlit run main.py
```

### Étape 3: Test des endpoints (optionnel)

Si vous avez configuré des moteurs SPARQL :

```bash
# Test Virtuoso
curl "http://localhost:8890/sparql?query=SELECT%20?s%20WHERE%20{%20?s%20?p%20?o%20}%20LIMIT%201"

# Test Fuseki
curl "http://localhost:3030/dataset/query?query=SELECT%20?s%20WHERE%20{%20?s%20?p%20?o%20}%20LIMIT%201"
```

## 🐛 Résolution des problèmes courants

### Erreur: "cannot import name 'render_sidebar'"

**Cause:** Structure de dossiers incorrecte ou fichiers manquants

**Solution:**

```bash
# Vérifier la structure
ls -la ui/
ls -la ui/tabs/

# Si les dossiers n'existent pas, les créer
mkdir -p ui/tabs ui/components

# Vérifier les fichiers __init__.py
touch ui/__init__.py ui/tabs/__init__.py ui/components/__init__.py
```

### Erreur: "ModuleNotFoundError"

**Cause:** Dépendances manquantes

**Solution:**

```bash
# Réinstaller les dépendances
pip install --upgrade streamlit pandas plotly SPARQLWrapper psutil requests openpyxl

# Ou utiliser le fichier requirements
pip install -r requirements.txt
```

### Erreur: "concurrent.futures" dans requirements.txt

**Cause:** Module intégré dans Python inclus par erreur

**Solution:**

```bash
# Éditer requirements.txt et supprimer la ligne:
# concurrent.futures

# Ou utiliser requirements-core.txt
pip install -r requirements-core.txt
```

### L'application se lance mais affiche des erreurs

**Diagnostic:**

1. Vérifiez que tous les fichiers Python sont présents
2. Assurez-vous que les imports sont corrects
3. Testez avec `main_test.py` d'abord

### Endpoints SPARQL non accessibles

**Solutions:**

1. **Vérifier que les services sont démarrés:**

   ```bash
   docker ps  # Si utilisation de Docker
   ```
2. **Tester manuellement:**

   ```bash
   curl http://localhost:8890/sparql
   curl http://localhost:3030
   ```
3. **Ajuster les URLs dans l'interface** si nécessaire

## 📊 Test avec des données d'exemple

### Option 1: Données en ligne (DBpedia)

- Utilisez l'endpoint public DBpedia : `https://dbpedia.org/sparql`
- Sélectionnez le jeu de données "DBpedia" dans l'interface

### Option 2: Données locales

1. **Télécharger un dataset LUBM:**

   ```bash
   wget http://swat.cse.lehigh.edu/onto/univ-bench.owl
   ```
2. **Charger dans Virtuoso/Fuseki** selon leur documentation
3. **Utiliser les requêtes LUBM** dans l'interface

## 🎯 Première utilisation

### Étape 1: Lancer l'application

```bash
streamlit run main.py
```

### Étape 2: Configuration initiale

1. **Endpoints:** Configurez les URLs dans la barre latérale
2. **Test de connectivité:** Utilisez le bouton "Tester la connectivité"
3. **Sélection des requêtes:** Choisissez les types de tests

### Étape 3: Premier test

1. Commencez avec le profil "Test rapide"
2. Sélectionnez uniquement "Requêtes simples"
3. Utilisez 3 itérations pour commencer
4. Cliquez sur "Exécuter les tests"

## 📚 Ressources supplémentaires

### Documentation

- **Streamlit:** [docs.streamlit.io](https://docs.streamlit.io)
- **Plotly:** [plotly.com/python](https://plotly.com/python/)
- **SPARQLWrapper:** [rdflib.dev](https://rdflib.dev/)

### Exemples de datasets

- **LUBM:** [Lehigh University Benchmark](http://swat.cse.lehigh.edu/projects/lubm/)
- **BSBM:** [Berlin SPARQL Benchmark](http://wifo5-03.informatik.uni-mannheim.de/bizer/berlinsparqlbenchmark/)
- **DBpedia:** [DBpedia.org](https://www.dbpedia.org/)

### Support

- **Issues GitHub:** Pour signaler des bugs
- **Documentation projet:** Consultez le README.md
- **Logs:** Vérifiez la console pour les erreurs détaillées

## ✅ Checklist de validation

Cochez chaque étape une fois complétée :

- [ ] Python 3.8+ installé
- [ ] Structure de dossiers créée
- [ ] Dépendances Python installées
- [ ] Fichiers Python copiés dans les bons dossiers
- [ ] Test d'import réussi (`main_test.py`)
- [ ] Application Streamlit lance sans erreur
- [ ] Interface accessible via navigateur
- [ ] Test de connectivité endpoints (optionnel)
- [ ] Premier test de performance réussi

## 🚀 Prêt à commencer !

Si toutes les étapes sont validées, votre plateforme d'évaluation SPARQL est prête !

Vous pouvez maintenant :

1. **Configurer vos endpoints** dans la barre latérale
2. **Sélectionner vos requêtes** de test
3. **Lancer vos premiers benchmarks**
4. **Analyser les résultats** dans les onglets dédiés
5. **Exporter vos rapports** pour votre mémoire

---

*Pour toute question, consultez d'abord ce guide, puis la documentation dans le README.md*
