"""
Script interactif de nettoyage des graphes
Permet de sélectionner manuellement les graphes à supprimer
"""

import sys
import io
from SPARQLWrapper import SPARQLWrapper
import requests

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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
        print(f"[ERREUR] Impossible de lister les graphes: {str(e)}")
        return []

def count_graph_triplets(endpoint, graph_uri):
    """Compte les triplets dans un graphe"""
    try:
        query = f"SELECT (COUNT(*) AS ?count) WHERE {{ GRAPH <{graph_uri}> {{ ?s ?p ?o }} }}"
        sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(query)
        sparql.setReturnFormat('json')
        result = sparql.query().convert()

        if 'results' in result and 'bindings' in result['results']:
            if result['results']['bindings']:
                return int(result['results']['bindings'][0]['count']['value'])
        return 0
    except:
        return 0

def clear_graph(endpoint, graph_uri, auth=None):
    """Supprime un graphe spécifique"""
    try:
        # Déterminer le type d'endpoint
        if "virtuoso" in endpoint or "8890" in endpoint:
            param_name = "query"
            if auth is None:
                auth = ("SPARQL", "admin123")
        else:
            param_name = "update"
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
        print(f"   [ERREUR] {str(e)}")
        return False

def clean_triplestore_interactive(name, endpoint, auth=None):
    """Nettoyage interactif d'un triplestore"""
    print(f"\n{'='*70}")
    print(f"Nettoyage : {name}")
    print(f"Endpoint : {endpoint}")
    print(f"{'='*70}")

    # Lister tous les graphes
    print("\nRecherche des graphes...")
    graphs = list_all_graphs(endpoint)

    if not graphs:
        print("   [INFO] Aucun graphe trouvé")
        return

    print(f"\n{len(graphs)} graphe(s) trouvé(s) :\n")

    # Graphes système à ne jamais supprimer
    system_graphs = [
        "http://www.openlinksw.com/schemas/virtrdf#",
        "http://www.w3.org/ns/ldp#",
        "urn:activitystreams-owl:map"
    ]

    # Afficher tous les graphes avec leur nombre de triplets
    for i, graph in enumerate(graphs, 1):
        if graph in system_graphs:
            print(f"   {i}. [SYSTEME] {graph}")
        else:
            count = count_graph_triplets(endpoint, graph)
            print(f"   {i}. {graph}")
            print(f"      -> {count:,} triplets")

    # Demander quels graphes supprimer
    print(f"\n{'='*70}")
    print("SUPPRESSION DE GRAPHES")
    print(f"{'='*70}")
    print("\nOptions :")
    print("  1. Supprimer TOUS les graphes de dataset (conserve les systèmes)")
    print("  2. Sélectionner manuellement les graphes à supprimer")
    print("  3. Annuler et quitter")

    choice = input("\nVotre choix (1/2/3) : ").strip()

    if choice == "3":
        print("\n[INFO] Nettoyage annulé")
        return

    graphs_to_delete = []

    if choice == "1":
        # Supprimer tous sauf les systèmes
        for graph in graphs:
            if graph not in system_graphs:
                graphs_to_delete.append(graph)

    elif choice == "2":
        # Sélection manuelle
        print("\nEntrez les numéros des graphes à supprimer (séparés par des virgules)")
        print("Exemple : 1,3,5")
        numbers = input("\nNuméros : ").strip()

        try:
            indices = [int(n.strip()) - 1 for n in numbers.split(',')]
            for idx in indices:
                if 0 <= idx < len(graphs):
                    graph = graphs[idx]
                    if graph in system_graphs:
                        print(f"[ATTENTION] Ignoré (graphe système) : {graph}")
                    else:
                        graphs_to_delete.append(graph)
        except:
            print("[ERREUR] Format invalide")
            return
    else:
        print("[ERREUR] Choix invalide")
        return

    if not graphs_to_delete:
        print("\n[INFO] Aucun graphe à supprimer")
        return

    # Confirmation finale
    print(f"\n{len(graphs_to_delete)} graphe(s) sera/seront supprimé(s) :")
    for graph in graphs_to_delete:
        print(f"   - {graph}")

    confirm = input(f"\nConfirmez la suppression (oui/non) : ").strip().lower()

    if confirm not in ['oui', 'o', 'yes', 'y']:
        print("\n[INFO] Suppression annulée")
        return

    # Supprimer les graphes
    print(f"\nSuppression en cours...")
    success_count = 0
    fail_count = 0

    for i, graph in enumerate(graphs_to_delete, 1):
        print(f"   [{i}/{len(graphs_to_delete)}] {graph[:60]}...", end=" ")
        if clear_graph(endpoint, graph, auth):
            print("[OK]")
            success_count += 1
        else:
            print("[ECHEC]")
            fail_count += 1

    # Résumé
    print(f"\nRésumé :")
    print(f"   [OK] Supprimés : {success_count}")
    print(f"   [ECHEC] Échecs : {fail_count}")
    print(f"   [INFO] Conservés : {len(graphs) - len(graphs_to_delete)}")

def main():
    """Fonction principale"""
    print("╔" + "═"*68 + "╗")
    print("║  NETTOYAGE INTERACTIF DES GRAPHES                                ║")
    print("╚" + "═"*68 + "╝")

    # Configuration des endpoints
    endpoints = {
        'Virtuoso': {
            'url': 'http://localhost:8890/sparql',
            'auth': ('SPARQL', 'admin123')
        },
        'Fuseki': {
            'url': 'http://localhost:3030/dataset/query',
            'auth': None
        }
    }

    # Menu de sélection
    print("\nQuel triplestore voulez-vous nettoyer ?")
    print("  1. Virtuoso")
    print("  2. Fuseki")
    print("  3. Les deux")
    print("  4. Quitter")

    choice = input("\nVotre choix (1/2/3/4) : ").strip()

    if choice == "4":
        print("\n[INFO] Au revoir !")
        sys.exit(0)
    elif choice == "1":
        targets = ['Virtuoso']
    elif choice == "2":
        targets = ['Fuseki']
    elif choice == "3":
        targets = ['Virtuoso', 'Fuseki']
    else:
        print("[ERREUR] Choix invalide")
        sys.exit(1)

    # Nettoyer les triplestores sélectionnés
    for target in targets:
        config = endpoints[target]
        clean_triplestore_interactive(
            name=target,
            endpoint=config['url'],
            auth=config['auth']
        )

    print(f"\n{'='*70}")
    print("Nettoyage terminé !")
    print(f"{'='*70}")
    print("\nVous pouvez relancer le diagnostic pour vérifier :")
    print("   python diagnostic_datasets.py")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Nettoyage interrompu par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n[ERREUR] Erreur fatale : {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
