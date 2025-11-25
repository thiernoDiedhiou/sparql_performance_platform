"""
Tests unitaires pour le module queries (catalog)
"""

import pytest
from queries.catalog import SPARQLQueryCatalog


class TestSPARQLQueryCatalog:
    """Tests pour la classe SPARQLQueryCatalog"""

    @pytest.fixture
    def catalog(self):
        """Fixture pour crï¿½er une instance de SPARQLQueryCatalog"""
        return SPARQLQueryCatalog()

    def test_init(self, catalog):
        """Test l'initialisation du catalogue"""
        assert catalog.lubm_queries is not None
        assert catalog.dbpedia_queries is not None
        assert catalog.generic_queries is not None

    def test_get_queries_by_type_lubm(self, catalog):
        """Test la rï¿½cupï¿½ration des requï¿½tes LUBM"""
        queries = catalog.get_queries_by_type("LUBM")

        assert isinstance(queries, dict)
        assert len(queries) > 0

    def test_get_queries_by_type_dbpedia(self, catalog):
        """Test la rï¿½cupï¿½ration des requï¿½tes DBpedia"""
        queries = catalog.get_queries_by_type("DBpedia")

        assert isinstance(queries, dict)
        assert len(queries) > 0

    def test_get_queries_by_type_bsbm(self, catalog):
        """Test la rï¿½cupï¿½ration des requï¿½tes BSBM (gï¿½nï¿½riques)"""
        queries = catalog.get_queries_by_type("BSBM")

        assert isinstance(queries, dict)
        # Devrait retourner les requï¿½tes gï¿½nï¿½riques

    def test_get_queries_by_type_unknown(self, catalog):
        """Test la rï¿½cupï¿½ration avec type inconnu (retourne gï¿½nï¿½riques)"""
        queries = catalog.get_queries_by_type("UnknownDataset")

        assert isinstance(queries, dict)
        # Devrait retourner les requï¿½tes gï¿½nï¿½riques par dï¿½faut

    def test_get_queries_by_category(self, catalog):
        """Test la rï¿½cupï¿½ration par catï¿½gorie"""
        queries = catalog.get_queries_by_category("LUBM", "simple")

        assert isinstance(queries, dict)

    def test_get_available_categories(self, catalog):
        """Test la rï¿½cupï¿½ration des catï¿½gories disponibles"""
        categories = catalog.get_available_categories("LUBM")

        assert isinstance(categories, list)
        assert len(categories) > 0
        assert "simple" in categories
        assert "jointure" in categories
        assert "aggregation" in categories

    def test_validate_query_valid_select(self, catalog):
        """Test la validation d'une requï¿½te SELECT valide"""
        query = "SELECT ?s ?p ?o WHERE { ?s ?p ?o }"
        result = catalog.validate_query(query)

        assert result["valid"] is True
        assert result["error"] == ""

    def test_validate_query_valid_ask(self, catalog):
        """Test la validation d'une requï¿½te ASK valide"""
        query = "ASK { ?s ?p ?o }"
        result = catalog.validate_query(query)

        assert result["valid"] is True

    def test_validate_query_valid_construct(self, catalog):
        """Test la validation d'une requï¿½te CONSTRUCT valide"""
        query = "CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }"
        result = catalog.validate_query(query)

        assert result["valid"] is True

    def test_validate_query_empty(self, catalog):
        """Test la validation d'une requï¿½te vide"""
        result = catalog.validate_query("")

        assert result["valid"] is False
        assert "vide" in result["error"]

    def test_validate_query_invalid(self, catalog):
        """Test la validation d'une requï¿½te invalide"""
        query = "INVALID SPARQL QUERY"
        result = catalog.validate_query(query)

        assert result["valid"] is False
        assert "non reconnu" in result["error"]

    def test_get_query_complexity_simple(self, catalog):
        """Test l'estimation de complexitï¿½ pour une requï¿½te simple"""
        query = "SELECT ?s WHERE { ?s ?p ?o }"
        complexity = catalog.get_query_complexity_estimate(query)

        assert complexity["level"] == "Faible"
        assert complexity["score"] == 0

    def test_get_query_complexity_with_filter(self, catalog):
        """Test l'estimation de complexitï¿½ avec FILTER"""
        query = "SELECT ?s WHERE { ?s ?p ?o . FILTER(?o > 10) }"
        complexity = catalog.get_query_complexity_estimate(query)

        assert complexity["score"] >= 1
        assert "Filtrage" in complexity["factors"]

    def test_get_query_complexity_with_aggregation(self, catalog):
        """Test l'estimation de complexitï¿½ avec GROUP BY"""
        query = "SELECT ?s (COUNT(?o) AS ?count) WHERE { ?s ?p ?o } GROUP BY ?s"
        complexity = catalog.get_query_complexity_estimate(query)

        assert complexity["score"] >= 1
        assert "Agrï¿½gation" in complexity["factors"]

    def test_get_query_complexity_with_optional(self, catalog):
        """Test l'estimation de complexitï¿½ avec OPTIONAL"""
        query = "SELECT ?s ?o WHERE { ?s ?p ?o . OPTIONAL { ?s ?p2 ?o2 } }"
        complexity = catalog.get_query_complexity_estimate(query)

        assert "Jointure optionnelle" in complexity["factors"]

    def test_get_query_complexity_with_union(self, catalog):
        """Test l'estimation de complexitï¿½ avec UNION"""
        query = """
        SELECT ?s WHERE {
            { ?s ?p1 ?o1 }
            UNION
            { ?s ?p2 ?o2 }
        }
        """
        complexity = catalog.get_query_complexity_estimate(query)

        assert "Union" in complexity["factors"]
        assert complexity["score"] >= 2

    def test_get_query_complexity_with_subquery(self, catalog):
        """Test l'estimation de complexitï¿½ avec sous-requï¿½te"""
        query = """
        SELECT ?s WHERE {
            ?s ?p ?o .
            FILTER EXISTS {
                SELECT ?s2 WHERE { ?s2 ?p2 ?o2 }
            }
        }
        """
        complexity = catalog.get_query_complexity_estimate(query)

        # Devrait dï¿½tecter la prï¿½sence de sous-requï¿½te
        assert complexity["score"] >= 3

    def test_get_query_complexity_very_complex(self, catalog):
        """Test l'estimation pour une requï¿½te trï¿½s complexe"""
        query = """
        SELECT ?s (COUNT(?o) AS ?count) WHERE {
            ?s ?p ?o .
            OPTIONAL { ?s ?p2 ?o2 }
            FILTER(?o > 10)
            {
                SELECT ?s2 WHERE { ?s2 ?p3 ?o3 }
            }
            UNION
            { ?s ?p4 ?o4 }
        }
        GROUP BY ?s
        ORDER BY DESC(?count)
        """
        complexity = catalog.get_query_complexity_estimate(query)

        assert complexity["level"] in ["ï¿½levï¿½e", "Trï¿½s ï¿½levï¿½e"]
        assert complexity["score"] > 5

    def test_estimate_execution_time_simple(self, catalog):
        """Test l'estimation du temps d'exï¿½cution simple"""
        time_estimate = catalog._estimate_execution_time(0)

        assert "< 1 seconde" in time_estimate

    def test_estimate_execution_time_medium(self, catalog):
        """Test l'estimation du temps d'exï¿½cution moyen"""
        time_estimate = catalog._estimate_execution_time(3)

        assert "1-5 secondes" in time_estimate

    def test_estimate_execution_time_high(self, catalog):
        """Test l'estimation du temps d'exï¿½cution ï¿½levï¿½"""
        time_estimate = catalog._estimate_execution_time(6)

        assert "5-30 secondes" in time_estimate

    def test_estimate_execution_time_very_high(self, catalog):
        """Test l'estimation du temps d'exï¿½cution trï¿½s ï¿½levï¿½"""
        time_estimate = catalog._estimate_execution_time(10)

        assert "> 30 secondes" in time_estimate


class TestSPARQLQueryCatalogIntegration:
    """Tests d'intï¿½gration pour le catalogue de requï¿½tes"""

    @pytest.fixture
    def catalog(self):
        return SPARQLQueryCatalog()

    def test_all_queries_are_valid(self, catalog):
        """Test que toutes les requï¿½tes prï¿½dï¿½finies sont valides"""
        dataset_types = ["LUBM", "DBpedia", "BSBM"]

        for dataset_type in dataset_types:
            queries = catalog.get_queries_by_type(dataset_type)

            for query_name, query_text in queries.items():
                validation = catalog.validate_query(query_text)
                assert validation["valid"], f"Requï¿½te invalide: {query_name} dans {dataset_type}"

    def test_query_complexity_consistency(self, catalog):
        """Test la cohï¿½rence des estimations de complexitï¿½"""
        simple_query = "SELECT ?s WHERE { ?s ?p ?o } LIMIT 10"
        complex_query = """
        SELECT ?s (COUNT(?o) AS ?count) WHERE {
            ?s ?p ?o .
            OPTIONAL { ?s ?p2 ?o2 }
            FILTER(?o > 10)
        }
        GROUP BY ?s
        ORDER BY DESC(?count)
        """

        simple_complexity = catalog.get_query_complexity_estimate(simple_query)
        complex_complexity = catalog.get_query_complexity_estimate(complex_query)

        # La requï¿½te complexe doit avoir un score plus ï¿½levï¿½
        assert complex_complexity["score"] > simple_complexity["score"]
