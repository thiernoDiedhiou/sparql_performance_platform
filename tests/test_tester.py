"""
Tests unitaires pour le module tester
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from core.tester import SPARQLPerformanceTester


class TestSPARQLPerformanceTester:
    """Tests pour la classe SPARQLPerformanceTester"""

    @pytest.fixture
    def tester(self):
        """Fixture pour crï¿½er une instance de SPARQLPerformanceTester"""
        return SPARQLPerformanceTester(
            virtuoso_endpoint="http://localhost:8890/sparql",
            fuseki_endpoint="http://localhost:3030/dataset/query"
        )

    def test_init(self, tester):
        """Test l'initialisation du testeur"""
        assert tester.virtuoso_endpoint == "http://localhost:8890/sparql"
        assert tester.fuseki_endpoint == "http://localhost:3030/dataset/query"
        assert isinstance(tester.results, dict)
        assert isinstance(tester.current_test_results, list)

    @patch('core.tester.MetricsCollector')
    @patch('core.tester.QueryExecutor')
    def test_execute_single_query_success(self, mock_executor_class, mock_metrics_class, tester):
        """Test l'exï¿½cution rï¿½ussie d'une seule requï¿½te"""
        # Mock du QueryExecutor
        mock_executor = MagicMock()
        mock_executor.execute_query.return_value = {
            "success": True,
            "result_count": 10,
            "error": ""
        }
        tester.executor = mock_executor

        # Mock du MetricsCollector
        mock_metrics = MagicMock()
        mock_metrics.collect_system_metrics.return_value = {
            "cpu": 20.0,
            "memory": 500.0
        }
        tester.metrics_collector = mock_metrics

        result = tester.execute_single_query(
            "Virtuoso",
            "http://localhost:8890/sparql",
            "SELECT * WHERE { ?s ?p ?o }",
            1
        )

        assert result["engine"] == "Virtuoso"
        assert result["iteration"] == 1
        assert result["success"] is True
        assert result["result_count"] == 10
        assert "execution_time" in result
        assert "cpu_usage" in result
        assert "memory_usage" in result

    @patch('core.tester.MetricsCollector')
    @patch('core.tester.QueryExecutor')
    def test_execute_single_query_failure(self, mock_executor_class, mock_metrics_class, tester):
        """Test l'exï¿½cution ï¿½chouï¿½e d'une requï¿½te"""
        mock_executor = MagicMock()
        mock_executor.execute_query.return_value = {
            "success": False,
            "result_count": 0,
            "error": "Timeout"
        }
        tester.executor = mock_executor

        mock_metrics = MagicMock()
        mock_metrics.collect_system_metrics.return_value = {
            "cpu": 10.0,
            "memory": 300.0
        }
        tester.metrics_collector = mock_metrics

        result = tester.execute_single_query(
            "Fuseki",
            "http://localhost:3030/dataset/query",
            "SELECT * WHERE { ?s ?p ?o }",
            1
        )

        assert result["success"] is False
        assert result["error"] == "Timeout"
        assert result["result_count"] == 0

    @patch('core.tester.SPARQLPerformanceTester.execute_single_query')
    def test_run_benchmark(self, mock_execute, tester):
        """Test l'exï¿½cution d'un benchmark complet"""
        mock_execute.return_value = {
            "engine": "Virtuoso",
            "iteration": 1,
            "execution_time": 0.5,
            "cpu_usage": 15.0,
            "memory_usage": 100.0,
            "success": True,
            "result_count": 10,
            "error": ""
        }

        query_name = "Test Query"
        query = "SELECT * WHERE { ?s ?p ?o } LIMIT 10"
        num_iterations = 3

        df = tester.run_benchmark(query_name, query, num_iterations)

        # Vï¿½rifier que execute_single_query a ï¿½tï¿½ appelï¿½ le bon nombre de fois
        # 2 moteurs x 3 itï¿½rations = 6 appels
        assert mock_execute.call_count == 6

        # Vï¿½rifier que les rï¿½sultats sont stockï¿½s
        assert query_name in tester.results

        # Vï¿½rifier que le DataFrame est retournï¿½
        assert isinstance(df, pd.DataFrame)
        assert len(tester.current_test_results) == 6

    @patch('core.tester.SPARQLPerformanceTester.execute_single_query')
    def test_run_benchmark_with_warmup(self, mock_execute, tester):
        """Test un benchmark avec itï¿½rations d'ï¿½chauffement"""
        mock_execute.return_value = {
            "engine": "Virtuoso",
            "iteration": 1,
            "execution_time": 0.5,
            "success": True,
            "result_count": 5,
            "cpu_usage": 10.0,
            "memory_usage": 50.0,
            "error": ""
        }

        # Phase d'ï¿½chauffement
        df_warmup = tester.run_benchmark(
            "Warmup Query",
            "SELECT * WHERE { ?s ?p ?o }",
            num_iterations=2,
            is_warmup=True
        )

        # Le DataFrame de warmup devrait ï¿½tre vide
        assert df_warmup.empty

        # Les rï¿½sultats de warmup ne devraient pas ï¿½tre dans self.results
        assert "Warmup Query" not in tester.results

    @patch('core.tester.ThreadPoolExecutor')
    @patch('core.tester.SPARQLPerformanceTester.execute_single_query')
    def test_run_concurrent_benchmark(self, mock_execute, mock_executor_class, tester):
        """Test un benchmark avec requï¿½tes concurrentes"""
        mock_execute.return_value = {
            "engine": "Virtuoso (Concurrent)",
            "iteration": 1,
            "execution_time": 0.3,
            "success": True,
            "result_count": 10,
            "cpu_usage": 50.0,
            "memory_usage": 200.0,
            "error": ""
        }

        # Mock du ThreadPoolExecutor
        mock_executor = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = mock_execute.return_value
        mock_executor.submit.return_value = mock_future
        mock_executor.__enter__.return_value = mock_executor
        mock_executor.__exit__.return_value = False
        mock_executor_class.return_value = mock_executor

        df = tester.run_concurrent_benchmark(
            "Concurrent Test",
            "SELECT * WHERE { ?s ?p ?o }",
            num_iterations=2,
            concurrent_level=3
        )

        # Vï¿½rifier que les rï¿½sultats sont stockï¿½s
        assert "Concurrent Test (Concurrent)" in tester.results
        assert isinstance(df, pd.DataFrame)

    def test_get_aggregated_results(self, tester):
        """Test l'agrï¿½gation de tous les rï¿½sultats"""
        # Simuler des rï¿½sultats de tests
        tester.results = {
            "Query 1": [
                {"engine": "Virtuoso", "execution_time": 0.5, "success": True},
                {"engine": "Fuseki", "execution_time": 0.7, "success": True}
            ],
            "Query 2": [
                {"engine": "Virtuoso", "execution_time": 0.3, "success": True},
                {"engine": "Fuseki", "execution_time": 0.4, "success": True}
            ]
        }

        df = tester.get_aggregated_results()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 4
        assert "query_name" in df.columns
        assert "Query 1" in df["query_name"].values
        assert "Query 2" in df["query_name"].values

    def test_get_aggregated_results_empty(self, tester):
        """Test l'agrï¿½gation sans rï¿½sultats"""
        df = tester.get_aggregated_results()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_clear_results(self, tester):
        """Test l'effacement des rï¿½sultats"""
        # Ajouter des rï¿½sultats
        tester.results = {"Query 1": [{"test": "data"}]}
        tester.current_test_results = [{"test": "data"}]

        # Effacer
        tester.clear_results()

        assert len(tester.results) == 0
        assert len(tester.current_test_results) == 0


class TestSPARQLPerformanceTesterEdgeCases:
    """Tests pour les cas limites"""

    @pytest.fixture
    def tester(self):
        return SPARQLPerformanceTester(
            virtuoso_endpoint="http://localhost:8890/sparql",
            fuseki_endpoint="http://localhost:3030/dataset/query"
        )

    @patch('core.tester.SPARQLPerformanceTester.execute_single_query')
    def test_run_benchmark_zero_iterations(self, mock_execute, tester):
        """Test un benchmark avec 0 itï¿½rations"""
        df = tester.run_benchmark("Test", "SELECT * WHERE { ?s ?p ?o }", 0)

        # Ne devrait pas appeler execute_single_query
        mock_execute.assert_not_called()
        assert isinstance(df, pd.DataFrame)

    @patch('core.tester.MetricsCollector')
    @patch('core.tester.QueryExecutor')
    def test_execute_query_with_zero_cpu_memory(self, mock_executor_class, mock_metrics_class, tester):
        """Test avec des mï¿½triques CPU/mï¿½moire nulles"""
        mock_executor = MagicMock()
        mock_executor.execute_query.return_value = {
            "success": True,
            "result_count": 0,
            "error": ""
        }
        tester.executor = mock_executor

        mock_metrics = MagicMock()
        mock_metrics.collect_system_metrics.return_value = {
            "cpu": 0.0,
            "memory": 0.0
        }
        tester.metrics_collector = mock_metrics

        result = tester.execute_single_query(
            "Virtuoso",
            "http://localhost:8890/sparql",
            "SELECT * WHERE { ?s ?p ?o }",
            1
        )

        assert result["cpu_usage"] == 0.0
        assert result["memory_usage"] == 0.0
