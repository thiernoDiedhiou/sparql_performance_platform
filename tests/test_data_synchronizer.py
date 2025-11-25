"""
Tests unitaires pour le module data_synchronizer
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from utils.data_synchronizer import DataSynchronizer


class TestDataSynchronizer:
    """Tests pour la classe DataSynchronizer"""

    @pytest.fixture
    def synchronizer(self):
        """Fixture pour créer une instance de DataSynchronizer"""
        return DataSynchronizer(
            virtuoso_endpoint="http://localhost:8890/sparql",
            fuseki_endpoint="http://localhost:3030/dataset/query"
        )

    def test_init(self, synchronizer):
        """Test l'initialisation du synchroniseur"""
        assert synchronizer.virtuoso_endpoint == "http://localhost:8890/sparql"
        assert synchronizer.fuseki_endpoint == "http://localhost:3030/dataset/query"
        assert synchronizer.fuseki_base_url == "http://localhost:3030/dataset"

    def test_extract_fuseki_base_url_with_query(self, synchronizer):
        """Test l'extraction de l'URL de base Fuseki avec /query"""
        url = synchronizer._extract_fuseki_base_url("http://localhost:3030/dataset/query")
        assert url == "http://localhost:3030/dataset"

    def test_extract_fuseki_base_url_with_sparql(self, synchronizer):
        """Test l'extraction de l'URL de base Fuseki avec /sparql"""
        url = synchronizer._extract_fuseki_base_url("http://localhost:3030/dataset/sparql")
        assert url == "http://localhost:3030/dataset"

    def test_extract_fuseki_base_url_already_base(self, synchronizer):
        """Test l'extraction quand l'URL est déjà une URL de base"""
        url = synchronizer._extract_fuseki_base_url("http://localhost:3030/dataset")
        assert url == "http://localhost:3030/dataset"

    @patch('utils.data_synchronizer.QueryExecutor')
    def test_count_triplets_success(self, mock_executor_class, synchronizer):
        """Test le comptage réussi des triplets"""
        mock_executor = MagicMock()
        mock_executor.execute_query.return_value = {
            "success": True,
            "results": {
                "results": {
                    "bindings": [
                        {"count": {"value": "12345"}}
                    ]
                }
            }
        }
        synchronizer.executor = mock_executor

        count = synchronizer.count_triplets("http://localhost:8890/sparql")

        assert count == 12345

    @patch('utils.data_synchronizer.QueryExecutor')
    def test_count_triplets_failure(self, mock_executor_class, synchronizer):
        """Test le comptage avec échec"""
        mock_executor = MagicMock()
        mock_executor.execute_query.return_value = {
            "success": False,
            "results": None
        }
        synchronizer.executor = mock_executor

        count = synchronizer.count_triplets("http://localhost:8890/sparql")

        assert count == 0

    @patch('utils.data_synchronizer.QueryExecutor')
    def test_count_triplets_empty_results(self, mock_executor_class, synchronizer):
        """Test le comptage avec résultats vides"""
        mock_executor = MagicMock()
        mock_executor.execute_query.return_value = {
            "success": True,
            "results": {
                "results": {
                    "bindings": []
                }
            }
        }
        synchronizer.executor = mock_executor

        count = synchronizer.count_triplets("http://localhost:8890/sparql")

        assert count == 0

    @patch('utils.data_synchronizer.QueryExecutor')
    def test_get_dataset_statistics_success(self, mock_executor_class, synchronizer):
        """Test la récupération réussie des statistiques"""
        mock_executor = MagicMock()

        # Mock des réponses pour chaque requête statistique
        def mock_execute_query(endpoint, query):
            if "COUNT(*)" in query or "COUNT(DISTINCT" in query:
                return {
                    "success": True,
                    "results": {
                        "results": {
                            "bindings": [{"count": {"value": "100"}}]
                        }
                    }
                }
            return {"success": False, "results": None}

        mock_executor.execute_query.side_effect = mock_execute_query
        mock_executor.test_connectivity.return_value = {"status": "online"}
        synchronizer.executor = mock_executor

        stats = synchronizer.get_dataset_statistics("http://localhost:8890/sparql")

        assert stats["accessible"] is True
        assert stats["total_triplets"] == 100
        assert stats["unique_subjects"] == 100
        assert stats["unique_predicates"] == 100

    @patch('utils.data_synchronizer.QueryExecutor')
    def test_get_dataset_statistics_offline(self, mock_executor_class, synchronizer):
        """Test les statistiques avec endpoint hors ligne"""
        mock_executor = MagicMock()
        mock_executor.test_connectivity.return_value = {"status": "offline"}
        synchronizer.executor = mock_executor

        stats = synchronizer.get_dataset_statistics("http://localhost:8890/sparql")

        assert stats["accessible"] is False
        assert stats["total_triplets"] == 0

    @patch('utils.data_synchronizer.SPARQLWrapper')
    def test_export_data_from_virtuoso_success(self, mock_sparql_class, synchronizer):
        """Test l'export réussi depuis Virtuoso"""
        mock_sparql = MagicMock()
        mock_sparql.query().convert.return_value = b"@prefix ex: <http://example.org/> .\nex:subject ex:predicate ex:object ."
        mock_sparql_class.return_value = mock_sparql

        with patch('streamlit.info'):
            turtle_data = synchronizer.export_data_from_virtuoso()

        assert turtle_data is not None
        assert "@prefix" in turtle_data
        assert "ex:subject" in turtle_data

    @patch('utils.data_synchronizer.SPARQLWrapper')
    def test_export_data_from_virtuoso_with_limit(self, mock_sparql_class, synchronizer):
        """Test l'export avec limite de triplets"""
        mock_sparql = MagicMock()
        mock_sparql.query().convert.return_value = b"@prefix ex: <http://example.org/> ."
        mock_sparql_class.return_value = mock_sparql

        with patch('streamlit.info'):
            turtle_data = synchronizer.export_data_from_virtuoso(limit=1000)

        assert turtle_data is not None
        # Vérifier que la requête CONSTRUCT contient LIMIT
        call_args = mock_sparql.setQuery.call_args
        assert "LIMIT 1000" in call_args[0][0]

    @patch('utils.data_synchronizer.SPARQLWrapper')
    def test_export_data_from_virtuoso_failure(self, mock_sparql_class, synchronizer):
        """Test l'échec d'export depuis Virtuoso"""
        mock_sparql = MagicMock()
        mock_sparql.query().convert.side_effect = Exception("Connection failed")
        mock_sparql_class.return_value = mock_sparql

        with patch('streamlit.info'), patch('streamlit.error'):
            turtle_data = synchronizer.export_data_from_virtuoso()

        assert turtle_data is None

    @patch('utils.data_synchronizer.requests.post')
    def test_clear_fuseki_dataset_success(self, mock_post, synchronizer):
        """Test le nettoyage réussi du dataset Fuseki"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        with patch('streamlit.info'):
            result = synchronizer.clear_fuseki_dataset()

        assert result is True

    @patch('utils.data_synchronizer.requests.post')
    def test_clear_fuseki_dataset_failure(self, mock_post, synchronizer):
        """Test l'échec du nettoyage du dataset Fuseki"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        with patch('streamlit.info'):
            result = synchronizer.clear_fuseki_dataset()

        assert result is False

    @patch('utils.data_synchronizer.requests.post')
    def test_upload_data_to_fuseki_success(self, mock_post, synchronizer):
        """Test l'upload réussi vers Fuseki"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        turtle_data = "@prefix ex: <http://example.org/> ."

        with patch('streamlit.info'):
            result = synchronizer.upload_data_to_fuseki(turtle_data)

        assert result is True

    @patch('utils.data_synchronizer.requests.post')
    def test_upload_data_to_fuseki_failure(self, mock_post, synchronizer):
        """Test l'échec de l'upload vers Fuseki"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        turtle_data = "@prefix ex: <http://example.org/> ."

        with patch('streamlit.info'), patch('streamlit.error'):
            result = synchronizer.upload_data_to_fuseki(turtle_data)

        assert result is False

    @patch('utils.data_synchronizer.DataSynchronizer.get_dataset_statistics')
    def test_verify_data_consistency_consistent(self, mock_get_stats, synchronizer):
        """Test la vérification avec données cohérentes"""
        mock_get_stats.side_effect = [
            {
                "accessible": True,
                "total_triplets": 1000,
                "unique_subjects": 100,
                "unique_predicates": 10,
                "classes": 5
            },
            {
                "accessible": True,
                "total_triplets": 1000,
                "unique_subjects": 100,
                "unique_predicates": 10,
                "classes": 5
            }
        ]

        with patch('streamlit.info'):
            report = synchronizer.verify_data_consistency()

        assert report["consistent"] is True
        assert len(report["differences"]) == 0

    @patch('utils.data_synchronizer.DataSynchronizer.get_dataset_statistics')
    def test_verify_data_consistency_inconsistent(self, mock_get_stats, synchronizer):
        """Test la vérification avec données incohérentes"""
        mock_get_stats.side_effect = [
            {
                "accessible": True,
                "total_triplets": 1000,
                "unique_subjects": 100,
                "unique_predicates": 10,
                "classes": 5
            },
            {
                "accessible": True,
                "total_triplets": 0,
                "unique_subjects": 0,
                "unique_predicates": 0,
                "classes": 0
            }
        ]

        with patch('streamlit.info'):
            report = synchronizer.verify_data_consistency()

        assert report["consistent"] is False
        assert len(report["differences"]) > 0
        assert "Synchroniser les données" in report["recommendations"][0]

    @patch('utils.data_synchronizer.DataSynchronizer.get_dataset_statistics')
    def test_verify_data_consistency_virtuoso_offline(self, mock_get_stats, synchronizer):
        """Test la vérification avec Virtuoso hors ligne"""
        mock_get_stats.return_value = {"accessible": False}

        with patch('streamlit.info'):
            report = synchronizer.verify_data_consistency()

        assert "Virtuoso n'est pas accessible" in report["recommendations"]

    @patch('utils.data_synchronizer.QueryExecutor')
    def test_auto_detect_dataset_format_lubm(self, mock_executor_class, synchronizer):
        """Test la détection automatique du format LUBM"""
        mock_executor = MagicMock()

        def mock_execute(endpoint, query):
            if "univ-bench.owl#University" in query:
                return {"success": True, "results": {"boolean": True}}
            return {"success": True, "results": {"boolean": False}}

        mock_executor.execute_query.side_effect = mock_execute
        synchronizer.executor = mock_executor

        format_detected = synchronizer.auto_detect_dataset_format("http://localhost:8890/sparql")

        assert "LUBM" in format_detected

    @patch('utils.data_synchronizer.QueryExecutor')
    def test_auto_detect_dataset_format_unknown(self, mock_executor_class, synchronizer):
        """Test la détection avec format inconnu"""
        mock_executor = MagicMock()
        mock_executor.execute_query.return_value = {
            "success": True,
            "results": {"boolean": False}
        }
        synchronizer.executor = mock_executor

        format_detected = synchronizer.auto_detect_dataset_format("http://localhost:8890/sparql")

        assert "générique" in format_detected or "inconnu" in format_detected


class TestDataSynchronizerIntegration:
    """Tests d'intégration pour la synchronisation complète"""

    @pytest.fixture
    def synchronizer(self):
        return DataSynchronizer(
            virtuoso_endpoint="http://localhost:8890/sparql",
            fuseki_endpoint="http://localhost:3030/dataset/query"
        )

    @patch('utils.data_synchronizer.DataSynchronizer.count_triplets')
    @patch('utils.data_synchronizer.DataSynchronizer.export_data_from_virtuoso')
    @patch('utils.data_synchronizer.DataSynchronizer.upload_data_to_fuseki')
    @patch('utils.data_synchronizer.DataSynchronizer.clear_fuseki_dataset')
    def test_synchronize_datasets_full_workflow(
        self, mock_clear, mock_upload, mock_export, mock_count, synchronizer
    ):
        """Test le workflow complet de synchronisation"""
        # Configuration des mocks
        mock_count.side_effect = [1000, 0, 1000]  # Virtuoso avant, Fuseki avant, Fuseki après
        mock_clear.return_value = True
        mock_export.return_value = "@prefix ex: <http://example.org/> ."
        mock_upload.return_value = True

        with patch('streamlit.subheader'), \
             patch('streamlit.write'), \
             patch('streamlit.columns'), \
             patch('streamlit.metric'), \
             patch('streamlit.warning'), \
             patch('streamlit.button', return_value=True), \
             patch('streamlit.spinner'), \
             patch('streamlit.success'), \
             patch('time.sleep'):

            result = synchronizer.synchronize_datasets(clear_target=True)

        assert result is True
        mock_clear.assert_called_once()
        mock_export.assert_called_once()
        mock_upload.assert_called_once()
