"""
Module d'exécution des requêtes SPARQL
"""

from SPARQLWrapper import SPARQLWrapper, JSON
from typing import Dict, Any
from config.settings import QUERY_TIMEOUT
from utils.helpers import log_message

class QueryExecutor:
    """Classe responsable de l'exécution des requêtes SPARQL"""
    
    def __init__(self, timeout: int = QUERY_TIMEOUT):
        """
        Initialise l'exécuteur de requêtes
        
        Args:
            timeout: Timeout pour les requêtes en secondes
        """
        self.timeout = timeout
    
    def setup_endpoint(self, endpoint_url: str, query: str) -> SPARQLWrapper:
        """
        Configure un endpoint SPARQL pour l'exécution d'une requête
        
        Args:
            endpoint_url: URL de l'endpoint SPARQL
            query: Requête SPARQL à configurer
            
        Returns:
            Instance configurée de SPARQLWrapper
        """
        sparql = SPARQLWrapper(endpoint_url)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        sparql.setTimeout(self.timeout)
        return sparql
    
    def execute_query(self, endpoint_url: str, query: str) -> Dict[str, Any]:
        """
        Exécute une requête SPARQL sur un endpoint donné
        
        Args:
            endpoint_url: URL de l'endpoint SPARQL
            query: Requête SPARQL à exécuter
            
        Returns:
            Dictionnaire contenant les résultats de l'exécution
        """
        try:
            sparql = self.setup_endpoint(endpoint_url, query)
            results = sparql.query().convert()
            
            # Compter les résultats
            result_count = 0
            if "results" in results and "bindings" in results["results"]:
                result_count = len(results["results"]["bindings"])
            
            return {
                "success": True,
                "result_count": result_count,
                "error": "",
                "results": results
            }
            
        except Exception as e:
            error_msg = str(e)
            log_message(f"Erreur lors de l'exécution de la requête: {error_msg}")
            
            return {
                "success": False,
                "result_count": 0,
                "error": error_msg,
                "results": None
            }
    
    def test_connectivity(self, endpoint_url: str) -> Dict[str, Any]:
        """
        Teste la connectivité d'un endpoint SPARQL
        
        Args:
            endpoint_url: URL de l'endpoint à tester
            
        Returns:
            Dictionnaire contenant le statut de connectivité
        """
        test_query = "SELECT ?s WHERE { ?s ?p ?o } LIMIT 1"
        
        try:
            result = self.execute_query(endpoint_url, test_query)
            
            if result["success"]:
                return {
                    "status": "online",
                    "message": "✅ En ligne",
                    "details": f"Requête de test réussie"
                }
            else:
                return {
                    "status": "error",
                    "message": f"❌ Erreur: {result['error']}",
                    "details": result['error']
                }
                
        except Exception as e:
            return {
                "status": "offline",
                "message": f"❌ Hors ligne: {str(e)}",
                "details": str(e)
            }
    
    def validate_query_syntax(self, query: str) -> Dict[str, Any]:
        """
        Valide la syntaxe d'une requête SPARQL (validation basique)
        
        Args:
            query: Requête SPARQL à valider
            
        Returns:
            Dictionnaire contenant le résultat de la validation
        """
        # Validation basique de la syntaxe SPARQL
        query_upper = query.upper().strip()
        
        # Vérifications basiques
        if not query_upper:
            return {"valid": False, "error": "Requête vide"}
        
        # Doit contenir SELECT, ASK, CONSTRUCT, ou DESCRIBE
        query_types = ["SELECT", "ASK", "CONSTRUCT", "DESCRIBE"]
        if not any(qtype in query_upper for qtype in query_types):
            return {"valid": False, "error": "Type de requête non reconnu"}
        
        # Doit contenir WHERE pour SELECT
        if "SELECT" in query_upper and "WHERE" not in query_upper:
            return {"valid": False, "error": "Clause WHERE manquante pour SELECT"}
        
        # Vérification des accolades équilibrées
        open_braces = query.count('{')
        close_braces = query.count('}')
        if open_braces != close_braces:
            return {"valid": False, "error": "Accolades non équilibrées"}
        
        return {"valid": True, "error": ""}
    
    def set_timeout(self, timeout: int):
        """
        Modifie le timeout des requêtes
        
        Args:
            timeout: Nouveau timeout en secondes
        """
        self.timeout = timeout
        log_message(f"Timeout mis à jour: {timeout} secondes")