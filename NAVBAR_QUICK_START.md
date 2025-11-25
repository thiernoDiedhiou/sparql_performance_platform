# 🚀 Quick Start : Remplacer la Navbar Actuelle

**Temps estimé** : 15 minutes
**Difficulté** : Facile

---

## 📋 Ce que Vous Allez Faire

Remplacer la navbar actuelle (lignes 343-478 de `main_v3_refactored.py`) par la **navbar custom professionnelle**.

---

## ⚡ Méthode Rapide (Copier-Coller)

### Étape 1 : Sauvegarder l'Ancien Code

```bash
# Créer une copie de sauvegarde
cp main_v3_refactored.py main_v3_refactored.py.backup
```

### Étape 2 : Ouvrir `main_v3_refactored.py`

Localisez ces lignes (environ ligne 343-478) :

```python
# ========================================================================
# NAVBAR STICKY PROFESSIONNELLE (COORDONNÉE AVEC SIDEBAR)
# ========================================================================
navbar_html = f"""
    <style>
        /* Forcer la largeur pleine en supprimant les marges Streamlit */
        .main .block-container {{
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 100% !important;
            padding-top: 1rem;
        }}
        # ... (beaucoup de CSS) ...
    </style>

    <div class="sticky-navbar" id="mainNavbar">
        # ...
    </div>
    <div class="navbar-spacer"></div>
"""
st.markdown(navbar_html, unsafe_allow_html=True)

# ========================================================================
# ONGLETS PRINCIPAUX OPTIMISÉS (5 AU LIEU DE 8)
# ========================================================================
tabs = st.tabs([
    "🚀 Configuration & Tests",
    "📦 Datasets",
    "📊 Résultats & Analyses",
    "📤 Export & Sessions",
    "📖 Documentation"
])
```

### Étape 3 : Remplacer par le Nouveau Code

**SUPPRIMER** tout le code ci-dessus et le **REMPLACER** par :

```python
# ========================================================================
# NAVBAR PROFESSIONNELLE (VERSION CUSTOM)
# ========================================================================
from ui.components.navbar_custom import render_custom_navbar

# Afficher la navbar et récupérer la page active
current_page = render_custom_navbar()

# Conteneur principal avec ID pour accessibilité
st.markdown('<main id="main-content" role="main">', unsafe_allow_html=True)
```

### Étape 4 : Adapter les Onglets

**AVANT** (avec `st.tabs`) :
```python
# ONGLET 1: CONFIGURATION & TESTS
with tabs[0]:
    st.markdown("### 🚀 Configuration & Exécution des Tests")
    # ... code de configuration ...

# ONGLET 2: DATASETS
with tabs[1]:
    st.markdown("### 📦 Gestion des Datasets")
    # ... code des datasets ...

# ONGLET 3: RÉSULTATS & ANALYSES
with tabs[2]:
    st.markdown("### 📊 Résultats & Analyses")
    # ... code des résultats ...

# ONGLET 4: EXPORT & SESSIONS
with tabs[3]:
    st.markdown("### 📤 Export & Sessions")
    # ... code export ...

# ONGLET 5: DOCUMENTATION
with tabs[4]:
    st.markdown("### 📖 Documentation")
    # ... code docs ...
```

**APRÈS** (avec navigation par page) :
```python
# ========================================================================
# ROUTER DE NAVIGATION
# ========================================================================

if current_page == "config":
    # =====================================================================
    # PAGE 1: CONFIGURATION & TESTS
    # =====================================================================
    st.markdown("### 🚀 Configuration & Exécution des Tests")
    # ... MÊME code de configuration (aucun changement) ...

elif current_page == "datasets":
    # =====================================================================
    # PAGE 2: DATASETS
    # =====================================================================
    st.markdown("### 📦 Gestion des Datasets")
    # ... MÊME code des datasets (aucun changement) ...

elif current_page == "results":
    # =====================================================================
    # PAGE 3: RÉSULTATS & ANALYSES
    # =====================================================================
    st.markdown("### 📊 Résultats & Analyses")
    # ... MÊME code des résultats (aucun changement) ...

elif current_page == "export":
    # =====================================================================
    # PAGE 4: EXPORT & SESSIONS
    # =====================================================================
    st.markdown("### 📤 Export & Sessions")
    # ... MÊME code export (aucun changement) ...

elif current_page == "docs":
    # =====================================================================
    # PAGE 5: DOCUMENTATION
    # =====================================================================
    st.markdown("### 📖 Documentation")
    # ... MÊME code docs (aucun changement) ...

# Fermer le conteneur main
st.markdown('</main>', unsafe_allow_html=True)
```

### Étape 5 : Tester

```bash
streamlit run main_v3_refactored.py
```

---

## 🔍 Changements Détaillés

### Ce qui Change

| Avant | Après |
|-------|-------|
| `with tabs[0]:` | `if current_page == "config":` |
| `with tabs[1]:` | `elif current_page == "datasets":` |
| `with tabs[2]:` | `elif current_page == "results":` |
| `with tabs[3]:` | `elif current_page == "export":` |
| `with tabs[4]:` | `elif current_page == "docs":` |

### Ce qui Ne Change PAS

✅ **Tout le contenu des pages reste identique** !
- Code de configuration ✅
- Code des datasets ✅
- Code des résultats ✅
- Code d'export ✅
- Code de documentation ✅

**Seule la structure de navigation change !**

---

## 📝 Code Complet de Remplacement

Voici le code exact à copier-coller :

```python
# ========================================================================
# NAVBAR PROFESSIONNELLE (VERSION CUSTOM)
# ========================================================================
from ui.components.navbar_custom import render_custom_navbar

# Afficher la navbar et récupérer la page active
current_page = render_custom_navbar()

# Conteneur principal avec ID pour accessibilité
st.markdown('<main id="main-content" role="main">', unsafe_allow_html=True)

# ========================================================================
# ROUTER DE NAVIGATION
# ========================================================================

if current_page == "config":
    # =====================================================================
    # PAGE 1: CONFIGURATION & TESTS (FUSION DE 2 ONGLETS)
    # =====================================================================
    st.markdown("### 🚀 Configuration & Exécution des Tests")
    st.caption("Configurez les endpoints SPARQL et lancez les benchmarks")

    create_divider()

    # Vérification de la connectivité
    st.markdown("#### 🔗 Vérification de la connectivité")
    render_connectivity_checker()

    create_divider()

    # Informations système
    st.markdown("#### 💻 Informations sur l'environnement")
    render_system_info()

    create_divider()

    # Configuration et exécution des tests
    render_configuration_tab()

elif current_page == "datasets":
    # =====================================================================
    # PAGE 2: GESTION DES DATASETS
    # =====================================================================
    st.markdown("### 📦 Gestion des Datasets")
    st.caption("Chargez et gérez vos datasets RDF pour les tests")

    create_divider()

    render_datasets_tab()

elif current_page == "results":
    # =====================================================================
    # PAGE 3: RÉSULTATS & ANALYSES (FUSION DE 2 ONGLETS)
    # =====================================================================
    st.markdown("### 📊 Résultats & Analyses")
    st.caption("Visualisez et analysez les résultats des benchmarks")

    create_divider()

    # Sous-onglets pour Résultats
    results_subtabs = st.tabs([
        "📈 Résultats Bruts",
        "📊 Visualisations",
        "🔬 Analyses Détaillées"
    ])

    with results_subtabs[0]:
        render_results_tab()

    with results_subtabs[1]:
        render_visualizations_tab()

    with results_subtabs[2]:
        render_detailed_analysis_tab()

elif current_page == "export":
    # =====================================================================
    # PAGE 4: EXPORT & SESSIONS
    # =====================================================================
    st.markdown("### 📤 Export & Sessions")
    st.caption("Exportez vos résultats et gérez vos sessions")

    create_divider()

    render_export_tab()

elif current_page == "docs":
    # =====================================================================
    # PAGE 5: DOCUMENTATION
    # =====================================================================
    st.markdown("### 📖 Documentation")
    st.caption("Guide d'utilisation de la plateforme")

    create_divider()

    st.markdown("""
    ## 🚀 Guide de Démarrage Rapide

    ### 1. Configuration des Endpoints

    Commencez par configurer vos endpoints SPARQL dans l'onglet **Configuration & Tests**.

    **Exemple pour Virtuoso** :
    ```
    http://localhost:8890/sparql
    ```

    **Exemple pour Jena Fuseki** :
    ```
    http://localhost:3030/dataset/query
    ```

    ### 2. Chargement des Datasets

    Rendez-vous dans l'onglet **Datasets** pour :
    - Charger des fichiers RDF (Turtle, N-Triples, RDF/XML)
    - Gérer vos datasets existants
    - Vérifier les statistiques

    ### 3. Exécution des Tests

    Dans l'onglet **Configuration & Tests** :
    1. Sélectionnez les requêtes à tester
    2. Configurez les paramètres (warmup, répétitions)
    3. Cliquez sur "Exécuter les tests"

    ### 4. Analyse des Résultats

    L'onglet **Résultats & Analyses** offre :
    - **Résultats bruts** : Tableau détaillé des exécutions
    - **Visualisations** : Graphiques interactifs (box plots, bar charts)
    - **Analyses détaillées** : Statistiques avancées, détection d'anomalies, recommandations

    ### 5. Export des Données

    Exportez vos résultats dans l'onglet **Export & Sessions** :
    - Format JSON (complet)
    - Format CSV (pour Excel)
    - Format Excel (avec graphiques)

    ---

    ## 📚 Ressources

    ### Documentation Technique

    - [SPARQL 1.1 Specification](https://www.w3.org/TR/sparql11-query/)
    - [RDF 1.1 Concepts](https://www.w3.org/TR/rdf11-concepts/)
    - [Virtuoso Documentation](http://docs.openlinksw.com/virtuoso/)
    - [Jena Fuseki Documentation](https://jena.apache.org/documentation/fuseki2/)

    ### Exemples de Requêtes

    #### Requête Simple (SELECT)
    ```sparql
    SELECT ?subject ?predicate ?object
    WHERE {
      ?subject ?predicate ?object
    }
    LIMIT 100
    ```

    #### Requête avec FILTER
    ```sparql
    SELECT ?person ?name
    WHERE {
      ?person rdf:type foaf:Person .
      ?person foaf:name ?name .
      FILTER(LANG(?name) = "fr")
    }
    ```

    #### Requête avec COUNT
    ```sparql
    SELECT (COUNT(?subject) AS ?count)
    WHERE {
      ?subject rdf:type ?type
    }
    ```

    ---

    ## ❓ FAQ

    ### Comment interpréter les résultats ?

    - **Temps d'exécution moyen** : Indicateur principal de performance
    - **Écart-type** : Mesure de la variabilité (plus c'est bas, mieux c'est)
    - **P95/P99** : 95% et 99% des requêtes sont plus rapides que cette valeur

    ### Que faire en cas d'anomalie détectée ?

    1. Vérifier les index sur les prédicats utilisés
    2. Analyser la complexité de la requête (JOINs, FILTERs)
    3. Augmenter les ressources allouées (mémoire, CPU)
    4. Tester avec un dataset plus petit

    ### Comment optimiser les performances ?

    - Activer le cache des requêtes
    - Augmenter les itérations de warmup
    - Créer des index sur les prédicats fréquents
    - Utiliser LIMIT pour limiter les résultats

    ---

    ## 🆘 Support

    En cas de problème, vérifiez :
    1. La connectivité aux endpoints SPARQL
    2. Les logs d'erreur dans la console
    3. Les ressources système (CPU, RAM)
    """)

# Fermer le conteneur main
st.markdown('</main>', unsafe_allow_html=True)
```

---

## ✅ Checklist de Validation

Après le remplacement, vérifiez :

- [ ] L'application démarre sans erreur
- [ ] La navbar est visible en haut
- [ ] Les 5 pages sont accessibles (config, datasets, results, export, docs)
- [ ] La page active est visuellement identifiée (fond blanc)
- [ ] Le contenu de chaque page s'affiche correctement
- [ ] La navbar reste fixe au scroll
- [ ] Pas de conflit avec la sidebar
- [ ] Navigation clavier fonctionnelle (Tab/Enter)

---

## 🐛 Problèmes Courants

### Erreur : "Module 'navbar_custom' not found"

**Solution** : Vérifiez que le fichier existe à :
```
ui/components/navbar_custom.py
```

### Navbar pas visible

**Solution** : Vérifiez que vous avez bien importé :
```python
from ui.components.navbar_custom import render_custom_navbar
```

### Contenu qui ne s'affiche pas

**Solution** : Vérifiez que vous avez bien remplacé `with tabs[X]:` par `if current_page == "xxx":`

### Navbar trop large ou trop étroite

**Solution** : Ajustez `left: 250px` dans le CSS de `navbar_custom.py` (ligne 362)

---

## 🔄 Rollback (Annuler les Changements)

Si vous voulez revenir en arrière :

```bash
# Restaurer l'ancienne version
cp main_v3_refactored.py.backup main_v3_refactored.py

# Relancer l'application
streamlit run main_v3_refactored.py
```

---

## 🎉 Résultat Attendu

Après le remplacement, vous devriez avoir :

```
╔═══════════════════════════════════════════════════════════════╗
║ ⚡ SPARQL Performance Platform                                ║
║ Benchmarking professionnel • v3.1                             ║
║                                                                ║
║ [🚀 Config] [📦 Datasets] [📊 Résultats] [📤 Export] [📖 Docs] ║
╚═══════════════════════════════════════════════════════════════╝

┌───────────────────────────────────────────────────────────────┐
│                                                               │
│  🚀 Configuration & Exécution des Tests                       │
│                                                               │
│  🔗 Vérification de la connectivité                          │
│  [Tester la connectivité]                                    │
│                                                               │
│  ... (contenu de la page)                                    │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

**Navbar** :
- ✅ Fixe en haut (ne bouge pas au scroll)
- ✅ Pleine largeur (après la sidebar)
- ✅ Page active visible (fond blanc)
- ✅ Hover fluide (fond semi-transparent)
- ✅ Accessible au clavier (Tab/Enter)

---

## 📚 Fichiers Modifiés

| Fichier | Action | Lignes |
|---------|--------|--------|
| `main_v3_refactored.py` | Modifié | ~150 lignes changées |
| `ui/components/navbar_custom.py` | Créé | +400 lignes |
| `requirements.txt` | Modifié | +2 lignes |

---

## 🚀 Prochaines Étapes

Une fois la navbar intégrée :

1. **Tester sur différents navigateurs** (Chrome, Firefox, Safari)
2. **Tester le responsive** (resize la fenêtre)
3. **Tester l'accessibilité** (navigation clavier)
4. **Personnaliser les couleurs** (si nécessaire)
5. **Ajouter des badges** "NEW" (optionnel)

---

**Temps total estimé** : 15 minutes
**Niveau de difficulté** : ⭐⭐☆☆☆ (Facile)

**Besoin d'aide ?** Consultez le guide complet : [NAVBAR_IMPLEMENTATION_GUIDE.md](NAVBAR_IMPLEMENTATION_GUIDE.md)
