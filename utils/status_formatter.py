"""
Module de formatage professionnel des statuts et messages
Compatible mode académique (publications) et mode interactif (démos)

Auteur: Plateforme SPARQL Performance Testing v2.0
Usage: Remplace les emojis par des symboles Unicode professionnels
"""

from typing import Literal, Dict

# Type hints pour les statuts disponibles
StatusType = Literal["success", "error", "warning", "info", "online", "offline"]

# Symboles Unicode professionnels (standards IEEE/ACM/ISO)
STATUS_SYMBOLS: Dict[str, str] = {
    "success": "✓",    # U+2713 - Check mark (standard IEEE)
    "error": "✗",      # U+2717 - Ballot X (standard IEEE)
    "warning": "⚠",    # U+26A0 - Warning sign (ISO 7010 standard)
    "info": "ⓘ",       # U+24D8 - Circled Latin small letter I
    "online": "●",     # U+25CF - Black circle
    "offline": "●"     # U+25CF - Black circle
}

# Texte académique strict (pour exports/publications)
STATUS_TEXT: Dict[str, str] = {
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "warning": "[WARNING]",
    "info": "[INFO]",
    "online": "[ONLINE]",
    "offline": "[OFFLINE]"
}

# Configuration globale du mode d'affichage
DISPLAY_MODE = "interactive"  # ou "publication"


def set_display_mode(mode: Literal["interactive", "publication"]) -> None:
    """
    Configure le mode d'affichage global

    Args:
        mode: 'interactive' pour interface web, 'publication' pour exports académiques
    """
    global DISPLAY_MODE
    DISPLAY_MODE = mode


def format_status(
    status: StatusType,
    message: str,
    mode: str = None
) -> str:
    """
    Formate un message avec indicateur professionnel

    Args:
        status: Type de statut ('success', 'error', 'warning', etc.)
        message: Message à afficher
        mode: Mode d'affichage ('interactive' ou 'publication')
              Si None, utilise le mode global DISPLAY_MODE

    Returns:
        Message formaté professionnellement

    Examples:
        >>> format_status("success", "Test completed")
        '✓ Test completed'

        >>> format_status("error", "Connection failed", mode="publication")
        '[ERROR] Connection failed'
    """
    display_mode = mode if mode is not None else DISPLAY_MODE

    if display_mode == "publication":
        prefix = STATUS_TEXT.get(status, "[INFO]")
    else:
        prefix = STATUS_SYMBOLS.get(status, "")

    return f"{prefix} {message}" if prefix else message


def format_connectivity_status(is_online: bool, endpoint_name: str = "Endpoint") -> str:
    """
    Formate le statut de connectivité d'un endpoint

    Args:
        is_online: True si l'endpoint est accessible
        endpoint_name: Nom de l'endpoint (optionnel)

    Returns:
        Message formaté de statut de connectivité
    """
    if is_online:
        return format_status("online", f"{endpoint_name} accessible")
    else:
        return format_status("offline", f"{endpoint_name} unreachable")


def format_percentage(value: float, label: str = "", threshold_warning: float = 80.0) -> str:
    """
    Formate un pourcentage avec indicateur de statut automatique

    Args:
        value: Valeur du pourcentage (0-100)
        label: Label optionnel
        threshold_warning: Seuil en dessous duquel afficher un warning

    Returns:
        Message formaté avec indicateur approprié
    """
    text = f"{label} {value:.1f}%" if label else f"{value:.1f}%"

    if value >= threshold_warning:
        return format_status("success", text)
    elif value >= 50:
        return format_status("warning", text)
    else:
        return format_status("error", text)


def format_count(count: int, item_name: str = "items", status: StatusType = "info") -> str:
    """
    Formate un compteur avec formatage des milliers

    Args:
        count: Nombre à formater
        item_name: Nom des items (singulier ou pluriel géré automatiquement)
        status: Type de statut à utiliser

    Returns:
        Message formaté avec nombre et unité

    Example:
        >>> format_count(1000000, "triplets", "success")
        '✓ 1,000,000 triplets'
    """
    # Gestion pluriel basique (ajoute 's' si > 1 et pas déjà au pluriel)
    if count != 1 and not item_name.endswith('s'):
        item_name += 's'

    formatted_count = f"{count:,}".replace(",", " ")  # Format français avec espaces
    message = f"{formatted_count} {item_name}"

    return format_status(status, message)


def get_tab_symbols() -> Dict[str, str]:
    """
    Retourne les symboles Unicode professionnels pour les onglets d'interface

    Returns:
        Dictionnaire de symboles pour chaque type d'onglet
    """
    return {
        "configuration": "⚙",  # U+2699 - Gear
        "results": "□",        # U+25A1 - White square
        "visualization": "▣",  # U+25A3 - White square containing black small square
        "export": "⎙",         # U+2399 - Print screen symbol
        "execution": "▶",      # U+25B6 - Black right-pointing triangle
        "analysis": "◈",       # U+25C8 - White diamond containing black small diamond
        "settings": "⚙",       # U+2699 - Gear
        "help": "?",           # Standard question mark
        "sync": "⇄"            # U+21C4 - Rightwards arrow over leftwards arrow
    }


def format_tab_name(tab_type: str, label: str) -> str:
    """
    Formate le nom d'un onglet avec symbole professionnel

    Args:
        tab_type: Type d'onglet (clé dans get_tab_symbols())
        label: Label textuel de l'onglet

    Returns:
        Nom d'onglet formaté avec symbole

    Example:
        >>> format_tab_name("configuration", "Configuration")
        '⚙ Configuration'
    """
    symbols = get_tab_symbols()
    symbol = symbols.get(tab_type, "")
    return f"{symbol} {label}" if symbol else label


# Raccourcis pour les cas d'usage courants
def success(message: str) -> str:
    """Raccourci pour format_status('success', message)"""
    return format_status("success", message)


def error(message: str) -> str:
    """Raccourci pour format_status('error', message)"""
    return format_status("error", message)


def warning(message: str) -> str:
    """Raccourci pour format_status('warning', message)"""
    return format_status("warning", message)


def info(message: str) -> str:
    """Raccourci pour format_status('info', message)"""
    return format_status("info", message)


# Export des fonctions principales
__all__ = [
    'format_status',
    'format_connectivity_status',
    'format_percentage',
    'format_count',
    'format_tab_name',
    'get_tab_symbols',
    'set_display_mode',
    'success',
    'error',
    'warning',
    'info',
    'STATUS_SYMBOLS',
    'STATUS_TEXT'
]
