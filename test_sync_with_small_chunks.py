"""
Test de synchronisation avec des chunks plus petits
Solution temporaire pour contourner le problème de synchronisation partielle
"""

import time
from utils.data_synchronizer_v2 import ChunkedDataSynchronizer
from utils.dataset_manager import DatasetManager

# Configuration
VIRTUOSO_ENDPOINT = "http://localhost:8890/sparql"
FUSEKI_ENDPOINT = "http://localhost:3030/dataset/query"

# Test avec différentes tailles de chunk
CHUNK_SIZES_TO_TEST = [10000, 25000, 50000, 100000]


def test_sync_with_chunk_size(chunk_size: int):
    """
    Teste la synchronisation avec une taille de chunk spécifique

    Args:
        chunk_size: Taille du chunk à tester
    """
    print("\n" + "="*80)
    print(f"TEST AVEC CHUNK SIZE = {chunk_size:,} triplets")
    print("="*80)

    # Créer le synchroniseur
    synchronizer = ChunkedDataSynchronizer(VIRTUOSO_ENDPOINT, FUSEKI_ENDPOINT)

    # Modifier temporairement le chunk size
    original_chunk_size = synchronizer.chunk_size
    synchronizer.chunk_size = chunk_size

    # Charger les métadonnées
    dataset_manager = DatasetManager(datasets_path="datasets")
    metadata = dataset_manager.load_all_metadata()

    virtuoso_graph_uri = metadata.get('virtuoso', {}).get('graph_uri')
    fuseki_graph_uri = metadata.get('fuseki', {}).get('graph_uri')

    if not virtuoso_graph_uri:
        print("❌ Aucun graphe source trouvé dans les métadonnées")
        return None

    print(f"📊 Graphe source: {virtuoso_graph_uri}")
    print(f"📊 Graphe cible: {fuseki_graph_uri}")

    # Compter avant
    v_before = synchronizer.count_triplets(VIRTUOSO_ENDPOINT, virtuoso_graph_uri)
    f_before = synchronizer.count_triplets(FUSEKI_ENDPOINT, fuseki_graph_uri)

    print(f"\n📈 État AVANT synchronisation:")
    print(f"   Virtuoso: {v_before:,} triplets")
    print(f"   Fuseki:   {f_before:,} triplets")

    if v_before == 0:
        print("❌ Virtuoso ne contient pas de données")
        return None

    # Nettoyer Fuseki
    print(f"\n🧹 Nettoyage de Fuseki...")
    synchronizer.clear_fuseki_dataset(fuseki_graph_uri)
    time.sleep(2)

    # Synchroniser
    print(f"\n🔄 Synchronisation en cours avec chunk size = {chunk_size:,}...")

    start_time = time.time()

    # Export chunks
    chunks = synchronizer.export_data_chunked(
        total_triplets=v_before,
        graph_uri=virtuoso_graph_uri,
        progress_callback=None
    )

    export_duration = time.time() - start_time

    print(f"\n📦 Export terminé:")
    print(f"   Nombre de chunks: {len(chunks)}")
    print(f"   Durée: {export_duration:.1f}s")

    if not chunks:
        print("❌ Aucun chunk exporté")
        return None

    # Upload chunks
    print(f"\n📤 Upload des chunks vers Fuseki...")
    upload_start = time.time()

    successful_uploads = 0
    for i, chunk in enumerate(chunks):
        if synchronizer.upload_chunk_to_fuseki(chunk, i + 1, fuseki_graph_uri):
            successful_uploads += 1
            print(f"   ✅ Chunk {i+1}/{len(chunks)} uploadé")
        else:
            print(f"   ❌ Chunk {i+1}/{len(chunks)} ÉCHOUÉ")

    upload_duration = time.time() - upload_start

    # Attendre que Fuseki traite
    print(f"\n⏳ Attente du traitement par Fuseki...")
    time.sleep(5)

    # Compter après
    f_after = synchronizer.count_triplets(FUSEKI_ENDPOINT, fuseki_graph_uri)

    total_duration = export_duration + upload_duration

    print(f"\n📊 État APRÈS synchronisation:")
    print(f"   Virtuoso: {v_before:,} triplets")
    print(f"   Fuseki:   {f_after:,} triplets")

    # Analyse
    success_rate = (f_after / v_before) * 100 if v_before > 0 else 0

    print(f"\n📈 Résultats:")
    print(f"   Chunks exportés:  {len(chunks)}")
    print(f"   Chunks uploadés:  {successful_uploads}/{len(chunks)}")
    print(f"   Taux de réussite: {success_rate:.1f}%")
    print(f"   Durée totale:     {total_duration:.1f}s")

    # Restaurer le chunk size original
    synchronizer.chunk_size = original_chunk_size

    return {
        "chunk_size": chunk_size,
        "num_chunks": len(chunks),
        "successful_uploads": successful_uploads,
        "virtuoso_count": v_before,
        "fuseki_count": f_after,
        "success_rate": success_rate,
        "duration": total_duration
    }


def main():
    """Teste différentes tailles de chunk"""
    print("="*80)
    print("TEST DE SYNCHRONISATION AVEC DIFFÉRENTES TAILLES DE CHUNK")
    print("="*80)
    print("\nObjectif: Identifier la taille de chunk optimale pour synchroniser")
    print("          100,000 triplets sans perte de données")
    print("="*80)

    results = []

    for chunk_size in CHUNK_SIZES_TO_TEST:
        result = test_sync_with_chunk_size(chunk_size)
        if result:
            results.append(result)

        # Pause entre les tests
        if chunk_size != CHUNK_SIZES_TO_TEST[-1]:
            print(f"\n⏸️  Pause de 5 secondes avant le prochain test...")
            time.sleep(5)

    # Résumé comparatif
    print("\n" + "="*80)
    print("RÉSUMÉ COMPARATIF")
    print("="*80)

    if results:
        print(f"\n{'Chunk Size':<15} {'Chunks':<10} {'Uploads':<10} {'Taux':<10} {'Durée':<10}")
        print("-" * 80)

        for r in results:
            print(
                f"{r['chunk_size']:>10,} {r['num_chunks']:>10} "
                f"{r['successful_uploads']:>10} {r['success_rate']:>9.1f}% "
                f"{r['duration']:>9.1f}s"
            )

        # Meilleur résultat
        best = max(results, key=lambda x: x['success_rate'])

        print("\n" + "="*80)
        print("RECOMMANDATION")
        print("="*80)
        print(f"\n✅ Meilleur chunk size: {best['chunk_size']:,} triplets")
        print(f"   Taux de réussite: {best['success_rate']:.1f}%")
        print(f"   Nombre de chunks: {best['num_chunks']}")
        print(f"   Durée: {best['duration']:.1f}s")

        if best['success_rate'] >= 99:
            print(f"\n🎉 Synchronisation complète réussie!")
            print(f"\n💡 Suggestion: Modifier SYNC_CHUNK_SIZE dans config/settings.py:")
            print(f"   SYNC_CHUNK_SIZE = {best['chunk_size']}")
        else:
            print(f"\n⚠️  Aucun chunk size n'a donné 100% de réussite")
            print(f"   Il peut y avoir un problème plus profond à investiguer")
            print(f"   Exécutez diagnose_sync_issue.py pour plus de détails")

    else:
        print("\n❌ Aucun test n'a réussi")
        print("   Vérifiez que:")
        print("   1. Virtuoso et Fuseki sont démarrés")
        print("   2. Un dataset est chargé dans Virtuoso")
        print("   3. Les endpoints sont corrects")


if __name__ == "__main__":
    main()
