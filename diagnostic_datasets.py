"""
Script de diagnostic et nettoyage des datasets
Vérifie la cohérence entre métadonnées et données réelles
"""

import json
import sys
from pathlib import Path
from SPARQLWrapper import SPARQLWrapper
import requests

def load_metadata():
    """Charge les métadonnées des datasets"""
    metadata_file = Path("datasets_metadata.json")
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def count_triplets_direct(endpoint, graph_uri=None):
    """Compte les triplets directement via SPARQL"""
    try:
        if graph_uri:
            query = f"SELECT (COUNT(*) AS ?count) WHERE {{ GRAPH <{graph_uri}> {{ ?s ?p ?o }} }}"
        else:
            query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }"

        sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(query)
        sparql.setReturnFormat('json')
        result = sparql.query().convert()

        if 'results' in result and 'bindings' in result['results']:
            bindings = result['results']['bindings']
            if bindings and 'count' in bindings[0]:
                return int(bindings[0]['count']['value'])
        return 0
    except Exception as e:
        print(f"❌ Erreur lors du comptage: {str(e)}")
        return -1

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

def diagnose_triplestore(name, endpoint):
    """Diagnostic complet d'un triplestore"""
    print(f"\n{'='*60}")
    print(f"🔍 Diagnostic : {name}")
    print(f"   Endpoint : {endpoint}")
    print(f"{'='*60}")

    # Compter tous les triplets
    print("\n📊 Comptage total des triplets...")
    total = count_triplets_direct(endpoint)
    if total >= 0:
        print(f"   Total : {total:,} triplets")
    else:
        print(f"   ❌ Impossible de compter (endpoint inaccessible ?)")
        return None

    # Lister les graphes
    print("\n📋 Graphes disponibles...")
    graphs = list_all_graphs(endpoint)
    if graphs:
        print(f"   Trouvé {len(graphs)} graphe(s) :")
        for i, graph in enumerate(graphs, 1):
            # Compter dans chaque graphe
            count = count_triplets_direct(endpoint, graph)
            print(f"   {i}. {graph}")
            print(f"      → {count:,} triplets")
    else:
        print(f"   ℹ️  Aucun graphe nommé (ou tous dans le graphe par défaut)")

    return {
        'total': total,
        'graphs': graphs
    }

def compare_with_metadata(metadata):
    """Compare les métadonnées avec la réalité"""
    print(f"\n{'='*60}")
    print(f"🔍 Comparaison Métadonnées vs Réalité")
    print(f"{'='*60}")

    endpoints = {
        'virtuoso': 'http://localhost:8890/sparql',
        'fuseki': 'http://localhost:3030/dataset/query'
    }

    for target, endpoint in endpoints.items():
        if target in metadata:
            meta = metadata[target]
            print(f"\n📊 {target.upper()}")
            print(f"   Métadonnées :")
            print(f"   • Dataset : {meta['dataset_name']} ({meta['size']})")
            print(f"   • Triplets déclarés : {meta['triplet_count']:,}")
            print(f"   • Graph URI : {meta['graph_uri']}")

            # Vérifier la réalité
            print(f"\n   Réalité (comptage direct) :")

            # Compter dans le graphe spécifique
            count_graph = count_triplets_direct(endpoint, meta['graph_uri'])
            if count_graph >= 0:
                print(f"   • Triplets dans le graphe : {count_graph:,}")
            else:
                print(f"   • ❌ Impossible de compter dans le graphe")

            # Compter tous les triplets
            count_total = count_triplets_direct(endpoint)
            if count_total >= 0:
                print(f"   • Triplets totaux : {count_total:,}")
            else:
                print(f"   • ❌ Impossible de compter le total")

            # Analyser les écarts
            if count_graph >= 0:
                if count_graph == meta['triplet_count']:
                    print(f"   ✅ Cohérent : {count_graph:,} triplets")
                elif count_graph == 0:
                    print(f"   ❌ PROBLÈME : Graphe vide (métadonnées obsolètes)")
                else:
                    diff = abs(count_graph - meta['triplet_count'])
                    pct = (diff / max(meta['triplet_count'], 1)) * 100
                    if pct < 5:
                        print(f"   ⚠️  Légère différence : {count_graph:,} vs {meta['triplet_count']:,} ({pct:.1f}%)")
                    else:
                        print(f"   ❌ INCOHÉRENCE : {count_graph:,} vs {meta['triplet_count']:,} ({pct:.1f}%)")

def main():
    """Fonction principale"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🔍 DIAGNOSTIC DES DATASETS - SPARQL PLATFORM             ║")
    print("╚════════════════════════════════════════════════════════════╝")

    # Charger les métadonnées
    print("\n📂 Chargement des métadonnées...")
    metadata = load_metadata()

    if metadata:
        print(f"✅ Métadonnées trouvées : {len(metadata)} moteur(s)")
        for target, meta in metadata.items():
            print(f"   • {target} : {meta['dataset_name']} ({meta['size']}) - {meta['triplet_count']:,} triplets")
    else:
        print("⚠️  Aucune métadonnée trouvée (fichier datasets_metadata.json absent)")

    # Diagnostic Virtuoso
    virtuoso_info = diagnose_triplestore("Virtuoso", "http://localhost:8890/sparql")

    # Diagnostic Fuseki
    fuseki_info = diagnose_triplestore("Jena Fuseki", "http://localhost:3030/dataset/query")

    # Comparer avec les métadonnées
    if metadata:
        compare_with_metadata(metadata)

    # Recommandations
    print(f"\n{'='*60}")
    print(f"💡 RECOMMANDATIONS")
    print(f"{'='*60}")

    if metadata:
        print("\n🔧 Actions suggérées :")

        issues = []

        for target in ['virtuoso', 'fuseki']:
            if target in metadata:
                meta = metadata[target]
                endpoint = "http://localhost:8890/sparql" if target == "virtuoso" else "http://localhost:3030/dataset/query"
                count = count_triplets_direct(endpoint, meta['graph_uri'])

                if count == 0:
                    issues.append(f"   ❌ {target.upper()} : Graphe vide - Effacer les métadonnées et recharger")
                elif count != meta['triplet_count']:
                    diff_pct = abs(count - meta['triplet_count']) / max(meta['triplet_count'], 1) * 100
                    if diff_pct > 10:
                        issues.append(f"   ⚠️  {target.upper()} : Incohérence majeure ({diff_pct:.1f}%) - Recharger le dataset")

        if issues:
            for issue in issues:
                print(issue)
            print("\n   📋 Pour nettoyer et recharger :")
            print("   1. Allez dans l'onglet 'Datasets'")
            print("   2. Effacez les datasets problématiques (bouton 🗑️)")
            print("   3. Rechargez-les proprement")
        else:
            print("   ✅ Aucun problème majeur détecté")
    else:
        print("\n   ℹ️  Aucune métadonnée à vérifier")
        print("   💡 Chargez un dataset via l'onglet 'Datasets' pour commencer")

    print(f"\n{'='*60}")
    print(f"✅ Diagnostic terminé")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Diagnostic interrompu par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Erreur fatale : {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
