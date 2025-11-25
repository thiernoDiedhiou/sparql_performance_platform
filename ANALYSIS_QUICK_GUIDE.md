# 🔬 Guide Rapide - Analyses Détaillées

**Version**: 1.0 | **Durée de lecture**: 2 minutes

---

## 🎯 Qu'est-ce que c'est ?

Un onglet qui **analyse automatiquement** vos résultats de benchmarks et vous donne :
- 📊 **Statistiques avancées** (moyenne, P95, P99)
- ⚠️ **Détection d'anomalies** (requêtes trop lentes)
- 💡 **Recommandations** personnalisées
- 📈 **Visualisations** interactives

---

## 🚀 Comment l'utiliser ?

### Étape 1 : Lancer des Tests

```
1. Aller dans l'onglet "🚀 Configuration & Tests"
2. Cliquer sur "Exécuter les tests"
3. Attendre la fin des benchmarks
```

### Étape 2 : Ouvrir les Analyses

```
1. Aller dans l'onglet "📊 Résultats & Analyses"
2. Cliquer sur le sous-onglet "🔬 Analyses Détaillées"
3. Consulter les insights automatiques
```

---

## 📊 Ce que vous verrez

### 1. Vue d'Ensemble (En Haut)

```
┌────────────────┬────────────────┐
│ Moyenne Virt.  │ P95 Virtuoso   │
│ 145.2 ms       │ 168.5 ms       │
├────────────────┼────────────────┤
│ Moyenne Fuseki │ P95 Fuseki     │
│ 189.7 ms       │ 215.2 ms       │
└────────────────┴────────────────┘

🏆 Gagnant : Virtuoso (+23.4%)
```

### 2. Statistiques Détaillées

Tableau complet avec :
- Moyenne / Médiane
- Min / Max
- Écart-type
- P95 / P99

### 3. Anomalies Détectées

```
⚠️ 2 anomalie(s) critique(s)

🔴 Requête #7 (Virtuoso)
- Temps : 1250 ms (moyenne: 145 ms)
- Écart : +761%
→ Action : Optimiser cette requête
```

### 4. Recommandations

Cartes colorées avec conseils :
- 🔴 **Critique** : Action immédiate requise
- 🟡 **Important** : À considérer
- 🔵 **Info** : Optimisations générales

### 5. Graphiques Interactifs

- **Box Plot** : Distribution comparée
- **Bar Chart** : Métriques côte à côte
- **Violin Plot** : Densité de probabilité

---

## 💡 Interprétation Rapide

### Si vous voyez...

| Observation | Signification | Action |
|-------------|---------------|--------|
| **Écart-type élevé** | Performances variables | Analyser requête par requête |
| **P95 >> Moyenne** | Quelques requêtes très lentes | Chercher les outliers |
| **Anomalies critiques** | Requêtes problématiques | Optimiser les index |
| **Gagnant clair (>30%)** | Choix évident | Utiliser le gagnant |

### Métriques Importantes

**P95** : 95% des requêtes sont plus rapides
- 📍 Exemple : P95 = 180ms → 95% < 180ms

**P99** : 99% des requêtes sont plus rapides
- 📍 Exemple : P99 = 250ms → "Pire cas réaliste"

**Écart-type** : Stabilité des performances
- ✅ Faible (<20% de la moyenne) : Stable
- ⚠️ Élevé (>80% de la moyenne) : Variable

---

## 📥 Export

### JSON (Complet)
```json
{
  "statistics": {...},
  "anomalies": [...],
  "recommendations": [...]
}
```
→ Pour archivage ou analyse externe

### CSV (Tableau)
```csv
Engine,Metric,Value
Virtuoso,mean,145.2
Virtuoso,p95,168.5
...
```
→ Pour Excel, R, Python

---

## 🎯 Cas d'Usage

### 1. Identifier les Requêtes Lentes

```
1. Consulter "Détection d'Anomalies"
2. Noter les IDs (ex: Requête #7, #12)
3. Retour aux résultats bruts
4. Analyser ces requêtes spécifiques
5. Optimiser (index, FILTER, JOIN)
```

### 2. Choisir Virtuoso ou Fuseki

```
1. Regarder "Vue d'Ensemble"
2. Si écart > 30% : Choix clair
3. Si écart 10-30% : Lire recommandations
4. Si écart < 10% : Autres critères (coût, facilité)
```

### 3. Valider une Optimisation

```
AVANT:
1. Lancer tests
2. Export JSON (sauvegarder)

OPTIMISATION:
3. Appliquer changements

APRÈS:
4. Relancer tests
5. Comparer les statistiques
6. Vérifier si anomalies réduites
```

---

## ⚙️ Configuration Requise

### Dépendances Python

```bash
pip install numpy pandas plotly
```

### Dans session_state

```python
st.session_state['benchmark_results'] = {
    'virtuoso': {'times': [...], 'queries': [...]},
    'fuseki': {'times': [...], 'queries': [...]}
}
```

---

## 🐛 Dépannage

### "Aucun résultat disponible"

**Cause** : Tests pas encore lancés
**Solution** : Aller dans "Configuration & Tests" → Exécuter

### "Module analysis_tab non disponible"

**Cause** : Fichier manquant ou erreur import
**Solution** : Vérifier que `ui/tabs/analysis_tab.py` existe

### Graphiques ne s'affichent pas

**Cause** : Plotly non installé
**Solution** : `pip install plotly`

---

## 📖 Documentation Complète

Pour plus de détails : [ANALYSIS_MODULE_COMPLETE.md](ANALYSIS_MODULE_COMPLETE.md)

---

**Créé le** : 11 Novembre 2025
**Version** : 1.0

---

# 🎉 Analysez vos benchmarks comme un pro ! 🔬
