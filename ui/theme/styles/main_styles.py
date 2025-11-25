"""
Styles CSS principaux de l'application SPARQL Performance Platform

Responsabilité : Générer le CSS complet de l'application
"""

from ui.theme.design_tokens import Colors, Typography, Spacing, Effects


def generate_main_css() -> str:
    """
    Génère le CSS principal de l'application

    Returns:
        str: CSS complet sous forme de chaîne
    """
    css = f"""
    <style>
        /* ================================================================
           RESET STREAMLIT
        ================================================================ */
        .main .block-container {{
            padding: 0 !important;
            max-width: 100% !important;
        }}

        section.main > div {{
            padding: 0 !important;
            max-width: 100% !important;
        }}

        /* ================================================================
           SIDEBAR ÉLARGIE
        ================================================================ */
        section[data-testid="stSidebar"] {{
            width: 280px !important;
            min-width: 280px !important;
        }}

        section[data-testid="stSidebar"] > div {{
            width: 280px !important;
        }}

        /* ================================================================
           NAVBAR STICKY - AVEC TRANSITION SIDEBAR
        ================================================================ */
        .navbar-header {{
            position: fixed !important;
            top: 0 !important;
            left: 280px !important;
            right: 0 !important;
            z-index: 9999 !important;

            margin: 0 !important;
            padding: {Spacing.LG} {Spacing.XL} !important;

            display: flex !important;
            align-items: center !important;
            gap: {Spacing.MD} !important;

            background: linear-gradient(135deg, {Colors.PRIMARY} 0%, {Colors.PRIMARY_DARK} 100%) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;

            transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }}

        /* CORRECTION : Navbar pleine largeur quand sidebar fermée */
        .main .navbar-header {{
            left: 0 !important;
        }}

        /* Quand sidebar ouverte, navbar décalée */
        section[data-testid="stSidebar"]:not([aria-expanded="false"]) ~ .main .navbar-header {{
            left: 280px !important;
        }}

        .navbar-logo {{
            font-size: 2rem !important;
            animation: pulse 3s ease-in-out infinite !important;
        }}

        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.08); }}
        }}

        .navbar-title {{
            color: {Colors.TEXT_ON_PRIMARY} !important;
            font-size: {Typography.SIZE_H3} !important;
            font-weight: {Typography.WEIGHT_BOLD} !important;
            margin: 0 !important;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        }}

        .navbar-subtitle {{
            color: rgba(255, 255, 255, 0.95) !important;
            font-size: {Typography.SIZE_BODY_SMALL} !important;
            margin: 0 !important;
        }}

        /* ================================================================
           TABS PRINCIPALES - STICKY AVEC TRANSITION
        ================================================================ */
        .stTabs [data-baseweb="tab-list"] {{
            position: fixed !important;
            top: 80px !important;
            left: 280px !important;
            right: 0 !important;
            z-index: 9998 !important;

            margin: 0 !important;
            padding: {Spacing.MD} {Spacing.XL} !important;

            gap: {Spacing.SM} !important;
            background: linear-gradient(135deg, {Colors.PRIMARY} 0%, {Colors.PRIMARY_DARK} 100%) !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;

            transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }}

        /* CORRECTION : Tabs pleine largeur quand sidebar fermée */
        .main .stTabs [data-baseweb="tab-list"] {{
            left: 0 !important;
        }}

        /* Quand sidebar ouverte, tabs décalées */
        section[data-testid="stSidebar"]:not([aria-expanded="false"]) ~ .main .stTabs [data-baseweb="tab-list"] {{
            left: 280px !important;
        }}

        .stTabs [data-baseweb="tab"] {{
            height: 50px !important;
            padding: 0 {Spacing.LG} !important;
            background: rgba(255, 255, 255, 0.12) !important;
            border-radius: {Effects.RADIUS_MD} !important;
            color: rgba(255, 255, 255, 0.88) !important;
            font-weight: {Typography.WEIGHT_MEDIUM} !important;
            border: 1px solid rgba(255, 255, 255, 0.25) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08) !important;
        }}

        .stTabs [data-baseweb="tab"]:hover {{
            background: rgba(255, 255, 255, 0.22) !important;
            color: {Colors.TEXT_ON_PRIMARY} !important;
            transform: translateY(-3px) !important;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15) !important;
        }}

        .stTabs [aria-selected="true"] {{
            background: {Colors.BG_CARD} !important;
            color: {Colors.PRIMARY} !important;
            font-weight: {Typography.WEIGHT_BOLD} !important;
            border-color: {Colors.BG_CARD} !important;
            box-shadow: 0 6px 16px rgba(0, 102, 204, 0.25) !important;
            transform: translateY(-3px) scale(1.02) !important;
        }}

        .stTabs [data-baseweb="tab-highlight"] {{
            background-color: transparent !important;
        }}

        /* ================================================================
           SOUS-TABS - CORRECTION CRITIQUE
        ================================================================ */

        /* Les sous-tabs ne doivent PAS être sticky */
        .stTabs [data-baseweb="tab-panel"] .stTabs [data-baseweb="tab-list"] {{
            position: relative !important;
            top: auto !important;
            left: auto !important;
            right: auto !important;
            z-index: auto !important;

            margin: {Spacing.LG} 0 !important;
            padding: {Spacing.SM} 0 !important;

            background: transparent !important;
            box-shadow: none !important;
            border-bottom: 2px solid {Colors.GRAY_200} !important;
        }}

        /* Styles des sous-tabs */
        .stTabs [data-baseweb="tab-panel"] .stTabs [data-baseweb="tab"] {{
            height: 45px !important;
            padding: 0 {Spacing.LG} !important;
            background: transparent !important;
            border-radius: {Effects.RADIUS_SM} !important;
            color: {Colors.TEXT_SECONDARY} !important;
            font-weight: {Typography.WEIGHT_MEDIUM} !important;
            border: none !important;
            border-bottom: 3px solid transparent !important;
            box-shadow: none !important;
            transform: none !important;
        }}

        .stTabs [data-baseweb="tab-panel"] .stTabs [data-baseweb="tab"]:hover {{
            background: {Colors.GRAY_100} !important;
            color: {Colors.PRIMARY} !important;
            border-bottom-color: {Colors.PRIMARY_LIGHT} !important;
            transform: none !important;
            box-shadow: none !important;
        }}

        .stTabs [data-baseweb="tab-panel"] .stTabs [aria-selected="true"] {{
            background: transparent !important;
            color: {Colors.PRIMARY} !important;
            font-weight: {Typography.WEIGHT_BOLD} !important;
            border-bottom-color: {Colors.PRIMARY} !important;
            box-shadow: none !important;
            transform: none !important;
        }}

        /* ================================================================
           CONTENU - OPTIMISÉ
        ================================================================ */
        .stTabs [data-baseweb="tab-panel"] {{
            background: {Colors.BG_SECONDARY} !important;
            padding: {Spacing.XL} {Spacing.XL} !important;
            margin-top: 165px !important;
            min-height: calc(100vh - 165px) !important;
        }}

        /* Les sous-panels n'ont pas de margin-top */
        .stTabs [data-baseweb="tab-panel"] .stTabs [data-baseweb="tab-panel"] {{
            margin-top: 0 !important;
            padding: {Spacing.LG} 0 !important;
        }}

        /* ================================================================
           BOUTONS SIDEBAR - ULTIMATE
        ================================================================ */
        section[data-testid="stSidebar"] .stButton > button {{
            border-radius: {Effects.RADIUS_LG} !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            font-weight: {Typography.WEIGHT_SEMIBOLD} !important;
            text-align: center !important;
            white-space: pre-line !important;
            box-shadow: {Effects.SHADOW_SM} !important;
        }}

        section[data-testid="stSidebar"] .stButton > button:hover {{
            transform: translateY(-3px) scale(1.02) !important;
            box-shadow: 0 6px 16px rgba(0, 102, 204, 0.25) !important;
        }}

        section[data-testid="stSidebar"] .stButton > button:active {{
            transform: translateY(-1px) scale(0.98) !important;
        }}

        /* ================================================================
           SCROLLBAR PERSONNALISÉE
        ================================================================ */
        ::-webkit-scrollbar {{
            width: 12px;
            height: 12px;
        }}

        ::-webkit-scrollbar-track {{
            background: {Colors.GRAY_100};
            border-radius: {Effects.RADIUS_MD};
        }}

        ::-webkit-scrollbar-thumb {{
            background: linear-gradient(135deg, {Colors.PRIMARY_LIGHT} 0%, {Colors.PRIMARY} 100%);
            border-radius: {Effects.RADIUS_FULL};
            border: 2px solid {Colors.GRAY_100};
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: linear-gradient(135deg, {Colors.PRIMARY} 0%, {Colors.PRIMARY_DARK} 100%);
        }}

        /* ================================================================
           FOCUS VISIBLE (ACCESSIBILITÉ)
        ================================================================ */
        *:focus-visible {{
            outline: 3px solid {Colors.PRIMARY} !important;
            outline-offset: 3px !important;
            border-radius: {Effects.RADIUS_SM} !important;
        }}

        /* ================================================================
           ANIMATIONS GLOBALES
        ================================================================ */
        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .element-container {{
            animation: fadeIn 0.4s ease-out !important;
        }}

        /* ================================================================
           RESPONSIVE
        ================================================================ */
        @media (max-width: 768px) {{
            .navbar-header {{
                left: 0 !important;
            }}

            .stTabs [data-baseweb="tab-list"] {{
                left: 0 !important;
            }}
        }}
    </style>
    """

    return css
