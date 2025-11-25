# 🔬 Module d'Analyses Détaillées - Documentation Complète

**Date**: 11 Novembre 2025
**Statut**: ✅ **TERMINÉ ET INTÉGRÉ**
**Version**: 1.0
**Fichier**: [ui/tabs/analysis_tab.py](ui/tabs/analysis_tab.py)

---

## 🎯 Vue d'Ensemble

Le module **analysis_tab.py** fournit des **analyses avancées automatiques** des résultats de benchmarks SPARQL avec :

- ✅ **Statistiques avancées** (moyenne, médiane, P95, P99, écart-type)
- ✅ **Détection automatique d'anomalies** (outliers)
- ✅ **Recommandations personnalisées** basées sur les patterns
- ✅ **Visualisations interactives** (box plots, violin plots, bar charts)
- ✅ **Export des analyses** (JSON, CSV)

---

## 📊 Fonctionnalités Principales

### 1. **Calculs Statistiques Automatiques**

```python
Statistics calculées pour chaque triplestore:
- Moyenne (mean)
- Médiane (median)
- Minimum / Maximum
- Écart-type (std)
- Percentiles: P25, P75, P95, P99
- Nombre de mesures (count)
```

**Pourquoi c'est utile** :
- P95/P99 montrent les "pires cas" (important pour la latence)
- Écart-type indique la stabilité des performances
- Médiane moins sensible aux outliers que la moyenne

---

### 2. **Détection Automatique d'Anomalies**

```python
Algorithme de détection:
1. Calculer moyenne et écart-type
2. Définir seuil = moyenne + 2.5 × écart-type
3. Marquer comme anomalie si temps > seuil
4. Classer par sévérité:
   - Critical: écart > 200% de la moyenne
   - Warning: écart > 150% de la moyenne
```

**Exemple d'anomalie détectée** :
```
🔴 Requête #7 (Virtuoso)
- Temps : 1250 ms (moyenne: 145 ms)
- Écart : +762% par rapport à la moyenne
- Raison : Temps anormalement élevé
```

---

### 3. **Système de Recommandations Intelligentes**

#### Types de Recommandations

**1. Comparaison Globale**
- Déclencheur : Différence > 30% entre Virtuoso et Fuseki
- Exemple : "Virtuoso est +42% plus rapide - Recommandation : Privilégier Virtuoso"

**2. Variabilité Élevée**
- Déclencheur : Coefficient de variation > 80%
- Exemple : "Variabilité de 120% détectée - Causes possibles : Cache non optimal, requêtes variées"

**3. Anomalies Critiques**
- Déclencheur : ≥1 anomalie avec écart > 200%
- Exemple : "3 requêtes anormalement lentes - Action : Vérifier les index"

**4. Optimisations Générales**
- Toujours affichée
- Conseils : Cache, Index, Warmup, Dataset size, Concurrency

---

### 4. **Visualisations Interactives**

#### Box Plot Comparatif

```
📊 Distribution des Temps de Réponse
┌─────────────────────────────────────┐
│        Virtuoso        Fuseki        │
│         [Box]          [Box]         │
│    Min─┬─Q1─┬─Med─┬─Q3─┬─Max       │
│        └────┴─────┴────┘             │
└─────────────────────────────────────┘
```

**Informations visibles** :
- Minimum / Maximum
- Quartiles (Q1, Q3)
- Médiane
- Outliers (points au-delà des moustaches)
- Moyenne (ligne pointillée)

#### Bar Chart - Métriques Clés

```
📊 Comparaison des Métriques Clés
     Virtuoso  Fuseki
Mean   ████     ██████
Med    ███      █████
P95    ████████ ███████
P99    ██████████ ████████
```

#### Violin Plot - Distribution Détaillée

```
📊 Distribution Détaillée
     Virtuoso      Fuseki
        ╱╲            ╱╲
       ╱  ╲          ╱  ╲
      ╱    ╲        ╱    ╲
     ╱      ╲      ╱      ╲
    ────────────────────────
    [Box]         [Box]
```

Montre la **densité de probabilité** des temps de réponse.

---

## 💻 Structure du Code

### Classes Principales

#### `PerformanceAnalyzer`

```python
class PerformanceAnalyzer:
    """Analyseur de performances avec statistiques et détection d'anomalies"""

    def __init__(self, results: Dict):
        """Initialise avec les résultats de benchmarks"""

    def _compute_statistics(self):
        """Calcule les statistiques pour chaque triplestore"""

    def _detect_anomalies(self):
        """Détecte les anomalies (outliers)"""

    def _generate_recommendations(self):
        """Génère des recommandations personnalisées"""

    def get_comparison_metrics(self) -> Dict:
        """Retourne les métriques de comparaison"""
```

### Fonctions de Visualisation

```python
def create_statistics_table(analyzer) -> str:
    """Crée un tableau HTML des statistiques"""

def create_box_plot(analyzer):
    """Crée un box plot comparatif avec Plotly"""

def create_comparison_bar_chart(analyzer):
    """Crée un graphique à barres comparatif"""

def create_violin_plot(analyzer):
    """Crée un violin plot pour la distribution"""
```

### Fonction Principale

```python
def render_detailed_analysis_tab():
    """Fonction principale pour afficher l'onglet"""

def render_analysis_tab():
    """Point d'entrée (alias)"""
```

---

## 📋 Format des Données Attendues

### Structure du `session_state['benchmark_results']`

```python
{
    'virtuoso': {
        'times': [12.5, 15.3, 18.7, ...],  # Temps en ms
        'queries': [1, 2, 3, ...]           # IDs des requêtes
    },
    'fuseki': {
        'times': [15.2, 18.1, 22.4, ...],
        'queries': [1, 2, 3, ...]
    }
}
```

**Important** :
- `times` : Liste de floats (temps en millisecondes)
- `queries` : Liste d'entiers (IDs des requêtes correspondantes)
- Les deux listes doivent avoir la même longueur

---

## 🎨 Interface Utilisateur

### Sections de l'Onglet

```
🔬 Analyses Détaillées
├── 📊 Vue d'Ensemble
│   ├── 4 Métriques Principales (Moyenne Virt/Fus, P95 Virt/Fus)
│   └── Bandeau Gagnant (si diff > 10%)
│
├── 📈 Statistiques Détaillées
│   └── Tableau comparatif (Mean, Median, Min, Max, Std, P95, P99)
│
├── ⚠️ Détection d'Anomalies
│   ├── Anomalies Critiques (rouge)
│   ├── Avertissements (orange)
│   └── Message si aucune anomalie (vert)
│
├── 💡 Recommandations Personnalisées
│   ├── Cartes colorées par niveau (critical/warning/info)
│   └── Contenu HTML formaté avec actions suggérées
│
├── 📊 Visualisations Avancées
│   ├── Box Plot Comparatif
│   ├── Bar Chart - Métriques Clés
│   └── Violin Plot - Distribution
│
└── 📥 Export des Analyses
    ├── Bouton Export JSON (stats + anomalies + recommandations)
    └── Bouton Export CSV (tableau des statistiques)
```

---

## 🔧 Utilisation

### Dans main_v3_refactored.py

```python
# Onglet "Résultats & Analyses"
with tabs[2]:
    sub_tabs = st.tabs([
        "📈 Résultats Bruts",
        "📊 Visualisations",
        "🔬 Analyses Détaillées"  # <-- Notre module
    ])

    with sub_tabs[2]:
        try:
            from ui.tabs.analysis_tab import render_analysis_tab
            render_analysis_tab()
        except ImportError:
            st.info("Module analysis_tab non disponible")
```

### Prérequis

1. **Résultats de benchmark** : Doit exister dans `st.session_state['benchmark_results']`
2. **Dépendances** :
   - `numpy` : Calculs statistiques
   - `pandas` : DataFrames (export CSV)
   - `plotly` : Visualisations interactives

**Installation** :
```bash
pip install numpy pandas plotly
```

---

## 📊 Exemples de Sortie

### Exemple 1 : Performance Stable

```
📊 Vue d'Ensemble
┌──────────────────────────────────────┐
│ Moyenne Virtuoso: 145.2 ms (±12.5)  │
│ P95 Virtuoso: 168.5 ms              │
│ Moyenne Fuseki: 189.7 ms (±15.3)    │
│ P95 Fuseki: 215.2 ms                │
└──────────────────────────────────────┘

🏆 Gagnant : Virtuoso
Virtuoso est 23.4% plus rapide en moyenne

⚠️ Détection d'Anomalies
✅ Aucune anomalie détectée - Les performances sont stables
```

### Exemple 2 : Anomalies Détectées

```
⚠️ Détection d'Anomalies
🔴 2 anomalie(s) critique(s) détectée(s) - Action requise

Requête #7 (Virtuoso)
- Temps : 1250.5 ms (moyenne: 145.2 ms)
- Écart : +761% par rapport à la moyenne
- Raison : Temps anormalement élevé

Requête #12 (Fuseki)
- Temps : 890.3 ms (moyenne: 189.7 ms)
- Écart : +369% par rapport à la moyenne
- Raison : Temps anormalement élevé

💡 Recommandations
🔴 2 anomalie(s) critique(s) détectée(s)
Action : Vérifier les index sur les prédicats utilisés
```

---

## 🎯 Algorithmes Utilisés

### 1. Détection d'Outliers (Z-Score)

```python
# Calcul du seuil
threshold = mean + 2.5 × std

# Classification
if time > threshold:
    if deviation > 200%:
        severity = "critical"
    else:
        severity = "warning"
```

**Justification** :
- 2.5 σ capture ~98.7% des données normales
- Au-delà = outlier probable

### 2. Coefficient de Variation (CV)

```python
CV = (std / mean) × 100

if CV > 80%:
    # Variabilité élevée
```

**Interprétation** :
- CV < 30% : Faible variabilité
- CV 30-80% : Variabilité modérée
- CV > 80% : Variabilité élevée

### 3. Comparaison Relative

```python
advantage = abs((mean_v - mean_f) / max(mean_v, mean_f)) × 100

if advantage > 30%:
    # Différence significative
elif advantage > 10%:
    # Différence notable
```

---

## 📈 Métriques Statistiques Expliquées

### Moyenne vs Médiane

**Moyenne** : Sensible aux outliers
- Utile pour le temps total

**Médiane** : Résistante aux outliers
- Utile pour le "temps typique"

**Exemple** :
```
Temps: [10, 12, 15, 18, 1000]
Moyenne: 211 ms  (biaisée par 1000)
Médiane: 15 ms   (représentative)
```

### Percentiles (P95, P99)

**P95** : 95% des requêtes sont plus rapides
- SLA typique : "P95 < 200ms"

**P99** : 99% des requêtes sont plus rapides
- Montre le "pire cas réaliste"

**Exemple** :
```
P95 = 180 ms : 95% des requêtes < 180ms
P99 = 250 ms : 99% des requêtes < 250ms
5% les plus lentes : 180-250 ms
```

---

## 🔍 Cas d'Usage

### Cas 1 : Identifier les Requêtes Problématiques

**Objectif** : Trouver quelles requêtes sont trop lentes

**Étapes** :
1. Lancer les tests
2. Aller dans "Analyses Détaillées"
3. Consulter la section "Détection d'Anomalies"
4. Noter les IDs des requêtes critiques
5. Optimiser ces requêtes spécifiquement

### Cas 2 : Choisir le Meilleur Triplestore

**Objectif** : Décider entre Virtuoso et Fuseki

**Étapes** :
1. Analyser la "Vue d'Ensemble"
2. Si différence > 30% : Choix clair
3. Si différence 10-30% : Analyser par type de requête
4. Si différence < 10% : Considérer d'autres critères (facilité, coût)

### Cas 3 : Valider une Optimisation

**Objectif** : Vérifier si une optimisation fonctionne

**Étapes** :
1. Lancer tests AVANT optimisation
2. Sauvegarder la session (Export JSON)
3. Appliquer l'optimisation
4. Lancer tests APRÈS
5. Comparer les statistiques (Mean, P95, anomalies)

---

## 📥 Export des Analyses

### Format JSON

```json
{
  "timestamp": "2025-11-11T15:30:45",
  "statistics": {
    "virtuoso": {
      "mean": 145.2,
      "median": 132.5,
      "std": 12.8,
      "p95": 168.5,
      "p99": 195.3
    },
    "fuseki": { ... }
  },
  "anomalies": [
    {
      "engine": "virtuoso",
      "query_id": 7,
      "time": 1250.5,
      "deviation": 761.2,
      "severity": "critical"
    }
  ],
  "recommendations": [
    {
      "title": "Performance globale...",
      "level": "important"
    }
  ]
}
```

### Format CSV

```csv
Engine,Metric,Value
Virtuoso,mean,145.2
Virtuoso,median,132.5
Virtuoso,std,12.8
Fuseki,mean,189.7
...
```

---

## ✅ Checklist de Validation

### Fonctionnalités
- [x] Calcul automatique des statistiques (mean, median, std, P95, P99)
- [x] Détection d'anomalies avec seuil 2.5σ
- [x] Génération de 4 types de recommandations
- [x] Box plot comparatif interactif
- [x] Bar chart des métriques clés
- [x] Violin plot de distribution
- [x] Export JSON des analyses
- [x] Export CSV des statistiques
- [x] Gestion des cas sans résultats
- [x] Gestion des erreurs d'import

### Interface
- [x] Vue d'ensemble avec 4 métriques principales
- [x] Bandeau gagnant si différence > 10%
- [x] Tableau HTML des statistiques
- [x] Section anomalies avec code couleur
- [x] Cartes de recommandations avec bordures colorées
- [x] 3 visualisations Plotly
- [x] 2 boutons d'export

### Documentation
- [x] Docstrings complètes
- [x] Commentaires dans le code
- [x] Guide d'utilisation (ce fichier)
- [x] Exemples de sortie
- [x] Explications des algorithmes

---

## 🚀 Améliorations Futures (Optionnelles)

### Phase 2 : Analyses Avancées

1. **Analyse par Type de Requête**
   - Regrouper par SELECT, CONSTRUCT, ASK, DESCRIBE
   - Statistiques séparées par type

2. **Corrélations**
   - Scatter plot : Taille résultat vs Temps
   - Corrélation : Complexité vs Performance

3. **Timeline**
   - Graphique d'évolution des performances dans le temps
   - Détection de dégradations progressives

4. **Comparaison de Sessions**
   - Charger 2 sessions JSON
   - Comparer côte à côte
   - Calculer les deltas

5. **Machine Learning**
   - Prédiction du temps d'exécution
   - Clustering des requêtes similaires
   - Suggestions d'optimisation basées sur ML

---

## 📞 Support

**Fichier** : [ui/tabs/analysis_tab.py](ui/tabs/analysis_tab.py)
**Documentation** : [ANALYSIS_MODULE_COMPLETE.md](ANALYSIS_MODULE_COMPLETE.md)
**Intégration** : [main_v3_refactored.py](main_v3_refactored.py) ligne 524-533

---

**Date de création** : 11 Novembre 2025
**Version** : 1.0
**Statut** : ✅ **PRODUCTION READY**
**Lignes de code** : ~650 lignes
**Tests** : Mode test inclus (voir `if __name__ == "__main__"`)

---

# 🎉 Module d'Analyses Détaillées Complet et Opérationnel ! 🔬
