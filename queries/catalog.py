"""
Catalogue principal des requêtes SPARQL
"""

from typing import Dict
from queries.lubm_queries import LUBMQueries
from queries.dbpedia_queries import DBpediaQueries
from queries.generic_queries import GenericQueries

class SPARQLQueryCatalog:
    """Catalogue principal pour gérer toutes les requêtes SPARQL"""
    
    def __init__(self):
        """Initialise le catalogue avec tous les types de requêtes"""
        self.lubm_queries = LUBMQueries()
        self.dbpedia_queries = DBpediaQueries()
        self.generic_queries = GenericQueries()
    
    def get_queries_by_type(self, dataset_type: str) -> Dict[str, str]:
        """
        Récupère les requêtes SPARQL par type de jeu de données
        
        Args:
            dataset_type: Type de jeu de données (LUBM, DBpedia, etc.)
            
        Returns:
            Dictionnaire des requêtes organisées par nom
        """
        if dataset_type == "LUBM":
            return self.lubm_queries.get_all_queries()
        elif dataset_type == "DBpedia":
            return self.dbpedia_queries.get_all_queries()
        elif dataset_type in ["BSBM", "YAGO", "Personnalisé"]:
            return self.generic_queries.get_all_queries()
        else:
            # Par défaut, retourner les requêtes génériques
            return self.generic_queries.get_all_queries()
    
    def get_queries_by_category(self, dataset_type: str, category: str) -> Dict[str, str]:
        """
        Récupère les requêtes d'une catégorie spécifique
        
        Args:
            dataset_type: Type de jeu de données
            category: Catégorie de requêtes (simple, jointure, etc.)
            
        Returns:
            Dictionnaire des requêtes de la catégorie demandée
        """
        if dataset_type == "LUBM":
            return self.lubm_queries.get_queries_by_category(category)
        elif dataset_type == "DBpedia":
            return self.dbpedia_queries.get_queries_by_category(category)
        else:
            return self.generic_queries.get_queries_by_category(category)
    
    def get_available_categories(self, dataset_type: str) -> list:
        """
        Récupère les catégories disponibles pour un type de dataset
        
        Args:
            dataset_type: Type de jeu de données
            
        Returns:
            Liste des catégories disponibles
        """
        categories = ["simple", "jointure", "aggregation", "filtre", "optional", "subquery"]
        return categories
    
    def validate_query(self, query: str) -> Dict[str, bool]:
        """
        Valide une requête SPARQL personnalisée
        
        Args:
            query: Requête SPARQL à valider
            
        Returns:
            Dictionnaire contenant le résultat de validation
        """
        # Validation basique
        if not query or not query.strip():
            return {"valid": False, "error": "Requête vide"}
        
        query_upper = query.upper().strip()
        
        # Vérifier les mots-clés SPARQL
        sparql_keywords = ["SELECT", "ASK", "CONSTRUCT", "DESCRIBE"]
        if not any(keyword in query_upper for keyword in sparql_keywords):
            return {"valid": False, "error": "Type de requête SPARQL non reconnu"}
        
        return {"valid": True, "error": ""}
    
    def get_query_complexity_estimate(self, query: str) -> Dict[str, any]:
        """
        Estime la complexité d'une requête SPARQL
        
        Args:
            query: Requête SPARQL à analyser
            
        Returns:
            Dictionnaire contenant l'estimation de complexité
        """
        query_upper = query.upper()
        
        complexity_score = 0
        complexity_factors = []
        
        # Facteurs de complexité
        if "JOIN" in query_upper or query.count("?") > 10:
            complexity_score += 2
            complexity_factors.append("Jointures multiples")
        
        if "GROUP BY" in query_upper:
            complexity_score += 1
            complexity_factors.append("Agrégation")
        
        if "ORDER BY" in query_upper:
            complexity_score += 1
            complexity_factors.append("Tri")
        
        if "UNION" in query_upper:
            complexity_score += 2
            complexity_factors.append("Union")
        
        if "OPTIONAL" in query_upper:
            complexity_score += 1
            complexity_factors.append("Jointure optionnelle")
        
        if "FILTER" in query_upper:
            complexity_score += 1
            complexity_factors.append("Filtrage")
        
        if query_upper.count("SELECT") > 1:
            complexity_score += 3
            complexity_factors.append("Sous-requêtes")
        
        # Classification de complexité
        if complexity_score == 0:
            complexity_level = "Faible"
        elif complexity_score <= 3:
            complexity_level = "Moyenne"
        elif complexity_score <= 6:
            complexity_level = "Élevée"
        else:
            complexity_level = "Très élevée"
        
        return {
            "score": complexity_score,
            "level": complexity_level,
            "factors": complexity_factors,
            "estimated_execution_time": self._estimate_execution_time(complexity_score)
        }
    
    def _estimate_execution_time(self, complexity_score: int) -> str:
        """
        Estime le temps d'exécution basé sur le score de complexité
        
        Args:
            complexity_score: Score de complexité calculé
            
        Returns:
            Estimation textuelle du temps d'exécution
        """
        if complexity_score == 0:
            return "< 1 seconde"
        elif complexity_score <= 3:
            return "1-5 secondes"
        elif complexity_score <= 6:
            return "5-30 secondes"
        else:
            return "> 30 secondes"