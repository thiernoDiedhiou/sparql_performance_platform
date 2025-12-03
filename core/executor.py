"""
Module d'exécution des requêtes SPARQL
Version améliorée avec support des graphes nommés (Named Graphs)
"""

from SPARQLWrapper import SPARQLWrapper, JSON
from typing import Dict, Any, Optional
import re
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
    
    def wrap_query_with_graph(self, query: str, graph_uri: str) -> str:
        """
        Wrappe une requête SPARQL avec une clause GRAPH pour interroger un graphe nommé

        Cette méthode est essentielle pour garantir des benchmarks équitables entre
        Virtuoso et Fuseki, car ils gèrent différemment le graphe par défaut.

        Args:
            query: Requête SPARQL originale
            graph_uri: URI du graphe nommé à interroger

        Returns:
            Requête modifiée avec clause GRAPH

        Example:
            >>> query = "SELECT ?s WHERE { ?s ?p ?o }"
            >>> graph_uri = "http://example.org/dataset"
            >>> wrapped = executor.wrap_query_with_graph(query, graph_uri)
            >>> # Résultat: SELECT ?s WHERE { GRAPH <http://example.org/dataset> { ?s ?p ?o } }
        """
        # Si la requête contient déjà GRAPH, ne pas modifier
        if "GRAPH" in query.upper():
            log_message("Requête contient déjà GRAPH, pas de wrapping", "debug")
            return query

        # Trouver la clause WHERE avec regex
        where_pattern = r'(WHERE\s*\{)'
        match = re.search(where_pattern, query, re.IGNORECASE | re.DOTALL)

        if not match:
            # Pas de WHERE trouvé, requête probablement ASK/CONSTRUCT sans WHERE
            log_message("Pas de clause WHERE trouvée, pas de wrapping", "debug")
            return query

        # Position de la clause WHERE
        where_start = match.start()
        where_end = match.end()

        # Extraire les parties de la requête
        before_where = query[:where_start]  # PREFIX, SELECT, etc.
        where_keyword = query[where_start:where_end]  # "WHERE {"

        # Trouver le contenu après WHERE { jusqu'au } final
        after_where_start = where_end

        # Compter les accolades pour trouver le } correspondant
        brace_count = 1
        i = after_where_start
        while i < len(query) and brace_count > 0:
            if query[i] == '{':
                brace_count += 1
            elif query[i] == '}':
                brace_count -= 1
            i += 1

        # Extraire le contenu du WHERE et ce qui suit
        where_content = query[after_where_start:i-1]  # Sans le } final
        after_where_block = query[i-1:]  # Du } final jusqu'à la fin

        # Reconstruire avec GRAPH
        wrapped_query = f"""{before_where}{where_keyword}
    GRAPH <{graph_uri}> {{
        {where_content.strip()}
    }}
{after_where_block}"""

        log_message(f"Requête wrappée avec GRAPH <{graph_uri}>", "debug")
        return wrapped_query

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
    
    def execute_query(self, endpoint_url: str, query: str,
                     graph_uri: Optional[str] = None,
                     skip_security_check: bool = False) -> Dict[str, Any]:
        """
        Exécute une requête SPARQL sur un endpoint donné avec validation de sécurité

        Version améliorée avec support des graphes nommés pour des benchmarks équitables.

        Args:
            endpoint_url: URL de l'endpoint SPARQL
            query: Requête SPARQL à exécuter
            graph_uri: URI du graphe nommé (optionnel, wrappe automatiquement la requête)
            skip_security_check: Si True, ignore la validation de sécurité (pour opérations internes)

        Returns:
            Dictionnaire contenant les résultats de l'exécution

        Note:
            Si graph_uri est fourni, la requête sera automatiquement wrappée avec
            GRAPH <graph_uri> { ... } pour garantir que les deux endpoints (Virtuoso et Fuseki)
            interrogent exactement les mêmes données.
        """
        try:
            # Wrapper avec GRAPH si graph_uri fourni
            original_query = query
            if graph_uri:
                query = self.wrap_query_with_graph(query, graph_uri)
                log_message(f"Requête wrappée avec graph_uri: {graph_uri[:50]}...", "debug")

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