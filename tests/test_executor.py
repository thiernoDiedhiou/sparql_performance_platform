"""
Tests unitaires pour le module executor
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from SPARQLWrapper import SPARQLWrapper
from core.executor import QueryExecutor


class TestQueryExecutor:
    """Tests pour la classe QueryExecutor"""

    @pytest.fixture
    def executor(self):
        """Fixture pour créer une instance de QueryExecutor"""
        return QueryExecutor(timeout=10)

    def test_init_default_timeout(self):
        """Test l'initialisation avec timeout par défaut"""
        executor = QueryExecutor()
        assert executor.timeout == 60  # QUERY_TIMEOUT par défaut

    def test_init_custom_timeout(self):
        """Test l'initialisation avec timeout personnalisé"""
        executor = QueryExecutor(timeout=30)
        assert executor.timeout == 30

    def test_setup_endpoint(self, executor):
        """Test la configuration d'un endpoint SPARQL"""
        endpoint_url = "http://localhost:8890/sparql"
        query = "SELECT * WHERE { ?s ?p ?o } LIMIT 10"

        sparql = executor.setup_endpoint(endpoint_url, query)

        assert isinstance(sparql, SPARQLWrapper)
        assert sparql.endpoint == endpoint_url

    @patch('core.executor.SPARQLWrapper')
    def test_execute_query_success(self, mock_sparql_class, executor):
        """Test l'exécution réussie d'une requête"""
        # Mock du résultat SPARQL
        mock_results = {
            "results": {
                "bindings": [
                    {"s": {"type": "uri", "value": "http://example.org/subject1"}},
                    {"s": {"type": "uri", "value": "http://example.org/subject2"}}
                ]
            }
        }

        mock_sparql = MagicMock()
        mock_sparql.query().convert.return_value = mock_results
        mock_sparql_class.return_value = mock_sparql

        result = executor.execute_query("http://localhost:8890/sparql", "SELECT * WHERE { ?s ?p ?o }")

        assert result["success"] is True
        assert result["result_count"] == 2
        assert result["error"] == ""
        assert result["results"] == mock_results

    @patch('core.executor.SPARQLWrapper')
    def test_execute_query_failure(self, mock_sparql_class, executor):
        """Test l'exécution échouée d'une requête"""
        mock_sparql = MagicMock()
        mock_sparql.query().convert.side_effect = Exception("Connection timeout")
        mock_sparql_class.return_value = mock_sparql

        result = executor.execute_query("http://localhost:8890/sparql", "SELECT * WHERE { ?s ?p ?o }")

        assert result["success"] is False
        assert result["result_count"] == 0
        assert "Connection timeout" in result["error"]
        assert result["results"] is None

    @patch('core.executor.SPARQLWrapper')
    def test_execute_query_empty_results(self, mock_sparql_class, executor):
        """Test l'exécution d'une requête sans résultats"""
        mock_results = {
            "results": {
                "bindings": []
            }
        }

        mock_sparql = MagicMock()
        mock_sparql.query().convert.return_value = mock_results
        mock_sparql_class.return_value = mock_sparql

        result = executor.execute_query("http://localhost:8890/sparql", "SELECT * WHERE { ?s ?p ?o }")

        assert result["success"] is True
        assert result["result_count"] == 0

    @patch('core.executor.QueryExecutor.execute_query')
    def test_connectivity_online(self, mock_execute, executor):
        """Test la connectivité avec un endpoint en ligne"""
        mock_execute.return_value = {
            "success": True,
            "result_count": 1,
            "error": ""
        }

        result = executor.test_connectivity("http://localhost:8890/sparql")

        assert result["status"] == "online"
        assert "En ligne" in result["message"]

    @patch('core.executor.QueryExecutor.execute_query')
    def test_connectivity_error(self, mock_execute, executor):
        """Test la connectivité avec une erreur"""
        mock_execute.return_value = {
            "success": False,
            "error": "Connection refused"
        }

        result = executor.test_connectivity("http://localhost:8890/sparql")

        assert result["status"] == "error"
        assert "Erreur" in result["message"]

    @patch('core.executor.QueryExecutor.execute_query')
    def test_connectivity_offline(self, mock_execute, executor):
        """Test la connectivité avec un endpoint hors ligne"""
        mock_execute.side_effect = Exception("Network unreachable")

        result = executor.test_connectivity("http://localhost:8890/sparql")

        assert result["status"] == "offline"
        assert "Hors ligne" in result["message"]

    def test_validate_query_syntax_valid_select(self, executor):
        """Test la validation d'une requête SELECT valide"""
        query = "SELECT ?s WHERE { ?s ?p ?o }"
        result = executor.validate_query_syntax(query)

        assert result["valid"] is True
        assert result["error"] == ""

    def test_validate_query_syntax_valid_ask(self, executor):
        """Test la validation d'une requête ASK valide"""
        query = "ASK { ?s ?p ?o }"
        result = executor.validate_query_syntax(query)

        assert result["valid"] is True

    def test_validate_query_syntax_empty(self, executor):
        """Test la validation d'une requête vide"""
        result = executor.validate_query_syntax("")

        assert result["valid"] is False
        assert "vide" in result["error"]

    def test_validate_query_syntax_invalid_type(self, executor):
        """Test la validation d'une requête sans type reconnu"""
        query = "INVALID QUERY"
        result = executor.validate_query_syntax(query)

        assert result["valid"] is False
        assert "non reconnu" in result["error"]

    def test_validate_query_syntax_missing_where(self, executor):
        """Test la validation d'une requête SELECT sans WHERE"""
        query = "SELECT ?s { ?s ?p ?o }"
        result = executor.validate_query_syntax(query)

        assert result["valid"] is False
        assert "WHERE" in result["error"]

    def test_validate_query_syntax_unbalanced_braces(self, executor):
        """Test la validation avec accolades non équilibrées"""
        query = "SELECT ?s WHERE { ?s ?p ?o"
        result = executor.validate_query_syntax(query)

        assert result["valid"] is False
        assert "Accolades" in result["error"]

    def test_set_timeout(self, executor):
        """Test la modification du timeout"""
        new_timeout = 120
        executor.set_timeout(new_timeout)

        assert executor.timeout == new_timeout


class TestQueryExecutorIntegration:
    """Tests d'intégration (nécessitent un endpoint SPARQL actif)"""

    @pytest.mark.integration
    def test_real_endpoint_connectivity(self):
        """Test la connectivité avec un vrai endpoint (optionnel)"""
        executor = QueryExecutor()
        # Ce test ne s'exécute que si un endpoint est disponible
        result = executor.test_connectivity("http://localhost:8890/sparql")
        # Assertion flexible selon la disponibilité
        assert result["status"] in ["online", "offline", "error"]
