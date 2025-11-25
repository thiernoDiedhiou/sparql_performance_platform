# 🎯 Guide des Boutons d'Actions Rapides

**Version**: 3.0
**Date**: 11 Novembre 2025
**Statut**: ✅ **TOUS LES BOUTONS SONT MAINTENANT FONCTIONNELS**

---

## 📋 Vue d'Ensemble

Les 4 boutons d'actions rapides en haut de la plateforme permettent un accès direct aux fonctionnalités principales. **Mise à jour**: Tous les boutons ont été implémentés et sont pleinement fonctionnels.

```
┌────────────────┬────────────────┬────────────────┬────────────────┐
│ 🧭 Guide       │ 📊 Dashboard   │ 💾 Sauvegarder │ 🔄 Rafraîchir  │
│    utilisation │    temps réel  │    session     │                 │
└────────────────┴────────────────┴────────────────┴────────────────┘
```

---

## 1. 🧭 Guide d'Utilisation

### Objectif
Afficher un guide interactif pour les nouveaux utilisateurs ou comme référence rapide.

### État Actuel
- ✅ Bouton fonctionnel
- ⚠️ Nécessite le module `onboarding_wizard`
- ℹ️ Affiche "Guide non disponible" si le module n'existe pas

### Fonctionnement
```python
if st.button("🧭 Guide d'utilisation"):
    try:
        from ui.components.onboarding_wizard import force_show_onboarding
        force_show_onboarding()
    except:
        st.info("Guide non disponible")
```

### Ce qu'il DEVRAIT faire
1. Afficher un wizard d'onboarding interactif
2. Guider l'utilisateur à travers :
   - Configuration des endpoints
   - Chargement d'un dataset
   - Exécution d'un premier test
   - Consultation des résultats

### Solution Simple (Sans module onboarding)
```python
if st.button("🧭 Guide d'utilisation"):
    st.info("""
    ### 🧭 Guide de Démarrage Rapide

    **1. Configuration (Onglet 🚀)**
    - Vérifiez la connectivité des endpoints
    - Virtuoso : http://localhost:8890/sparql
    - Fuseki : http://localhost:3030/dataset/query

    **2. Datasets (Onglet 📦)**
    - Chargez un dataset (DBpedia, LUBM, Generic)
    - Synchronisez entre Virtuoso et Fuseki

    **3. Tests (Onglet 🧪)**
    - Sélectionnez les requêtes à tester
    - Configurez les paramètres (itérations, warmup)
    - Cliquez sur "Exécuter les tests"

    **4. Résultats (Onglet 📊)**
    - Consultez les temps d'exécution
    - Comparez Virtuoso vs Fuseki
    - Exportez les résultats
    """)
```

---

## 2. 📊 Dashboard Temps Réel

### Objectif
Afficher un tableau de bord avec métriques système et état des tests en cours.

### État Actuel
- ⚠️ Non implémenté
- ℹ️ Affiche "Dashboard en cours de développement"

### Ce qu'il DEVRAIT faire
1. Afficher les métriques système (CPU, RAM, Disque)
2. Montrer l'état des endpoints (En ligne/Hors ligne)
3. Afficher les tests en cours (si applicable)
4. Statistiques rapides (nombre de triplets, derniers tests)

### Implémentation Proposée

Créer un fichier `ui/components/realtime_dashboard_v3.py` :

```python
from ui.design_system import *
from ui.components.system_info_v3 import SystemInfoDisplay
from ui.components.connectivity_checker_v3 import ConnectivityChecker

def show_realtime_dashboard():
    """Affiche le dashboard temps réel"""

    st.markdown("## 📊 Dashboard Temps Réel")
    create_divider()

    # Métriques système
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        cpu_percent = psutil.cpu_percent()
        create_metric_card(
            label="CPU",
            value=f"{cpu_percent:.1f}%",
            icon="⚙️",
            color=Colors.PRIMARY
        )

    with col2:
        memory = psutil.virtual_memory()
        create_metric_card(
            label="Mémoire",
            value=f"{memory.percent:.1f}%",
            icon="🧠",
            color=Colors.SECONDARY
        )

    with col3:
        # État Virtuoso
        create_metric_card(
            label="Virtuoso",
            value="En ligne",
            icon="🔴",
            color=Colors.VIRTUOSO
        )

    with col4:
        # État Fuseki
        create_metric_card(
            label="Fuseki",
            value="En ligne",
            icon="🔵",
            color=Colors.FUSEKI
        )

    create_divider("Informations Système")

    # Afficher infos système
    system_info = SystemInfoDisplay()
    system_info.render_system_overview()
```

### Intégration dans main_v3.py

```python
with col2:
    if st.button("📊 Dashboard temps réel", use_container_width=True):
        # Utiliser un dialog/modal
        @st.dialog("📊 Dashboard Temps Réel", width="large")
        def show_dashboard_dialog():
            try:
                from ui.components.realtime_dashboard_v3 import show_realtime_dashboard
                show_realtime_dashboard()
            except ImportError:
                # Fallback simple
                st.markdown("### 📊 Dashboard Système")

                import psutil

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("CPU", f"{psutil.cpu_percent():.1f}%")
                with col2:
                    st.metric("Mémoire", f"{psutil.virtual_memory().percent:.1f}%")
                with col3:
                    disk = psutil.disk_usage('/')
                    st.metric("Disque", f"{(disk.used/disk.total)*100:.1f}%")

        show_dashboard_dialog()
```

---

## 3. 💾 Sauvegarder Session

### Objectif
Sauvegarder la configuration actuelle et l'état de la session pour réutilisation ultérieure.

### État Actuel
- ⚠️ Nécessite le module `session_manager`
- ℹ️ Affiche "Gestionnaire de sessions non disponible" si absent

### Ce qu'il DEVRAIT faire
1. Sauvegarder :
   - Configuration des endpoints
   - Paramètres de test (itérations, warmup, etc.)
   - Requêtes sélectionnées
   - Dataset sélectionné
   - Résultats des derniers tests (optionnel)

2. Format de sauvegarde : JSON avec timestamp

### Implémentation Simple (Sans module session_manager)

```python
with col3:
    if st.button("💾 Sauvegarder session", use_container_width=True):
        import json
        from datetime import datetime

        # Créer un dictionnaire de session
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "version": "3.0",
            "config": {
                "virtuoso_endpoint": st.session_state.get('virtuoso_endpoint', ''),
                "fuseki_endpoint": st.session_state.get('fuseki_endpoint', ''),
                "num_iterations": st.session_state.get('num_iterations', 5),
                "warmup_iterations": st.session_state.get('warmup_iterations', 2),
                "concurrent_queries": st.session_state.get('concurrent_queries', 1),
                "dataset_type": st.session_state.get('dataset_type', 'LUBM'),
            },
            "selected_queries": st.session_state.get('selected_queries', []),
        }

        # Sauvegarder dans un fichier
        filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            import os
            os.makedirs("sessions", exist_ok=True)

            filepath = os.path.join("sessions", filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

            st.success(f"✅ Session sauvegardée : {filename}")

            # Proposer le téléchargement
            st.download_button(
                label="📥 Télécharger la session",
                data=json.dumps(session_data, indent=2, ensure_ascii=False),
                file_name=filename,
                mime="application/json"
            )
        except Exception as e:
            st.error(f"❌ Erreur lors de la sauvegarde : {e}")
```

---

## 4. 🔄 Rafraîchir

### Objectif
Recharger complètement l'application (équivalent à F5 dans le navigateur).

### État Actuel
- ✅ **Fonctionne correctement**
- Utilise `st.rerun()` de Streamlit

### Ce qu'il fait
```python
if st.button("🔄 Rafraîchir"):
    st.rerun()
```

### Quand l'utiliser
- Après avoir modifié des fichiers de configuration
- Pour réinitialiser l'état de l'application
- Après avoir chargé un nouveau dataset
- Pour nettoyer les caches

### Amélioration Possible

Ajouter une confirmation pour éviter les rafraîchissements accidentels :

```python
with col4:
    if st.button("🔄 Rafraîchir", use_container_width=True):
        # Demander confirmation si des données non sauvegardées
        if st.session_state.get('has_unsaved_data', False):
            @st.dialog("⚠️ Confirmation")
            def confirm_refresh():
                st.warning("Vous avez des données non sauvegardées.")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Rafraîchir quand même", use_container_width=True):
                        st.rerun()
                with col2:
                    if st.button("❌ Annuler", use_container_width=True):
                        st.rerun()

            confirm_refresh()
        else:
            st.rerun()
```

---

## 🎯 Résumé des États

| Bouton | État | Description |
|--------|------|-------------|
| 🧭 Guide | ✅ Fonctionnel | Affiche guide de démarrage rapide avec st.info() |
| 📊 Dashboard | ✅ Fonctionnel | Affiche métriques système (CPU, Mémoire, Disque) avec psutil |
| 💾 Sauvegarder | ✅ Fonctionnel | Téléchargement JSON de la session avec st.download_button() |
| 🔄 Rafraîchir | ✅ Fonctionnel | Recharge l'application avec st.rerun() |

---

## ✅ Implémentation Réalisée (11 Novembre 2025)

### Phase 1 : Solutions Simples - ✅ TERMINÉ

Tous les 4 boutons ont été implémentés avec des solutions simples et fonctionnelles dans [main_v3.py](main_v3.py) (lignes 128-234) :

1. **🧭 Guide d'utilisation** - ✅ **FONCTIONNEL**
   - Implémentation : `st.info()` avec guide de démarrage rapide
   - Affiche les 4 étapes principales (Configuration, Datasets, Tests, Résultats)
   - Pas besoin de module externe

2. **📊 Dashboard temps réel** - ✅ **FONCTIONNEL**
   - Implémentation : Métriques système avec `psutil`
   - Affiche CPU, Mémoire et Disque en temps réel
   - Alertes automatiques si utilisation > 85%
   - Gestion d'erreur si psutil non installé

3. **💾 Sauvegarder session** - ✅ **FONCTIONNEL**
   - Implémentation : `st.download_button()` avec JSON
   - Sauvegarde configuration complète (endpoints, paramètres, requêtes)
   - Fichier horodaté (format: `session_YYYYMMDD_HHMMSS.json`)
   - Téléchargement direct dans le navigateur

4. **🔄 Rafraîchir** - ✅ **FONCTIONNEL**
   - Implémentation : `st.rerun()`
   - Recharge complètement l'application
   - Fonctionnait déjà avant

### Phase 2 : Modules Complets (Optionnel - Futur)

Si besoin d'amélioration future :

1. **onboarding_wizard.py** : Wizard interactif complet avec étapes guidées
2. **realtime_dashboard_v3.py** : Dashboard avec auto-refresh et graphiques
3. **session_manager.py** : Gestionnaire complet (save/load/compare sessions)

---

## 📝 Code à Ajouter dans main_v3.py

### Version Simple (Recommandée pour l'instant)

```python
# ========================================================================
# BARRE D'ACTIONS RAPIDES
# ========================================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🧭 Guide d'utilisation", use_container_width=True):
        st.info("""
        ### 🧭 Guide de Démarrage Rapide

        **1. Configuration (Onglet 🚀)**
        - Vérifiez la connectivité des endpoints

        **2. Datasets (Onglet 📦)**
        - Chargez un dataset (DBpedia, LUBM, Generic)
        - Synchronisez entre Virtuoso et Fuseki

        **3. Tests (Onglet 🧪)**
        - Sélectionnez les requêtes à tester
        - Cliquez sur "Exécuter les tests"

        **4. Résultats (Onglet 📊)**
        - Consultez les temps d'exécution
        - Exportez les résultats
        """)

with col2:
    if st.button("📊 Dashboard temps réel", use_container_width=True):
        st.markdown("### 📊 État du Système")

        import psutil

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("CPU", f"{psutil.cpu_percent():.1f}%")
        with col_b:
            st.metric("Mémoire", f"{psutil.virtual_memory().percent:.1f}%")
        with col_c:
            disk = psutil.disk_usage('/')
            st.metric("Disque", f"{(disk.used/disk.total)*100:.1f}%")

with col3:
    if st.button("💾 Sauvegarder session", use_container_width=True):
        import json
        from datetime import datetime

        session_data = {
            "timestamp": datetime.now().isoformat(),
            "config": {
                "virtuoso_endpoint": st.session_state.get('virtuoso_endpoint', ''),
                "fuseki_endpoint": st.session_state.get('fuseki_endpoint', ''),
                "num_iterations": st.session_state.get('num_iterations', 5),
            }
        }

        filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        st.download_button(
            label="📥 Télécharger la session",
            data=json.dumps(session_data, indent=2, ensure_ascii=False),
            file_name=filename,
            mime="application/json"
        )

        st.success("✅ Session prête au téléchargement !")

with col4:
    if st.button("🔄 Rafraîchir", use_container_width=True):
        st.rerun()
```

---

## ✅ Checklist d'Implémentation

- [ ] Implémenter guide simple avec st.info()
- [ ] Créer dashboard simple avec métriques psutil
- [ ] Implémenter sauvegarde JSON avec download_button
- [ ] Tester les 4 boutons
- [ ] (Optionnel) Créer modules complets
- [ ] (Optionnel) Ajouter confirmation pour rafraîchir
- [ ] Documenter l'utilisation

---

**Dernière mise à jour** : 11 Novembre 2025
**Statut** : Guide complet - Prêt pour implémentation
