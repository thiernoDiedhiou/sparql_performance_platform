# 🚀 Quick Start Guide - SPARQL Performance Platform v3.1

**Version**: 3.1 - Interface Ultra-Professionnelle
**Date**: 11 Novembre 2025
**Durée**: 5 minutes pour être opérationnel

---

## 📋 Pré-requis

- ✅ Python 3.8+ installé
- ✅ Virtuoso en cours d'exécution (port 8890)
- ✅ Jena Fuseki en cours d'exécution (port 3030)

---

## 🎯 Lancement Rapide

### Méthode 1 : Script Windows (Recommandée)

```bash
run_v3.1.bat
```

Le script va :
1. Vérifier que Python est installé
2. Installer Streamlit si nécessaire
3. Installer psutil si nécessaire (pour le monitoring)
4. Lancer l'application v3.1

### Méthode 2 : Ligne de Commande

```bash
# Activer l'environnement virtuel (si utilisé)
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Lancer l'application
streamlit run main_v3_refactored.py
```

---

## 🎨 Découverte de l'Interface v3.1

### 1. **Sidebar (Colonne de Gauche)**

La sidebar contient tout ce dont vous avez besoin en permanence :

```
┌─────────────────────┐
│  ⚡ SPARQL Performance │
│  v3.1 Professional   │
├─────────────────────┤
│  ⚡ Actions Rapides   │
│  [🧭 Guide] [🔄]     │
│  [📊 État Système]   │
├─────────────────────┤
│  💻 Monitoring       │
│  CPU:  45.2%  🟢    │
│  RAM:  62.8%  🟡    │
├─────────────────────┤
│  🔧 Configuration    │
│  Endpoints SPARQL... │
└─────────────────────┘
```

**Actions Rapides** :
- **🧭 Guide** : Affiche le guide de démarrage en overlay
- **🔄 Rafraîchir** : Recharge l'application
- **📊 État Système** : Ouvre le dashboard système complet

**Monitoring Compact** :
- Métriques CPU et RAM en temps réel
- Couleurs adaptatives :
  - 🟢 Vert : < 60% (bon)
  - 🟡 Orange : 60-85% (moyen)
  - 🔴 Rouge : > 85% (critique)

---

### 2. **5 Onglets Principaux**

Navigation ultra-simple avec 5 onglets bien organisés :

#### 🚀 **Configuration & Tests**
- Vérifier la connectivité des endpoints
- Sélectionner les requêtes à tester
- Configurer les paramètres (itérations, warmup)
- Lancer les benchmarks

#### 📦 **Datasets**
- Charger un dataset (DBpedia, LUBM, Generic)
- Valider le nombre de triplets
- Synchroniser entre Virtuoso et Fuseki
- Vérifier la cohérence

#### 📊 **Résultats & Analyses**
3 sous-onglets pour organiser :
- **📈 Résultats Bruts** : Tableaux de performances
- **📊 Visualisations** : Graphiques comparatifs
- **🔬 Analyses Détaillées** : Insights et recommandations

#### 📤 **Export & Sessions**
2 colonnes :
- **Gauche** : Export CSV, Excel, JSON
- **Droite** : Sauvegarde/Chargement de sessions

#### 📖 **Documentation**
- Guides utilisateur
- Documentation technique
- FAQ et dépannage

---

## 🎯 Workflow Recommandé

### Étape 1 : Cliquer sur "🧭 Guide" (Sidebar)

→ Affiche un overlay avec 4 cartes expliquant chaque étape

### Étape 2 : Onglet "🚀 Configuration & Tests"

1. Vérifier la connectivité :
   - Cliquer sur "Tester la connectivité"
   - Vérifier que Virtuoso et Fuseki sont en ligne

2. (Optionnel) Configurer les paramètres dans la sidebar :
   - Endpoints SPARQL
   - Itérations, warmup, etc.

### Étape 3 : Onglet "📦 Datasets"

1. Sélectionner un dataset (ex: LUBM 10K)
2. Cliquer sur "Charger le dataset"
3. Attendre la synchronisation
4. Vérifier les triplets chargés

### Étape 4 : Retour à "🚀 Configuration & Tests"

1. Sélectionner les requêtes à tester
2. Cliquer sur "Exécuter les tests"
3. Surveiller la progression

### Étape 5 : Onglet "📊 Résultats & Analyses"

1. Consulter les résultats bruts
2. Explorer les visualisations
3. Analyser les performances

### Étape 6 : Onglet "📤 Export & Sessions"

1. **Sauvegarder** : Cliquer sur "💾 Sauvegarder la session actuelle"
2. **Exporter** : Télécharger en CSV/Excel/JSON

---

## 💡 Astuces & Bonnes Pratiques

### 1. **Utiliser le Monitoring Permanent**

La sidebar affiche en permanence CPU et RAM :
- Si rouge (> 85%) : Fermez des applications
- Si orange (60-85%) : Surveillez
- Si vert (< 60%) : Tout va bien

### 2. **Sauvegarder Régulièrement**

Avant de lancer des tests longs :
1. Aller dans "📤 Export & Sessions"
2. Cliquer sur "💾 Sauvegarder la session actuelle"
3. Télécharger le fichier JSON

### 3. **Utiliser les Overlays**

Les overlays sont plus immersifs que les popups :
- **Guide** : Pour se rappeler le workflow
- **Dashboard Système** : Pour analyser les performances

### 4. **Navigation par Sous-Onglets**

L'onglet "📊 Résultats" utilise des sous-onglets :
- Facilite l'organisation
- Pas de surcharge visuelle

### 5. **Rafraîchir en Cas de Problème**

Si l'interface ne répond plus :
- Cliquer sur "🔄 Rafraîchir" (sidebar)
- Ou appuyer sur F5

---

## 🐛 Dépannage

### Problème : "Module sidebar non disponible"

**Solution** : Module optionnel manquant
- L'interface de remplacement s'affiche automatiquement
- Fonctionnalités principales préservées

### Problème : "Module psutil non disponible"

**Solution** : Installer psutil
```bash
pip install psutil
```

Ou utiliser le script `run_v3.1.bat` qui l'installe automatiquement.

### Problème : "Monitoring non disponible"

**Cause** : psutil non installé
**Impact** : Monitoring désactivé (fonctionnalité optionnelle)
**Solution** : Voir ci-dessus

### Problème : Endpoints inaccessibles

1. Vérifier que Virtuoso est en cours d'exécution :
   ```bash
   # Test manuel
   curl http://localhost:8890/sparql
   ```

2. Vérifier que Fuseki est en cours d'exécution :
   ```bash
   # Test manuel
   curl http://localhost:3030/dataset/query
   ```

3. Si nécessaire, redémarrer les services

---

## 📊 Nouveautés v3.1 vs v3.0

| Fonctionnalité | v3.0 | v3.1 |
|----------------|------|------|
| **Nombre d'onglets** | 8 | 5 (**-37.5%**) |
| **Actions rapides** | En-tête | Sidebar (**Toujours visible**) |
| **Monitoring** | Sur demande | **Permanent** |
| **Guide** | Popup st.info() | **Overlay immersif** |
| **Dashboard système** | Modal basique | **Dashboard complet** |
| **Redondances** | 1 (Sessions) | 0 (**Éliminées**) |
| **Hauteur en-tête** | ~150px | ~100px (**-33%**) |

---

## ✅ Checklist de Premier Lancement

- [ ] Lancer `run_v3.1.bat`
- [ ] Attendre que Streamlit s'ouvre dans le navigateur
- [ ] Vérifier que la sidebar s'affiche à gauche
- [ ] Cliquer sur "🧭 Guide" pour voir l'overlay
- [ ] Vérifier le monitoring CPU/RAM dans la sidebar
- [ ] Explorer les 5 onglets principaux
- [ ] Tester la sauvegarde de session
- [ ] Marquer comme favoris dans le navigateur

---

## 🎓 Ressources Complémentaires

### Documentation

1. **[REFACTORING_V3.1_COMPLETE.md](REFACTORING_V3.1_COMPLETE.md)**
   - Détails complets de la refactorisation
   - Comparaison avant/après
   - Architecture visuelle

2. **[DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)**
   - Guide complet du design system
   - Couleurs, typographie, espacements
   - Composants réutilisables

3. **[REDESIGN_V3_FINAL_SUMMARY.md](REDESIGN_V3_FINAL_SUMMARY.md)**
   - Historique du redesign v3.0
   - Métriques d'amélioration

### Fichiers Principaux

- **main_v3_refactored.py** : Application v3.1
- **ui/design_system.py** : Design system complet
- **run_v3.1.bat** : Script de lancement Windows

---

## 📞 Support

**Issues** : https://github.com/thiernoDiedhiou/sparql_performance_platform/issues

**Questions** : Consulter la documentation dans l'onglet "📖 Documentation"

---

**Dernière mise à jour** : 11 Novembre 2025
**Version** : 3.1.0
**Statut** : ✅ Production Ready

---

# 🎉 Bon benchmark avec la v3.1 ! 🚀
