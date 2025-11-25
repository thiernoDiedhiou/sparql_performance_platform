"""
Diagnostic détaillé pour comprendre l'état réel de Fuseki
"""

import sys
import io
from SPARQLWrapper import SPARQLWrapper

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def query_fuseki(query, description):
    """Exécute une requête sur Fuseki et affiche le résultat"""
    print(f"\n{'='*70}")
    print(f"{description}")
    print(f"{'='*70}")

    endpoint = "http://localhost:3030/dataset/query"
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat('json')

    try:
        result = sparql.query().convert()

        if 'results' in result and 'bindings' in result['results']:
            bindings = result['results']['bindings']
            if bindings:
                for binding in bindings:
                    for key, value in binding.items():
                        print(f"  {key}: {value.get('value', 'N/A')}")
            else:
                print("  (Aucun résultat)")
        elif 'boolean' in result:
            print(f"  Résultat: {result['boolean']}")
        else:
            print(f"  Résultat brut: {result}")

    except Exception as e:
        print(f"  ERREUR: {str(e)}")

# Test 1: Comptage global
query_fuseki(
    "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }",
    "TEST 1: Comptage GLOBAL (tous graphes confondus)"
)

# Test 2: Liste des graphes
query_fuseki(
    "SELECT DISTINCT ?g WHERE { GRAPH ?g { ?s ?p ?o } }",
    "TEST 2: Liste de TOUS les graphes"
)

# Test 3: Comptage par graphe
query_fuseki(
    """
    SELECT ?g (COUNT(*) AS ?count)
    WHERE {
        GRAPH ?g { ?s ?p ?o }
    }
    GROUP BY ?g
    ORDER BY DESC(?count)
    """,
    "TEST 3: Nombre de triplets PAR GRAPHE"
)

# Test 4: Comptage dans le graphe par défaut
query_fuseki(
    "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o . FILTER(!isBLANK(?s)) }",
    "TEST 4: Triplets dans le graphe PAR DÉFAUT"
)

# Test 5: Vérifier si le graphe DBpedia existe
graph_uri = "http://example.org/dataset_DBpedia_10K_1761855828"  # Depuis metadata
query_fuseki(
    f"""
    ASK {{
        GRAPH <{graph_uri}> {{ ?s ?p ?o }}
    }}
    """,
    f"TEST 5: Le graphe {graph_uri[-40:]} existe-t-il ?"
)

# Test 6: Comptage dans le graphe DBpedia spécifique (si vous connaissez l'URI)
query_fuseki(
    f"""
    SELECT (COUNT(*) AS ?count)
    WHERE {{
        GRAPH <{graph_uri}> {{ ?s ?p ?o }}
    }}
    """,
    f"TEST 6: Nombre de triplets dans le graphe DBpedia"
)

# Test 7: Exemples de triplets
query_fuseki(
    """
    SELECT ?g ?s ?p ?o
    WHERE {
        GRAPH ?g { ?s ?p ?o }
    }
    LIMIT 5
    """,
    "TEST 7: 5 exemples de triplets (avec leur graphe)"
)

print(f"\n{'='*70}")
print("Diagnostic terminé")
print(f"{'='*70}")
print("\nInterprétation :")
print("- Si TEST 1 montre 2484 et TEST 3 montre plusieurs graphes avec 10000+ triplets")
print("  → Fuseki compte mal globalement (bug connu)")
print("- Si TEST 3 ne montre aucun graphe avec 10000 triplets")
print("  → Le chargement n'a pas fonctionné")
print("- Si TEST 5 retourne false")
print("  → Le graphe DBpedia n'existe pas dans Fuseki")
