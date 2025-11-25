# 🧩 Components UI - SPARQL Performance Platform

Ce dossier contient les composants d'interface réutilisables de l'application.

---

## 📂 Structure

```
ui/components/
├── __init__.py                    # Exports des composants
├── connectivity_checker.py        # Vérification connectivité endpoints
├── system_info.py                 # Informations système (CPU, RAM)
├── navbar_simple.py              # 🆕 Navbar simple (streamlit-option-menu)
├── navbar_custom.py              # 🆕 Navbar custom (HTML/CSS)
└── README.md                      # Ce fichier
```

---

## 🆕 Nouveaux Composants de Navigation

### navbar_simple.py

**Description** : Barre de navigation basée sur `streamlit-option-menu`

**Avantages** :
- ✅ Installation rapide (1 commande pip)
- ✅ Responsive par défaut
- ✅ Icons Bootstrap intégrés
- ✅ Peu de code (~100 lignes)

**Utilisation** :
```python
from ui.components.navbar_simple import render_simple_navbar_with_logo

selected_page = render_simple_navbar_with_logo()

if selected_page == "Configuration & Tests":
    st.title("🚀 Configuration")
```

**Prérequis** :
```bash
pip install streamlit-option-menu
```

---

### navbar_custom.py ⭐ RECOMMANDÉ

**Description** : Barre de navigation professionnelle HTML/CSS intégrée au design system

**Avantages** :
- ✅ Aucune dépendance externe
- ✅ Contrôle total du design
- ✅ Accessibilité complète (WCAG 2.1 AA)
- ✅ Responsive optimisé
- ✅ Intégration design system
- ✅ Performance maximale

**Utilisation** :
```python
from ui.components.navbar_custom import render_custom_navbar

current_page = render_custom_navbar()

if current_page == "config":
    st.title("🚀 Configuration")
elif current_page == "datasets":
    st.title("📦 Datasets")
# etc.
```

**Prérequis** : Aucun ✅

**Configuration** : Les pages sont définies dans la classe `CustomNavbar.__init__()` :
```python
self.pages = [
    {
        "id": "config",
        "label": "Configuration & Tests",
        "icon": "🚀",
        "description": "Configurer et exécuter les tests SPARQL"
    },
    # ...
]
```

---

## 🎨 Intégration Design System

Les composants utilisent les constantes du design system :

```python
from ui.design_system import Colors, Typography, Spacing, Effects

# Exemple d'utilisation dans les composants
background: {Colors.PRIMARY}
font-size: {Typography.SIZE_H4}
padding: {Spacing.LG}
border-radius: {Effects.RADIUS_MD}
```

**Avantage** : Changement global en modifiant uniquement `ui/design_system.py` !

---

## 📚 Documentation Complète

- **Guide d'implémentation** : [NAVBAR_IMPLEMENTATION_GUIDE.md](../../NAVBAR_IMPLEMENTATION_GUIDE.md)
- **Quick Start** : [NAVBAR_QUICK_START.md](../../NAVBAR_QUICK_START.md)

---

## 🔧 Maintenance

### Ajouter un Nouveau Composant

1. Créer le fichier `mon_composant.py`
2. Implémenter la fonction `render_mon_composant()`
3. Exporter dans `__init__.py`
4. Documenter dans ce README

**Template** :
```python
"""
Description du composant
"""

import streamlit as st
from ui.design_system import Colors, Typography, Spacing, Effects

def render_mon_composant():
    """
    Affiche mon composant personnalisé

    Args:
        None

    Returns:
        None
    """

    st.markdown(f"""
    <div style="
        background: {Colors.BG_CARD};
        padding: {Spacing.LG};
        border-radius: {Effects.RADIUS_MD};
    ">
        <h3>Mon Composant</h3>
        <p>Contenu du composant</p>
    </div>
    """, unsafe_allow_html=True)
```

### Modifier un Composant Existant

1. Éditer le fichier du composant
2. Tester l'impact sur l'application
3. Mettre à jour la documentation si nécessaire

---

## ✅ Tests

### Test Manuel

```bash
# Tester navbar_simple.py
streamlit run ui/components/navbar_simple.py

# Tester navbar_custom.py
streamlit run ui/components/navbar_custom.py
```

### Test d'Intégration

```bash
# Tester dans l'application complète
streamlit run main_v3_refactored.py
```

---

## 🐛 Problèmes Connus

### navbar_simple.py

- **Problème** : Layout complexe avec logo + menu + actions
- **Solution** : Utiliser `st.columns()` (voir exemple dans le fichier)

### navbar_custom.py

- **Problème** : Position `left: 250px` peut varier selon la sidebar
- **Solution** : Ajuster manuellement ou utiliser JavaScript pour détection dynamique

---

## 📝 Changelog

### v3.1.3 (12 Novembre 2025)

**Ajouté** :
- ✅ `navbar_simple.py` - Navigation simple avec streamlit-option-menu
- ✅ `navbar_custom.py` - Navigation professionnelle custom
- ✅ Documentation complète (guide + quick start)

**Modifié** :
- ✅ `__init__.py` - Exports des nouveaux composants

---

## 🚀 Roadmap

### v3.2.0 (Prévu)

- [ ] Navbar avec menu hamburger (mobile)
- [ ] Composant de breadcrumb navigation
- [ ] Composant de notifications toast
- [ ] Composant de modal/dialog
- [ ] Composant de stepper (wizard)

---

## 📞 Support

**Questions ?** Consultez :
- [Guide complet](../../NAVBAR_IMPLEMENTATION_GUIDE.md)
- [Quick Start](../../NAVBAR_QUICK_START.md)
- [Changelog principal](../../CHANGELOG_v3.1.3.md)

---

**Dernière mise à jour** : 12 Novembre 2025
**Composants disponibles** : 4
**Nouveaux composants** : 2 (navbar_simple, navbar_custom)
