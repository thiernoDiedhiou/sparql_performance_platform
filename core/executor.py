"""
Module d'exécution des requêtes SPARQL
"""

from SPARQLWrapper import SPARQLWrapper, JSON
from typing import Dict, Any
from config.settings import (
    QUERY_TIMEOUT,
    SECURITY_MAX_QUERY_LENGTH,
    SECURITY_MAX_NESTING_LEVEL
)
from utils.helpers import log_message
from utils.status_formatter import format_status

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
    
    def execute_query(self, endpoint_url: str, query: str, skip_security_check: bool = False) -> Dict[str, Any]:
        """
        Exécute une requête SPARQL sur un endpoint donné avec validation de sécurité

        Args:
            endpoint_url: URL de l'endpoint SPARQL
            query: Requête SPARQL à exécuter
            skip_security_check: Si True, ignore la validation de sécurité (pour opérations internes)

        Returns:
            Dictionnaire contenant les résultats de l'exécution
        """
        try:
            # Validation de sécurité (sauf si explicitement désactivée)
            if not skip_security_check:
                security_check = self.validate_query_security(query)
                if not security_check["valid"]:
                    log_message(f"⚠️ Requête bloquée pour raison de sécurité: {security_check['error']}", "warning")
                    return {
                        "success": False,
                        "result_count": 0,
                        "error": f"Validation de sécurité échouée: {security_check['error']}",
                        "results": None,
                        "security_blocked": True
                    }

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
                "results": results,
                "security_blocked": False
            }

        except Exception as e:
            error_msg = str(e)
            log_message(f"Erreur lors de l'exécution de la requête: {error_msg}")

            return {
                "success": False,
                "result_count": 0,
                "error": error_msg,
                "results": None,
                "security_blocked": False
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
            # Skip security check pour le test de connectivité
            result = self.execute_query(endpoint_url, test_query, skip_security_check=True)
            
            if result["success"]:
                return {
                    "status": "online",
                    "message": format_status("online", "Endpoint accessible"),
                    "details": "Query test successful"
                }
            else:
                return {
                    "status": "error",
                    "message": format_status("error", f"Connection error: {result['error']}"),
                    "details": result['error']
                }

        except Exception as e:
            return {
                "status": "offline",
                "message": format_status("offline", f"Endpoint unreachable: {str(e)}"),
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

        # Doit contenir WHERE ou { pour SELECT (SPARQL 1.1 permet WHERE optionnel)
        if "SELECT" in query_upper and "WHERE" not in query_upper and "{" not in query:
            return {"valid": False, "error": "Clause WHERE ou bloc {} manquant pour SELECT"}

        # Vérification des accolades équilibrées
        open_braces = query.count('{')
        close_braces = query.count('}')
        if open_braces != close_braces:
            return {"valid": False, "error": "Accolades non équilibrées"}

        return {"valid": True, "error": ""}

    def validate_query_security(self, query: str) -> Dict[str, Any]:
        """
        Valide la sécurité d'une requête SPARQL (protection anti-injection basique)

        Args:
            query: Requête SPARQL à valider

        Returns:
            Dictionnaire contenant le résultat de la validation sécurité
        """
        query_upper = query.upper().strip()

        # Liste de mots-clés potentiellement dangereux (opérations de modification)
        dangerous_keywords = [
            "INSERT", "DELETE", "DROP", "CREATE", "LOAD", "CLEAR",
            "COPY", "MOVE", "ADD"
        ]

        # Vérifier la présence de mots-clés dangereux (avec délimiteurs pour éviter faux-positifs)
        import re
        for keyword in dangerous_keywords:
            # Chercher le mot-clé comme mot complet, mais pas après ? (variable SPARQL)
            # Pattern: mot-clé non précédé de ? et avec limites de mots
            pattern = r'(?<!\?)\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, query_upper):
                return {
                    "valid": False,
                    "error": f"Opération '{keyword}' non autorisée - Seules les requêtes de lecture sont permises",
                    "security_issue": True
                }

        # Vérifier la longueur de la requête (protection DoS)
        if len(query) > SECURITY_MAX_QUERY_LENGTH:
            return {
                "valid": False,
                "error": f"Requête trop longue ({len(query)} caractères, max: {SECURITY_MAX_QUERY_LENGTH})",
                "security_issue": True
            }

        # Vérifier la complexité (nombre de clauses imbriquées)
        nesting_level = query.count('{')
        if nesting_level > SECURITY_MAX_NESTING_LEVEL:
            return {
                "valid": False,
                "error": f"Requête trop complexe ({nesting_level} niveaux d'imbrication, max: {SECURITY_MAX_NESTING_LEVEL})",
                "security_issue": True
            }

        return {"valid": True, "error": "", "security_issue": False}
    
    def set_timeout(self, timeout: int):
        """
        Modifie le timeout des requêtes
        
        Args:
            timeout: Nouveau timeout en secondes
        """
        self.timeout = timeout
        log_message(f"Timeout mis à jour: {timeout} secondes")