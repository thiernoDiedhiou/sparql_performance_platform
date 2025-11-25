"""
UI Components Module - SPARQL Performance Platform

Composants d'interface réutilisables pour l'application.

Composants disponibles:
- navbar_custom: Barre de navigation professionnelle (HTML/CSS custom)
- navbar_simple: Barre de navigation simple (streamlit-option-menu) [optionnel]
"""

# Composants de navigation (v3.1.3+)
from ui.components.navbar_custom import render_custom_navbar, CustomNavbar

# Version simple (optionnelle - nécessite streamlit-option-menu)
try:
    from ui.components.navbar_simple import (
        render_simple_navbar,
        render_simple_navbar_with_logo
    )
    NAVBAR_SIMPLE_AVAILABLE = True
except ImportError:
    NAVBAR_SIMPLE_AVAILABLE = False
    # streamlit-option-menu non installé

__all__ = [
    # Navigation (custom - toujours disponible)
    'render_custom_navbar',
    'CustomNavbar',

    # Navigation (simple - si streamlit-option-menu installé)
    'render_simple_navbar',
    'render_simple_navbar_with_logo',
    'NAVBAR_SIMPLE_AVAILABLE',
]

__version__ = '3.1.3'
