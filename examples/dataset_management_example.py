"""
Exemples d'utilisation du système de gestion des datasets
Démontre les fonctionnalités principales du DatasetManager
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(str(Path(__file__).parent.parent))

from utils.dataset_manager import DatasetManager
from config.settings import get_datasets_config
from utils.helpers import log_message


def example_1_load_dataset():
    """Exemple 1: Charger un dataset simple"""
    print("\n" + "="*60)
    print("EXEMPLE 1: Charger un dataset dans Virtuoso")
    print("="*60)

    # Initialiser le gestionnaire
    manager = DatasetManager("datasets")

    # Obtenir les informations du dataset
    file_info = manager.get_dataset_file_info("Generic", "10K")

    if file_info.get("exists"):
        print(f"✅ Fichier trouvé: {file_info['path']}")
        print(f"   Taille: {file_info['size_mb']} MB")
        print(f"   Format: {file_info['format']}")

        # Charger dans Virtuoso
        print("\n🔄 Chargement dans Virtuoso...")
        success, message = manager.load_to_virtuoso(
            file_path=file_info["path"],
            endpoint="http://localhost:8890/sparql",
            graph_uri="http://example.org/generic_test"
        )

        if success:
            print(f"✅ {message}")

            # Sauvegarder les métadonnées
            manager.save_dataset_metadata(
                dataset_name="Generic",
                size="10K",
                target="virtuoso",
                graph_uri="http://example.org/generic_test",
                triplet_count=10000
            )

            # Mettre à jour le .env
            manager.update_env_file("Generic", "10K", "virtuoso")

            print("✅ Métadonnées et configuration sauvegardées")
        else:
            print(f"❌ {message}")
    else:
        print(f"❌ Fichier non trouvé: {file_info.get('error')}")


def example_2_list_available_datasets():
    """Exemple 2: Lister les datasets disponibles"""
    print("\n" + "="*60)
    print("EXEMPLE 2: Lister les datasets disponibles")
    print("="*60)

    manager = DatasetManager("datasets")

    # Obtenir les datasets disponibles
    available = manager.get_available_datasets()

    print(f"\n📦 {len(available)} dataset(s) trouvé(s):\n")

    for dataset_name, sizes in available.items():
        color = manager.DATASET_INFO[dataset_name]['color']
        description = manager.DATASET_INFO[dataset_name]['description']

        print(f"{color} {dataset_name}")
        print(f"   Description: {description}")
        print(f"   Tailles disponibles: {', '.join(sizes)}")

        # Afficher les détails de chaque taille
        for size in sizes:
            info = manager.get_dataset_file_info(dataset_name, size)
            time_estimate = manager.estimate_load_time(dataset_name, size)
            print(f"      - {size}: {info['size_mb']} MB (~{time_estimate}s)")

        print()


def example_3_get_statistics():
    """Exemple 3: Obtenir les statistiques des datasets chargés"""
    print("\n" + "="*60)
    print("EXEMPLE 3: Statistiques des datasets chargés")
    print("="*60)

    manager = DatasetManager("datasets")

    # Obtenir les statistiques
    stats = manager.get_dataset_statistics()

    print(f"\n📊 Total de datasets chargés: {stats['total_datasets_loaded']}")
    print(f"📊 Total de triplets: {stats['total_triplets']:,}\n")

    # Afficher les détails par moteur
    for target in ['virtuoso', 'fuseki']:
        if stats[target]:
            info = stats[target]
            print(f"{'🔵 Virtuoso' if target == 'virtuoso' else '🟢 Fuseki'}:")
            print(f"   Dataset: {info['dataset']}")
            print(f"   Triplets: {info['triplets']:,}")
            print(f"   Chargé le: {info['loaded_at']}")
            print(f"   Graph URI: {info['graph_uri']}")
            print()
        else:
            print(f"{'🔵 Virtuoso' if target == 'virtuoso' else '🟢 Fuseki'}: Aucun dataset chargé\n")


def example_4_clear_dataset():
    """Exemple 4: Effacer un dataset"""
    print("\n" + "="*60)
    print("EXEMPLE 4: Effacer un dataset de Virtuoso")
    print("="*60)

    manager = DatasetManager("datasets")

    # Vérifier s'il y a un dataset chargé
    info = manager.get_loaded_dataset_info("virtuoso")

    if info:
        print(f"\n📦 Dataset actuellement chargé dans Virtuoso:")
        print(f"   Nom: {info['dataset_name']} ({info['size']})")
        print(f"   Triplets: {info['triplet_count']:,}")
        print(f"   Graph URI: {info['graph_uri']}")

        # Demander confirmation
        response = input("\n⚠️  Voulez-vous vraiment effacer ce dataset ? (oui/non): ")

        if response.lower() == "oui":
            print("\n🔄 Suppression en cours...")

            success, message = manager.clear_dataset(
                target="virtuoso",
                endpoint="http://localhost:8890/sparql"
            )

            if success:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
        else:
            print("❌ Suppression annulée")
    else:
        print("\nℹ️  Aucun dataset chargé dans Virtuoso")


def example_5_load_with_validation():
    """Exemple 5: Charger un dataset avec validation complète"""
    print("\n" + "="*60)
    print("EXEMPLE 5: Chargement avec validation complète")
    print("="*60)

    manager = DatasetManager("datasets")

    dataset_name = "DBpedia"
    size = "10K"

    # 1. Valider la cohérence du dataset
    print("\n🔍 Étape 1: Validation de la cohérence...")
    is_coherent, msg, details = manager.validate_dataset_coherence(dataset_name, size)

    if is_coherent:
        print(f"✅ {msg}")
        print(f"   Format: {details['format']}")
        print(f"   Triplets estimés: ~{details['estimated_triplets']}")
        print(f"   Préfixes trouvés: {details['prefixes_found']}")
    else:
        print(f"❌ {msg}")
        return

    # 2. Vérifier les ressources disponibles
    print("\n🔍 Étape 2: Vérification des ressources...")
    recommendations = manager.get_loading_recommendations(dataset_name, size)

    print(f"   Mémoire requise: {recommendations['memory_required_mb']} MB")
    print(f"   Temps estimé: ~{recommendations['estimated_time_seconds']}s")

    if not recommendations['memory_available']:
        print(f"❌ {recommendations['memory_message']}")
        return
    else:
        print(f"✅ {recommendations['memory_message']}")

    # 3. Charger le dataset
    print("\n🔄 Étape 3: Chargement du dataset...")
    file_info = manager.get_dataset_file_info(dataset_name, size)

    success, message = manager.load_to_virtuoso(
        file_path=file_info["path"],
        endpoint="http://localhost:8890/sparql",
        graph_uri=f"http://example.org/{dataset_name}_{size}"
    )

    if not success:
        print(f"❌ {message}")
        return

    print(f"✅ {message}")

    # 4. Valider le chargement
    print("\n🔍 Étape 4: Validation du chargement...")
    is_valid, msg, count = manager.validate_loaded_dataset(
        endpoint="http://localhost:8890/sparql",
        dataset_name=dataset_name
    )

    if is_valid:
        print(f"✅ {msg}")

        # 5. Sauvegarder les métadonnées
        print("\n💾 Étape 5: Sauvegarde des métadonnées...")

        manager.save_dataset_metadata(
            dataset_name=dataset_name,
            size=size,
            target="virtuoso",
            graph_uri=f"http://example.org/{dataset_name}_{size}",
            triplet_count=count
        )

        manager.update_env_file(dataset_name, size, "virtuoso")

        print("✅ Toutes les étapes complétées avec succès!")
    else:
        print(f"⚠️ {msg}")


def example_6_check_permissions():
    """Exemple 6: Vérifier les permissions Virtuoso"""
    print("\n" + "="*60)
    print("EXEMPLE 6: Vérifier les permissions Virtuoso")
    print("="*60)

    manager = DatasetManager("datasets")

    print("\n🔍 Vérification des permissions...")

    has_perms, message, details = manager.check_virtuoso_permissions(
        endpoint="http://localhost:8890/sparql",
        username="SPARQL",
        password="admin123"
    )

    print(f"\n{message}\n")

    print("Détails des permissions:")
    print(f"   ✓ Authentification: {'✅' if details.get('authentication') else '❌'}")
    print(f"   ✓ SPARQL_UPDATE: {'✅' if details.get('sparql_update') else '❌'}")
    print(f"   Utilisateur: {details.get('username', 'N/A')}")

    if not has_perms:
        print("\n💡 Pour donner les permissions:")
        print("   1. Connectez-vous à Virtuoso: isql 1111 dba dba")
        print('   2. Exécutez: GRANT SPARQL_UPDATE TO "SPARQL";')


def example_7_get_configuration():
    """Exemple 7: Obtenir la configuration des datasets"""
    print("\n" + "="*60)
    print("EXEMPLE 7: Configuration des datasets")
    print("="*60)

    config = get_datasets_config()

    print("\n⚙️ Configuration actuelle:\n")
    print(f"Chemin des datasets: {config['datasets_path']}")
    print(f"Fichier métadonnées: {config['metadata_file']}")
    print(f"Chunk size: {config['chunk_size']} triplets")
    print(f"Timeout: {config['load_timeout']}s")

    print("\nAuthentification Virtuoso:")
    print(f"   Username: {config['virtuoso_auth']['username']}")
    print(f"   Password: {'*' * len(config['virtuoso_auth']['password'])}")

    print("\nDatasets disponibles:")
    for name, conf in config['available_datasets'].items():
        print(f"   {conf['color']} {name}")
        print(f"      Format: {conf['format']}")
        print(f"      Tailles: {', '.join(conf['sizes'])}")


def main():
    """Menu principal"""
    print("\n" + "="*60)
    print("EXEMPLES DE GESTION DES DATASETS")
    print("="*60)

    examples = {
        "1": ("Charger un dataset simple", example_1_load_dataset),
        "2": ("Lister les datasets disponibles", example_2_list_available_datasets),
        "3": ("Obtenir les statistiques", example_3_get_statistics),
        "4": ("Effacer un dataset", example_4_clear_dataset),
        "5": ("Chargement avec validation complète", example_5_load_with_validation),
        "6": ("Vérifier les permissions Virtuoso", example_6_check_permissions),
        "7": ("Obtenir la configuration", example_7_get_configuration),
        "0": ("Quitter", None)
    }

    while True:
        print("\n" + "-"*60)
        print("Choisissez un exemple:")
        print("-"*60)

        for key, (description, _) in examples.items():
            print(f"  {key}. {description}")

        choice = input("\nVotre choix: ").strip()

        if choice == "0":
            print("\n👋 Au revoir!")
            break
        elif choice in examples and examples[choice][1] is not None:
            try:
                examples[choice][1]()
            except Exception as e:
                print(f"\n❌ Erreur: {str(e)}")
                import traceback
                traceback.print_exc()

            input("\n⏎ Appuyez sur Entrée pour continuer...")
        else:
            print("\n❌ Choix invalide, veuillez réessayer.")


if __name__ == "__main__":
    # Vérifier si on exécute un exemple spécifique
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        examples_map = {
            "1": example_1_load_dataset,
            "2": example_2_list_available_datasets,
            "3": example_3_get_statistics,
            "4": example_4_clear_dataset,
            "5": example_5_load_with_validation,
            "6": example_6_check_permissions,
            "7": example_7_get_configuration
        }

        if example_num in examples_map:
            try:
                examples_map[example_num]()
            except Exception as e:
                print(f"\n❌ Erreur: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print(f"❌ Exemple {example_num} non trouvé")
            print(f"Exemples disponibles: {', '.join(examples_map.keys())}")
    else:
        main()
