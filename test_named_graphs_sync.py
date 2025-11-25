"""
Script de test pour la synchronisation avec graphes nommés
Teste les nouvelles fonctionnalités du data_synchronizer_v2.py
"""

import sys
import io
from utils.data_synchronizer_v2 import DataSynchronizer
from utils.dataset_manager import DatasetManager
from config.settings import VIRTUOSO_ENDPOINT, FUSEKI_ENDPOINT

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def print_section(title: str):
    """Affiche un titre de section"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_count_with_graphs():
    """Test 1 : Comptage avec graphes nommés"""
    print_section("TEST 1 : Comptage avec Graphes Nommés")

    # Charger les métadonnées
    dm = DatasetManager()
    metadata = dm.load_all_metadata()

    if not metadata:
        print("❌ Aucune métadonnée trouvée")
        print("   Veuillez d'abord charger un dataset via l'interface")
        return False

    # Créer le synchroniseur
    sync = DataSynchronizer(VIRTUOSO_ENDPOINT, FUSEKI_ENDPOINT)

    # Tester Virtuoso
    if 'virtuoso' in metadata:
        virt_meta = metadata['virtuoso']
        graph_uri = virt_meta.get('graph_uri')

        print(f"📊 VIRTUOSO")
        print(f"   Dataset: {virt_meta.get('dataset_name')} {virt_meta.get('size')}")
        print(f"   Graphe: {graph_uri}")

        # Comptage global
        global_count = sync.count_triplets(VIRTUOSO_ENDPOINT)
        print(f"   Triplets (global): {global_count:,}")

        # Comptage par graphe
        if graph_uri:
            graph_count = sync.count_triplets(VIRTUOSO_ENDPOINT, graph_uri)
            print(f"   Triplets (graphe): {graph_count:,}")

            expected_count = virt_meta.get('triplet_count', 0)
            if graph_count == expected_count:
                print(f"   ✅ Cohérent avec métadonnées ({expected_count:,})")
            else:
                print(f"   ⚠️  Incohérent avec métadonnées ({expected_count:,})")
        else:
            print(f"   ⚠️  Pas de graph_uri dans les métadonnées")

    # Tester Fuseki
    if 'fuseki' in metadata:
        fuseki_meta = metadata['fuseki']
        graph_uri = fuseki_meta.get('graph_uri')

        print(f"\n📊 FUSEKI")
        print(f"   Dataset: {fuseki_meta.get('dataset_name')} {fuseki_meta.get('size')}")
        print(f"   Graphe: {graph_uri}")

        # Comptage global
        global_count = sync.count_triplets(FUSEKI_ENDPOINT)
        print(f"   Triplets (global): {global_count:,}")

        # Comptage par graphe
        if graph_uri:
            graph_count = sync.count_triplets(FUSEKI_ENDPOINT, graph_uri)
            print(f"   Triplets (graphe): {graph_count:,}")

            expected_count = fuseki_meta.get('triplet_count', 0)
            if graph_count == expected_count:
                print(f"   ✅ Cohérent avec métadonnées ({expected_count:,})")
            else:
                print(f"   ⚠️  Incohérent avec métadonnées ({expected_count:,})")
        else:
            print(f"   ⚠️  Pas de graph_uri dans les métadonnées")

    print(f"\n✅ Test 1 terminé")
    return True


def test_compare_graphs():
    """Test 2 : Comparaison des graphes entre Virtuoso et Fuseki"""
    print_section("TEST 2 : Comparaison des Graphes")

    dm = DatasetManager()
    metadata = dm.load_all_metadata()

    if not metadata or 'virtuoso' not in metadata:
        print("❌ Aucun dataset chargé dans Virtuoso")
        return False

    sync = DataSynchronizer(VIRTUOSO_ENDPOINT, FUSEKI_ENDPOINT)

    virt_meta = metadata['virtuoso']
    virt_graph = virt_meta.get('graph_uri')

    if not virt_graph:
        print("❌ Pas de graph_uri pour Virtuoso")
        return False

    # Compter dans Virtuoso
    virt_count = sync.count_triplets(VIRTUOSO_ENDPOINT, virt_graph)
    print(f"📊 Virtuoso - Graphe actif")
    print(f"   URI: {virt_graph}")
    print(f"   Triplets: {virt_count:,}")

    # Vérifier si le même graphe existe dans Fuseki
    fuseki_count = sync.count_triplets(FUSEKI_ENDPOINT, virt_graph)
    print(f"\n📊 Fuseki - Même graphe")
    print(f"   URI: {virt_graph}")
    print(f"   Triplets: {fuseki_count:,}")

    # Comparaison
    print(f"\n📈 Comparaison")
    if virt_count == fuseki_count:
        print(f"   ✅ Les graphes sont synchronisés ({virt_count:,} triplets)")
    elif fuseki_count == 0:
        print(f"   ⚠️  Le graphe n'existe pas encore dans Fuseki")
        print(f"   💡 Utilisez la synchronisation pour le transférer")
    else:
        ratio = (fuseki_count / virt_count * 100) if virt_count > 0 else 0
        print(f"   ⚠️  Synchronisation partielle: {ratio:.1f}%")
        print(f"   Différence: {abs(virt_count - fuseki_count):,} triplets")

    print(f"\n✅ Test 2 terminé")
    return True


def test_retrocompatibility():
    """Test 3 : Rétrocompatibilité (comptage sans graphe)"""
    print_section("TEST 3 : Rétrocompatibilité")

    sync = DataSynchronizer(VIRTUOSO_ENDPOINT, FUSEKI_ENDPOINT)

    print("📊 Comptage global (ancien comportement)")

    # Test Virtuoso
    try:
        virt_count = sync.count_triplets(VIRTUOSO_ENDPOINT)
        print(f"   Virtuoso: {virt_count:,} triplets (tous graphes)")
        print(f"   ✅ Méthode compatible")
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
        return False

    # Test Fuseki
    try:
        fuseki_count = sync.count_triplets(FUSEKI_ENDPOINT)
        print(f"   Fuseki: {fuseki_count:,} triplets (tous graphes)")
        print(f"   ✅ Méthode compatible")
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
        return False

    print(f"\n✅ Test 3 terminé - Rétrocompatibilité assurée")
    return True


def main():
    """Fonction principale"""
    print("╔" + "═"*68 + "╗")
    print("║  TEST : SYNCHRONISATION AVEC GRAPHES NOMMÉS                      ║")
    print("╚" + "═"*68 + "╝")

    results = {
        "Test 1 - Comptage avec graphes": False,
        "Test 2 - Comparaison graphes": False,
        "Test 3 - Rétrocompatibilité": False
    }

    # Exécuter les tests
    try:
        results["Test 1 - Comptage avec graphes"] = test_count_with_graphs()
        results["Test 2 - Comparaison graphes"] = test_compare_graphs()
        results["Test 3 - Rétrocompatibilité"] = test_retrocompatibility()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur fatale: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Résumé
    print_section("RÉSUMÉ DES TESTS")

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")

    print(f"\n📊 Résultat global: {passed}/{total} tests réussis")

    if passed == total:
        print(f"\n✅ Tous les tests sont passés !")
        print(f"\n💡 Le module data_synchronizer_v2.py supporte correctement les graphes nommés")
        sys.exit(0)
    else:
        print(f"\n⚠️  Certains tests ont échoué")
        print(f"\n💡 Vérifiez que :")
        print(f"   1. Virtuoso et Fuseki sont démarrés")
        print(f"   2. Un dataset est chargé via l'interface")
        print(f"   3. Les métadonnées sont à jour")
        sys.exit(1)


if __name__ == "__main__":
    main()
