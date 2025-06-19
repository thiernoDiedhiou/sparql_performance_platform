"""
Requêtes SPARQL spécifiques au jeu de données DBpedia
"""

from typing import Dict

class DBpediaQueries:
    """Classe contenant toutes les requêtes SPARQL pour DBpedia"""
    
    def __init__(self):
        """Initialise les requêtes DBpedia"""
        self.prefix = """
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX dbp: <http://dbpedia.org/property/>
            PREFIX dbr: <http://dbpedia.org/resource/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        """
    
    def get_simple_queries(self) -> Dict[str, str]:
        """Retourne les requêtes simples DBpedia"""
        return {
            "Simple - Villes françaises": f"""
            {self.prefix}
            SELECT ?city ?name
            WHERE {{
                ?city a dbo:City ;
                      dbo:country dbr:France ;
                      rdfs:label ?name .
                FILTER(LANG(?name) = "fr")
            }}
            LIMIT 100
            """,
            
            "Simple - Personnes célèbres": f"""
            {self.prefix}
            SELECT ?person ?name ?birthDate
            WHERE {{
                ?person a dbo:Person ;
                        rdfs:label ?name ;
                        dbo:birthDate ?birthDate .
                FILTER(LANG(?name) = "fr")
            }}
            LIMIT 100
            """,
            
            "Simple - Films récents": f"""
            {self.prefix}
            SELECT ?film ?name ?releaseDate
            WHERE {{
                ?film a dbo:Film ;
                      rdfs:label ?name ;
                      dbo:releaseDate ?releaseDate .
                FILTER(YEAR(?releaseDate) >= 2020)
                FILTER(LANG(?name) = "fr")
            }}
            LIMIT 100
            """
        }
    
    def get_join_queries(self) -> Dict[str, str]:
        """Retourne les requêtes de jointure DBpedia"""
        return {
            "Jointure - Films et leurs réalisateurs": f"""
            {self.prefix}
            SELECT ?film ?filmName ?director ?directorName
            WHERE {{
                ?film a dbo:Film ;
                      rdfs:label ?filmName ;
                      dbo:director ?director .
                ?director rdfs:label ?directorName .
                FILTER(LANG(?filmName) = "fr")
                FILTER(LANG(?directorName) = "fr")
            }}
            LIMIT 100
            """,
            
            "Jointure - Acteurs et leurs films": f"""
            {self.prefix}
            SELECT ?actor ?actorName ?film ?filmName
            WHERE {{
                ?film a dbo:Film ;
                      rdfs:label ?filmName ;
                      dbo:starring ?actor .
                ?actor rdfs:label ?actorName .
                FILTER(LANG(?filmName) = "fr")
                FILTER(LANG(?actorName) = "fr")
            }}
            LIMIT 100
            """,
            
            "Jointure - Musiciens et leurs albums": f"""
            {self.prefix}
            SELECT ?musician ?musicianName ?album ?albumName
            WHERE {{
                ?album a dbo:Album ;
                       rdfs:label ?albumName ;
                       dbo:artist ?musician .
                ?musician rdfs:label ?musicianName .
                FILTER(LANG(?albumName) = "fr")
                FILTER(LANG(?musicianName) = "fr")
            }}
            LIMIT 100
            """
        }
    
    def get_aggregation_queries(self) -> Dict[str, str]:
        """Retourne les requêtes d'agrégation DBpedia"""
        return {
            "Agrégation - Nombre de films par année": f"""
            {self.prefix}
            SELECT ?year (COUNT(?film) as ?count)
            WHERE {{
                ?film a dbo:Film ;
                      dbo:releaseDate ?date .
                BIND(YEAR(?date) as ?year)
                FILTER(?year >= 1990)
            }}
            GROUP BY ?year
            ORDER BY DESC(?count)
            LIMIT 20
            """,
            
            "Agrégation - Films par réalisateur": f"""
            {self.prefix}
            SELECT ?director ?directorName (COUNT(?film) AS ?filmCount)
            WHERE {{
                ?film a dbo:Film ;
                      dbo:director ?director .
                ?director rdfs:label ?directorName .
                FILTER(LANG(?directorName) = "fr")
            }}
            GROUP BY ?director ?directorName
            ORDER BY DESC(?filmCount)
            LIMIT 50
            """,
            
            "Agrégation - Population par pays": f"""
            {self.prefix}
            SELECT ?country ?countryName (AVG(?population) AS ?avgPopulation)
            WHERE {{
                ?city a dbo:City ;
                      dbo:country ?country ;
                      dbo:populationTotal ?population .
                ?country rdfs:label ?countryName .
                FILTER(LANG(?countryName) = "fr")
                FILTER(?population > 0)
            }}
            GROUP BY ?country ?countryName
            ORDER BY DESC(?avgPopulation)
            LIMIT 30
            """
        }
    
    def get_filter_queries(self) -> Dict[str, str]:
        """Retourne les requêtes avec filtres DBpedia"""
        return {
            "Filtre - Personnes nées après 1990": f"""
            {self.prefix}
            SELECT ?person ?name ?birthDate
            WHERE {{
                ?person a dbo:Person ;
                        rdfs:label ?name ;
                        dbo:birthDate ?birthDate .
                FILTER(YEAR(?birthDate) > 1990)
                FILTER(LANG(?name) = "fr")
            }}
            LIMIT 100
            """,
            
            "Filtre - Grandes villes": f"""
            {self.prefix}
            SELECT ?city ?name ?population
            WHERE {{
                ?city a dbo:City ;
                      rdfs:label ?name ;
                      dbo:populationTotal ?population .
                FILTER(?population > 1000000)
                FILTER(LANG(?name) = "fr")
            }}
            ORDER BY DESC(?population)
            LIMIT 50
            """,
            
            "Filtre - Livres récents": f"""
            {self.prefix}
            SELECT ?book ?title ?publicationDate
            WHERE {{
                ?book a dbo:Book ;
                      rdfs:label ?title ;
                      dbo:publicationDate ?publicationDate .
                FILTER(YEAR(?publicationDate) >= 2015)
                FILTER(LANG(?title) = "fr")
            }}
            ORDER BY DESC(?publicationDate)
            LIMIT 100
            """
        }
    
    def get_optional_queries(self) -> Dict[str, str]:
        """Retourne les requêtes avec OPTIONAL/UNION DBpedia"""
        return {
            "UNION - Acteurs ou réalisateurs français": f"""
            {self.prefix}
            SELECT ?person ?name ?profession
            WHERE {{
                {{
                    ?person a dbo:Actor ;
                            dbo:nationality dbr:France ;
                            rdfs:label ?name .
                    BIND("Acteur" AS ?profession)
                }}
                UNION
                {{
                    ?person a dbo:FilmDirector ;
                            dbo:nationality dbr:France ;
                            rdfs:label ?name .
                    BIND("Réalisateur" AS ?profession)
                }}
                FILTER(LANG(?name) = "fr")
            }}
            LIMIT 100
            """,
            
            "OPTIONAL - Films avec récompenses": f"""
            {self.prefix}
            SELECT ?film ?filmName ?award
            WHERE {{
                ?film a dbo:Film ;
                      rdfs:label ?filmName .
                OPTIONAL {{ ?film dbo:award ?award . }}
                FILTER(LANG(?filmName) = "fr")
            }}
            LIMIT 100
            """,
            
            "OPTIONAL - Personnes et leurs professions": f"""
            {self.prefix}
            SELECT ?person ?name ?occupation
            WHERE {{
                ?person a dbo:Person ;
                        rdfs:label ?name .
                OPTIONAL {{ ?person dbo:occupation ?occupation . }}
                FILTER(LANG(?name) = "fr")
            }}
            LIMIT 100
            """
        }
    
    def get_subquery_queries(self) -> Dict[str, str]:
        """Retourne les requêtes avec sous-requêtes DBpedia"""
        return {
            "Sous-requête - Réalisateurs avec le plus de films": f"""
            {self.prefix}
            SELECT ?director ?directorName ?count
            WHERE {{
                {{
                    SELECT ?director (COUNT(?film) AS ?count)
                    WHERE {{
                        ?film a dbo:Film ;
                              dbo:director ?director .
                    }}
                    GROUP BY ?director
                    ORDER BY DESC(?count)
                }}
                ?director rdfs:label ?directorName .
                FILTER(LANG(?directorName) = "fr")
                FILTER(?count >= 5)
            }}
            LIMIT 20
            """,
            
            "Sous-requête - Pays avec le plus de villes importantes": f"""
            {self.prefix}
            SELECT ?country ?countryName ?cityCount
            WHERE {{
                {{
                    SELECT ?country (COUNT(?city) AS ?cityCount)
                    WHERE {{
                        ?city a dbo:City ;
                              dbo:country ?country ;
                              dbo:populationTotal ?population .
                        FILTER(?population > 500000)
                    }}
                    GROUP BY ?country
                }}
                ?country rdfs:label ?countryName .
                FILTER(LANG(?countryName) = "fr")
                FILTER(?cityCount >= 3)
            }}
            ORDER BY DESC(?cityCount)
            LIMIT 15
            """,
            
            "Sous-requête - Acteurs dans des films populaires": f"""
            {self.prefix}
            SELECT ?actor ?actorName ?popularFilms
            WHERE {{
                ?actor rdfs:label ?actorName .
                {{
                    SELECT ?actor (COUNT(?film) AS ?popularFilms)
                    WHERE {{
                        ?film a dbo:Film ;
                              dbo:starring ?actor ;
                              dbo:budget ?budget .
                        FILTER(?budget > 50000000)
                    }}
                    GROUP BY ?actor
                }}
                FILTER(?popularFilms >= 2)
                FILTER(LANG(?actorName) = "fr")
            }}
            ORDER BY DESC(?popularFilms)
            LIMIT 25
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
        """Retourne toutes les requêtes DBpedia"""
        all_queries = {}
        
        all_queries.update(self.get_simple_queries())
        all_queries.update(self.get_join_queries())
        all_queries.update(self.get_aggregation_queries())
        all_queries.update(self.get_filter_queries())
        all_queries.update(self.get_optional_queries())
        all_queries.update(self.get_subquery_queries())
        
        return all_queries