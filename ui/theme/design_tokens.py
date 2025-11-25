"""
Design Tokens - Constantes de design de SPARQL Performance Platform

Responsabilité : Définir UNIQUEMENT les constantes de design (couleurs, typographie, espacements, effets, layout)
Pas de logique, pas de fonctions, uniquement des classes de constantes.

VERSION 3.4 - Architecture refactorisée selon le principe SRP
"""


# ============================================================================
# PALETTE DE COULEURS PROFESSIONNELLE
# ============================================================================

class Colors:
    """Palette de couleurs cohérente inspirée des meilleures pratiques UI/UX"""

    # Couleurs primaires
    PRIMARY = "#0066CC"           # Bleu professionnel (principal)
    PRIMARY_DARK = "#004C99"      # Bleu foncé (hover, emphasis)
    PRIMARY_LIGHT = "#3385DB"     # Bleu clair (backgrounds)
    PRIMARY_PALE = "#E6F2FF"      # Bleu très pâle (cards, sections)

    # Couleurs secondaires
    SECONDARY = "#7C3AED"         # Violet moderne (accents)
    SECONDARY_DARK = "#5B21B6"    # Violet foncé
    SECONDARY_LIGHT = "#A78BFA"   # Violet clair
    SECONDARY_PALE = "#F5F3FF"    # Violet très pâle

    # Couleurs de succès
    SUCCESS = "#10B981"           # Vert succès
    SUCCESS_DARK = "#059669"      # Vert foncé
    SUCCESS_LIGHT = "#34D399"     # Vert clair
    SUCCESS_PALE = "#D1FAE5"      # Vert pâle

    # Couleurs d'avertissement
    WARNING = "#F59E0B"           # Orange warning
    WARNING_DARK = "#D97706"      # Orange foncé
    WARNING_LIGHT = "#FBBF24"     # Orange clair
    WARNING_PALE = "#FEF3C7"      # Orange pâle

    # Couleurs d'erreur
    ERROR = "#EF4444"             # Rouge erreur
    ERROR_DARK = "#DC2626"        # Rouge foncé
    ERROR_LIGHT = "#F87171"       # Rouge clair
    ERROR_PALE = "#FEE2E2"        # Rouge pâle

    # Couleurs d'information
    INFO = "#3B82F6"              # Bleu info
    INFO_DARK = "#2563EB"         # Bleu info foncé
    INFO_LIGHT = "#60A5FA"        # Bleu info clair
    INFO_PALE = "#DBEAFE"         # Bleu info pâle

    # Couleurs neutres (gris)
    GRAY_900 = "#111827"          # Presque noir (texte principal)
    GRAY_800 = "#1F2937"          # Gris très foncé
    GRAY_700 = "#374151"          # Gris foncé (texte secondaire)
    GRAY_600 = "#4B5563"          # Gris moyen-foncé
    GRAY_500 = "#6B7280"          # Gris moyen
    GRAY_400 = "#9CA3AF"          # Gris moyen-clair
    GRAY_300 = "#D1D5DB"          # Gris clair (borders)
    GRAY_200 = "#E5E7EB"          # Gris très clair
    GRAY_100 = "#F3F4F6"          # Gris ultra-clair (backgrounds)
    GRAY_50 = "#F9FAFB"           # Presque blanc

    # Couleurs spécifiques aux triplestores
    VIRTUOSO = "#E11D48"          # Rouge Virtuoso
    VIRTUOSO_LIGHT = "#FDA4AF"    # Rouge clair Virtuoso
    FUSEKI = "#0891B2"            # Cyan Fuseki
    FUSEKI_LIGHT = "#67E8F9"      # Cyan clair Fuseki

    # Backgrounds
    BG_PRIMARY = "#FFFFFF"        # Blanc pur
    BG_SECONDARY = "#F9FAFB"      # Gris ultra-clair
    BG_CARD = "#FFFFFF"           # Blanc pour cards
    BG_SIDEBAR = "#F3F4F6"        # Gris clair pour sidebar

    # Textes
    TEXT_PRIMARY = "#111827"      # Texte principal
    TEXT_SECONDARY = "#6B7280"    # Texte secondaire
    TEXT_DISABLED = "#9CA3AF"     # Texte désactivé
    TEXT_ON_PRIMARY = "#FFFFFF"   # Texte sur couleur primaire
    TEXT_ON_PRIMARY_MUTED = "rgba(255, 255, 255, 0.8)"      # Texte sur primaire (atténué)
    TEXT_ON_PRIMARY_SECONDARY = "rgba(255, 255, 255, 0.85)" # Texte sur primaire (secondaire)

    # Overlays et transparences
    OVERLAY_LIGHT = "rgba(255, 255, 255, 0.15)"    # Overlay blanc léger
    OVERLAY_MEDIUM = "rgba(255, 255, 255, 0.3)"    # Overlay blanc moyen
    OVERLAY_DARK = "rgba(0, 0, 0, 0.1)"            # Overlay noir léger


# ============================================================================
# TYPOGRAPHIE
# ============================================================================

class Typography:
    """Système typographique cohérent"""

    # Tailles de police
    SIZE_DISPLAY = "3rem"         # 48px - Titres principaux
    SIZE_H1 = "2.25rem"           # 36px - H1
    SIZE_H2 = "1.875rem"          # 30px - H2
    SIZE_H3 = "1.5rem"            # 24px - H3
    SIZE_H4 = "1.25rem"           # 20px - H4
    SIZE_H5 = "1.125rem"          # 18px - H5
    SIZE_BODY_LARGE = "1.125rem"  # 18px - Corps large
    SIZE_BODY = "1rem"            # 16px - Corps normal
    SIZE_BODY_SMALL = "0.875rem"  # 14px - Corps petit
    SIZE_CAPTION = "0.75rem"      # 12px - Légendes

    # Poids de police
    WEIGHT_LIGHT = "300"
    WEIGHT_REGULAR = "400"
    WEIGHT_MEDIUM = "500"
    WEIGHT_SEMIBOLD = "600"
    WEIGHT_BOLD = "700"
    WEIGHT_EXTRABOLD = "800"

    # Hauteur de ligne
    LINE_HEIGHT_TIGHT = "1.2"
    LINE_HEIGHT_NORMAL = "1.5"
    LINE_HEIGHT_RELAXED = "1.75"
    LINE_HEIGHT_LOOSE = "2"


# ============================================================================
# ESPACEMENTS
# ============================================================================

class Spacing:
    """Système d'espacement cohérent (basé sur 4px)"""

    XS = "0.25rem"    # 4px
    SM = "0.5rem"     # 8px
    MD = "1rem"       # 16px
    LG = "1.5rem"     # 24px
    XL = "2rem"       # 32px
    XXL = "3rem"      # 48px
    XXXL = "4rem"     # 64px


# ============================================================================
# BORDERS & SHADOWS
# ============================================================================

class Effects:
    """Effets visuels (ombres, bordures, rayons)"""

    # Border radius
    RADIUS_NONE = "0"
    RADIUS_SM = "0.25rem"     # 4px
    RADIUS_MD = "0.5rem"      # 8px
    RADIUS_LG = "0.75rem"     # 12px
    RADIUS_XL = "1rem"        # 16px
    RADIUS_FULL = "9999px"    # Arrondi complet

    # Box shadows
    SHADOW_NONE = "none"
    SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    SHADOW_XL = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"

    # Border widths
    BORDER_THIN = "1px"
    BORDER_MEDIUM = "2px"
    BORDER_THICK = "4px"


# ============================================================================
# LAYOUT & NAVIGATION
# ============================================================================

class Layout:
    """Constantes de layout et navigation"""

    # Navbar
    NAVBAR_HEIGHT = "80px"
    NAVBAR_Z_INDEX = "1001"  # Navbar au-dessus de tout
    NAVBAR_GRADIENT = f"linear-gradient(135deg, {Colors.PRIMARY} 0%, {Colors.PRIMARY_DARK} 100%)"

    # Tabs
    TABS_HEIGHT = "50px"
    TABS_TOP_OFFSET = "80px"  # Juste en dessous de la navbar
    TABS_Z_INDEX = "1000"     # Tabs juste en dessous de navbar

    # Autres éléments
    SIDEBAR_Z_INDEX = "999"   # Sidebar en arrière-plan
    MODAL_Z_INDEX = "2000"    # Modals au-dessus de navbar

    # Container
    CONTAINER_MAX_WIDTH = "1400px"
    CONTAINER_MAX_WIDTH_FULL = "100%"
