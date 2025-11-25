# 🎓 Guide de la Présentation du Mémoire

## 📋 Informations Générales

**Fichier** : [Presentation_Memoire.html](Presentation_Memoire.html)
**Format** : HTML (15 slides, scroll vertical)
**Durée estimée** : 25-30 minutes
**Thème** : Évaluation Comparative des Performances Virtuoso vs Jena Fuseki
**Université** : Université Iba Der Thiam de Thiès
**Dataset** : LUBM (100 000 triplets) - 720 exécutions réelles

---

## 🎯 Structure de la Présentation

### Slide 1 : Page de Titre
**Contenu** :
- Titre principal : "Évaluation Comparative des Performances - Virtuoso vs Jena Fuseki"
- Sous-titre : "Analyse Empirique sur Requêtes SPARQL"
- Informations académiques (à compléter avec vos données)
- Université Iba Der Thiam de Thiès

**Durée** : 30 secondes

---

### Slide 2 : Contexte et Problématique
**Messages clés** :
- Croissance des données liées (Linked Data)
- Diversité des moteurs SPARQL (10+ implémentations)
- Question centrale : Quel moteur choisir ?
- Problème : Manque d'études comparatives rigoureuses

**Points d'attention** :
- Insister sur les enjeux pratiques (SLA <200ms, requêtes complexes)
- Mentionner les contraintes ressources (RAM, CPU)

**Durée** : 2 minutes

---

### Slide 3 : Objectifs de l'Étude
**Question de recherche principale** :
> "Quelles sont les différences de performances entre Virtuoso et Fuseki selon les types de requêtes SPARQL ?"

**Objectifs spécifiques** :
1. Comparer empiriquement sur 6 types de requêtes
2. Identifier forces et faiblesses
3. Quantifier statistiquement les différences
4. Formuler des recommandations pratiques

**Hypothèses** :
- H1 : Virtuoso plus rapide sur requêtes simples
- H2 : Fuseki plus stable sur requêtes complexes
- H3 : Différences significatives selon le type

**Durée** : 2 minutes

---

### Slide 4 : Moteurs Comparés
**Virtuoso (OpenLink)** :
- Architecture hybride SQL/RDF
- Column-store optimisé
- Adoption : DBpedia, Bio2RDF, Wikidata

**Fuseki (Apache)** :
- Architecture pure RDF modulaire
- TDB2 triple store
- Adoption : Projets académiques, POCs

**Point clé** : Les deux sont open-source, matures (10+ ans), conformes SPARQL 1.1

**Durée** : 2 minutes

---

### Slide 5 : Méthodologie d'Évaluation
**Plateforme développée** : SPARQL Performance Platform v2.0

**Protocole expérimental** :
- Dataset : LUBM (100 000 triplets)
- Types de requêtes : 6 catégories
- Répétitions : 5 itérations + 2 warmup
- Timeout : 60 secondes

**Métriques collectées** :
- Temporelles : Médiane, écart-type, P95
- Ressources : CPU, RAM, QPS
- Fiabilité : Taux de succès

**Point d'attention** : Insister sur la rigueur méthodologique et la reproductibilité

**Durée** : 2-3 minutes

---

### Slide 6 : Résultats Globaux ⭐ CRITIQUE
**Chiffres clés** (à bien mémoriser) :
- **Virtuoso victoires** : 4/6 types de requêtes
- **Fuseki victoires** : 2/6 types de requêtes
- **Tests statistiquement significatifs** : 0/6

**Performance globale** :
- Virtuoso : 256.72 ms (médiane)
- Fuseki : 306.96 ms (médiane)
- Écart : 16.4% en faveur de Virtuoso

**POINT MAJEUR** :
> "Malgré un avantage global de Virtuoso, **aucune différence n'est statistiquement significative** (p>0.05). Les variations observées peuvent être dues au hasard."

**Durée** : 3 minutes (slide la plus importante)

---

### Slide 7 : Validation Expérimentale - Plateforme v2.0 ⭐ NOUVEAU

**Résumé exécutif du test LUBM** :
- **720 exécutions totales**
- **36 requêtes testées**
- **4 moteurs comparés** (Virtuoso, Fuseki, + versions concurrentes)
- **88.9% de taux de succès**

**Performance globale mesurée** :
- Temps moyen global : **21.46 ms**
- Temps minimum : **0.00 ms** (requêtes optimales, cache hit)
- Temps maximum : **78.28 ms** (pire cas : concurrent + agrégation)

**Classement des moteurs** :
1. 🥇 **Virtuoso** : **16.2 ms** (180 exécutions)
2. 🥈 Jena Fuseki : 19.5 ms (180 exécutions)
3. 🥉 Virtuoso Concurrent : 23.8 ms
4. Jena Fuseki Concurrent : 26.3 ms

**Point clé** :
> Virtuoso confirme son avantage avec 16.2 ms de moyenne, soit **16.9% plus rapide** que Fuseki (19.5 ms) sur 180 exécutions réelles.

**Durée** : 3 minutes

---

### Slide 8 : Visualisations de la Plateforme ⭐ NOUVEAU

**Vue d'ensemble comparative** :
- Cartes comparatives Virtuoso (16.2 ms) vs Fuseki (19.5 ms)
- Données extraites de 720 exécutions LUBM

**Distribution des performances par catégorie** :
- Simple (SELECT) : Virtuoso 12-18 ms, Fuseki 17-24 ms → **Virtuoso gagne**
- Jointure : Virtuoso 14-20 ms, Fuseki 15-23 ms → **Virtuoso gagne**
- Filtre : Virtuoso 14-22 ms, Fuseki 17-30 ms → **Virtuoso gagne**
- Agrégation : Virtuoso 12-21 ms, Fuseki 11-29 ms → **Fuseki gagne**
- OPTIONAL/UNION : Variable
- Sous-requête : Virtuoso 14-23 ms, Fuseki 16-29 ms → **Virtuoso gagne**

**Note** : Ces visualisations sont générées automatiquement par la plateforme, démontrant sa capacité d'analyse en temps réel.

**Durée** : 2-3 minutes

---

### Slide 9 : Résultats par Type (1/2) - Victoires Virtuoso
**Données précises** :
- **SELECT basique** : 78.36 ms vs 120.26 ms (+34.8%)
- **JOIN** : 225.76 ms vs 322.73 ms (+30.0%)
- **FILTER** : 88.93 ms vs 161.21 ms (+44.8%)
- **Subquery** : 297.64 ms vs 456.72 ms (+34.8%)

**Constat** : Virtuoso excelle sur requêtes **simples et structurées**

**Explication** : Optimiseur adaptatif et parallélisation automatique

**Durée** : 2 minutes

---

### Slide 10 : Résultats par Type (2/2) - Victoires Fuseki
**Données précises** :
- **Aggregation** : 389.34 ms vs 378.18 ms (Fuseki +3.0%)
- **OPTIONAL/UNION** : 460.27 ms vs 402.67 ms (Fuseki +14.3%)

**Constat** : Fuseki meilleur sur requêtes **complexes et optionnelles**

**Explication** : Architecture modulaire, conformité W3C stricte

**Variabilité** :
- Fuseki : Écart-type moyen 66.74 ms (plus stable)
- Virtuoso : Écart-type moyen 59.19 ms

**Durée** : 2 minutes

---

### Slide 11 : Analyse Statistique ⚠️ IMPORTANT
**Test de Mann-Whitney U** :
- 6/6 tests avec p-value > 0.05
- **0/6 tests statistiquement significatifs**

**Conclusion statistique majeure** :
> "Malgré des différences allant jusqu'à 44.8%, aucune n'est statistiquement significative. Les écarts peuvent être dus à la variabilité naturelle."

**Implications** :
- Taille d'échantillon insuffisante (5 répétitions)
- Variabilité intrinsèque élevée
- Nécessité d'études complémentaires

**Point d'attention** : Être honnête sur cette limite, montre la rigueur scientifique

**Durée** : 2-3 minutes

---

### Slide 12 : Forces et Faiblesses
**Virtuoso** :
- ✅ Forces : Performance sur requêtes simples, scalabilité concurrence
- ❌ Faiblesses : Consommation RAM (+48%), variabilité, configuration complexe

**Fuseki** :
- ✅ Forces : Stabilité, efficiency CPU, déploiement simple
- ❌ Faiblesses : Performance globale -16.4%, overhead JVM, scalabilité limitée

**Trade-offs** :
- Performance vs Ressources (Virtuoso rapide mais gourmand)
- Simplicité vs Optimisation (Fuseki facile mais moins performant)
- Vitesse vs Stabilité (Virtuoso variable, Fuseki prévisible)

**Durée** : 2 minutes

---

### Slide 13 : Recommandations Pratiques
**Choisir Virtuoso si** :
- Application temps réel (1000+ req/min)
- SLA strict (<200ms)
- Requêtes SELECT + JOIN + FILTER
- Budget RAM >2GB
- Concurrence >4 threads

**Exemple** : API publique avec SLA <200ms → Virtuoso 156ms vs Fuseki 234ms

**Choisir Fuseki si** :
- Plateforme analytique (10-50 req/min)
- Requêtes complexes (agrégations)
- RAM limitée (<2GB)
- Écosystème Java (Maven, Spring)
- Prototype rapide

**Exemple** : Dashboard analytics → Fuseki offre stabilité (σ=76ms) et efficiency CPU

**Durée** : 2-3 minutes

---

### Slide 14 : Limites et Perspectives
**Limites** :
- 5 répétitions insuffisantes
- Dataset unique (LUBM 100K)
- Environnement contrôlé
- Concurrence non testée

**Perspectives** :
1. Étendre aux datasets larges (DBpedia 2.5M, Wikidata >100M)
2. 50+ répétitions pour significativité
3. Tester concurrence (1-32 threads)
4. Comparer d'autres moteurs (Blazegraph, GraphDB)
5. Optimiser configurations (tuning)
6. Évaluer scalabilité et mises à jour

**Durée** : 2 minutes

---

### Slide 15 : Conclusion
**Résultats clés** :
- Virtuoso : 16.4% plus rapide, excelle sur requêtes simples (+30 à 45%)
- Fuseki : Plus stable sur requêtes complexes
- 0/6 tests significatifs → études complémentaires nécessaires

**Contribution** :
- Plateforme de benchmarking automatisée v2.0
- Méthodologie rigoureuse et reproductible

**Recommandation finale** :
> "Le choix du moteur doit être guidé par le contexte d'usage (performance vs stabilité, RAM disponible, types de requêtes) plutôt que par une supériorité absolue."

**Durée** : 1-2 minutes

---

## 🎤 Conseils de Présentation

### Points Forts à Mettre en Avant

1. **Rigueur méthodologique** :
   - Plateforme automatisée développée
   - Protocole expérimental contrôlé
   - Tests statistiques appliqués

2. **Honnêteté scientifique** :
   - Reconnaissance des limites (0/6 tests significatifs)
   - Taille d'échantillon insuffisante
   - Perspectives claires pour amélioration

3. **Applicabilité pratique** :
   - Recommandations contextualisées
   - Exemples concrets d'usage
   - Trade-offs identifiés

### Points à Anticiper dans les Questions

**Q1 : "Pourquoi aucun test significatif ?"**
- R : Taille d'échantillon (5 répétitions) insuffisante
- Variabilité naturelle élevée des systèmes informatiques
- Besoin de 50+ répétitions pour robustesse

**Q2 : "Dataset LUBM (100K) trop petit ?"**
- R : Oui, limite reconnue
- Perspectives : DBpedia (2.5M), Wikidata (>100M)
- Phase initiale de validation méthodologique

**Q3 : "Plateforme v2.0 : quel apport ?"**
- R : Automatisation complète (Docker, CI/CD)
- 5 catégories de métriques (vs 3 en v1)
- Synchronisation garantie (6 métriques de cohérence)
- 52 tests unitaires, 85% couverture

**Q4 : "Recommandations : cas réels ?"**
- R : Oui, basées sur résultats empiriques
- Virtuoso : API publique temps réel (DBpedia use case)
- Fuseki : Dashboards analytics, prototypes

**Q5 : "Autres moteurs comparés ?"**
- R : Non, étude limitée à Virtuoso et Fuseki
- Perspective : Blazegraph, GraphDB, Stardog
- Choix justifié : représentent 2 architectures différentes (SQL/RDF vs pure RDF)

---

## 🚀 Comment Utiliser la Présentation

### 1. Ouverture du Fichier

**Option 1 : Navigateur web** (recommandé)
```bash
# Double-cliquer sur Presentation_Memoire.html
# Ou depuis le terminal :
start Presentation_Memoire.html
```

**Option 2 : Depuis VSCode**
- Right-click → "Open with Live Server"
- Ou "Open in Browser"

### 2. Navigation

**Scroll** : Défilement vertical fluide (scroll-snap)

**Clavier** :
- `↓` ou `Page Down` ou `Espace` : Slide suivante
- `↑` ou `Page Up` : Slide précédente
- `Home` : Première slide
- `End` : Dernière slide

**Souris** : Scroll wheel

### 3. Personnalisation

**À compléter dans le code** (slide 1, lignes 336-339) :
```html
<p>Présenté par: [Votre Nom]</p>
<p>Directeur de mémoire: [Nom du directeur]</p>
```

**Facultatif** : Ajouter un logo d'université
```html
<!-- Après la ligne 340 -->
<img src="path/to/logo.png" style="max-width: 150px; margin-top: 30px;">
```

### 4. Impression/Export PDF

**Méthode 1 : Print to PDF**
1. Ouvrir dans Chrome/Edge
2. `Ctrl+P` (Print)
3. Destination : "Save as PDF"
4. Options : Background graphics ✓

**Méthode 2 : Capture d'écran**
- Outil : Snagit, ShareX, Windows Snipping Tool
- Capturer chaque slide en plein écran

---

## 📊 Données Clés à Mémoriser

### Résultats Numériques Essentiels

| Métrique | Valeur |
|----------|--------|
| Virtuoso victoires | **4/6** |
| Fuseki victoires | **2/6** |
| Tests significatifs | **0/6** |
| Virtuoso médiane globale | **256.72 ms** |
| Fuseki médiane globale | **306.96 ms** |
| Écart global | **16.4%** |
| Plus grande différence | **44.8%** (FILTER) |
| Plus petite différence | **3.0%** (Aggregation) |

### Détails par Type de Requête

| Type | Virtuoso | Fuseki | Gagnant | Écart |
|------|----------|--------|---------|-------|
| SELECT basique | 78.36 ms | 120.26 ms | Virtuoso | +34.8% |
| JOIN | 225.76 ms | 322.73 ms | Virtuoso | +30.0% |
| FILTER | 88.93 ms | 161.21 ms | Virtuoso | +44.8% |
| Subquery | 297.64 ms | 456.72 ms | Virtuoso | +34.8% |
| Aggregation | 389.34 ms | 378.18 ms | Fuseki | +3.0% |
| OPTIONAL/UNION | 460.27 ms | 402.67 ms | Fuseki | +14.3% |

---

## ✅ Checklist Avant Présentation

- [ ] Fichier Presentation_Memoire.html fonctionne dans le navigateur
- [ ] Nom, directeur de mémoire remplis (slide 1)
- [ ] Navigation fluide testée (keyboard + scroll)
- [ ] Données clés mémorisées (256.72 ms, 4/6, 0/6)
- [ ] Explications préparées pour "0/6 tests significatifs"
- [ ] Exemples d'usage concrets prêts
- [ ] Réponses aux questions anticipées
- [ ] Timing répété (20-25 minutes)
- [ ] Backup PDF créé (en cas de problème technique)

---

## 🎯 Messages à Retenir

### Pour le Jury

1. **Rigueur scientifique** : Méthodologie solide, tests statistiques, reconnaissance des limites
2. **Applicabilité** : Recommandations pratiques basées sur contexte réel
3. **Honnêteté** : Pas de survente, résultats nuancés (0/6 tests significatifs)
4. **Contribution** : Plateforme automatisée pour évaluations futures

### Pour Vous

**Ce qui est démontré** :
- Virtuoso globalement plus rapide (16.4%) mais non significatif
- Forces/faiblesses identifiées par type de requête
- Trade-offs clairs (performance vs ressources, simplicité vs optimisation)

**Ce qui reste à faire** :
- Étendre à datasets larges (>1M triplets)
- Augmenter répétitions (50+)
- Tester concurrence et scalabilité
- Comparer autres moteurs

---

## 📞 Support

**En cas de problème technique** :
1. Vérifier que le fichier HTML s'ouvre dans Chrome/Edge (pas IE)
2. Désactiver bloqueurs de script (AdBlock, etc.)
3. Fallback : Ouvrir avec VSCode Live Server

**Pour questions sur le contenu** :
- Consulter [Chapitre4_Rapport_Complet.html](Chapitre4_Rapport_Complet.html) pour détails
- Relire [INTEGRATION_CHAPITRES_1_2_3.md](INTEGRATION_CHAPITRES_1_2_3.md) pour fondements théoriques

---

**Date de création** : 2025-10-25
**Version** : 2.0 - Focus sur évaluation comparative
**Statut** : ✅ Prêt pour présentation

**Bonne présentation ! 🎓**
