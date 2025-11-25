"""
Classe de base abstraite pour toutes les requêtes SPARQL
"""

from abc import ABC, abstractmethod
from typing import Dict


class BaseQueries(ABC):
    """Classe de base abstraite pour gérer les requêtes SPARQL"""

    def __init__(self):
        """Initialise la classe de base"""
        self.prefix = ""

    @abstractmethod
    def get_simple_queries(self) -> Dict[str, str]:
        """Retourne les requêtes simples - À implémenter dans les sous-classes"""
        pass

    @abstractmethod
    def get_join_queries(self) -> Dict[str, str]:
        """Retourne les requêtes de jointure - À implémenter dans les sous-classes"""
        pass

    @abstractmethod
    def get_aggregation_queries(self) -> Dict[str, str]:
        """Retourne les requêtes d'agrégation - À implémenter dans les sous-classes"""
        pass

    @abstractmethod
    def get_filter_queries(self) -> Dict[str, str]:
        """Retourne les requêtes avec filtres - À implémenter dans les sous-classes"""
        pass

    @abstractmethod
    def get_optional_queries(self) -> Dict[str, str]:
        """Retourne les requêtes avec OPTIONAL/UNION - À implémenter dans les sous-classes"""
        pass

    @abstractmethod
    def get_subquery_queries(self) -> Dict[str, str]:
        """Retourne les requêtes avec sous-requêtes - À implémenter dans les sous-classes"""
        pass

    def get_queries_by_category(self, category: str) -> Dict[str, str]:
        """
        Retourne les requêtes d'une catégorie spécifique

        Args:
            category: Catégorie de requêtes demandée

        Returns:
            Dictionnaire des requêtes de la catégorie
        """
        category_map = {
            "simple": self.get_simple_queries(),
            "jointure": self.get_join_queries(),
            "aggregation": self.get_aggregation_queries(),
            "filtre": self.get_filter_queries(),
            "optional": self.get_optional_queries(),
            "subquery": self.get_subquery_queries()
        }

        return category_map.get(category.lower(), {})

    def get_all_queries(self) -> Dict[str, str]:
        """Retourne toutes les requêtes - Implémentation par défaut"""
        all_queries = {}

        all_queries.update(self.get_simple_queries())
        all_queries.update(self.get_join_queries())
        all_queries.update(self.get_aggregation_queries())
        all_queries.update(self.get_filter_queries())
        all_queries.update(self.get_optional_queries())
        all_queries.update(self.get_subquery_queries())

        return all_queries

    def get_available_categories(self) -> list:
        """
        Retourne les catégories disponibles

        Returns:
            Liste des catégories disponibles
        """
        return ["simple", "jointure", "aggregation", "filtre", "optional", "subquery"]
