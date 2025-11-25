"""
Script de diagnostic pour identifier le problème de synchronisation partielle
Analyse: 10,001 triplets transférés au lieu de 100,000 (10%)
"""

import sys
from SPARQLWrapper import SPARQLWrapper, TURTLE, JSON
from typing import Optional
import requests

# Configuration
VIRTUOSO_ENDPOINT = "http://localhost:8890/sparql"
FUSEKI_ENDPOINT = "http://localhost:3030/dataset/query"
FUSEKI_UPDATE_ENDPOINT = "http://localhost:3030/dataset/update"
FUSEKI_DATA_ENDPOINT = "http://localhost:3030/dataset/data"

# Graph URI depuis les métadonnées
GRAPH_URI = "http://example.org/dataset_LUBM_100K_1761863353"


def count_triplets(endpoint: str, graph_uri: Optional[str] = None) -> int:
    """Compte les triplets dans un endpoint"""
    sparql = SPARQLWrapper(endpoint)

    if graph_uri:
        query = f"SELECT (COUNT(*) AS ?count) WHERE {{ GRAPH <{graph_uri}> {{ ?s ?p ?o }} }}"
    else:
        query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }"

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()
        count = int(results["results"]["bindings"][0]["count"]["value"])
        return count
    except Exception as e:
        print(f"❌ Erreur de comptage: {e}")
        return 0


def test_construct_query_size():
    """Teste combien de triplets sont réellement récupérés par CONSTRUCT"""
    print("\n" + "="*80)
    print("TEST 1: Taille du résultat CONSTRUCT depuis Virtuoso")
    print("="*80)

    sparql = SPARQLWrapper(VIRTUOSO_ENDPOINT)

    # Test avec LIMIT croissants
    for limit in [10, 100, 1000, 10000, 100000]:
        query = f"""
        CONSTRUCT {{ ?s ?p ?o }}
        WHERE {{
            GRAPH <{GRAPH_URI}> {{
                ?s ?p ?o
            }}
        }}
        LIMIT {limit}
        """

        sparql.setQuery(query)
        sparql.setReturnFormat(TURTLE)
        sparql.setTimeout(300)

        try:
            print(f"\n📊 Test avec LIMIT {limit:,}...")
            result = sparql.query().convert()

            if isinstance(result, bytes):
                turtle_data = result.decode('utf-8')
            else:
                turtle_data = str(result)

            lines = len(turtle_data.splitlines())
            size_kb = len(turtle_data.encode('utf-8')) / 1024

            print(f"   ✅ Résultat: {lines:,} lignes, {size_kb:.2f} KB")

            # Compter approximativement les triplets (chaque triplet = ~1-3 lignes)
            estimated_triplets = turtle_data.count('.') - turtle_data.count('@prefix')
            print(f"   📈 Triplets estimés dans le résultat: ~{estimated_triplets:,}")

            if limit == 100000:
                # Sauvegarder pour inspection
                with open('export_test_100k.ttl', 'w', encoding='utf-8') as f:
                    f.write(turtle_data)
                print(f"   💾 Données sauvegardées dans export_test_100k.ttl")

        except Exception as e:
            print(f"   ❌ Erreur: {e}")


def test_fuseki_upload_capacity():
    """Teste la capacité d'upload de Fuseki"""
    print("\n" + "="*80)
    print("TEST 2: Capacité d'upload de Fuseki")
    print("="*80)

    # Créer des données de test de taille croissante
    test_graph = "http://example.org/test_upload"

    for num_triplets in [10, 100, 1000, 10000]:
        print(f"\n📤 Test upload de {num_triplets:,} triplets...")

        # Générer des données de test
        turtle_data = "@prefix ex: <http://example.org/> .\n\n"
        for i in range(num_triplets):
            turtle_data += f"ex:subject{i} ex:predicate ex:object{i} .\n"

        # Uploader vers Fuseki
        upload_url = f"{FUSEKI_DATA_ENDPOINT}?graph={test_graph}"
        headers = {'Content-Type': 'text/turtle; charset=utf-8'}

        try:
            response = requests.post(
                upload_url,
                data=turtle_data.encode('utf-8'),
                headers=headers,
                timeout=300
            )

            if response.status_code in [200, 201, 204]:
                print(f"   ✅ Upload réussi (HTTP {response.status_code})")

                # Vérifier le comptage
                count = count_triplets(FUSEKI_ENDPOINT, test_graph)
                print(f"   📊 Triplets comptés: {count:,}")

                if count == num_triplets:
                    print(f"   ✅ Comptage correct!")
                else:
                    print(f"   ⚠️  Comptage incorrect! Attendu: {num_triplets:,}, Reçu: {count:,}")
            else:
                print(f"   ❌ Échec upload (HTTP {response.status_code})")
                print(f"   Réponse: {response.text[:200]}")

        except Exception as e:
            print(f"   ❌ Erreur: {e}")

        # Nettoyer le graphe de test
        try:
            clear_query = f"CLEAR GRAPH <{test_graph}>"
            requests.post(
                FUSEKI_UPDATE_ENDPOINT,
                data={'update': clear_query},
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
        except:
            pass


def test_current_dataset_state():
    """Vérifie l'état actuel des datasets"""
    print("\n" + "="*80)
    print("TEST 3: État actuel du dataset LUBM 100K")
    print("="*80)

    print(f"\n📊 Graphe: {GRAPH_URI}")

    # Virtuoso
    v_count = count_triplets(VIRTUOSO_ENDPOINT, GRAPH_URI)
    print(f"\n🟦 Virtuoso:")
    print(f"   Triplets dans le graphe: {v_count:,}")

    # Fuseki
    f_count = count_triplets(FUSEKI_ENDPOINT, GRAPH_URI)
    print(f"\n🟧 Fuseki:")
    print(f"   Triplets dans le graphe: {f_count:,}")

    # Analyse
    if v_count > 0 and f_count > 0:
        percentage = (f_count / v_count) * 100
        print(f"\n📈 Analyse:")
        print(f"   Pourcentage transféré: {percentage:.2f}%")

        if percentage < 100:
            missing = v_count - f_count
            print(f"   ⚠️  Triplets manquants: {missing:,}")


def test_chunk_export():
    """Teste l'export d'un chunk complet"""
    print("\n" + "="*80)
    print("TEST 4: Export d'un chunk de 100,000 triplets")
    print("="*80)

    sparql = SPARQLWrapper(VIRTUOSO_ENDPOINT)

    query = f"""
    CONSTRUCT {{ ?s ?p ?o }}
    WHERE {{
        GRAPH <{GRAPH_URI}> {{
            ?s ?p ?o
        }}
    }}
    LIMIT 100000
    OFFSET 0
    """

    sparql.setQuery(query)
    sparql.setReturnFormat(TURTLE)
    sparql.setTimeout(300)

    try:
        print("⏳ Export en cours (cela peut prendre quelques minutes)...")
        import time
        start = time.time()

        result = sparql.query().convert()

        duration = time.time() - start

        if isinstance(result, bytes):
            turtle_data = result.decode('utf-8')
        else:
            turtle_data = str(result)

        lines = len(turtle_data.splitlines())
        size_mb = len(turtle_data.encode('utf-8')) / (1024 * 1024)

        print(f"\n✅ Export réussi en {duration:.1f}s")
        print(f"   📄 Lignes: {lines:,}")
        print(f"   💾 Taille: {size_mb:.2f} MB")

        # Compter les triplets approximativement
        estimated = turtle_data.count('.') - turtle_data.count('@prefix')
        print(f"   📊 Triplets estimés: ~{estimated:,}")

        # Vérifier si le résultat est complet
        if estimated < 90000:  # Tolérance de 10%
            print(f"\n⚠️  WARNING: Le chunk semble incomplet!")
            print(f"   Attendu: ~100,000 triplets")
            print(f"   Reçu: ~{estimated:,} triplets")
        else:
            print(f"\n✅ Le chunk semble complet")

        return turtle_data

    except Exception as e:
        print(f"❌ Erreur lors de l'export: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Exécute tous les tests de diagnostic"""
    print("="*80)
    print("DIAGNOSTIC DE SYNCHRONISATION PARTIELLE")
    print("Problème: 10,001 triplets au lieu de 100,000 (10%)")
    print("="*80)

    # Test 1: État actuel
    test_current_dataset_state()

    # Test 2: Capacité d'export CONSTRUCT
    test_construct_query_size()

    # Test 3: Capacité d'upload Fuseki
    test_fuseki_upload_capacity()

    # Test 4: Export d'un chunk complet
    chunk_data = test_chunk_export()

    print("\n" + "="*80)
    print("RÉSUMÉ DU DIAGNOSTIC")
    print("="*80)
    print("\nVérifiez les résultats ci-dessus pour identifier:")
    print("1. Si Virtuoso exporte bien 100,000 triplets")
    print("2. Si Fuseki peut recevoir de gros uploads")
    print("3. Où se produit la perte de données (export vs upload)")
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
