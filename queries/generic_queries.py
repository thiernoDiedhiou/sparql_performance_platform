"""
Requêtes SPARQL génériques pour tous types de jeux de données
"""

from typing import Dict

class GenericQueries:
    """Classe contenant toutes les requêtes SPARQL génériques"""
    
    def __init__(self):
        """Initialise les requêtes génériques"""
        self.prefix = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
        """
    
    def get_simple_queries(self) -> Dict[str, str]:
        """Retourne les requêtes simples génériques"""
        return {
            "Simple - Triple patterns basiques": f"""
            {self.prefix}
            SELECT ?s ?p ?o
            WHERE {{
                ?s ?p ?o .
            }}
            LIMIT 100
            """,
            
            "Simple - Types d'entités": f"""
            {self.prefix}
            SELECT ?type (COUNT(?entity) AS ?count)
            WHERE {{
                ?entity rdf:type ?type .
            }}
            GROUP BY ?type
            ORDER BY DESC(?count)
            LIMIT 20
            """,
            
            "Simple - Propriétés utilisées": f"""
            {self.prefix}
            SELECT ?property (COUNT(*) AS ?usage)
            WHERE {{
                ?s ?property ?o .
            }}
            GROUP BY ?property
            ORDER BY DESC(?usage)
            LIMIT 50
            """
        }
    
    def get_join_queries(self) -> Dict[str, str]:
        """Retourne les requêtes de jointure génériques"""
        return {
            "Jointure - Patrons de triplets en étoile": f"""
            {self.prefix}
            SELECT ?s ?p1 ?o1 ?p2 ?o2
            WHERE {{
                ?s ?p1 ?o1 .
                ?s ?p2 ?o2 .
                FILTER (?p1 != ?p2)
            }}
            LIMIT 100
            """,
            
            "Jointure - Chaînes de propriétés": f"""
            {self.prefix}
            SELECT ?s ?intermediate ?o
            WHERE {{
                ?s ?p1 ?intermediate .
                ?intermediate ?p2 ?o .
            }}
            LIMIT 100
            """,
            
            "Jointure - Entités liées": f"""
            {self.prefix}
            SELECT ?entity1 ?entity2 ?relation
            WHERE {{
                ?entity1 ?relation ?entity2 .
                ?entity1 rdf:type ?type1 .
                ?entity2 rdf:type ?type2 .
                FILTER (?type1 != ?type2)
            }}
            LIMIT 100
            """
        }
    
    def get_aggregation_queries(self) -> Dict[str, str]:
        """Retourne les requêtes d'agrégation génériques"""
        return {
            "Agrégation - Comptage de triplets par prédicat": f"""
            {self.prefix}
            SELECT ?p (COUNT(*) as ?count)
            WHERE {{
                ?s ?p ?o .
            }}
            GROUP BY ?p
            ORDER BY DESC(?count)
            LIMIT 20
            """,
            
            "Agrégation - Entités par type": f"""
            {self.prefix}
            SELECT ?type (COUNT(?entity) AS ?entityCount)
            WHERE {{
                ?entity rdf:type ?type .
            }}
            GROUP BY ?type
            ORDER BY DESC(?entityCount)
            LIMIT 30
            """,
            
            "Agrégation - Propriétés par domaine": f"""
            {self.prefix}
            SELECT ?domain (COUNT(DISTINCT ?property) AS ?propCount)
            WHERE {{
                ?property rdfs:domain ?domain .
            }}
            GROUP BY ?domain
            ORDER BY DESC(?propCount)
            LIMIT 25
            """
        }
    
    def get_filter_queries(self) -> Dict[str, str]:
        """Retourne les requêtes avec filtres génériques"""
        return {
            "Filtre - Filtrage sur littéraux": f"""
            {self.prefix}
            SELECT ?s ?p ?o
            WHERE {{
                ?s ?p ?o .
                FILTER (isLiteral(?o))
            }}
            LIMIT 100
            """,
            
            "Filtre - Entités avec labels": f"""
            {self.prefix}
            SELECT ?entity ?label
            WHERE {{
                ?entity rdfs:label ?label .
                FILTER (LANG(?label) = "en" || LANG(?label) = "fr")
            }}
            LIMIT 100
            """,
            
            "Filtre - URIs spécifiques": f"""
            {self.prefix}
            SELECT ?s ?p ?o
            WHERE {{
                ?s ?p ?o .
                FILTER (isURI(?s) && isURI(?o))
            }}
            LIMIT 100
            """
        }
    
    def get_optional_queries(self) -> Dict[str, str]:
        """Retourne les requêtes avec OPTIONAL/UNION génériques"""
        return {
            "OPTIONAL - Jointure externe gauche": f"""
            {self.prefix}
            SELECT ?s ?p1 ?o1 ?p2 ?o2
            WHERE {{
                ?s ?p1 ?o1 .
                OPTIONAL {{ ?s ?p2 ?o2 . FILTER(?p1 != ?p2) }}
            }}
            LIMIT 100
            """,
            
            "UNION - Types alternatifs": f"""
            {self.prefix}
            SELECT ?entity ?type
            WHERE {{
                {{
                    ?entity rdf:type ?type .
                }}
                UNION
                {{
                    ?entity rdf:type owl:Class .
                    BIND(owl:Class AS ?type)
                }}
            }}
            LIMIT 100
            """,
            
            "OPTIONAL - Entités avec descriptions": f"""
            {self.prefix}
            SELECT ?entity ?label ?description
            WHERE {{
                ?entity rdfs:label ?label .
                OPTIONAL {{ ?entity rdfs:comment ?description . }}
            }}
            LIMIT 100
            """
        }
    
    def get_subquery_queries(self) -> Dict[str, str]:
        """Retourne les requêtes avec sous-requêtes génériques"""
        return {
            "Sous-requête - Sélection imbriquée": f"""
            {self.prefix}
            SELECT ?p ?count
            WHERE {{
                {{
                    SELECT ?p (COUNT(?s) as ?count)
                    WHERE {{
                        ?s ?p ?o .
                    }}
                    GROUP BY ?p
                }}
                FILTER(?count > 10)
                ORDER BY DESC(?count)
            }}
            LIMIT 10
            """,
            
            "Sous-requête - Entités populaires": f"""
            {self.prefix}
            SELECT ?entity ?connections
            WHERE {{
                {{
                    SELECT ?entity (COUNT(*) AS ?connections)
                    WHERE {{
                        {{ ?entity ?p ?o . }}
                        UNION
                        {{ ?s ?p ?entity . }}
                    }}
                    GROUP BY ?entity
                }}
                FILTER(?connections > 5)
                ORDER BY DESC(?connections)
            }}
            LIMIT 20
            """,
            
            "Sous-requête - Types complexes": f"""
            {self.prefix}
            SELECT ?type ?instances
            WHERE {{
                {{
                    SELECT ?type (COUNT(?instance) AS ?instances)
                    WHERE {{
                        ?instance rdf:type ?type .
                        ?type rdfs:subClassOf* owl:Thing .
                    }}
                    GROUP BY ?type
                }}
                FILTER(?instances >= 3)
            }}
            ORDER BY DESC(?instances)
            LIMIT 15
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
        """Retourne toutes les requêtes génériques"""
        all_queries = {}
        
        all_queries.update(self.get_simple_queries())
        all_queries.update(self.get_join_queries())
        all_queries.update(self.get_aggregation_queries())
        all_queries.update(self.get_filter_queries())
        all_queries.update(self.get_optional_queries())
        all_queries.update(self.get_subquery_queries())
        
        return all_queries