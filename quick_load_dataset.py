"""
Script rapide pour charger un dataset et le synchroniser
"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from utils.dataset_manager import DatasetManager
from utils.data_synchronizer_v2 import DataSynchronizer

VIRTUOSO_ENDPOINT = "http://localhost:8890/sparql"
FUSEKI_ENDPOINT = "http://localhost:3030/dataset/query"

def main():
    print("="*80)
    print("CHARGEMENT RAPIDE D'UN DATASET")
    print("="*80)

    # Initialiser le gestionnaire de datasets
    dataset_manager = DatasetManager(datasets_path="datasets")

    print("\n[DATASETS] Datasets disponibles:")
    datasets = dataset_manager.list_available_datasets()

    for i, (name, sizes) in enumerate(datasets.items(), 1):
        print(f"  {i}. {name}")
        print(f"     Tailles: {', '.join(sizes)}")

    if not datasets:
        print("\n[ERROR] Aucun dataset trouve dans le dossier 'datasets'")
        return

    # Choix du dataset
    print("\n[SELECT] Quel dataset voulez-vous charger?")
    print("  Exemples:")
    print("    - DBpedia 100K (recommande pour tests)")
    print("    - LUBM 100K")

    choice = input("\nNom du dataset (ex: DBpedia): ").strip()

    if choice not in datasets:
        print(f"\n[ERROR] Dataset '{choice}' non trouve")
        return

    # Choix de la taille
    available_sizes = datasets[choice]
    print(f"\n[SIZES] Tailles disponibles pour {choice}: {', '.join(available_sizes)}")

    size = input(f"Taille (ex: 100K): ").strip()

    if size not in available_sizes:
        print(f"\n[ERROR] Taille '{size}' non disponible")
        return

    # Chargement dans Virtuoso
    print(f"\n[LOAD_VIRTUOSO] Chargement de {choice} {size} dans Virtuoso...")

    success_v = dataset_manager.load_dataset_to_virtuoso(
        dataset_name=choice,
        size=size,
        endpoint=VIRTUOSO_ENDPOINT
    )

    if not success_v:
        print("\n[ERROR] Echec du chargement dans Virtuoso")
        return

    print(f"\n[SUCCESS] {choice} {size} charge dans Virtuoso!")

    # Chargement dans Fuseki
    print(f"\n[LOAD_FUSEKI] Chargement de {choice} {size} dans Fuseki...")

    success_f = dataset_manager.load_dataset_to_fuseki(
        dataset_name=choice,
        size=size,
        endpoint=FUSEKI_ENDPOINT
    )

    if not success_f:
        print("\n[ERROR] Echec du chargement dans Fuseki")
        print("[INFO] Vous pouvez utiliser la synchronisation a la place")

        # Proposer la synchronisation
        sync_choice = input("\nVoulez-vous synchroniser Virtuoso -> Fuseki? (o/n): ").strip().lower()

        if sync_choice == 'o':
            print("\n[SYNC] Synchronisation en cours...")

            synchronizer = DataSynchronizer(VIRTUOSO_ENDPOINT, FUSEKI_ENDPOINT)

            # Charger les metadonnees
            metadata = dataset_manager.load_all_metadata()
            v_graph_uri = metadata.get('virtuoso', {}).get('graph_uri')
            f_graph_uri = v_graph_uri  # Utiliser le meme graph_uri

            if not v_graph_uri:
                print("\n[ERROR] Pas de graph_uri trouve dans les metadonnees")
                return

            # Synchroniser
            print(f"[INFO] Graph URI: {v_graph_uri}")

            # Export
            chunks = synchronizer.export_data_chunked(
                graph_uri=v_graph_uri,
                progress_callback=None
            )

            if not chunks:
                print("\n[ERROR] Echec de l'export")
                return

            print(f"[SUCCESS] {len(chunks)} chunks exportes")

            # Upload
            successful = 0
            for i, chunk in enumerate(chunks):
                if synchronizer.upload_chunk_to_fuseki(chunk, i + 1, f_graph_uri):
                    successful += 1
                    print(f"  [{i+1}/{len(chunks)}] Uploade")

            print(f"\n[RESULT] {successful}/{len(chunks)} chunks uploades")

            # Verifier
            import time
            time.sleep(3)

            v_count = synchronizer.count_triplets(VIRTUOSO_ENDPOINT, v_graph_uri)
            f_count = synchronizer.count_triplets(FUSEKI_ENDPOINT, f_graph_uri)

            print(f"\n[VERIFICATION]")
            print(f"  Virtuoso: {v_count:,} triplets")
            print(f"  Fuseki:   {f_count:,} triplets")

            if v_count == f_count:
                print(f"\n[SUCCESS] Synchronisation complete!")
            else:
                print(f"\n[WARNING] Synchronisation partielle")

    else:
        print(f"\n[SUCCESS] {choice} {size} charge dans Fuseki!")

    # Résumé final
    print("\n" + "="*80)
    print("RESUME")
    print("="*80)

    metadata = dataset_manager.load_all_metadata()

    print(f"\n[VIRTUOSO]")
    if 'virtuoso' in metadata:
        v_meta = metadata['virtuoso']
        print(f"  Dataset: {v_meta.get('dataset_name')} {v_meta.get('size')}")
        print(f"  Triplets: {v_meta.get('triplet_count'):,}")
        print(f"  Graph URI: {v_meta.get('graph_uri')}")

    print(f"\n[FUSEKI]")
    if 'fuseki' in metadata:
        f_meta = metadata['fuseki']
        print(f"  Dataset: {f_meta.get('dataset_name')} {f_meta.get('size')}")
        print(f"  Triplets: {f_meta.get('triplet_count'):,}")
        print(f"  Graph URI: {f_meta.get('graph_uri')}")

    print("\n[NEXT_STEPS]")
    print("  1. Relancez Streamlit")
    print("  2. L'avertissement devrait disparaitre")
    print("  3. Vous pouvez executer les tests de performance")

    print("\n" + "="*80)


if __name__ == "__main__":
    main()
