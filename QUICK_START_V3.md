# 🚀 Guide de Démarrage Rapide - Version 3.0

Lancez rapidement la **SPARQL Performance Platform v3.0** avec son nouveau design professionnel !

---

## ⚡ Démarrage en 3 Étapes

### 1️⃣ Vérifier les Prérequis

```bash
# Python 3.8 ou supérieur
python --version

# Streamlit installé
pip list | grep streamlit
```

Si Streamlit n'est pas installé :
```bash
pip install streamlit
```

### 2️⃣ Lancer la Plateforme v3.0

**Windows** :
```bash
run_v3.bat
```

**Linux/Mac** :
```bash
streamlit run main_v3.py
```

### 3️⃣ Accéder à l'Application

Ouvrez votre navigateur à l'adresse :
```
http://localhost:8501
```

---

## 🎨 Aperçu du Nouveau Design

### En-Tête Moderne

```
┌────────────────────────────────────────────────────────────┐
│                                                             │
│  ⚡ SPARQL Performance Platform               ┌──────┐    │
│  Plateforme professionnelle de benchmarking  │ v3.0 │    │
│  Virtuoso vs Jena Fuseki • v3.0              │  Pro │    │
│                                                └──────┘    │
└────────────────────────────────────────────────────────────┘
```

**Améliorations** :
- ✅ Gradient bleu professionnel
- ✅ Typographie Display size (48px)
- ✅ Badge de version avec effet glassmorphism
- ✅ Ombre portée pour profondeur

### Barre d'Actions Rapides

```
┌────────────────┬────────────────┬────────────────┬────────────────┐
│ 🧭 Guide       │ 📊 Dashboard   │ 💾 Sauvegarder │ 🔄 Rafraîchir  │
│    utilisation │    temps réel  │    session     │                 │
└────────────────┴────────────────┴────────────────┴────────────────┘
```

**Fonctionnalités** :
- ✅ Guide d'onboarding accessible en 1 clic
- ✅ Dashboard temps réel (préparé)
- ✅ Sauvegarde rapide de session
- ✅ Rafraîchissement de l'application

### Onglets avec Design Amélioré

```
┌────────────────────────────────────────────────────────────────┐
│ 🚀 Configuration  📦 Datasets  🧪 Tests  📊 Résultats  ...   │
│═══════════════════════════════════════════════════════════════│
│                                                                 │
│  Contenu de l'onglet actif                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Améliorations** :
- ✅ Bordures arrondies et ombres
- ✅ États hover et actif clairement différenciés
- ✅ Icônes significatives
- ✅ Transition douce

---

## 🎨 Palette de Couleurs v3.0

### Couleurs Primaires

| Couleur | Hex | Aperçu |
|---------|-----|--------|
| PRIMARY | `#0066CC` | 🔵 Bleu professionnel |
| SUCCESS | `#10B981` | 🟢 Vert succès |
| WARNING | `#F59E0B` | 🟡 Orange warning |
| ERROR | `#EF4444` | 🔴 Rouge erreur |
| INFO | `#3B82F6` | 🔵 Bleu info |

### Couleurs Spécifiques

| Couleur | Hex | Aperçu |
|---------|-----|--------|
| VIRTUOSO | `#E11D48` | 🔴 Rouge Virtuoso |
| FUSEKI | `#0891B2` | 🔵 Cyan Fuseki |

---

## 📦 Nouveaux Composants

### 1. Carte (Card)

```python
from ui.design_system import create_card

create_card(
    title="Mon Titre",
    icon="🎨",
    content="Contenu de la carte..."
)
```

**Résultat visuel** :
```
┌─────────────────────────────────────┐
│ 🎨 Mon Titre                        │
│─────────────────────────────────────│
│ Contenu de la carte...               │
│                                      │
└─────────────────────────────────────┘
```

### 2. Carte de Métrique

```python
from ui.design_system import create_metric_card

create_metric_card(
    label="TEMPS MOYEN",
    value="145 ms",
    delta="+12%",
    delta_positive=False,
    icon="⏱️"
)
```

**Résultat visuel** :
```
┌─────────────────────────────────────┐
│ TEMPS MOYEN                     ⏱️  │
│                                      │
│ 145 ms                               │
│ +12% 🔴                               │
└─────────────────────────────────────┘
```

### 3. Alerte

```python
from ui.design_system import create_alert

create_alert(
    "Opération réussie !",
    alert_type="success"
)
```

**Résultat visuel** :
```
┃ ✅ Opération réussie !
┃
```

### 4. Badge de Statut

```python
from ui.design_system import create_status_badge

badge = create_status_badge("En cours", status="info")
```

**Résultat visuel** :
```
[ ℹ️ En cours ]
```

### 5. Séparateur

```python
from ui.design_system import create_divider

create_divider(text="OU")
```

**Résultat visuel** :
```
──────────────── OU ────────────────
```

---

## 🎯 Fonctionnalités Principales

### Onglet 1 : Configuration 🚀

**Ce que vous pouvez faire** :
- ✅ Configurer les endpoints Virtuoso et Fuseki
- ✅ Tester la connectivité
- ✅ Voir les statistiques de chaque triplestore
- ✅ Configurer les paramètres de test

### Onglet 2 : Gestion des Datasets 📦

**Ce que vous pouvez faire** :
- ✅ Charger des datasets (DBpedia, LUBM, Generic)
- ✅ Valider les datasets avant chargement
- ✅ Consulter les statistiques des datasets
- ✅ Synchroniser les datasets entre Virtuoso et Fuseki

### Onglet 3 : Tests de Performance 🧪

**Ce que vous pouvez faire** :
- ✅ Exécuter des benchmarks SPARQL
- ✅ Comparer les performances Virtuoso vs Fuseki
- ✅ Configurer les types de requêtes
- ✅ Voir les résultats en temps réel

### Onglet 4 : Résultats & Analyses 📊

**Ce que vous pouvez faire** :
- ✅ Consulter les résultats détaillés
- ✅ Analyser les performances par type de requête
- ✅ Comparer les temps d'exécution
- ✅ Identifier les requêtes les plus lentes

### Onglet 5 : Visualisations 📈

**Ce que vous pouvez faire** :
- ✅ Voir des graphiques interactifs
- ✅ Comparer visuellement Virtuoso vs Fuseki
- ✅ Analyser les tendances
- ✅ Exporter les graphiques

### Onglet 6 : Export & Rapports 📤

**Ce que vous pouvez faire** :
- ✅ Exporter les résultats en CSV, Excel, JSON
- ✅ Générer des rapports PDF
- ✅ Sauvegarder les configurations
- ✅ Partager les résultats

### Onglet 7 : Sessions 💾

**Ce que vous pouvez faire** :
- ✅ Sauvegarder votre configuration actuelle
- ✅ Charger une configuration précédente
- ✅ Comparer deux sessions (A vs B)
- ✅ Exporter/Importer des sessions

### Onglet 8 : Documentation 📖

**Ce que vous pouvez faire** :
- ✅ Lire la documentation complète
- ✅ Consulter les guides d'utilisation
- ✅ Voir les exemples de code
- ✅ Accéder au support

---

## 📚 Ressources

### Documentation

- **[DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)** : Documentation complète du design system
- **[DESIGN_V3_IMPROVEMENTS.md](DESIGN_V3_IMPROVEMENTS.md)** : Détails des améliorations v3.0
- **[CONFIG_MODULE_IMPROVEMENTS.md](CONFIG_MODULE_IMPROVEMENTS.md)** : Améliorations du module config
- **[SYNC_PROBLEM_SOLVED.md](SYNC_PROBLEM_SOLVED.md)** : Solution au problème de synchronisation

### Code Source

- **[ui/design_system.py](ui/design_system.py)** : Module du design system
- **[main_v3.py](main_v3.py)** : Application principale v3.0
- **[config/settings.py](config/settings.py)** : Configuration de la plateforme
- **[config/env_loader.py](config/env_loader.py)** : Chargement des variables d'environnement

### Scripts

- **[run_v3.bat](run_v3.bat)** : Script de lancement Windows
- **[check_config_consistency.py](check_config_consistency.py)** : Vérification de cohérence

---

## 🆘 Dépannage

### Problème : "Streamlit n'est pas installé"

**Solution** :
```bash
pip install streamlit
```

### Problème : "Module 'ui.design_system' not found"

**Solution** :
Assurez-vous d'être dans le bon répertoire :
```bash
cd c:\Users\hp\Documents\M2\Web Semantique\Mémoire\Code_NV\sparql_v2
python -c "import ui.design_system"
```

### Problème : "Port 8501 déjà utilisé"

**Solution** :
Spécifiez un autre port :
```bash
streamlit run main_v3.py --server.port 8502
```

### Problème : "Virtuoso/Fuseki non connecté"

**Solution** :
1. Vérifiez que Virtuoso est démarré sur le port 8890
2. Vérifiez que Fuseki est démarré sur le port 3030
3. Testez la connectivité dans l'onglet Configuration

---

## 🎓 Prochaines Étapes

Une fois la plateforme lancée :

1. **Configurez les endpoints** dans l'onglet Configuration
2. **Testez la connectivité** pour vérifier que les triplestores répondent
3. **Chargez un dataset** dans l'onglet Datasets
4. **Synchronisez les données** entre Virtuoso et Fuseki
5. **Exécutez vos premiers tests** dans l'onglet Tests de Performance
6. **Analysez les résultats** dans l'onglet Résultats & Analyses

---

## 💡 Conseils

- ✅ Utilisez le **Guide d'utilisation** (bouton 🧭) pour une visite guidée
- ✅ **Sauvegardez régulièrement** vos sessions pour ne pas perdre votre travail
- ✅ **Consultez la documentation** pour des exemples détaillés
- ✅ **Testez avec de petits datasets** (10K triplets) avant de passer à des datasets plus grands

---

## 🎉 Profitez de la v3.0 !

La **SPARQL Performance Platform v3.0** vous offre maintenant une expérience professionnelle et conviviale pour vos benchmarks SPARQL. Profitez-en ! 🚀

---

**Version** : 3.0.0
**Date** : 11 Novembre 2025
**Statut** : ✅ Production-Ready
**Support** : [Issues GitHub](https://github.com/thiernoDiedhiou/sparql_performance_platform/issues)
