"""
Composant pour vérifier la connectivité des endpoints SPARQL
"""

import requests
from typing import Dict, Any
from core.executor import QueryExecutor
from config.settings import CONNECTIVITY_TIMEOUT
from utils.helpers import log_message

class ConnectivityChecker:
    """Classe pour vérifier la connectivité des endpoints SPARQL"""
    
    def __init__(self, timeout: int = CONNECTIVITY_TIMEOUT):
        """
        Initialise le vérificateur de connectivité
        
        Args:
            timeout: Timeout pour les tests de connectivité
        """
        self.timeout = timeout
        self.executor = QueryExecutor(timeout=timeout)
    
    def test_endpoint(self, endpoint_url: str, engine_name: str = "Unknown") -> Dict[str, Any]:
        """
        Teste la connectivité d'un endpoint SPARQL
        
        Args:
            endpoint_url: URL de l'endpoint à tester
            engine_name: Nom du moteur pour les logs
            
        Returns:
            Dictionnaire contenant le statut de connectivité
        """
        log_message(f"Test de connectivité pour {engine_name}: {endpoint_url}")
        
        try:
            # Test basique avec une requête simple
            connectivity_result = self.executor.test_connectivity(endpoint_url)
            
            if connectivity_result["status"] == "online":
                # Test plus approfondi avec comptage
                detailed_result = self._test_detailed_connectivity(endpoint_url)
                
                return {
                    "status": "online",
                    "message": f"✅ En ligne ({detailed_result['result_info']})",
                    "details": {
                        "response_time": detailed_result.get("response_time", "N/A"),
                        "triple_count": detailed_result.get("triple_count", "N/A"),
                        "server_info": detailed_result.get("server_info", "N/A")
                    }
                }
            else:
                return connectivity_result
                
        except Exception as e:
            error_msg = str(e)
            log_message(f"Erreur de connectivité pour {engine_name}: {error_msg}", "error")
            
            return {
                "status": "error",
                "message": f"❌ Erreur: {error_msg}",
                "details": {"error": error_msg}
            }
    
    def _test_detailed_connectivity(self, endpoint_url: str) -> Dict[str, Any]:
        """
        Effectue un test de connectivité détaillé
        
        Args:
            endpoint_url: URL de l'endpoint
            
        Returns:
            Dictionnaire avec les détails du test
        """
        import time
        
        # Requête pour compter les triplets
        count_query = """
        SELECT (COUNT(*) AS ?count)
        WHERE {
            ?s ?p ?o .
        }
        """
        
        try:
            start_time = time.time()
            result = self.executor.execute_query(endpoint_url, count_query)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # en millisecondes
            
            if result["success"] and result["results"]:
                bindings = result["results"].get("results", {}).get("bindings", [])
                if bindings:
                    count = bindings[0].get("count", {}).get("value", "0")
                    return {
                        "result_info": f"{count} triplets",
                        "response_time": f"{response_time:.2f}ms",
                        "triple_count": count
                    }
            
            return {
                "result_info": "Endpoint accessible",
                "response_time": f"{response_time:.2f}ms",
                "triple_count": "N/A"
            }
            
        except Exception as e:
            return {
                "result_info": "Test basique réussi",
                "response_time": "N/A",
                "triple_count": "N/A",
                "error": str(e)
            }
    
    def test_endpoints_batch(self, endpoints: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """
        Teste plusieurs endpoints en parallèle
        
        Args:
            endpoints: Dictionnaire {nom: url} des endpoints à tester
            
        Returns:
            Dictionnaire des résultats par endpoint
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=len(endpoints)) as executor:
            # Soumettre tous les tests
            future_to_name = {
                executor.submit(self.test_endpoint, url, name): name 
                for name, url in endpoints.items()
            }
            
            # Collecter les résultats
            for future in as_completed(future_to_name):
                endpoint_name = future_to_name[future]
                try:
                    results[endpoint_name] = future.result()
                except Exception as e:
                    results[endpoint_name] = {
                        "status": "error",
                        "message": f"❌ Erreur lors du test: {str(e)}",
                        "details": {"error": str(e)}
                    }
        
        return results
    
    def get_endpoint_info(self, endpoint_url: str) -> Dict[str, Any]:
        """
        Récupère des informations détaillées sur un endpoint
        
        Args:
            endpoint_url: URL de l'endpoint
            
        Returns:
            Dictionnaire contenant les informations de l'endpoint
        """
        info_queries = {
            "version": "SELECT * WHERE { ?s ?p ?o } LIMIT 1",
            "namespaces": """
                SELECT DISTINCT ?prefix ?namespace
                WHERE {
                    ?s ?p ?o .
                    BIND(SUBSTR(STR(?p), 1, STRLASTOF(STR(?p), "#")) AS ?namespace)
                    BIND(SUBSTR(STR(?p), 1, STRLASTOF(STR(?p), "/")) AS ?prefix)
                }
                LIMIT 10
            """,
            "classes": """
                SELECT (COUNT(DISTINCT ?class) AS ?classCount)
                WHERE {
                    ?s a ?class .
                }
            """,
            "properties": """
                SELECT (COUNT(DISTINCT ?property) AS ?propCount)
                WHERE {
                    ?s ?property ?o .
                }
            """
        }
        
        endpoint_info = {
            "url": endpoint_url,
            "accessible": False,
            "statistics": {}
        }
        
        try:
            # Test de base
            connectivity = self.test_endpoint(endpoint_url)
            endpoint_info["accessible"] = connectivity["status"] == "online"
            
            if endpoint_info["accessible"]:
                # Exécuter les requêtes d'information
                for info_type, query in info_queries.items():
                    try:
                        result = self.executor.execute_query(endpoint_url, query)
                        if result["success"]:
                            endpoint_info["statistics"][info_type] = result["result_count"]
                    except Exception:
                        endpoint_info["statistics"][info_type] = "N/A"
            
        except Exception as e:
            endpoint_info["error"] = str(e)
        
        return endpoint_info
    
    def benchmark_endpoint_response(self, endpoint_url: str, iterations: int = 5) -> Dict[str, Any]:
        """
        Benchmark les temps de réponse d'un endpoint
        
        Args:
            endpoint_url: URL de l'endpoint
            iterations: Nombre de tests à effectuer
            
        Returns:
            Statistiques de performance de l'endpoint
        """
        import time
        import statistics
        
        simple_query = "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10"
        response_times = []
        
        for i in range(iterations):
            try:
                start_time = time.time()
                result = self.executor.execute_query(endpoint_url, simple_query)
                end_time = time.time()
                
                if result["success"]:
                    response_time = (end_time - start_time) * 1000  # en ms
                    response_times.append(response_time)
                
            except Exception:
                continue
        
        if response_times:
            return {
                "iterations": len(response_times),
                "avg_response_time": statistics.mean(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "std_response_time": statistics.stdev(response_times) if len(response_times) > 1 else 0,
                "success_rate": (len(response_times) / iterations) * 100
            }
        else:
            return {
                "iterations": 0,
                "avg_response_time": 0,
                "min_response_time": 0,
                "max_response_time": 0,
                "std_response_time": 0,
                "success_rate": 0
            }