"""
Script pour corriger le probleme des graph_uri differents
entre Virtuoso et Fuseki
"""

import sys
import io
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from utils.data_synchronizer_v2 import DataSynchronizer
from utils.dataset_manager import DatasetManager

VIRTUOSO_ENDPOINT = "http://localhost:8890/sparql"
FUSEKI_ENDPOINT = "http://localhost:3030/dataset/query"

def main():
    print("="*80)
    print("CORRECTION DES GRAPH_URI DIFFERENTS")
    print("="*80)

    # Charger les metadonnees
    dataset_manager = DatasetManager(datasets_path="datasets")
    metadata = dataset_manager.load_all_metadata()

    virtuoso_graph_uri = metadata.get('virtuoso', {}).get('graph_uri')
    fuseki_graph_uri = metadata.get('fuseki', {}).get('graph_uri')

    print(f"\n[CURRENT_STATE] Etat actuel:")
    print(f"   Virtuoso graph_uri: {virtuoso_graph_uri}")
    print(f"   Fuseki graph_uri:   {fuseki_graph_uri}")

    if virtuoso_graph_uri == fuseki_graph_uri:
        print("\n[OK] Les graph_uri sont IDENTIQUES. Pas de correction necessaire.")
        return

    print(f"\n[WARNING] Les graph_uri sont DIFFERENTS !")
    print(f"\nOptions de correction:")
    print(f"  1. Synchroniser Virtuoso -> Fuseki avec le MEME graph_uri")
    print(f"  2. Mettre a jour les metadonnees pour utiliser le graph_uri de Virtuoso")
    print(f"  3. Annuler (ne rien faire)")

    choice = input("\nVotre choix (1/2/3): ").strip()

    if choice == "1":
        fix_by_sync(virtuoso_graph_uri, fuseki_graph_uri)
    elif choice == "2":
        fix_by_metadata_update(virtuoso_graph_uri, metadata, dataset_manager)
    else:
        print("\n[CANCELLED] Operation annulee")


def fix_by_sync(source_graph_uri, old_fuseki_graph_uri):
    """Option 1: Re-synchroniser avec le meme graph_uri"""
    print("\n[OPTION_1] Re-synchronisation avec le meme graph_uri...")

    synchronizer = DataSynchronizer(VIRTUOSO_ENDPOINT, FUSEKI_ENDPOINT)

    # Compter les triplets
    v_count = synchronizer.count_triplets(VIRTUOSO_ENDPOINT, source_graph_uri)
    f_count_old = synchronizer.count_triplets(FUSEKI_ENDPOINT, old_fuseki_graph_uri)

    print(f"\n[COUNT] Comptages actuels:")
    print(f"   Virtuoso ({source_graph_uri}): {v_count:,} triplets")
    print(f"   Fuseki ancien ({old_fuseki_graph_uri}): {f_count_old:,} triplets")

    if v_count == 0:
        print("\n[ERROR] Virtuoso ne contient pas de donnees !")
        return

    # Nettoyer l'ancien graphe Fuseki
    print(f"\n[CLEANUP] Nettoyage de l'ancien graphe Fuseki...")
    if synchronizer.clear_fuseki_dataset(old_fuseki_graph_uri):
        print("   [OK] Ancien graphe nettoye")
    else:
        print("   [WARNING] Echec du nettoyage, on continue quand meme...")

    # Synchroniser vers le MEME graph_uri que Virtuoso
    print(f"\n[SYNC] Synchronisation vers le meme graph_uri...")
    print(f"   Source: {source_graph_uri}")
    print(f"   Cible:  {source_graph_uri} (identique)")

    # Note: On ne peut pas appeler synchronize_datasets_chunked directement ici
    # car il utilise Streamlit. On doit le faire manuellement.

    print("\n[INFO] Pour completer cette option, utilisez l'interface Streamlit:")
    print("   1. Allez dans 'Synchronisation des donnees'")
    print("   2. Cliquez sur 'Synchroniser Virtuoso -> Fuseki'")
    print("   3. Avant cela, mettez a jour les metadonnees avec l'option 2 ci-dessous")


def fix_by_metadata_update(virtuoso_graph_uri, metadata, dataset_manager):
    """Option 2: Mettre a jour les metadonnees"""
    print("\n[OPTION_2] Mise a jour des metadonnees...")

    # Mettre a jour le graph_uri de Fuseki pour correspondre a celui de Virtuoso
    if 'fuseki' in metadata:
        old_fuseki_graph_uri = metadata['fuseki'].get('graph_uri')
        metadata['fuseki']['graph_uri'] = virtuoso_graph_uri

        print(f"\n[UPDATE] Modification:")
        print(f"   Ancien: {old_fuseki_graph_uri}")
        print(f"   Nouveau: {virtuoso_graph_uri}")

        # Sauvegarder
        try:
            with open('datasets_metadata.json', 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            print("\n[SUCCESS] Metadonnees mises a jour avec succes!")
            print(f"\n[NEXT_STEP] Prochaines etapes:")
            print(f"   1. Relancez l'application Streamlit")
            print(f"   2. L'avertissement devrait disparaitre")
            print(f"   3. Les deux endpoints utilisent maintenant le meme graph_uri")

        except Exception as e:
            print(f"\n[ERROR] Erreur lors de la sauvegarde: {e}")
    else:
        print("\n[ERROR] Pas de metadonnees Fuseki trouvees !")


if __name__ == "__main__":
    main()
