"""
Script de nettoyage des graphes résiduels
Supprime tous les graphes SAUF celui actuellement référencé dans les métadonnées
"""

import json
import sys
import io
from pathlib import Path
from SPARQLWrapper import SPARQLWrapper
import requests

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def load_metadata():
    """Charge les métadonnées des datasets"""
    metadata_file = Path("datasets_metadata.json")
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def list_all_graphs(endpoint):
    """Liste tous les graphes dans le triplestore"""
    try:
        query = "SELECT DISTINCT ?g WHERE { GRAPH ?g { ?s ?p ?o } }"
        sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(query)
        sparql.setReturnFormat('json')
        result = sparql.query().convert()

        graphs = []
        if 'results' in result and 'bindings' in result['results']:
            for binding in result['results']['bindings']:
                if 'g' in binding:
                    graphs.append(binding['g']['value'])
        return graphs
    except Exception as e:
        print(f"❌ Erreur lors de la liste des graphes: {str(e)}")
        return []

def clear_graph(endpoint, graph_uri, auth=None):
    """Supprime un graphe spécifique"""
    try:
        # Déterminer le type d'endpoint et le paramètre approprié
        if "virtuoso" in endpoint or "8890" in endpoint:
            # Virtuoso utilise "query" pour les UPDATE
            param_name = "query"
            if auth is None:
                auth = ("SPARQL", "admin123")
        else:
            # Fuseki utilise "update"
            param_name = "update"
            # Modifier l'endpoint pour Fuseki
            endpoint = endpoint.replace("/query", "/update")

        clear_query = f"CLEAR GRAPH <{graph_uri}>"

        response = requests.post(
            endpoint,
            data={param_name: clear_query},
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            auth=auth,
            timeout=30
        )

        return response.status_code in [200, 201, 204]
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
        return False

def clean_triplestore(name, endpoint, active_graph_uri, auth=None):
    """Nettoie les graphes résiduels d'un triplestore"""
    print(f"\n{'='*60}")
    print(f"🧹 Nettoyage : {name}")
    print(f"   Endpoint : {endpoint}")
    print(f"{'='*60}")

    # Lister tous les graphes
    print("\n📋 Recherche des graphes...")
    graphs = list_all_graphs(endpoint)

    if not graphs:
        print("   ℹ️  Aucun graphe trouvé")
        return

    print(f"   Trouvé {len(graphs)} graphe(s)")

    # Filtrer les graphes à supprimer
    graphs_to_delete = []
    system_graphs = [
        "http://www.openlinksw.com/schemas/virtrdf#",
        "http://www.w3.org/ns/ldp#",
        "urn:activitystreams-owl:map"
    ]

    for graph in graphs:
        # Ne pas supprimer le graphe actif
        if graph == active_graph_uri:
            print(f"   ✅ Graphe actif (conservé) : {graph}")
            continue

        # Ne pas supprimer les graphes système
        if graph in system_graphs:
            print(f"   ⚙️  Graphe système (conservé) : {graph}")
            continue

        # Ajouter aux graphes à supprimer
        graphs_to_delete.append(graph)

    if not graphs_to_delete:
        print("\n   ✅ Aucun graphe résiduel à nettoyer")
        return

    # Demander confirmation
    print(f"\n⚠️  {len(graphs_to_delete)} graphe(s) résiduel(s) trouvé(s) :")
    for i, graph in enumerate(graphs_to_delete, 1):
        print(f"   {i}. {graph}")

    response = input(f"\n🗑️  Voulez-vous supprimer ces {len(graphs_to_delete)} graphe(s) ? (oui/non) : ")

    if response.lower() not in ['oui', 'o', 'yes', 'y']:
        print("   ❌ Nettoyage annulé")
        return

    # Supprimer les graphes
    print(f"\n🔄 Suppression en cours...")
    success_count = 0
    fail_count = 0

    for i, graph in enumerate(graphs_to_delete, 1):
        print(f"   [{i}/{len(graphs_to_delete)}] Suppression de {graph[:50]}...", end=" ")
        if clear_graph(endpoint, graph, auth):
            print("✅")
            success_count += 1
        else:
            print("❌")
            fail_count += 1

    # Résumé
    print(f"\n📊 Résumé du nettoyage :")
    print(f"   ✅ Supprimés : {success_count}")
    print(f"   ❌ Échecs : {fail_count}")
    print(f"   ⏭️  Conservés : {len(graphs) - len(graphs_to_delete)}")

def main():
    """Fonction principale"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🧹 NETTOYAGE DES GRAPHES RÉSIDUELS                       ║")
    print("╚════════════════════════════════════════════════════════════╝")

    # Charger les métadonnées
    print("\n📂 Chargement des métadonnées...")
    metadata = load_metadata()

    if not metadata:
        print("❌ Aucune métadonnée trouvée (datasets_metadata.json)")
        print("\n💡 Ce script nettoie les graphes SAUF celui actuellement actif.")
        print("   Sans métadonnées, nous ne savons pas quel graphe conserver.")
        print("\n🔧 Solutions :")
        print("   1. Chargez d'abord un dataset via l'onglet 'Datasets'")
        print("   2. Ou utilisez le nettoyage manuel via l'interface")
        sys.exit(1)

    print(f"✅ Métadonnées trouvées : {len(metadata)} moteur(s)")

    # Préparer les endpoints
    endpoints = {
        'virtuoso': {
            'url': 'http://localhost:8890/sparql',
            'auth': ('SPARQL', 'admin123')
        },
        'fuseki': {
            'url': 'http://localhost:3030/dataset/query',
            'auth': None
        }
    }

    # Nettoyer chaque triplestore
    for target, config in endpoints.items():
        if target in metadata:
            active_graph = metadata[target]['graph_uri']
            print(f"\n📌 {target.upper()} - Graphe actif : {active_graph}")
            clean_triplestore(
                name=target.upper(),
                endpoint=config['url'],
                active_graph_uri=active_graph,
                auth=config['auth']
            )
        else:
            print(f"\n⏭️  {target.upper()} - Aucun dataset actif (pas de nettoyage)")

    print(f"\n{'='*60}")
    print(f"✅ Nettoyage terminé")
    print(f"{'='*60}")
    print(f"\n💡 Vous pouvez maintenant exécuter le diagnostic pour vérifier :")
    print(f"   python diagnostic_datasets.py")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Nettoyage interrompu par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Erreur fatale : {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
