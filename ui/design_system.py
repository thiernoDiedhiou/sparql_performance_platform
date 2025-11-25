"""
Système de Design Unifié pour SPARQL Performance Platform
Composants UI réutilisables

Responsabilité : Fournir des composants UI stylisés (cards, alerts, badges, etc.)
Les constantes de design sont importées depuis ui/theme/design_tokens.py

VERSION 3.4 - Architecture refactorisée selon le principe SRP
"""

import streamlit as st
from typing import Dict, Optional

# Import des constantes de design depuis le nouveau package ui/theme
from ui.theme.design_tokens import Colors, Typography, Spacing, Effects, Layout


# ============================================================================
# COMPOSANTS STYLISÉS
# ============================================================================

def create_card(
    content: str,
    title: Optional[str] = None,
    icon: Optional[str] = None,
    color: str = Colors.BG_CARD,
    border_color: str = Colors.GRAY_200,
    content_type: str = "markdown"  # "markdown" ou "html"
) -> None:
    """
    Crée une carte stylisée avec contenu (CORRIGÉ pour wizard + gestion débordement)

    Args:
        content: Contenu (Markdown ou HTML selon content_type)
        title: Titre optionnel de la carte
        icon: Icône optionnelle (emoji)
        color: Couleur de fond
        border_color: Couleur de la bordure
        content_type: "markdown" (par défaut) ou "html"
    """
    # Conteneur de la carte avec styles améliorés (anti-débordement)
    card_container_start = f"""
    <div style="
        background: {color};
        border: {Effects.BORDER_THIN} solid {border_color};
        border-radius: {Effects.RADIUS_LG};
        padding: {Spacing.LG};
        box-shadow: {Effects.SHADOW_SM};
        margin: {Spacing.MD} 0;
        overflow: hidden;
        word-wrap: break-word;
        word-break: break-word;
    ">
    """

    card_container_end = "</div>"

    # En-tête si titre fourni avec gestion du débordement
    card_header = ""
    if title:
        card_header = f"""
        <div style="
            display: flex;
            align-items: center;
            margin-bottom: {Spacing.MD};
            overflow: hidden;
        ">
            {f'<span style="font-size: {Typography.SIZE_H4}; margin-right: {Spacing.SM}; flex-shrink: 0;">{icon}</span>' if icon else ''}
            <h3 style="
                margin: 0;
                color: {Colors.TEXT_PRIMARY};
                font-size: {Typography.SIZE_H4};
                font-weight: {Typography.WEIGHT_SEMIBOLD};
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            ">{title}</h3>
        </div>
        """

    # Conteneur de contenu avec gestion du débordement
    content_wrapper_start = f"""
    <div style="
        overflow: hidden;
        word-wrap: break-word;
        word-break: break-word;
        line-height: 1.6;
    ">
    """
    content_wrapper_end = "</div>"

    # Rendu selon le type de contenu
    if content_type == "html":
        # Mode HTML : tout dans un seul bloc avec wrapper de contenu
        full_html = (card_container_start + card_header +
                     content_wrapper_start + content + content_wrapper_end +
                     card_container_end)
        st.markdown(full_html, unsafe_allow_html=True)
    else:
        # Mode Markdown (par défaut) : Streamlit rend le Markdown
        st.markdown(card_container_start + card_header + content_wrapper_start, unsafe_allow_html=True)
        st.markdown(content)  # Streamlit rend le Markdown ici
        st.markdown(content_wrapper_end + card_container_end, unsafe_allow_html=True)


def create_metric_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    delta_positive: bool = True,
    icon: Optional[str] = None,
    color: str = Colors.PRIMARY
) -> None:
    """
    Crée une carte de métrique stylisée

    Args:
        label: Libellé de la métrique
        value: Valeur principale
        delta: Variation optionnelle
        delta_positive: Si True, delta en vert, sinon en rouge
        icon: Icône optionnelle
        color: Couleur d'accent
    """
    # Convertir en chaînes pour éviter erreurs de type
    label = str(label)
    value = str(value)
    delta_color = Colors.SUCCESS if delta_positive else Colors.ERROR

    # Construire le HTML par concaténation pour éviter TOUT problème d'échappement
    metric_html = ('<div style="background: ' + Colors.BG_CARD + '; border: ' + Effects.BORDER_THIN +
                   ' solid ' + Colors.GRAY_200 + '; border-left: ' + Effects.BORDER_THICK +
                   ' solid ' + color + '; border-radius: ' + Effects.RADIUS_LG + '; padding: ' +
                   Spacing.LG + '; box-shadow: ' + Effects.SHADOW_SM + '; margin: ' + Spacing.MD +
                   ' 0; overflow: hidden;">')

    metric_html += ('<div style="display: flex; justify-content: space-between; align-items: center; gap: ' +
                    Spacing.MD + ';">')

    metric_html += '<div style="flex: 1; min-width: 0;">'

    metric_html += ('<div style="color: ' + Colors.TEXT_SECONDARY + '; font-size: ' +
                    Typography.SIZE_BODY_SMALL + '; font-weight: ' + Typography.WEIGHT_MEDIUM +
                    '; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: ' +
                    Spacing.SM + '; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">' +
                    label + '</div>')

    metric_html += ('<div style="color: ' + Colors.TEXT_PRIMARY + '; font-size: ' + Typography.SIZE_H3 +
                    '; font-weight: ' + Typography.WEIGHT_BOLD + '; line-height: ' +
                    Typography.LINE_HEIGHT_TIGHT + ';">' + value + '</div>')

    if delta:
        metric_html += ('<div style="color: ' + delta_color + '; font-size: ' + Typography.SIZE_BODY_SMALL +
                        '; font-weight: ' + Typography.WEIGHT_MEDIUM + '; margin-top: ' + Spacing.XS +
                        ';">' + str(delta) + '</div>')

    metric_html += '</div>'

    if icon:
        metric_html += '<div style="font-size: 2rem; opacity: 0.15; flex-shrink: 0;">' + icon + '</div>'

    metric_html += '</div></div>'

    st.markdown(metric_html, unsafe_allow_html=True)


def create_status_badge(
    text: str,
    status: str = "info"  # info, success, warning, error
) -> str:
    """
    Crée un badge de statut coloré

    Args:
        text: Texte du badge
        status: Type de statut (info, success, warning, error)

    Returns:
        HTML du badge
    """
    status_colors = {
        "info": (Colors.INFO, Colors.INFO_PALE),
        "success": (Colors.SUCCESS, Colors.SUCCESS_PALE),
        "warning": (Colors.WARNING, Colors.WARNING_PALE),
        "error": (Colors.ERROR, Colors.ERROR_PALE)
    }

    text_color, bg_color = status_colors.get(status, status_colors["info"])

    return f"""
    <span style="
        display: inline-block;
        background: {bg_color};
        color: {text_color};
        padding: {Spacing.XS} {Spacing.MD};
        border-radius: {Effects.RADIUS_FULL};
        font-size: {Typography.SIZE_BODY_SMALL};
        font-weight: {Typography.WEIGHT_SEMIBOLD};
        line-height: 1;
    ">
        {text}
    </span>
    """


def create_alert(
    message: str,
    alert_type: str = "info",  # info, success, warning, error
    dismissible: bool = False
) -> None:
    """
    Crée une alerte stylisée

    Args:
        message: Message de l'alerte
        alert_type: Type d'alerte
        dismissible: Si True, ajoute un bouton de fermeture
    """
    alert_configs = {
        "info": {
            "bg": Colors.INFO_PALE,
            "border": Colors.INFO,
            "text": Colors.INFO_DARK,
            "icon": "ℹ️"
        },
        "success": {
            "bg": Colors.SUCCESS_PALE,
            "border": Colors.SUCCESS,
            "text": Colors.SUCCESS_DARK,
            "icon": "✅"
        },
        "warning": {
            "bg": Colors.WARNING_PALE,
            "border": Colors.WARNING,
            "text": Colors.WARNING_DARK,
            "icon": "⚠️"
        },
        "error": {
            "bg": Colors.ERROR_PALE,
            "border": Colors.ERROR,
            "text": Colors.ERROR_DARK,
            "icon": "❌"
        }
    }

    config = alert_configs.get(alert_type, alert_configs["info"])

    alert_html = f"""
    <div style="
        background: {config['bg']};
        border-left: {Effects.BORDER_THICK} solid {config['border']};
        border-radius: {Effects.RADIUS_MD};
        padding: {Spacing.LG};
        margin: {Spacing.MD} 0;
        display: flex;
        align-items: center;
    ">
        <span style="font-size: {Typography.SIZE_H4}; margin-right: {Spacing.MD};">{config['icon']}</span>
        <div style="color: {config['text']}; flex: 1; line-height: {Typography.LINE_HEIGHT_RELAXED};">
            {message}
        </div>
    </div>
    """
    st.markdown(alert_html, unsafe_allow_html=True)


def create_divider(
    text: Optional[str] = None,
    color: str = Colors.GRAY_300
) -> None:
    """
    Crée une ligne de séparation optionnellement avec texte

    Args:
        text: Texte optionnel au centre du divider
        color: Couleur de la ligne
    """
    if text:
        divider_html = f"""
        <div style="
            display: flex;
            align-items: center;
            text-align: center;
            margin: {Spacing.XL} 0;
        ">
            <div style="flex: 1; border-bottom: {Effects.BORDER_THIN} solid {color};"></div>
            <span style="
                padding: 0 {Spacing.LG};
                color: {Colors.TEXT_SECONDARY};
                font-size: {Typography.SIZE_BODY_SMALL};
                font-weight: {Typography.WEIGHT_MEDIUM};
                text-transform: uppercase;
                letter-spacing: 0.05em;
            ">{text}</span>
            <div style="flex: 1; border-bottom: {Effects.BORDER_THIN} solid {color};"></div>
        </div>
        """
    else:
        divider_html = f"""
        <div style="
            border-bottom: {Effects.BORDER_THIN} solid {color};
            margin: {Spacing.XL} 0;
        "></div>
        """

    st.markdown(divider_html, unsafe_allow_html=True)


# ============================================================================
# CUSTOM CSS
# ============================================================================

def apply_custom_css():
    """
    Applique le CSS personnalisé global pour améliorer l'apparence Streamlit
    VERSION 3.2 - Compatible avec navbar sticky de main.py
    """

    custom_css = f"""
    <style>
        /* ===== VARIABLES CSS ===== */
        :root {{
            --primary-color: {Colors.PRIMARY};
            --secondary-color: {Colors.SECONDARY};
            --success-color: {Colors.SUCCESS};
            --warning-color: {Colors.WARNING};
            --error-color: {Colors.ERROR};
            --text-primary: {Colors.TEXT_PRIMARY};
            --text-secondary: {Colors.TEXT_SECONDARY};
            --bg-primary: {Colors.BG_PRIMARY};
            --bg-secondary: {Colors.BG_SECONDARY};
        }}

        /* ===== CORPS DE LA PAGE ===== */
        .main {{
            background-color: {Colors.BG_SECONDARY};
        }}

        /* SUPPRIMÉ - main.py gère le block-container pour la navbar
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }}
        */

        /* ===== SIDEBAR ===== */
        section[data-testid="stSidebar"] {{
            background-color: {Colors.BG_SIDEBAR};
        }}

        section[data-testid="stSidebar"] .block-container {{
            padding-top: 2rem;
        }}

        /* ===== TITRES ===== */
        h1 {{
            color: {Colors.TEXT_PRIMARY} !important;
            font-weight: {Typography.WEIGHT_BOLD} !important;
            line-height: {Typography.LINE_HEIGHT_TIGHT} !important;
            margin-bottom: {Spacing.LG} !important;
        }}

        h2 {{
            color: {Colors.TEXT_PRIMARY} !important;
            font-weight: {Typography.WEIGHT_SEMIBOLD} !important;
            line-height: {Typography.LINE_HEIGHT_TIGHT} !important;
            margin-top: {Spacing.XL} !important;
            margin-bottom: {Spacing.MD} !important;
        }}

        h3 {{
            color: {Colors.TEXT_PRIMARY} !important;
            font-weight: {Typography.WEIGHT_SEMIBOLD} !important;
            line-height: {Typography.LINE_HEIGHT_NORMAL} !important;
            margin-top: {Spacing.LG} !important;
            margin-bottom: {Spacing.SM} !important;
        }}

        /* ===== ONGLETS - SUPPRIMÉ, main.py gère les styles ===== */
        /* La gestion des tabs est faite dans main.py pour compatibilité avec sticky navbar */

        /* ===== BOUTONS ===== */
        .stButton > button {{
            background-color: {Colors.PRIMARY};
            color: {Colors.TEXT_ON_PRIMARY};
            border: none;
            border-radius: {Effects.RADIUS_MD};
            padding: {Spacing.SM} {Spacing.LG};
            font-weight: {Typography.WEIGHT_SEMIBOLD};
            box-shadow: {Effects.SHADOW_SM};
            transition: all 0.2s ease;
        }}

        .stButton > button:hover {{
            background-color: {Colors.PRIMARY_DARK};
            box-shadow: {Effects.SHADOW_MD};
            transform: translateY(-1px);
        }}

        /* Boutons secondaires */
        .stButton > button[kind="secondary"] {{
            background-color: {Colors.BG_CARD};
            color: {Colors.PRIMARY};
            border: {Effects.BORDER_THIN} solid {Colors.PRIMARY};
        }}

        .stButton > button[kind="secondary"]:hover {{
            background-color: {Colors.PRIMARY_PALE};
        }}

        /* ===== INPUTS ===== */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div,
        .stMultiSelect > div > div {{
            border-radius: {Effects.RADIUS_MD};
            border: {Effects.BORDER_THIN} solid {Colors.GRAY_300};
            padding: {Spacing.SM};
        }}

        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus {{
            border-color: {Colors.PRIMARY};
            box-shadow: 0 0 0 1px {Colors.PRIMARY};
        }}

        /* ===== MÉTRIQUES ===== */
        [data-testid="stMetricValue"] {{
            font-size: {Typography.SIZE_H2};
            font-weight: {Typography.WEIGHT_BOLD};
            color: {Colors.TEXT_PRIMARY};
        }}

        [data-testid="stMetricDelta"] {{
            font-size: {Typography.SIZE_BODY_SMALL};
            font-weight: {Typography.WEIGHT_MEDIUM};
        }}

        /* ===== CARTES / CONTAINERS ===== */
        .element-container {{
            margin-bottom: {Spacing.MD};
        }}

        /* ===== EXPANDERS ===== */
        .streamlit-expanderHeader {{
            background-color: {Colors.BG_CARD};
            border: {Effects.BORDER_THIN} solid {Colors.GRAY_200};
            border-radius: {Effects.RADIUS_MD};
            padding: {Spacing.MD};
            font-weight: {Typography.WEIGHT_SEMIBOLD};
        }}

        .streamlit-expanderHeader:hover {{
            background-color: {Colors.GRAY_50};
        }}

        /* ===== DATAFRAMES / TABLES ===== */
        .dataframe {{
            border: {Effects.BORDER_THIN} solid {Colors.GRAY_200} !important;
            border-radius: {Effects.RADIUS_MD} !important;
        }}

        /* ===== SPINNER ===== */
        .stSpinner > div {{
            border-top-color: {Colors.PRIMARY} !important;
        }}

        /* ===== SUCCESS/ERROR/WARNING/INFO BOXES ===== */
        .stSuccess {{
            background-color: {Colors.SUCCESS_PALE};
            border-left: {Effects.BORDER_THICK} solid {Colors.SUCCESS};
            border-radius: {Effects.RADIUS_MD};
            padding: {Spacing.LG};
        }}

        .stError {{
            background-color: {Colors.ERROR_PALE};
            border-left: {Effects.BORDER_THICK} solid {Colors.ERROR};
            border-radius: {Effects.RADIUS_MD};
            padding: {Spacing.LG};
        }}

        .stWarning {{
            background-color: {Colors.WARNING_PALE};
            border-left: {Effects.BORDER_THICK} solid {Colors.WARNING};
            border-radius: {Effects.RADIUS_MD};
            padding: {Spacing.LG};
        }}

        .stInfo {{
            background-color: {Colors.INFO_PALE};
            border-left: {Effects.BORDER_THICK} solid {Colors.INFO};
            border-radius: {Effects.RADIUS_MD};
            padding: {Spacing.LG};
        }}

        /* ===== PROGRESS BAR ===== */
        .stProgress > div > div > div {{
            background-color: {Colors.PRIMARY};
        }}

        /* ===== SELECTBOX / MULTISELECT DROPDOWN ===== */
        [data-baseweb="select"] > div {{
            border-radius: {Effects.RADIUS_MD};
        }}

        /* ===== CACHE POUR AMÉLIORER LES PERFORMANCES ===== */
        @media (prefers-reduced-motion: reduce) {{
            * {{
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }}
        }}
    </style>
    """

    st.markdown(custom_css, unsafe_allow_html=True)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_color_by_performance(value: float, threshold_good: float, threshold_bad: float) -> str:
    """
    Retourne une couleur basée sur la performance

    Args:
        value: Valeur à évaluer
        threshold_good: Seuil pour "bon"
        threshold_bad: Seuil pour "mauvais"

    Returns:
        Couleur appropriée
    """
    if value <= threshold_good:
        return Colors.SUCCESS
    elif value <= threshold_bad:
        return Colors.WARNING
    else:
        return Colors.ERROR


def format_number(value: float, unit: str = "", decimals: int = 2) -> str:
    """
    Formate un nombre avec séparateurs et unité

    Args:
        value: Valeur à formater
        unit: Unité optionnelle
        decimals: Nombre de décimales

    Returns:
        Nombre formaté
    """
    if value >= 1_000_000:
        return f"{value/1_000_000:.{decimals}f}M {unit}".strip()
    elif value >= 1_000:
        return f"{value/1_000:.{decimals}f}K {unit}".strip()
    else:
        return f"{value:.{decimals}f} {unit}".strip()


def get_usage_color(percent: float,
                   threshold_good: float = 60,
                   threshold_bad: float = 85) -> str:
    """
    Retourne une couleur selon le pourcentage d'utilisation système

    Args:
        percent: Pourcentage d'utilisation (0-100)
        threshold_good: Seuil pour "bon" (défaut: 60%)
        threshold_bad: Seuil pour "mauvais" (défaut: 85%)

    Returns:
        Couleur appropriée (SUCCESS, WARNING, ERROR)

    Example:
        >>> get_usage_color(45)
        '#10B981'  # SUCCESS (< 60%)
        >>> get_usage_color(75)
        '#F59E0B'  # WARNING (60-85%)
        >>> get_usage_color(92)
        '#EF4444'  # ERROR (>= 85%)
    """
    if percent < threshold_good:
        return Colors.SUCCESS
    elif percent < threshold_bad:
        return Colors.WARNING
    else:
        return Colors.ERROR


def get_navbar_logo_css(logo_base64: str) -> str:
    """
    Génère le CSS pour intégrer le logo dans la navbar via pseudo-élément

    Args:
        logo_base64: Logo encodé en base64 (data URI)

    Returns:
        CSS pour pseudo-élément ::before avec logo
    """
    if not logo_base64:
        return ""

    return f"""
    <style>
        /* Logo intégré dans navbar via pseudo-élément ::before */
        .stTabs [data-baseweb="tab-list"]::before {{
            content: "";
            position: absolute;
            left: {Spacing.XL};
            top: 50%;
            transform: translateY(-50%);
            width: 50px;
            height: 50px;
            background: url('{logo_base64}') no-repeat center;
            background-size: contain;
            z-index: {Layout.NAVBAR_Z_INDEX};
        }}

        /* Décalage des tabs pour laisser place au logo */
        .stTabs [data-baseweb="tab-list"] {{
            padding-left: calc({Spacing.XL} + 70px) !important;
        }}
    </style>
    """


# ============================================================================
# API PUBLIQUE
# ============================================================================

__all__ = [
    # Tokens de design
    'Colors',
    'Typography',
    'Spacing',
    'Effects',
    'Layout',
    # Composants UI
    'create_card',
    'create_metric_card',
    'create_status_badge',
    'create_alert',
    'create_divider',
    # CSS
    'apply_custom_css',
    'get_navbar_logo_css',
    # Helpers
    'get_color_by_performance',
    'get_usage_color',
    'format_number'
]