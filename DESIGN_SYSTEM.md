# 🎨 Design System - SPARQL Performance Platform v3.0

Documentation complète du système de design professionnel de la plateforme.

---

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Palette de couleurs](#palette-de-couleurs)
3. [Typographie](#typographie)
4. [Espacements](#espacements)
5. [Effets visuels](#effets-visuels)
6. [Composants](#composants)
7. [Guide d'utilisation](#guide-dutilisation)
8. [Exemples](#exemples)

---

## 🎯 Vue d'ensemble

Le Design System v3.0 fournit un ensemble cohérent de styles, composants et guidelines pour créer une interface utilisateur professionnelle et conviviale.

### Principes de design

1. **Cohérence** : Utilisation systématique des mêmes couleurs, espacements et typographie
2. **Clarté** : Hiérarchie visuelle claire et navigation intuitive
3. **Performance** : Optimisation du rendu et des animations
4. **Accessibilité** : Contraste suffisant et textes lisibles
5. **Professionnalisme** : Apparence moderne et soignée

---

## 🎨 Palette de Couleurs

### Couleurs Primaires

| Nom | Hex | Utilisation |
|-----|-----|-------------|
| **PRIMARY** | `#0066CC` | Boutons principaux, liens, accents |
| **PRIMARY_DARK** | `#004C99` | Hover states, emphasis |
| **PRIMARY_LIGHT** | `#3385DB` | Backgrounds clairs |
| **PRIMARY_PALE** | `#E6F2FF` | Cards, sections |

```python
from ui.design_system import Colors

# Utilisation
color = Colors.PRIMARY
```

### Couleurs Secondaires

| Nom | Hex | Utilisation |
|-----|-----|-------------|
| **SECONDARY** | `#7C3AED` | Accents secondaires |
| **SECONDARY_DARK** | `#5B21B6` | Hover secondaire |
| **SECONDARY_LIGHT** | `#A78BFA` | Backgrounds secondaires |
| **SECONDARY_PALE** | `#F5F3FF` | Cards secondaires |

### Couleurs Sémantiques

#### Succès (Vert)
- **SUCCESS**: `#10B981` - Actions réussies
- **SUCCESS_DARK**: `#059669`
- **SUCCESS_LIGHT**: `#34D399`
- **SUCCESS_PALE**: `#D1FAE5`

#### Avertissement (Orange)
- **WARNING**: `#F59E0B` - Avertissements
- **WARNING_DARK**: `#D97706`
- **WARNING_LIGHT**: `#FBBF24`
- **WARNING_PALE**: `#FEF3C7`

#### Erreur (Rouge)
- **ERROR**: `#EF4444` - Erreurs
- **ERROR_DARK**: `#DC2626`
- **ERROR_LIGHT**: `#F87171`
- **ERROR_PALE**: `#FEE2E2`

#### Information (Bleu)
- **INFO**: `#3B82F6` - Informations
- **INFO_DARK**: `#2563EB`
- **INFO_LIGHT**: `#60A5FA`
- **INFO_PALE**: `#DBEAFE`

### Couleurs Spécifiques

#### Triplestores
- **VIRTUOSO**: `#E11D48` - Rouge Virtuoso
- **VIRTUOSO_LIGHT**: `#FDA4AF`
- **FUSEKI**: `#0891B2` - Cyan Fuseki
- **FUSEKI_LIGHT**: `#67E8F9`

### Couleurs Neutres (Gris)

| Nom | Hex | Utilisation |
|-----|-----|-------------|
| **GRAY_900** | `#111827` | Texte principal |
| **GRAY_800** | `#1F2937` | Texte foncé |
| **GRAY_700** | `#374151` | Texte secondaire |
| **GRAY_600** | `#4B5563` | Texte moyen-foncé |
| **GRAY_500** | `#6B7280` | Texte moyen |
| **GRAY_400** | `#9CA3AF` | Texte moyen-clair |
| **GRAY_300** | `#D1D5DB` | Bordures |
| **GRAY_200** | `#E5E7EB` | Bordures claires |
| **GRAY_100** | `#F3F4F6` | Backgrounds |
| **GRAY_50** | `#F9FAFB` | Backgrounds ultra-clairs |

---

## 📝 Typographie

### Tailles de Police

| Nom | Taille | Utilisation |
|-----|--------|-------------|
| **SIZE_DISPLAY** | 3rem (48px) | Titres principaux |
| **SIZE_H1** | 2.25rem (36px) | H1 |
| **SIZE_H2** | 1.875rem (30px) | H2 |
| **SIZE_H3** | 1.5rem (24px) | H3 |
| **SIZE_H4** | 1.25rem (20px) | H4 |
| **SIZE_H5** | 1.125rem (18px) | H5 |
| **SIZE_BODY_LARGE** | 1.125rem (18px) | Corps large |
| **SIZE_BODY** | 1rem (16px) | Corps normal |
| **SIZE_BODY_SMALL** | 0.875rem (14px) | Corps petit |
| **SIZE_CAPTION** | 0.75rem (12px) | Légendes |

```python
from ui.design_system import Typography

# Utilisation
font_size = Typography.SIZE_H1
```

### Poids de Police

- **WEIGHT_LIGHT**: 300
- **WEIGHT_REGULAR**: 400
- **WEIGHT_MEDIUM**: 500
- **WEIGHT_SEMIBOLD**: 600
- **WEIGHT_BOLD**: 700
- **WEIGHT_EXTRABOLD**: 800

### Hauteur de Ligne

- **LINE_HEIGHT_TIGHT**: 1.2 - Pour les titres
- **LINE_HEIGHT_NORMAL**: 1.5 - Pour le corps de texte
- **LINE_HEIGHT_RELAXED**: 1.75 - Pour les paragraphes
- **LINE_HEIGHT_LOOSE**: 2 - Pour les textes aérés

---

## 📏 Espacements

Système d'espacement basé sur une grille de 4px.

| Nom | Taille | Pixels | Utilisation |
|-----|--------|--------|-------------|
| **XS** | 0.25rem | 4px | Micro-espacements |
| **SM** | 0.5rem | 8px | Petits espacements |
| **MD** | 1rem | 16px | Espacements moyens |
| **LG** | 1.5rem | 24px | Grands espacements |
| **XL** | 2rem | 32px | Très grands espacements |
| **XXL** | 3rem | 48px | Espacements extra-larges |
| **XXXL** | 4rem | 64px | Espacements massifs |

```python
from ui.design_system import Spacing

# Utilisation
padding = Spacing.MD
margin = Spacing.LG
```

---

## ✨ Effets Visuels

### Border Radius (Arrondis)

| Nom | Taille | Utilisation |
|-----|--------|-------------|
| **RADIUS_NONE** | 0 | Pas d'arrondi |
| **RADIUS_SM** | 0.25rem (4px) | Petits arrondis |
| **RADIUS_MD** | 0.5rem (8px) | Arrondis moyens |
| **RADIUS_LG** | 0.75rem (12px) | Grands arrondis |
| **RADIUS_XL** | 1rem (16px) | Très grands arrondis |
| **RADIUS_FULL** | 9999px | Arrondi complet (cercles) |

### Box Shadows (Ombres)

| Nom | Utilisation |
|-----|-------------|
| **SHADOW_NONE** | Pas d'ombre |
| **SHADOW_SM** | Ombre légère (cards au repos) |
| **SHADOW_MD** | Ombre moyenne (cards hover) |
| **SHADOW_LG** | Ombre grande (modals, popovers) |
| **SHADOW_XL** | Ombre extra-large (emphasis) |

### Border Widths (Largeurs de Bordures)

- **BORDER_THIN**: 1px - Bordures fines
- **BORDER_MEDIUM**: 2px - Bordures moyennes
- **BORDER_THICK**: 4px - Bordures épaisses (accents)

```python
from ui.design_system import Effects

# Utilisation
border_radius = Effects.RADIUS_LG
box_shadow = Effects.SHADOW_MD
```

---

## 🧩 Composants

### 1. Cartes (Cards)

```python
from ui.design_system import create_card

create_card(
    content="Contenu de la carte",
    title="Titre optionnel",
    icon="🎨",
    color=Colors.BG_CARD,
    border_color=Colors.GRAY_200
)
```

**Utilisation** : Regrouper du contenu connexe

### 2. Cartes de Métrique

```python
from ui.design_system import create_metric_card

create_metric_card(
    label="Temps moyen",
    value="145 ms",
    delta="+12%",
    delta_positive=False,
    icon="⏱️",
    color=Colors.PRIMARY
)
```

**Utilisation** : Afficher des KPIs et métriques importantes

### 3. Badges de Statut

```python
from ui.design_system import create_status_badge

badge_html = create_status_badge(
    text="En cours",
    status="info"  # info, success, warning, error
)
st.markdown(badge_html, unsafe_allow_html=True)
```

**Utilisation** : Indiquer l'état d'une ressource

### 4. Alertes

```python
from ui.design_system import create_alert

create_alert(
    message="Opération réussie !",
    alert_type="success",  # info, success, warning, error
    dismissible=False
)
```

**Utilisation** : Notifications et messages importants

### 5. Séparateurs (Dividers)

```python
from ui.design_system import create_divider

# Divider simple
create_divider()

# Divider avec texte
create_divider(text="OU")
```

**Utilisation** : Séparer des sections de contenu

---

## 📖 Guide d'Utilisation

### Initialisation

Dans votre fichier principal (main_v3.py) :

```python
from ui.design_system import apply_custom_css

def main():
    st.set_page_config(...)

    # Appliquer le design system
    apply_custom_css()

    # Reste du code...
```

### Importer les Composants

```python
from ui.design_system import (
    Colors, Typography, Spacing, Effects,
    create_card, create_metric_card, create_alert
)
```

### Bonnes Pratiques

1. **Toujours utiliser les couleurs du Design System**
   ```python
   # ✅ BON
   color = Colors.PRIMARY

   # ❌ MAUVAIS
   color = "#0066CC"
   ```

2. **Utiliser les espacements cohérents**
   ```python
   # ✅ BON
   padding = Spacing.MD

   # ❌ MAUVAIS
   padding = "15px"
   ```

3. **Utiliser les composants pré-construits**
   ```python
   # ✅ BON
   create_alert("Message", alert_type="success")

   # ❌ MAUVAIS
   st.success("Message")  # Moins cohérent visuellement
   ```

4. **Respecter la hiérarchie typographique**
   - H1 : Titre principal de la page (1 par page)
   - H2 : Sections principales
   - H3 : Sous-sections
   - Body : Texte normal
   - Caption : Textes secondaires

---

## 🎯 Exemples

### Exemple 1 : Page de Configuration

```python
from ui.design_system import *

def render_configuration_page():
    apply_custom_css()

    # En-tête
    st.markdown("### 🚀 Configuration")
    st.caption("Configurez vos endpoints SPARQL")

    create_divider()

    # Carte d'information
    create_alert(
        "Assurez-vous que Virtuoso et Fuseki sont démarrés avant de continuer.",
        alert_type="info"
    )

    # Métriques
    col1, col2 = st.columns(2)

    with col1:
        create_metric_card(
            label="Virtuoso",
            value="12,484 triplets",
            delta="✅ Connecté",
            delta_positive=True,
            icon="🔴",
            color=Colors.VIRTUOSO
        )

    with col2:
        create_metric_card(
            label="Fuseki",
            value="10,000 triplets",
            delta="✅ Connecté",
            delta_positive=True,
            icon="🔵",
            color=Colors.FUSEKI
        )
```

### Exemple 2 : Dashboard de Résultats

```python
def render_results_dashboard():
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        create_metric_card(
            label="Tests exécutés",
            value="24",
            icon="🧪",
            color=Colors.PRIMARY
        )

    with col2:
        create_metric_card(
            label="Temps moyen",
            value="145 ms",
            delta="-12%",
            delta_positive=True,
            icon="⏱️",
            color=Colors.SUCCESS
        )

    with col3:
        create_metric_card(
            label="Taux de réussite",
            value="98.5%",
            delta="+2.1%",
            delta_positive=True,
            icon="✅",
            color=Colors.SUCCESS
        )

    with col4:
        create_metric_card(
            label="Requêtes/sec",
            value="6.89",
            delta="+15%",
            delta_positive=True,
            icon="⚡",
            color=Colors.WARNING
        )

    create_divider("Détails par triplestore")

    # Comparaison Virtuoso vs Fuseki
    col1, col2 = st.columns(2)

    with col1:
        create_card(
            title="Virtuoso",
            icon="🔴",
            content="""
            <ul>
                <li><strong>Temps moyen:</strong> 132 ms</li>
                <li><strong>Écart-type:</strong> ±18 ms</li>
                <li><strong>Plus rapide:</strong> 89 ms</li>
                <li><strong>Plus lent:</strong> 201 ms</li>
            </ul>
            """,
            border_color=Colors.VIRTUOSO
        )

    with col2:
        create_card(
            title="Fuseki",
            icon="🔵",
            content="""
            <ul>
                <li><strong>Temps moyen:</strong> 158 ms</li>
                <li><strong>Écart-type:</strong> ±24 ms</li>
                <li><strong>Plus rapide:</strong> 112 ms</li>
                <li><strong>Plus lent:</strong> 234 ms</li>
            </ul>
            """,
            border_color=Colors.FUSEKI
        )
```

---

## 🔧 Personnalisation

### Modifier les Couleurs

Pour adapter les couleurs à votre marque, modifiez [ui/design_system.py](ui/design_system.py) :

```python
class Colors:
    PRIMARY = "#0066CC"  # Votre couleur primaire
    SECONDARY = "#7C3AED"  # Votre couleur secondaire
    # ...
```

### Ajouter de Nouveaux Composants

Créez vos propres composants dans `ui/design_system.py` :

```python
def create_custom_component(param1, param2):
    """Description du composant"""

    html = f"""
    <div style="...">
        {param1}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
```

---

## ✅ Checklist de Migration

Pour migrer une page existante vers le Design System v3.0 :

- [ ] Importer `apply_custom_css()` et l'appeler en début de page
- [ ] Remplacer les couleurs hardcodées par `Colors.*`
- [ ] Remplacer les espacements hardcodés par `Spacing.*`
- [ ] Utiliser `create_card()` pour les groupes de contenu
- [ ] Utiliser `create_metric_card()` pour les KPIs
- [ ] Utiliser `create_alert()` pour les messages
- [ ] Utiliser `create_divider()` pour les séparations
- [ ] Utiliser `create_status_badge()` pour les statuts
- [ ] Respecter la hiérarchie typographique

---

## 📚 Ressources

- [Code source du Design System](ui/design_system.py)
- [Application principale v3.0](main_v3.py)
- [Exemples de composants](ui/components/)

---

## 🎉 Conclusion

Le Design System v3.0 vous permet de créer des interfaces cohérentes, professionnelles et maintenables. Utilisez-le systématiquement pour garantir une expérience utilisateur optimale !

**Dernière mise à jour** : 11 Novembre 2025
**Version** : 3.0.0
**Statut** : ✅ Production-Ready
