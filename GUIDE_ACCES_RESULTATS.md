# 📊 Guide d'Accès aux Résultats depuis la Plateforme

## Comment accéder aux visualisations et analyses du Chapitre 4 depuis la plateforme SPARQL Performance Platform

---

## 🚀 Démarrage de la Plateforme

### Étape 1 : Lancer la Plateforme

```bash
# Depuis le terminal, dans le dossier du projet
cd c:\Users\hp\Documents\M2\Web Semantique\Mémoire\Code_NV\Extract\nv\sparql_v2

# Activer l'environnement virtuel (si nécessaire)
.\venv\Scripts\activate

# Lancer Streamlit
streamlit run main.py
```

**Ou simplement :**
```bash
# Si vous êtes déjà dans le bon dossier
streamlit run main.py
```

La plateforme s'ouvrira automatiquement dans votre navigateur à l'adresse : `http://localhost:8501`

---

## 📍 Navigation dans la Plateforme

### Interface Principale

Une fois la plateforme lancée, vous verrez la barre de navigation en haut avec plusieurs onglets :

```
🏠 Accueil | ⚙️ Configuration & Tests | 📊 Datasets | 📈 Résultats & Analyses | 💾 Export & Sessions | 📖 Documentation
```

---

## 📈 Accès aux Résultats et Visualisations

### Méthode 1 : Onglet "Résultats & Analyses" (Principal) ⭐

**Navigation :** Cliquez sur l'onglet **"📈 Résultats & Analyses"**

#### Sections Disponibles :

1. **📊 Vue d'Ensemble**
   - Résumé des derniers tests exécutés
   - Métriques clés : temps moyen, médiane, écart-type
   - Tableau récapitulatif des performances

2. **📉 Comparaison des Moteurs**
   - Graphique en barres : Comparaison Virtuoso vs Fuseki
   - Temps d'exécution par type de requête
   - Visualisation interactive (Plotly)

3. **📦 Distribution des Performances**
   - **Box Plots** : Distribution statistique des temps d'exécution
   - **Violin Plots** : Densité de probabilité
   - Détection des outliers

4. **📈 Analyses Avancées**
   - **CDF (Cumulative Distribution Function)** : Percentiles
   - **Waterfall Chart** : Contribution par type de requête
   - Corrélation taille du résultat vs temps

5. **🔍 Analyses Détaillées**
   - Statistiques complètes (moyenne, médiane, min, max, P95, P99)
   - Tests statistiques (Mann-Whitney U, p-values)
   - Intervalles de confiance

---

### Méthode 2 : Onglet "Export & Sessions"

**Navigation :** Cliquez sur l'onglet **"💾 Export & Sessions"**

#### Fonctionnalités :

1. **📥 Exporter les Résultats**
   - **Format CSV** : Données brutes pour analyse externe
   - **Format Excel** : Tableaux formatés avec graphiques
   - **Format JSON** : Données structurées pour scripts
   - **Rapport HTML** : Rapport complet avec visualisations intégrées

2. **💾 Sauvegarder/Charger Sessions**
   - Sauvegarder l'état complet de la session
   - Recharger une session précédente
   - Comparer plusieurs sessions

3. **📊 Générer Rapport Complet**
   - Rapport automatique incluant :
     - Résumé exécutif
     - Métriques détaillées
     - Visualisations
     - Recommandations

---

## 🎨 Visualisations Disponibles dans la Plateforme

### 1. Graphiques de Comparaison

**Accès :** Onglet "Résultats & Analyses" → Section "Comparaison des Moteurs"

**Types de graphiques :**
- ✅ **Bar Chart** : Comparaison des temps moyens
- ✅ **Grouped Bar Chart** : Comparaison par type de requête
- ✅ **Scatter Plot** : Corrélation performances

**Interactivité :**
- Zoom sur les zones d'intérêt
- Affichage des valeurs au survol (hover)
- Export en PNG haute résolution

### 2. Graphiques de Distribution

**Accès :** Onglet "Résultats & Analyses" → Section "Distribution des Performances"

**Types de graphiques :**
- ✅ **Box Plots** : Distribution avec quartiles
- ✅ **Violin Plots** : Densité de probabilité
- ✅ **Histogrammes** : Fréquence des temps d'exécution

**Informations affichées :**
- Médiane (ligne centrale)
- Quartiles Q1 (25%) et Q3 (75%)
- Min et Max (moustaches)
- Outliers (points isolés)

### 3. Analyses Avancées

**Accès :** Onglet "Résultats & Analyses" → Section "Analyses Avancées"

**Types de graphiques :**
- ✅ **CDF (Cumulative Distribution Function)** : Percentiles cumulés
- ✅ **Waterfall Chart** : Contribution au temps total
- ✅ **Heatmap** : Matrice moteur × type de requête
- ✅ **Radar Chart** : Comparaison multi-critères

### 4. Métriques et Statistiques

**Accès :** Onglet "Résultats & Analyses" → Section "Analyses Détaillées"

**Tableaux disponibles :**
- ✅ **Statistiques descriptives** : Moyenne, médiane, écart-type, min, max
- ✅ **Percentiles** : P25, P50 (médiane), P75, P95, P99
- ✅ **Tests statistiques** : Mann-Whitney U, p-values, significativité
- ✅ **Intervalles de confiance** : IC 95% (Bootstrap)

---

## 📊 Utilisation des Ressources Système

### Accès au Monitoring en Temps Réel

**Sidebar (barre latérale gauche) → Section "💻 Monitoring"**

**Métriques affichées :**
- ✅ **CPU** : Pourcentage d'utilisation
- ✅ **RAM** : Pourcentage de mémoire utilisée

**Codes couleur :**
- 🟢 Vert : Utilisation normale (<60%)
- 🟡 Jaune : Utilisation modérée (60-85%)
- 🔴 Rouge : Utilisation élevée (>85%)

### Dashboard Système Complet

**Sidebar → Bouton "📊 État Système"**

**Informations détaillées :**
- CPU : Utilisation globale et par cœur
- RAM : Utilisée, disponible, totale
- Disque : Espace utilisé et libre
- Processus : Liste des processus actifs

---

## 🔄 Workflow Complet pour Accéder aux Résultats

### Scénario 1 : Consulter les Résultats d'un Test Existant

1. **Démarrer la plateforme** : `streamlit run main.py`
2. **Cliquer sur "📈 Résultats & Analyses"**
3. **Sélectionner une session** (si plusieurs disponibles)
4. **Explorer les sections** :
   - Vue d'ensemble pour résumé
   - Comparaison pour graphiques
   - Distribution pour box plots
   - Analyses avancées pour CDF/Waterfall
5. **Exporter** (optionnel) : Onglet "💾 Export & Sessions" → Télécharger CSV/Excel

### Scénario 2 : Générer de Nouvelles Visualisations

1. **Démarrer la plateforme**
2. **Onglet "⚙️ Configuration & Tests"**
3. **Configurer les endpoints** (Virtuoso, Fuseki)
4. **Sélectionner les requêtes** à tester
5. **Lancer le benchmark** → Bouton "🚀 Lancer le Benchmark"
6. **Attendre la fin des tests** (barre de progression)
7. **Basculer sur "📈 Résultats & Analyses"** pour voir les visualisations
8. **Exporter les images** :
   - Clic droit sur un graphique → "Enregistrer l'image sous..."
   - Ou utiliser le bouton d'export de Plotly (icône caméra en haut à droite du graphique)

### Scénario 3 : Exporter un Rapport Complet

1. **Onglet "💾 Export & Sessions"**
2. **Section "Générer Rapport"**
3. **Sélectionner le format** :
   - **HTML** : Rapport interactif avec graphiques cliquables (recommandé pour mémoire)
   - **PDF** : Rapport figé pour impression
   - **Excel** : Données + graphiques dans un classeur
4. **Cliquer sur "📄 Générer le Rapport"**
5. **Télécharger le fichier** généré

---

## 📸 Capture des Visualisations pour le Mémoire

### Méthode 1 : Export Direct depuis Plotly

**Pour chaque graphique Plotly :**

1. **Survoler le graphique** → Barre d'outils apparaît en haut à droite
2. **Cliquer sur l'icône caméra** 📷
3. **Sélectionner le format** :
   - PNG (recommandé pour le mémoire)
   - SVG (qualité vectorielle pour impression)
   - JPEG
4. **Télécharger** l'image

**Résolution :** Par défaut haute résolution (1200×800px)

### Méthode 2 : Capture d'Écran

**Outil Windows :**
1. **Ouvrir l'outil Capture d'écran** : `Win + Shift + S`
2. **Sélectionner la zone** du graphique
3. **Coller** dans un éditeur d'image ou directement dans Word

**Outil de Capture Complète :**
- **Snipping Tool** (Windows 10/11)
- **Snagit** (payant, haute qualité)
- **ShareX** (gratuit, open-source)

### Méthode 3 : Export Programmatique

**Si vous avez besoin de haute résolution :**

```python
# Dans le code de la plateforme (pour développeurs)
import plotly.graph_objects as go

fig = go.Figure(...)  # Votre graphique
fig.write_image("graphique.png", width=1920, height=1080, scale=2)
```

---

## 📂 Localisation des Fichiers Exportés

### Dossiers de Résultats

**Par défaut, les fichiers sont enregistrés dans :**

```
sparql_v2/
├── results/                    # Résultats des tests
│   ├── session_YYYYMMDD_HHMMSS/
│   │   ├── raw_results.json
│   │   ├── metrics_summary.csv
│   │   └── report.html
│   └── latest/                 # Dernier test (lien symbolique)
│
├── exports/                    # Exports manuels
│   ├── comparison_chart.png
│   ├── box_plots.png
│   └── rapport_complet.html
│
└── images/
    └── images_mémoire/         # Images utilisées dans le mémoire
        ├── Page d'accueil 1.png
        ├── Comparaison des temps d'exécution...
        └── ... (18 images au total)
```

### Chemin d'Accès

**Pour retrouver vos fichiers :**

```bash
# Ouvrir le dossier des résultats
cd c:\Users\hp\Documents\M2\Web Semantique\Mémoire\Code_NV\Extract\nv\sparql_v2\results

# Lister les sessions disponibles
dir

# Ouvrir la dernière session
cd latest
```

**Ou via l'explorateur Windows :**
- Coller ce chemin dans l'explorateur :
  ```
  c:\Users\hp\Documents\M2\Web Semantique\Mémoire\Code_NV\Extract\nv\sparql_v2\results
  ```

---

## 🔍 Trouver les Visualisations Spécifiques du Chapitre 4

### Images Déjà Disponibles

**Dossier :** `images/images_mémoire/`

**Liste complète (18 images) :**

1. **Interface Plateforme**
   - `Page d'accueil 1.png`
   - `Page d'accueil 2.png`

2. **Comparaisons**
   - `Comparaison des temps d'exécution Virtuoso vs Jena Fuseki.png`
   - `Temps d'exécution par requête et moteur.png`
   - `Comparaison des métriques Clés.png`

3. **Distributions**
   - `Box Plot.png`
   - `Violin Plot.png`
   - `Analyse de Distribution_BoxPlot_ViolinPlot.png`
   - `Distribution des temps de Réponse.png`
   - `Distribution Détaillée (Violin Plot).png`

4. **Analyses Avancées**
   - `CDF (Percentiles).png`
   - `Waterfall (Contribution).png`
   - `Analyse Avancée_CDF_Waterfall.png`

5. **Métriques et Statistiques**
   - `Métriques Statistiques Complètes.png`
   - `Analyses Détaillées.png`
   - `Analyses Détaillées.csv`

6. **Ressources Système**
   - `Utilisation CPU.png`
   - `Utilisation mémoire.png`
   - `Mémoire & CPU.png`

**Accès direct :**
```bash
# Ouvrir le dossier des images
cd c:\Users\hp\Documents\M2\Web Semantique\Mémoire\Code_NV\Extract\nv\sparql_v2\images\images_mémoire

# Ou via l'explorateur
explorer images\images_mémoire
```

---

## 💡 Conseils Pratiques

### Pour Générer de Nouvelles Visualisations

1. **Utiliser le profil "Standard"** : Équilibre entre exhaustivité et durée (10 minutes)
2. **Sélectionner les 6 types de requêtes** : SELECT, JOIN, FILTER, Aggregation, OPTIONAL/UNION, Subquery
3. **Configurer 5-10 répétitions** : Compromis entre fiabilité et temps
4. **Vérifier la synchronisation des datasets** : Onglet "Datasets" → Bouton "Vérifier la Cohérence"

### Pour des Graphiques de Haute Qualité

1. **Maximiser la fenêtre du navigateur** avant capture
2. **Utiliser le thème clair** (meilleur contraste pour impression)
3. **Exporter en PNG** plutôt que JPEG (pas de compression)
4. **Résolution minimale** : 1200×800px (Plotly par défaut)

### Pour Reproduire les Résultats du Chapitre 4

**Configuration exacte utilisée :**

```yaml
# Paramètres de test
Profil: Standard (10 minutes)
Itérations: 5 + 2 warmup
Timeout: 60 secondes par requête
Dataset: LUBM (100 000 triplets)

# Endpoints
Virtuoso: http://localhost:8890/sparql
Fuseki: http://localhost:3030/dataset/query

# Requêtes testées (6 types)
- SELECT_basic (3 requêtes)
- JOIN (3 requêtes)
- FILTER (3 requêtes)
- Aggregation (3 requêtes)
- OPTIONAL_UNION (3 requêtes)
- Subquery (3 requêtes)
```

**Pour reproduire :**
1. Onglet "⚙️ Configuration & Tests"
2. Sélectionner "Profil Standard"
3. Cocher les 18 requêtes LUBM (6 types × 3 requêtes)
4. Cliquer "🚀 Lancer le Benchmark"

---

## 🆘 Dépannage

### La plateforme ne démarre pas

**Erreur :** `streamlit: command not found`

**Solution :**
```bash
# Activer l'environnement virtuel
.\venv\Scripts\activate

# Vérifier l'installation
pip list | findstr streamlit

# Si absent, réinstaller
pip install streamlit
```

### Les graphiques ne s'affichent pas

**Cause probable :** Données manquantes ou session vide

**Solution :**
1. Vérifier qu'un test a été exécuté
2. Onglet "📈 Résultats & Analyses" → Section "Charger Session"
3. Sélectionner une session existante

### Les images ne se téléchargent pas

**Cause :** Bloqueur de pop-ups ou téléchargement automatique désactivé

**Solution :**
1. Autoriser les pop-ups pour `localhost:8501`
2. Vérifier les paramètres de téléchargement du navigateur
3. Utiliser la capture d'écran en fallback

---

## 📞 Support

### Documentation Complète

- **Guide principal** : `README.md` (racine du projet)
- **Guide présentation** : `GUIDE_PRESENTATION.md`
- **Guide finalisation** : `GUIDE_FINALISATION_MEMOIRE.md`
- **Index complet** : `MEMOIRE_COMPLET_INDEX.md`

### Ressources Techniques

- **Streamlit Docs** : [https://docs.streamlit.io/](https://docs.streamlit.io/)
- **Plotly Docs** : [https://plotly.com/python/](https://plotly.com/python/)
- **SPARQLWrapper** : [https://sparqlwrapper.readthedocs.io/](https://sparqlwrapper.readthedocs.io/)

---

## ✅ Checklist d'Accès aux Résultats

- [ ] Plateforme démarrée (`streamlit run main.py`)
- [ ] Onglet "Résultats & Analyses" accessible
- [ ] Visualisations affichées correctement
- [ ] Possibilité d'export des graphiques (PNG)
- [ ] Rapport HTML généré (optionnel)
- [ ] Images sauvegardées dans `images/images_mémoire/`
- [ ] Chemins des images notés pour inclusion dans le mémoire

---

## 🎉 Conclusion

Vous avez maintenant **toutes les clés** pour accéder aux résultats et visualisations depuis la plateforme !

**Workflow recommandé :**
1. ✅ Démarrer la plateforme
2. ✅ Naviguer vers "Résultats & Analyses"
3. ✅ Explorer les visualisations interactives
4. ✅ Exporter les graphiques nécessaires
5. ✅ Intégrer dans le mémoire (référencées dans le Chapitre 4)

**Les 18 images du Chapitre 4 sont déjà disponibles** dans `images/images_mémoire/` et référencées dans `CHAPITRE 4 - COMPLET.md` ! 📊✨

---

**Généré le :** 24 novembre 2025
**Version :** 1.0
**Statut :** Guide Complet d'Accès
