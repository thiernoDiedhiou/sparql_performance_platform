"""
Tests unitaires pour le module helpers
"""

import pytest
from unittest.mock import patch
from utils.helpers import (
    log_message,
    format_duration,
    format_memory_size,
    safe_divide,
    validate_endpoint_url
)


class TestHelpers:
    """Tests pour les fonctions utilitaires"""

    def test_format_duration_milliseconds(self):
        """Test le formatage de durée en millisecondes"""
        result = format_duration(0.5)
        assert "500" in result
        assert "ms" in result

    def test_format_duration_seconds(self):
        """Test le formatage de durée en secondes"""
        result = format_duration(5.5)
        assert "5.5" in result or "5.50" in result
        assert "s" in result

    def test_format_duration_minutes(self):
        """Test le formatage de durée en minutes"""
        result = format_duration(125)  # 2 minutes 5 secondes
        assert "2" in result
        assert "m" in result  # Le format utilise "m" au lieu de "min"

    def test_format_duration_hours(self):
        """Test le formatage de durée en heures"""
        result = format_duration(3665)  # 1h 1min 5s
        assert "1" in result
        assert "h" in result

    def test_format_duration_zero(self):
        """Test le formatage de durée nulle"""
        result = format_duration(0)
        assert "0" in result

    def test_format_memory_size_bytes(self):
        """Test le formatage de mémoire en bytes"""
        result = format_memory_size(512)
        assert "512" in result
        assert "B" in result

    def test_format_memory_size_kb(self):
        """Test le formatage de mémoire en KB"""
        result = format_memory_size(2048)
        assert "2" in result
        assert "KB" in result or "Ko" in result

    def test_format_memory_size_mb(self):
        """Test le formatage de mémoire en MB"""
        result = format_memory_size(1024 * 1024 * 5)
        assert "5" in result
        assert "MB" in result or "Mo" in result

    def test_format_memory_size_gb(self):
        """Test le formatage de mémoire en GB"""
        result = format_memory_size(1024 * 1024 * 1024 * 2)
        assert "2" in result
        assert "GB" in result or "Go" in result

    def test_format_memory_size_zero(self):
        """Test le formatage de mémoire nulle"""
        result = format_memory_size(0)
        assert "0" in result

    def test_safe_divide_normal(self):
        """Test la division sécurisée normale"""
        result = safe_divide(10, 2)
        assert result == 5.0

    def test_safe_divide_by_zero(self):
        """Test la division par zéro"""
        result = safe_divide(10, 0)
        assert result == 0.0

    def test_safe_divide_negative(self):
        """Test la division avec nombres négatifs"""
        result = safe_divide(-10, 2)
        assert result == -5.0

    def test_safe_divide_float(self):
        """Test la division avec nombres à virgule"""
        result = safe_divide(7.5, 2.5)
        assert result == 3.0

    def test_validate_endpoint_url_valid_http(self):
        """Test la validation d'URL HTTP valide"""
        result = validate_endpoint_url("http://localhost:8890/sparql")
        assert result["valid"] is True

    def test_validate_endpoint_url_valid_https(self):
        """Test la validation d'URL HTTPS valide"""
        result = validate_endpoint_url("https://dbpedia.org/sparql")
        assert result["valid"] is True

    def test_validate_endpoint_url_missing_protocol(self):
        """Test la validation d'URL sans protocole"""
        result = validate_endpoint_url("localhost:8890/sparql")
        assert result["valid"] is False

    def test_validate_endpoint_url_empty(self):
        """Test la validation d'URL vide"""
        result = validate_endpoint_url("")
        assert result["valid"] is False

    def test_validate_endpoint_url_invalid_protocol(self):
        """Test la validation d'URL avec protocole invalide"""
        result = validate_endpoint_url("ftp://localhost:8890/sparql")
        assert result["valid"] is False

    @patch('utils.helpers.logger')
    def test_log_message_info(self, mock_logger):
        """Test le logging d'un message info"""
        log_message("Test message", level="info")
        mock_logger.info.assert_called_once()

    @patch('utils.helpers.logger')
    def test_log_message_error(self, mock_logger):
        """Test le logging d'un message erreur"""
        log_message("Error message", level="error")
        mock_logger.error.assert_called_once()

    @patch('utils.helpers.logger')
    def test_log_message_warning(self, mock_logger):
        """Test le logging d'un message warning"""
        log_message("Warning message", level="warning")
        mock_logger.warning.assert_called_once()


class TestHelpersEdgeCases:
    """Tests pour les cas limites des helpers"""

    def test_format_duration_very_large(self):
        """Test le formatage d'une très grande durée"""
        result = format_duration(1000000)  # ~11.5 jours
        # Devrait gérer les grandes valeurs sans erreur
        assert isinstance(result, str)

    def test_format_memory_size_very_large(self):
        """Test le formatage d'une très grande taille mémoire"""
        result = format_memory_size(1024 * 1024 * 1024 * 1024)  # 1 TB
        assert "TB" in result or "To" in result

    def test_safe_divide_both_zero(self):
        """Test la division de zéro par zéro"""
        result = safe_divide(0, 0)
        assert result == 0.0

    def test_safe_divide_very_small(self):
        """Test la division avec très petits nombres"""
        result = safe_divide(0.000001, 0.000002)
        assert result == 0.5

    def test_validate_endpoint_url_with_port(self):
        """Test la validation d'URL avec port spécifique"""
        result = validate_endpoint_url("http://localhost:8890/sparql")
        assert result["valid"] is True

    def test_validate_endpoint_url_with_path(self):
        """Test la validation d'URL avec chemin complexe"""
        result = validate_endpoint_url("http://example.org/rdf/sparql/endpoint")
        assert result["valid"] is True
