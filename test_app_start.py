"""
Script de test pour vérifier que l'application peut démarrer
"""

import sys

print("="*80)
print("TEST DE DEMARRAGE DE L'APPLICATION")
print("="*80)
print()

# Test 1: Import config
print("[1/5] Test import config...")
try:
    from config import settings
    print("  OK: Module config importe")
except Exception as e:
    print(f"  ERREUR: {e}")
    sys.exit(1)

# Test 2: Import core
print("[2/5] Test import core.executor...")
try:
    from core.executor import QueryExecutor
    print("  OK: Module core.executor importe")
except Exception as e:
    print(f"  ERREUR: {e}")
    sys.exit(1)

# Test 3: Import UI sidebar
print("[3/5] Test import ui.sidebar...")
try:
    from ui.sidebar import render_sidebar
    print("  OK: Module ui.sidebar importe")
except Exception as e:
    print(f"  ERREUR: {e}")
    sys.exit(1)

# Test 4: Import UI tabs
print("[4/5] Test import ui.tabs...")
try:
    from ui.tabs.configuration_tab import render_configuration_tab
    print("  OK: Module ui.tabs.configuration_tab importe")
except Exception as e:
    print(f"  ERREUR: {e}")
    sys.exit(1)

# Test 5: Test validation sécurité
print("[5/5] Test validation securite...")
try:
    executor = QueryExecutor()
    result = executor.validate_query_security("SELECT * WHERE { ?s ?p ?o } LIMIT 10")
    if result['valid']:
        print("  OK: Validation securite fonctionne")
    else:
        print(f"  ERREUR: Validation a echoue: {result['error']}")
        sys.exit(1)
except Exception as e:
    print(f"  ERREUR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("="*80)
print("SUCCESS: Tous les tests sont passes !")
print("L'application est prete a demarrer.")
print()
print("Lancer avec:")
print("  streamlit run main.py")
print("="*80)
