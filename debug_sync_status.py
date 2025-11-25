"""
Script de debug pour verifier le statut de synchronisation
"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from utils.data_synchronizer_v2 import DataSynchronizer
from utils.dataset_manager import DatasetManager
from utils.helpers import format_sync_status

VIRTUOSO_ENDPOINT = "http://localhost:8890/sparql"
FUSEKI_ENDPOINT = "http://localhost:3030/dataset/query"

def main():
    print("="*80)
    print("DEBUG: Verification du statut de synchronisation")
    print("="*80)

    try:
        # Initialiser le synchroniseur
        synchronizer = DataSynchronizer(VIRTUOSO_ENDPOINT, FUSEKI_ENDPOINT)

        # Charger les metadonnees
        dataset_manager = DatasetManager(datasets_path="datasets")
        metadata = dataset_manager.load_all_metadata()

        print("\n[METADATA] Metadonnees chargees:")
        print(f"   Virtuoso: {metadata.get('virtuoso', {})}")
        print(f"   Fuseki: {metadata.get('fuseki', {})}")

        virtuoso_graph_uri = metadata.get('virtuoso', {}).get('graph_uri') if metadata else None
        fuseki_graph_uri = metadata.get('fuseki', {}).get('graph_uri') if metadata else None

        print(f"\n[GRAPH_URI] Graph URIs:")
        print(f"   Virtuoso: {virtuoso_graph_uri}")
        print(f"   Fuseki: {fuseki_graph_uri}")

        # Compter les triplets SANS graphe nomme (ancien comportement)
        print("\n[COUNT_GLOBAL] Comptage SANS graphe nomme (ancien comportement):")
        v_count_global = synchronizer.count_triplets(VIRTUOSO_ENDPOINT)
        f_count_global = synchronizer.count_triplets(FUSEKI_ENDPOINT)
        print(f"   Virtuoso global: {v_count_global:,} triplets")
        print(f"   Fuseki global: {f_count_global:,} triplets")

        # Compter les triplets AVEC graphe nomme (nouveau comportement)
        print("\n[COUNT_GRAPH] Comptage AVEC graphe nomme (nouveau comportement):")
        v_count = synchronizer.count_triplets(VIRTUOSO_ENDPOINT, virtuoso_graph_uri)
        f_count = synchronizer.count_triplets(FUSEKI_ENDPOINT, fuseki_graph_uri)
        print(f"   Virtuoso dans graphe: {v_count:,} triplets")
        print(f"   Fuseki dans graphe: {f_count:,} triplets")

        # Analyser le statut
        print("\n[ANALYSIS] Analyse du statut:")
        print(f"   v_count == f_count: {v_count == f_count}")
        print(f"   v_count > 0: {v_count > 0}")
        print(f"   f_count > 0: {f_count > 0}")

        # Appeler format_sync_status
        status_info = format_sync_status(v_count, f_count)

        print("\n[FORMAT_SYNC] Resultat de format_sync_status:")
        print(f"   synchronized: {status_info['synchronized']}")
        print(f"   message: {status_info['message']}")
        print(f"   action_needed: {status_info['action_needed']}")
        print(f"   icon: {status_info['icon']}")

        # Construire le resultat final
        result = {
            "status": "synchronized" if status_info["synchronized"] else "not_synchronized",
            "message": status_info["message"],
            "action_needed": status_info["action_needed"],
            "virtuoso_count": v_count,
            "fuseki_count": f_count,
            "can_test": status_info["synchronized"] and v_count > 0
        }

        print("\n[FINAL_RESULT] Resultat final (get_sync_status_summary):")
        for key, value in result.items():
            print(f"   {key}: {value}")

        # Diagnostic
        print("\n[DIAGNOSTIC] Diagnostic:")
        if v_count == f_count and v_count > 0:
            print("   [OK] Les datasets DEVRAIENT etre consideres comme synchronises")
            if not status_info["synchronized"]:
                print("   [ERROR] PROBLEME: format_sync_status retourne synchronized=False !")
        else:
            print(f"   [WARNING] Les datasets ne sont pas synchronises")
            print(f"      Virtuoso: {v_count:,}, Fuseki: {f_count:,}")
            print(f"      Difference: {abs(v_count - f_count):,} triplets")

    except Exception as e:
        print(f"\n[ERROR] Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
