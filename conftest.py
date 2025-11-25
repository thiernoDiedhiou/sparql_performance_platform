"""
Configuration pytest pour les tests
"""

import pytest
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))


def pytest_configure(config):
    """Configuration pytest - enregistrer les markers personnalisés"""
    config.addinivalue_line(
        "markers", "integration: marque un test comme test d'intégration (nécessite des endpoints actifs)"
    )
    config.addinivalue_line(
        "markers", "slow: marque un test comme lent (peut prendre plusieurs secondes)"
    )
    config.addinivalue_line(
        "markers", "unit: marque un test comme test unitaire (rapide, sans dépendances externes)"
    )


@pytest.fixture(scope="session")
def mock_virtuoso_endpoint():
    """Fixture pour fournir un endpoint Virtuoso mock"""
    return "http://localhost:8890/sparql"


@pytest.fixture(scope="session")
def mock_fuseki_endpoint():
    """Fixture pour fournir un endpoint Fuseki mock"""
    return "http://localhost:3030/dataset/query"


@pytest.fixture
def sample_sparql_query():
    """Fixture pour fournir une requête SPARQL d'exemple"""
    return "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10"


@pytest.fixture
def sample_sparql_results():
    """Fixture pour fournir des résultats SPARQL mockés"""
    return {
        "results": {
            "bindings": [
                {
                    "s": {"type": "uri", "value": "http://example.org/subject1"},
                    "p": {"type": "uri", "value": "http://example.org/predicate1"},
                    "o": {"type": "literal", "value": "Object 1"}
                },
                {
                    "s": {"type": "uri", "value": "http://example.org/subject2"},
                    "p": {"type": "uri", "value": "http://example.org/predicate2"},
                    "o": {"type": "literal", "value": "Object 2"}
                }
            ]
        }
    }


@pytest.fixture
def sample_test_results():
    """Fixture pour fournir des résultats de tests mockés"""
    return [
        {
            "query_name": "Test Query 1",
            "engine": "Virtuoso",
            "iteration": 1,
            "execution_time": 0.5,
            "cpu_usage": 15.0,
            "memory_usage": 100.0,
            "success": True,
            "result_count": 10,
            "error": ""
        },
        {
            "query_name": "Test Query 1",
            "engine": "Jena Fuseki",
            "iteration": 1,
            "execution_time": 0.7,
            "cpu_usage": 20.0,
            "memory_usage": 150.0,
            "success": True,
            "result_count": 10,
            "error": ""
        }
    ]
