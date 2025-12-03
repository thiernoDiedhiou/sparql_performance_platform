"""
Classe principale pour gérer les tests de performance SPARQL
Version améliorée avec support des graphes nommés pour benchmarks équitables
"""

import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any, Optional
from core.executor import QueryExecutor
from core.metrics import MetricsCollector
from utils.helpers import log_message

class SPARQLPerformanceTester:
    """Classe principale pour effectuer les tests de performance SPARQL"""

    def __init__(self, virtuoso_endpoint: str, fuseki_endpoint: str,
                 virtuoso_graph_uri: Optional[str] = None,
                 fuseki_graph_uri: Optional[str] = None):
        """
        Initialise le testeur de performance SPARQL

        Args:
            virtuoso_endpoint: URL de l'endpoint Virtuoso
            fuseki_endpoint: URL de l'endpoint Jena Fuseki
            virtuoso_graph_uri: URI du graphe nommé Virtuoso (optionnel)
            fuseki_graph_uri: URI du graphe nommé Fuseki (optionnel)

        Note:
            Si les graph_uri sont fournis, toutes les requêtes seront automatiquement
            wrappées avec GRAPH <uri> { ... } pour garantir des benchmarks équitables
            entre Virtuoso et Fuseki.
        """
        self.virtuoso_endpoint = virtuoso_endpoint
        self.fuseki_endpoint = fuseki_endpoint
        self.virtuoso_graph_uri = virtuoso_graph_uri
        self.fuseki_graph_uri = fuseki_graph_uri
        self.results = {}
        self.current_test_results = []
        self.executor = QueryExecutor()
        self.metrics_collector = MetricsCollector()
        
    def execute_single_query(self, engine_name: str, endpoint_url: str,
                           query: str, iteration: int) -> Dict[str, Any]:
        """
        Exécute une seule requête SPARQL et collecte les métriques

        Args:
            engine_name: Nom du moteur SPARQL
            endpoint_url: URL de l'endpoint
            query: Requête SPARQL à exécuter
            iteration: Numéro d'itération

        Returns:
            Dictionnaire contenant les résultats et métriques
        """
        log_message(f"Exécution {iteration} sur {engine_name}")

        # Collecte des métriques de départ
        start_time = time.time()

        # Déterminer le graph_uri à utiliser selon l'endpoint
        graph_uri = None
        if endpoint_url == self.virtuoso_endpoint:
            graph_uri = self.virtuoso_graph_uri
        elif endpoint_url == self.fuseki_endpoint:
            graph_uri = self.fuseki_graph_uri

        # Exécution de la requête avec graph_uri si disponible
        query_result = self.executor.execute_query(endpoint_url, query, graph_uri=graph_uri)

        # Collecte des métriques de fin
        end_time = time.time()

        # Collecte des métriques système après l'exécution
        # Note: CPU et mémoire sont des valeurs instantanées, pas cumulatives
        current_metrics = self.metrics_collector.collect_system_metrics()

        # Calcul des métriques finales
        execution_time = end_time - start_time
        # Utiliser les valeurs actuelles (pas de soustraction pour les pourcentages)
        cpu_usage = current_metrics['cpu']
        memory_usage = current_metrics['memory']
        
        result = {
            "engine": engine_name,
            "iteration": iteration,
            "execution_time": execution_time,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "success": query_result['success'],
            "result_count": query_result['result_count'],
            "error": query_result['error']
        }
        
        self.current_test_results.append(result)
        return result
    
    def run_benchmark(self, query_name: str, query: str, 
                     num_iterations: int, warmup_iterations: int = 0, 
                     is_warmup: bool = False) -> pd.DataFrame:
        """
        Exécute un benchmark complet pour une requête donnée
        
        Args:
            query_name: Nom de la requête
            query: Requête SPARQL
            num_iterations: Nombre d'itérations
            warmup_iterations: Nombre d'itérations d'échauffement
            is_warmup: Indique si c'est une phase d'échauffement
            
        Returns:
            DataFrame contenant tous les résultats
        """
        if not is_warmup:
            self.current_test_results = []
            log_message(f"Début du benchmark pour: {query_name}")
        
        # Exécution sur Virtuoso
        for i in range(1, num_iterations + 1):
            self.execute_single_query("Virtuoso", self.virtuoso_endpoint, query, i)
            
        # Exécution sur Jena Fuseki
        for i in range(1, num_iterations + 1):
            self.execute_single_query("Jena Fuseki", self.fuseki_endpoint, query, i)
            
        if not is_warmup:
            self.results[query_name] = self.current_test_results
            # Ajouter le nom de la requête à chaque résultat
            for result in self.current_test_results:
                result["query_name"] = query_name
            
            log_message(f"Benchmark terminé pour: {query_name}")
            return pd.DataFrame(self.current_test_results)
        
        return pd.DataFrame()
    
    def run_concurrent_benchmark(self, query_name: str, query: str, 
                               num_iterations: int, concurrent_level: int) -> pd.DataFrame:
        """
        Exécute un benchmark avec des requêtes concurrentes
        
        Args:
            query_name: Nom de la requête
            query: Requête SPARQL
            num_iterations: Nombre d'itérations
            concurrent_level: Niveau de concurrence
            
        Returns:
            DataFrame contenant tous les résultats
        """
        self.current_test_results = []
        log_message(f"Début du benchmark concurrent pour: {query_name} (niveau: {concurrent_level})")
        
        def run_concurrent_query(engine, endpoint, query, iteration):
            return self.execute_single_query(f"{engine} (Concurrent)", endpoint, query, iteration)
        
        with ThreadPoolExecutor(max_workers=concurrent_level) as executor:
            # Requêtes concurrentes pour Virtuoso
            virtuoso_futures = [
                executor.submit(run_concurrent_query, "Virtuoso", self.virtuoso_endpoint, query, i)
                for i in range(1, num_iterations + 1)
            ]
            
            # Requêtes concurrentes pour Jena Fuseki
            fuseki_futures = [
                executor.submit(run_concurrent_query, "Jena Fuseki", self.fuseki_endpoint, query, i)
                for i in range(1, num_iterations + 1)
            ]
            
            # Attendre la completion de tous les futures
            for future in virtuoso_futures + fuseki_futures:
                future.result()
        
        self.results[f"{query_name} (Concurrent)"] = self.current_test_results
        
        # Ajouter le nom de la requête à chaque résultat
        for result in self.current_test_results:
            result["query_name"] = f"{query_name} (Concurrent)"
        
        log_message(f"Benchmark concurrent terminé pour: {query_name}")
        return pd.DataFrame(self.current_test_results)
    
    def get_aggregated_results(self) -> pd.DataFrame:
        """
        Agrège tous les résultats de tests effectués
        
        Returns:
            DataFrame contenant tous les résultats agrégés
        """
        all_results = []
        for query_name, results in self.results.items():
            for result in results:
                result["query_name"] = query_name
                all_results.append(result)
        
        return pd.DataFrame(all_results)
    
    def clear_results(self):
        """Efface tous les résultats stockés"""
        self.results = {}
        self.current_test_results = []
        log_message("Résultats effacés")