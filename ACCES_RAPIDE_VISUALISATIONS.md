# ⚡ Accès Rapide aux Visualisations - Guide Visuel

## 🎯 En 3 Étapes Simples

---

## 📍 ÉTAPE 1 : Démarrer la Plateforme

### Dans le Terminal

```bash
# Naviguer vers le dossier du projet
cd c:\Users\hp\Documents\M2\Web Semantique\Mémoire\Code_NV\Extract\nv\sparql_v2

# Lancer Streamlit
streamlit run main.py
```

**Résultat :** Une fenêtre de navigateur s'ouvre automatiquement à `http://localhost:8501`

---

## 📊 ÉTAPE 2 : Naviguer vers les Résultats

### Interface Principale

Vous verrez la **barre de navigation** en haut de la page :

```
┌─────────────────────────────────────────────────────────────────┐
│  🏠 Accueil  |  ⚙️ Configuration & Tests  |  📊 Datasets  │
│  📈 Résultats & Analyses  |  💾 Export & Sessions  |  📖 Doc  │
└─────────────────────────────────────────────────────────────────┘
```

### ⭐ Cliquez sur "📈 Résultats & Analyses"

---

## 🎨 ÉTAPE 3 : Explorer les Visualisations

### Menu de Sélection des Visualisations

Une fois dans l'onglet "Résultats & Analyses", vous verrez un **menu radio** avec 10 types de visualisations :

```
📊 Type de visualisation :
  ⚪ Temps d'exécution
  ⚪ Utilisation ressources
  ⚪ Comparaison directe
  ⚪ Tendances de performance
  🔘 Distribution (Box Plot)          ← Sélectionné
  ⚪ Distribution (Violin Plot)
  ⚪ Analyse percentiles (CDF)
  ⚪ Contribution requêtes (Waterfall)
  ⚪ Heatmap des performances
  ⚪ Tableau de bord complet
```

### Sélectionnez un Type de Visualisation

**Exemple : Distribution (Box Plot)**

→ Le graphique s'affiche immédiatement en dessous

---

## 🖼️ Types de Visualisations Disponibles

### 1. 📊 Temps d'Exécution

**Ce que vous voyez :**
- Graphique en barres comparant Virtuoso et Fuseki
- Temps moyen par type de requête
- Temps par requête individuelle

**Utilisation :**
- Identifier rapidement quel moteur est plus rapide
- Comparer par type de requête (SELECT, JOIN, FILTER, etc.)

**Pour le Chapitre 4 :**
- Figure 4.4 : "Temps d'exécution par requête et moteur"

---

### 2. 📦 Distribution (Box Plot)

**Ce que vous voyez :**
- Boîtes à moustaches pour chaque moteur
- Médiane (ligne centrale)
- Quartiles Q1 et Q3 (boîte)
- Min et Max (moustaches)
- Outliers (points isolés)

**Utilisation :**
- Analyser la dispersion des temps d'exécution
- Détecter les valeurs aberrantes
- Comparer la stabilité des moteurs

**Pour le Chapitre 4 :**
- Figure 4.5 : "Box Plot - Distribution des temps d'exécution"

---

### 3. 🎻 Distribution (Violin Plot)

**Ce que vous voyez :**
- Forme de "violon" montrant la densité de probabilité
- Plus large = plus de valeurs à ce niveau
- Box plot intégré au centre

**Utilisation :**
- Visualiser la distribution complète des performances
- Identifier les modes (pics de fréquence)
- Comparer les formes de distribution

**Pour le Chapitre 4 :**
- Figure 4.6 : "Violin Plot - Densité de probabilité"

---

### 4. 📈 Analyse Percentiles (CDF)

**Ce que vous voyez :**
- Courbe cumulative montant de 0% à 100%
- Axe X : Temps d'exécution (ms)
- Axe Y : Pourcentage de requêtes terminées

**Utilisation :**
- Répondre à "Quel % de requêtes se termine en <X ms ?"
- Définir des SLA (Service Level Agreements)
- Calculer P95, P99

**Pour le Chapitre 4 :**
- Figure 4.9 : "CDF (Percentiles) - Analyse de percentiles"

---

### 5. 💧 Contribution Requêtes (Waterfall)

**Ce que vous voyez :**
- Diagramme en cascade
- Contribution de chaque type au temps total
- Barres empilées ou séquentielles

**Utilisation :**
- Identifier les types de requêtes les plus coûteux
- Prioriser les optimisations
- Analyser la répartition du temps

**Pour le Chapitre 4 :**
- Figure 4.10 : "Waterfall - Contribution au temps total"

---

### 6. 🔥 Heatmap des Performances

**Ce que vous voyez :**
- Matrice colorée (Moteur × Type de requête)
- Rouge = Lent, Vert = Rapide
- Échelle de couleur graduée

**Utilisation :**
- Vue d'ensemble rapide des performances
- Identifier visuellement les points faibles
- Comparer les patterns entre moteurs

---

### 7. 📊 Comparaison Directe

**Ce que vous voyez :**
- Graphique scatter plot (nuage de points)
- Axe X : Temps Virtuoso
- Axe Y : Temps Fuseki
- Ligne de référence (performances égales)

**Utilisation :**
- Comparer requête par requête
- Identifier les requêtes où un moteur excelle
- Détecter les écarts importants

**Pour le Chapitre 4 :**
- Figure 4.3 : "Scatter plot - Comparaison directe"

---

### 8. 💻 Utilisation Ressources

**Ce que vous voyez :**
- Graphiques CPU et RAM au fil du temps
- Courbes d'évolution
- Pics et moyennes

**Utilisation :**
- Analyser la consommation des ressources
- Détecter les goulots d'étranglement
- Comparer l'efficience des moteurs

**Pour le Chapitre 4 :**
- Figure 6.1 : "Utilisation mémoire"
- Figure 6.2 : "Utilisation CPU"
- Figure 6.3 : "Mémoire & CPU consolidé"

---

### 9. 📉 Tendances de Performance

**Ce que vous voyez :**
- Évolution des temps au fil des itérations
- Courbes pour chaque moteur
- Effet de warmup visible

**Utilisation :**
- Observer l'amélioration avec le warmup
- Détecter les régressions
- Analyser la stabilité dans le temps

---

### 10. 🎛️ Tableau de Bord Complet

**Ce que vous voyez :**
- Vue multi-panneaux
- Métriques clés (cartes)
- Graphiques principaux (barres, box plots)
- Statistiques détaillées (tableaux)

**Utilisation :**
- Vue d'ensemble exhaustive
- Présentation complète des résultats
- Export pour rapport

---

## 📸 Comment Exporter les Graphiques

### Méthode 1 : Bouton d'Export Plotly ⭐ RECOMMANDÉ

**Pour chaque graphique :**

1. **Survoler le graphique** → Barre d'outils apparaît en haut à droite
2. **Icônes disponibles :**
   ```
   📷 Télécharger en PNG
   🔍 Zoom
   ➕ Zoom avant
   ➖ Zoom arrière
   📐 Pan (déplacer)
   🏠 Réinitialiser
   ```
3. **Cliquer sur 📷** (icône caméra)
4. **Format automatique :** PNG haute résolution (1200×800px)
5. **Téléchargement :** Fichier enregistré dans votre dossier "Téléchargements"

### Méthode 2 : Capture d'Écran

**Windows :**
```
1. Appuyer sur : Win + Shift + S
2. Sélectionner la zone du graphique
3. Image copiée dans le presse-papiers
4. Coller dans Word, PowerPoint, ou Paint
```

**Ou utiliser l'Outil Capture d'écran :**
- Rechercher "Outil Capture d'écran" dans le menu Démarrer
- Mode "Capture rectangulaire"
- Sélectionner le graphique
- Enregistrer en PNG

---

## 📂 Où Trouver les Images Téléchargées

### Emplacement par Défaut

**Windows :**
```
C:\Users\hp\Downloads\
```

**Nom des fichiers :**
- `newplot.png` (nom par défaut Plotly)
- Renommer immédiatement pour identifier :
  - `box_plot_virtuoso_fuseki.png`
  - `cdf_percentiles.png`
  - `waterfall_contribution.png`
  - etc.

### Organiser les Images

**Créer un dossier dédié :**
```bash
# Dans le projet
mkdir images\captures_nouvelles

# Déplacer les images téléchargées
move C:\Users\hp\Downloads\newplot.png images\captures_nouvelles\box_plot.png
```

---

## 🎯 Workflow Recommandé pour le Mémoire

### Étape 1 : Lancer la Plateforme
```bash
streamlit run main.py
```

### Étape 2 : Parcourir les 10 Types de Visualisations
Pour chaque type :
1. Sélectionner dans le menu radio
2. Observer le graphique
3. Cliquer sur 📷 pour exporter
4. Renommer immédiatement le fichier téléchargé

### Étape 3 : Organiser les Images
```
images/
├── images_mémoire/              # Images existantes (18 déjà là)
└── captures_nouvelles/          # Nouvelles captures
    ├── box_plot_nouveau.png
    ├── cdf_nouveau.png
    └── waterfall_nouveau.png
```

### Étape 4 : Référencer dans le Chapitre 4
Le fichier `CHAPITRE 4 - COMPLET.md` contient déjà les références aux 18 images existantes. Vous pouvez en ajouter d'autres si nécessaire.

---

## 🔍 Vérifier les Visualisations Disponibles

### Images Déjà Capturées (18)

**Pour vérifier :**
```bash
# Lister les images
dir images\images_mémoire

# Ou ouvrir le dossier
explorer images\images_mémoire
```

**Liste complète :**
1. Page d'accueil 1.png
2. Page d'accueil 2.png
3. Comparaison des temps d'exécution Virtuoso vs Jena Fuseki.png
4. Temps d'exécution par requête et moteur.png
5. Box Plot.png
6. Violin Plot.png
7. Analyse de Distribution_BoxPlot_ViolinPlot.png
8. CDF (Percentiles).png
9. Waterfall (Contribution).png
10. Analyse Avancée_CDF_Waterfall.png
11. Comparaison des métriques Clés.png
12. Métriques Statistiques Complètes.png
13. Distribution des temps de Réponse.png
14. Distribution Détaillée (Violin Plot).png
15. Analyses Détaillées.png
16. Utilisation CPU.png
17. Utilisation mémoire.png
18. Mémoire & CPU.png

**✅ Toutes ces images sont déjà référencées dans le Chapitre 4 !**

---

## 💡 Astuces Pro

### 1. Maximiser la Qualité des Graphiques

**Avant de capturer :**
- ✅ Mettre la fenêtre du navigateur en **plein écran** (F11)
- ✅ Zoomer si nécessaire (Ctrl + molette)
- ✅ Utiliser le **thème clair** (meilleur contraste pour impression)

### 2. Capturer Plusieurs Variations

Pour une même visualisation, capturez :
- Vue d'ensemble (tous les moteurs)
- Zoom sur une zone spécifique
- Avec et sans légende

### 3. Annoter les Graphiques

**Après export, utilisez un éditeur d'image pour :**
- Ajouter des flèches pointant vers des éléments clés
- Surligner les différences importantes
- Ajouter des légendes explicatives

**Outils recommandés :**
- **Paint** (Windows, gratuit)
- **Paint.NET** (gratuit, plus avancé)
- **Photopea** (en ligne, gratuit, type Photoshop)

---

## 🆘 Problèmes Courants

### "Aucun résultat disponible"

**Cause :** Pas de test exécuté récemment

**Solution :**
1. Aller dans "⚙️ Configuration & Tests"
2. Configurer les endpoints (Virtuoso, Fuseki)
3. Sélectionner les requêtes à tester
4. Cliquer "🚀 Lancer le Benchmark"
5. Attendre la fin (barre de progression)
6. Revenir dans "📈 Résultats & Analyses"

### Le graphique ne s'affiche pas

**Cause :** Données insuffisantes ou erreur

**Solution :**
1. Vérifier le message d'erreur en bas de page
2. Rafraîchir la page (F5)
3. Relancer le test si nécessaire

### Le bouton 📷 ne fonctionne pas

**Cause :** Bloqueur de pop-ups ou téléchargements

**Solution :**
1. Autoriser les téléchargements pour `localhost:8501`
2. Vérifier les paramètres du navigateur
3. Utiliser la capture d'écran (Win + Shift + S) en fallback

---

## 📞 Besoin d'Aide ?

### Guides Complets

- **Guide détaillé** : `GUIDE_ACCES_RESULTATS.md` (ce guide)
- **Guide finalisation** : `GUIDE_FINALISATION_MEMOIRE.md`
- **Index complet** : `MEMOIRE_COMPLET_INDEX.md`

### Documentation Technique

- **Streamlit** : https://docs.streamlit.io/
- **Plotly** : https://plotly.com/python/

---

## ✅ Checklist Rapide

- [ ] Plateforme lancée (`streamlit run main.py`)
- [ ] Onglet "Résultats & Analyses" ouvert
- [ ] 10 types de visualisations explorées
- [ ] Graphiques exportés en PNG
- [ ] Fichiers renommés et organisés
- [ ] Images prêtes pour le mémoire

---

## 🎉 C'est Tout !

**En résumé :**

1. ✅ `streamlit run main.py`
2. ✅ Cliquer sur "📈 Résultats & Analyses"
3. ✅ Sélectionner un type de visualisation
4. ✅ Cliquer sur 📷 pour exporter
5. ✅ Renommer et organiser

**Les 18 images du Chapitre 4 sont déjà disponibles dans `images/images_mémoire/` !** 🎨✨

---

**Généré le :** 24 novembre 2025
**Version :** 1.0
**Statut :** Guide Visuel Simplifié
