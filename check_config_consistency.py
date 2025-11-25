"""
Script de verification de la coherence de la configuration
Verifie que toutes les valeurs par defaut sont coherentes entre :
- config/settings.py
- config/env_loader.py
- .env.example
"""

import sys
import io
import re
from typing import Dict, List, Tuple

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def extract_from_settings() -> Dict[str, any]:
    """Extrait les valeurs de config/settings.py"""
    values = {}

    with open('config/settings.py', 'r', encoding='utf-8') as f:
        content = f.read()

        # Expressions regulieres pour extraire les valeurs
        patterns = {
            'SYNC_CHUNK_SIZE': r'SYNC_CHUNK_SIZE\s*=\s*(\d+)',
            'DEFAULT_NUM_ITERATIONS': r'DEFAULT_NUM_ITERATIONS\s*=\s*(\d+)',
            'DEFAULT_WARMUP_ITERATIONS': r'DEFAULT_WARMUP_ITERATIONS\s*=\s*(\d+)',
            'QUERY_TIMEOUT': r'QUERY_TIMEOUT\s*=\s*(\d+)',
            'CONNECTIVITY_TIMEOUT': r'CONNECTIVITY_TIMEOUT\s*=\s*(\d+)',
            'SYNCHRONIZATION_TIMEOUT': r'SYNCHRONIZATION_TIMEOUT\s*=\s*(\d+)',
            'MAX_SYNC_TRIPLETS': r'MAX_SYNC_TRIPLETS\s*=\s*(\d+)',
            'DEFAULT_VIRTUOSO_ENDPOINT': r'DEFAULT_VIRTUOSO_ENDPOINT\s*=\s*"([^"]+)"',
            'DEFAULT_FUSEKI_ENDPOINT': r'DEFAULT_FUSEKI_ENDPOINT\s*=\s*"([^"]+)"',
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                value = match.group(1)
                # Convertir en int si c'est un nombre
                if key not in ['DEFAULT_VIRTUOSO_ENDPOINT', 'DEFAULT_FUSEKI_ENDPOINT']:
                    value = int(value)
                values[key] = value

    return values


def extract_from_env_loader() -> Dict[str, any]:
    """Extrait les valeurs par defaut de config/env_loader.py"""
    values = {}

    with open('config/env_loader.py', 'r', encoding='utf-8') as f:
        content = f.read()

        # Patterns pour get_env avec valeurs par defaut
        patterns = {
            'SYNC_CHUNK_SIZE': r'"sync_chunk_size":\s*get_env\("SYNC_CHUNK_SIZE",\s*(\d+)',
            'DEFAULT_NUM_ITERATIONS': r'"num_iterations":\s*get_env\("DEFAULT_NUM_ITERATIONS",\s*(\d+)',
            'DEFAULT_WARMUP_ITERATIONS': r'"warmup_iterations":\s*get_env\("DEFAULT_WARMUP_ITERATIONS",\s*(\d+)',
            'QUERY_TIMEOUT': r'"query_timeout":\s*get_env\("QUERY_TIMEOUT",\s*(\d+)',
            'CONNECTIVITY_TIMEOUT': r'"connectivity_timeout":\s*get_env\("CONNECTIVITY_TIMEOUT",\s*(\d+)',
            'SYNCHRONIZATION_TIMEOUT': r'"synchronization_timeout":\s*get_env\("SYNCHRONIZATION_TIMEOUT",\s*(\d+)',
            'MAX_SYNC_TRIPLETS': r'"max_sync_triplets":\s*get_env\("MAX_SYNC_TRIPLETS",\s*(\d+)',
            'DEFAULT_VIRTUOSO_ENDPOINT': r'"virtuoso_endpoint":\s*get_env\("VIRTUOSO_ENDPOINT",\s*"([^"]+)"',
            'DEFAULT_FUSEKI_ENDPOINT': r'"fuseki_endpoint":\s*get_env\("FUSEKI_ENDPOINT",\s*"([^"]+)"',
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                value = match.group(1)
                # Convertir en int si c'est un nombre
                if key not in ['DEFAULT_VIRTUOSO_ENDPOINT', 'DEFAULT_FUSEKI_ENDPOINT']:
                    value = int(value)
                values[key] = value

    return values


def extract_from_env_example() -> Dict[str, any]:
    """Extrait les valeurs de .env.example"""
    values = {}

    with open('.env.example', 'r', encoding='utf-8') as f:
        content = f.read()

        patterns = {
            'SYNC_CHUNK_SIZE': r'^SYNC_CHUNK_SIZE=(\d+)',
            'DEFAULT_NUM_ITERATIONS': r'^DEFAULT_NUM_ITERATIONS=(\d+)',
            'DEFAULT_WARMUP_ITERATIONS': r'^DEFAULT_WARMUP_ITERATIONS=(\d+)',
            'QUERY_TIMEOUT': r'^QUERY_TIMEOUT=(\d+)',
            'CONNECTIVITY_TIMEOUT': r'^CONNECTIVITY_TIMEOUT=(\d+)',
            'SYNCHRONIZATION_TIMEOUT': r'^SYNCHRONIZATION_TIMEOUT=(\d+)',
            'MAX_SYNC_TRIPLETS': r'^MAX_SYNC_TRIPLETS=(\d+)',
            'DEFAULT_VIRTUOSO_ENDPOINT': r'^VIRTUOSO_ENDPOINT=(.+)$',
            'DEFAULT_FUSEKI_ENDPOINT': r'^FUSEKI_ENDPOINT=(.+)$',
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                value = match.group(1).strip()
                # Convertir en int si c'est un nombre
                if key not in ['DEFAULT_VIRTUOSO_ENDPOINT', 'DEFAULT_FUSEKI_ENDPOINT']:
                    value = int(value)
                values[key] = value

    return values


def compare_values(settings: Dict, env_loader: Dict, env_example: Dict) -> Tuple[List[str], List[str]]:
    """Compare les valeurs entre les trois sources"""
    errors = []
    warnings = []

    # Toutes les cles
    all_keys = set(settings.keys()) | set(env_loader.keys()) | set(env_example.keys())

    for key in sorted(all_keys):
        s_val = settings.get(key)
        e_val = env_loader.get(key)
        ex_val = env_example.get(key)

        # Verifier la coherence
        values = [v for v in [s_val, e_val, ex_val] if v is not None]

        if len(set(map(str, values))) > 1:
            # Valeurs differentes trouvees
            error_msg = f"INCOHERENCE: {key}"
            if s_val is not None:
                error_msg += f"\n  settings.py: {s_val}"
            if e_val is not None:
                error_msg += f"\n  env_loader.py: {e_val}"
            if ex_val is not None:
                error_msg += f"\n  .env.example: {ex_val}"

            errors.append(error_msg)
        else:
            # Valeurs coherentes
            if s_val is not None:
                warnings.append(f"OK: {key} = {s_val}")

    return errors, warnings


def main():
    print("=" * 80)
    print("VERIFICATION DE LA COHERENCE DE LA CONFIGURATION")
    print("=" * 80)

    print("\n[1/3] Extraction depuis config/settings.py...")
    settings = extract_from_settings()
    print(f"   {len(settings)} valeurs extraites")

    print("\n[2/3] Extraction depuis config/env_loader.py...")
    env_loader = extract_from_env_loader()
    print(f"   {len(env_loader)} valeurs extraites")

    print("\n[3/3] Extraction depuis .env.example...")
    env_example = extract_from_env_example()
    print(f"   {len(env_example)} valeurs extraites")

    print("\n" + "=" * 80)
    print("COMPARAISON DES VALEURS")
    print("=" * 80)

    errors, ok_values = compare_values(settings, env_loader, env_example)

    if errors:
        print(f"\n ERREURS TROUVEES ({len(errors)}):\n")
        for error in errors:
            print(f"  {error}\n")
    else:
        print("\n AUCUNE INCOHERENCE TROUVEE")

    print(f"\n VALEURS COHERENTES ({len(ok_values)}):\n")
    for ok in ok_values:
        print(f"  {ok}")

    print("\n" + "=" * 80)

    if errors:
        print(f"RESULTAT: ECHEC - {len(errors)} incoherence(s) trouvee(s)")
        print("=" * 80)
        sys.exit(1)
    else:
        print("RESULTAT: SUCCES - Toutes les valeurs sont coherentes")
        print("=" * 80)
        sys.exit(0)


if __name__ == "__main__":
    main()
