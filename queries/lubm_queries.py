"""
Requêtes SPARQL spécifiques au benchmark LUBM
"""

from typing import Dict

class LUBMQueries:
    """Classe contenant toutes les requêtes SPARQL pour le benchmark LUBM"""
    
    def __init__(self):
        """Initialise les requêtes LUBM"""
        self.prefix = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX ub: <http://www.lehigh.edu/~zhp2/2004/0401/univ-bench.owl#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        """
    
    def get_simple_queries(self) -> Dict[str, str]:
        """Retourne les requêtes simples LUBM"""
        return {
            "Simple - Publications par chercheur": f"""
            {self.prefix}
            SELECT ?professor ?publication
            WHERE {{
                ?professor rdf:type ub:FullProfessor .
                ?publication ub:publicationAuthor ?professor .
            }}
            LIMIT 100
            """,
            
            "Simple - Étudiants gradués": f"""
            {self.prefix}
            SELECT ?student ?name
            WHERE {{
                ?student rdf:type ub:GraduateStudent .
                ?student ub:name ?name .
            }}
            LIMIT 100
            """,
            
            "Simple - Cours disponibles": f"""
            {self.prefix}
            SELECT ?course ?name
            WHERE {{
                ?course rdf:type ub:Course .
                ?course ub:name ?name .
            }}
            LIMIT 100
            """
        }
    
    def get_join_queries(self) -> Dict[str, str]:
        """Retourne les requêtes de jointure LUBM"""
        return {
            "Jointure - Professeurs et leurs cours": f"""
            {self.prefix}
            SELECT ?professor ?course ?department
            WHERE {{
                ?professor rdf:type ub:FullProfessor .
                ?professor ub:worksFor ?department .
                ?professor ub:teacherOf ?course .
            }}
            LIMIT 100
            """,
            
            "Jointure - Étudiants et leurs conseillers": f"""
            {self.prefix}
            SELECT ?student ?advisor ?department
            WHERE {{
                ?student rdf:type ub:GraduateStudent .
                ?student ub:advisor ?advisor .
                ?student ub:memberOf ?department .
            }}
            LIMIT 100
            """,
            
            "Jointure - Publications et auteurs": f"""
            {self.prefix}
            SELECT ?publication ?author ?department
            WHERE {{
                ?publication ub:publicationAuthor ?author .
                ?author ub:worksFor ?department .
            }}
            LIMIT 100
            """
        }
    
    def get_aggregation_queries(self) -> Dict[str, str]:
        """Retourne les requêtes d'agrégation LUBM"""
        return {
            "Agrégation - Nombre d'étudiants par département": f"""
            {self.prefix}
            SELECT ?department (COUNT(?student) AS ?studentCount)
            WHERE {{
                ?student rdf:type ub:GraduateStudent .
                ?student ub:memberOf ?department .
            }}
            GROUP BY ?department
            ORDER BY DESC(?studentCount)
            """,
            
            "Agrégation - Nombre de cours par professeur": f"""
            {self.prefix}
            SELECT ?professor (COUNT(?course) AS ?courseCount)
            WHERE {{
                ?professor rdf:type ub:FullProfessor .
                ?professor ub:teacherOf ?course .
            }}
            GROUP BY ?professor
            ORDER BY DESC(?courseCount)
            """,
            
            "Agrégation - Publications par département": f"""
            {self.prefix}
            SELECT ?department (COUNT(?publication) AS ?pubCount)
            WHERE {{
                ?author ub:worksFor ?department .
                ?publication ub:publicationAuthor ?author .
            }}
            GROUP BY ?department
            ORDER BY DESC(?pubCount)
            """
        }
    
    def get_filter_queries(self) -> Dict[str, str]:
        """Retourne les requêtes avec filtres LUBM"""
        return {
            "Filtre - Cours avec plus de 10 crédits": f"""
            {self.prefix}
            SELECT ?course ?credits
            WHERE {{
                ?course rdf:type ub:Course .
                ?course ub:credits ?credits .
                FILTER (?credits > 10)
            }}
            LIMIT 100
            """,
            
            "Filtre - Professeurs expérimentés": f"""
            {self.prefix}
            SELECT ?professor ?experience
            WHERE {{
                ?professor rdf:type ub:FullProfessor .
                ?professor ub:experience ?experience .
                FILTER (?experience > 15)
            }}
            LIMIT 100
            """,
            
            "Filtre - Départements spécifiques": f"""
            {self.prefix}
            SELECT ?student ?department
            WHERE {{
                ?student rdf:type ub:UndergraduateStudent .
                ?student ub:memberOf ?department .
                FILTER (CONTAINS(STR(?department), "Computer"))
            }}
            LIMIT 100
            """
        }
    
    def get_optional_queries(self) -> Dict[str, str]:
        """Retourne les requêtes avec OPTIONAL/UNION LUBM"""
        return {
            "OPTIONAL - Étudiants et leurs conseillers": f"""
            {self.prefix}
            SELECT ?student ?advisor
            WHERE {{
                ?student rdf:type ub:GraduateStudent .
                OPTIONAL {{ ?student ub:advisor ?advisor . }}
            }}
            LIMIT 100
            """,
            
            "UNION - Personnel académique": f"""
            {self.prefix}
            SELECT ?person ?type ?department
            WHERE {{
                {{
                    ?person rdf:type ub:FullProfessor .
                    ?person ub:worksFor ?department .
                    BIND("Professor" AS ?type)
                }}
                UNION
                {{
                    ?person rdf:type ub:Lecturer .
                    ?person ub:worksFor ?department .
                    BIND("Lecturer" AS ?type)
                }}
            }}
            LIMIT 100
            """,
            
            "OPTIONAL - Cours et prérequis": f"""
            {self.prefix}
            SELECT ?course ?prerequisite
            WHERE {{
                ?course rdf:type ub:Course .
                OPTIONAL {{ ?course ub:prerequisite ?prerequisite . }}
            }}
            LIMIT 100
            """
        }
    
    def get_subquery_queries(self) -> Dict[str, str]:
        """Retourne les requêtes avec sous-requêtes LUBM"""
        return {
            "Sous-requête - Départements avec le plus d'étudiants": f"""
            {self.prefix}
            SELECT ?department ?count
            WHERE {{
                {{
                    SELECT ?department (COUNT(?student) AS ?count)
                    WHERE {{
                        ?student rdf:type ub:UndergraduateStudent .
                        ?student ub:memberOf ?department .
                    }}
                    GROUP BY ?department
                }}
                ORDER BY DESC(?count)
            }}
            LIMIT 10
            """,
            
            "Sous-requête - Professeurs les plus prolifiques": f"""
            {self.prefix}
            SELECT ?professor ?pubCount
            WHERE {{
                {{
                    SELECT ?professor (COUNT(?publication) AS ?pubCount)
                    WHERE {{
                        ?professor rdf:type ub:FullProfessor .
                        ?publication ub:publicationAuthor ?professor .
                    }}
                    GROUP BY ?professor
                }}
                FILTER (?pubCount > 5)
                ORDER BY DESC(?pubCount)
            }}
            LIMIT 20
            """,
            
            "Sous-requête - Étudiants dans les grands départements": f"""
            {self.prefix}
            SELECT ?student ?department
            WHERE {{
                ?student ub:memberOf ?department .
                {{
                    SELECT ?department
                    WHERE {{
                        {{
                            SELECT ?department (COUNT(?member) AS ?count)
                            WHERE {{
                                ?member ub:memberOf ?department .
                            }}
                            GROUP BY ?department
                        }}
                        FILTER (?count > 50)
                    }}
                }}
            }}
            LIMIT 100
            """
        }
    
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
        """Retourne toutes les requêtes LUBM"""
        all_queries = {}
        
        all_queries.update(self.get_simple_queries())
        all_queries.update(self.get_join_queries())
        all_queries.update(self.get_aggregation_queries())
        all_queries.update(self.get_filter_queries())
        all_queries.update(self.get_optional_queries())
        all_queries.update(self.get_subquery_queries())
        
        return all_queries