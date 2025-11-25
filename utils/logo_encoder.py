"""
Utilitaire pour encoder le logo en base64 pour utilisation CSS
Avec cache LRU et détection automatique du format d'image
"""
import base64
from pathlib import Path
from functools import lru_cache
from typing import Optional


# Mapping des extensions vers MIME types
MIME_TYPES = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.webp': 'image/webp'
}


@lru_cache(maxsize=10)
def encode_image_to_base64(image_path: str) -> str:
    """
    Encode une image en base64 avec détection automatique du format

    Args:
        image_path: Chemin vers l'image

    Returns:
        String data URI encodée en base64 ou chaîne vide si erreur

    Raises:
        FileNotFoundError: Si le fichier n'existe pas
        ValueError: Si le format d'image n'est pas supporté
    """
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Image introuvable: {image_path}")

    # Détection automatique du MIME type
    mime_type = MIME_TYPES.get(path.suffix.lower())
    if not mime_type:
        raise ValueError(f"Format d'image non supporté: {path.suffix}. Formats supportés: {list(MIME_TYPES.keys())}")

    try:
        with open(path, "rb") as f:
            image_bytes = f.read()
            image_base64 = base64.b64encode(image_bytes).decode()
            return f"data:{mime_type};base64,{image_base64}"
    except Exception as e:
        raise RuntimeError(f"Erreur lors de l'encodage de l'image: {e}")


def get_logo_base64(logo_path: Optional[str] = None) -> str:
    """
    Convertit le logo en base64 pour intégration CSS

    Args:
        logo_path: Chemin optionnel vers le logo (défaut: images/logo/logo.png)

    Returns:
        String base64 du logo ou chaîne vide si erreur
    """
    if logo_path is None:
        logo_path = "images/logo/logo.png"

    try:
        return encode_image_to_base64(logo_path)
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"Erreur encodage logo: {e}")
        return ""


if __name__ == "__main__":
    # Test
    result = get_logo_base64()
    print(f"Logo encodé : {result[:100]}..." if result else "Erreur")
