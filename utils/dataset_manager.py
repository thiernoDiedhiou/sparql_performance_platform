"""
Module de gestion intelligente des datasets locaux
Gère le chargement, la validation et la cohérence des datasets
"""

import os
import psutil
import time
import json
import streamlit as st
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from SPARQLWrapper import SPARQLWrapper, POST, DIGEST
import requests
from datetime import datetime
from utils.helpers import log_message, format_memory_size


class DatasetManager:
    """Gestionnaire intelligent de datasets avec validation et optimisations"""

    # Configuration des datasets supportés
    DATASET_INFO = {
        "DBpedia": {
            "description": "DBpedia Knowledge Base - Données structurées de Wikipedia",
            "format": "N-Triples",
            "ontology": "http://dbpedia.org/ontology/",
            "validation_query": "ASK { ?s <http://dbpedia.org/ontology/bandMember> ?o }",
            "typical_predicates": ["bandMember", "genre", "hometown"],
            "color": "🔵"
        },
        "LUBM": {
            "description": "Lehigh University Benchmark - Benchmark académique",
            "format": "Turtle",
            "ontology": "http://www.lehigh.edu/~zhp2/2004/0401/univ-bench.owl#",
            "validation_query": "ASK { ?s a <http://www.lehigh.edu/~zhp2/2004/0401/univ-bench.owl#University> }",
            "typical_predicates": ["University", "Department", "Professor"],
            "color": "🟢"
        },
        "Generic": {
            "description": "Dataset générique - Données synthétiques de test",
            "format": "Turtle",
            "ontology": "http://example.org/",
            "validation_query": "ASK { ?s a <http://example.org/Person> }",
            "typical_predicates": ["Person", "hasProperty"],
            "color": "🟡"
        }
    }

    # Configuration des tailles autorisées
    ALLOWED_SIZES = {
        "10K": {
            "label": "10K ⚡ Ultra-rapide",
            "max_triplets": 15000,
            "estimated_load_time": 5,  # secondes
            "memory_required": 50,      # MB
            "recommended_for": "Démo rapide, premiers tests"
        },
        "100K": {
            "label": "100K 🎯 Recommandé",
            "max_triplets": 150000,
            "estimated_load_time": 45,
            "memory_required": 200,
            "recommended_for": "Tests de performance, comparaisons"
        }
    }

    def __init__(self, datasets_path: str):
        """
        Initialise le gestionnaire de datasets

        Args:
            datasets_path: Chemin vers le dossier contenant les datasets
        """
        self.datasets_path = Path(datasets_path)
        self.metadata_file = Path("datasets_metadata.json")
        self.env_file = Path(".env")
        self.validate_datasets_directory()

    def validate_datasets_directory(self) -> bool:
        """Vérifie que le dossier de datasets existe et est accessible"""
        if not self.datasets_path.exists():
            raise FileNotFoundError(
                f"Le dossier de datasets n'existe pas : {self.datasets_path}\n"
                "Veuillez créer ce dossier et y placer vos fichiers .ttl"
            )

        log_message(f"Dossier de datasets validé : {self.datasets_path}")
        return True

    def get_available_datasets(self) -> Dict[str, List[str]]:
        """
        Scanne et retourne les datasets disponibles

        Returns:
            Dictionnaire {dataset_name: [sizes_available]}
        """
        available = {}

        for dataset_name in self.DATASET_INFO.keys():
            dataset_folder = self.datasets_path / dataset_name

            if not dataset_folder.exists():
                log_message(f"Dataset {dataset_name} non trouvé dans {self.datasets_path}", "warning")
                continue

            sizes = []
            for size in self.ALLOWED_SIZES.keys():
                file_path = dataset_folder / f"{size}.ttl"
                if file_path.exists() and file_path.stat().st_size > 0:
                    sizes.append(size)

            if sizes:
                available[dataset_name] = sizes

        return available

    def get_dataset_file_info(self, dataset_name: str, size: str) -> Dict:
        """
        Récupère les informations détaillées sur un fichier dataset

        Args:
            dataset_name: Nom du dataset (DBpedia, LUBM, Generic)
            size: Taille (10K, 100K)

        Returns:
            Dictionnaire avec les informations du fichier
        """
        file_path = self.datasets_path / dataset_name / f"{size}.ttl"

        if not file_path.exists():
            return {"error": "Fichier introuvable", "exists": False}

        file_size = file_path.stat().st_size

        if file_size == 0:
            return {"error": "Fichier vide", "exists": False}

        # Informations du dataset
        info = self.DATASET_INFO[dataset_name].copy()
        size_info = self.ALLOWED_SIZES[size].copy()

        return {
            "exists": True,
            "path": str(file_path),
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024**2), 2),
            "dataset_type": dataset_name,
            "dataset_size": size,
            **info,
            **size_info
        }

    def validate_dataset_structure(self, file_path: Path) -> Tuple[bool, str, Dict]:
        """
        Valide la structure d'un fichier dataset

        Args:
            file_path: Chemin vers le fichier .ttl

        Returns:
            Tuple (is_valid, message, statistics)
        """
        try:
            triplet_count = 0
            has_prefixes = False
            prefixes = []
            sample_triples = []

            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    line = line.strip()

                    # Détecter les préfixes
                    if line.startswith('@prefix'):
                        has_prefixes = True
                        prefixes.append(line)

                    # Compter les triplets (lignes se terminant par .)
                    elif line.endswith('.') and not line.startswith('#'):
                        triplet_count += 1
                        if len(sample_triples) < 5:
                            sample_triples.append(line[:100])  # Premier 100 chars

                    # Limiter la lecture aux 1000 premières lignes pour performance
                    if i > 1000:
                        break

            statistics = {
                "estimated_triplets": triplet_count,
                "has_prefixes": has_prefixes,
                "prefix_count": len(prefixes),
                "sample_triples": sample_triples
            }

            if triplet_count == 0:
                return False, "Aucun triplet RDF trouvé dans le fichier", statistics

            return True, f"Dataset valide : ~{triplet_count} triplets détectés", statistics

        except Exception as e:
            return False, f"Erreur lors de la validation : {str(e)}", {}

    def check_memory_available(self, required_mb: int) -> Tuple[bool, str, int]:
        """
        Vérifie si suffisamment de mémoire est disponible

        Args:
            required_mb: Mémoire requise en MB

        Returns:
            Tuple (is_available, message, available_mb)
        """
        memory = psutil.virtual_memory()
        available_mb = memory.available / (1024**2)

        # Ajouter une marge de sécurité de 1GB
        required_with_margin = required_mb + 1024

        if available_mb < required_with_margin:
            return (
                False,
                f"Mémoire insuffisante ! Disponible: {int(available_mb)}MB, Requis: {required_with_margin}MB",
                int(available_mb)
            )

        return (
            True,
            f"Mémoire suffisante : {int(available_mb)}MB disponibles",
            int(available_mb)
        )

    def estimate_load_time(self, dataset_name: str, size: str) -> int:
        """
        Estime le temps de chargement d'un dataset

        Args:
            dataset_name: Nom du dataset
            size: Taille du dataset

        Returns:
            Temps estimé en secondes
        """
        base_time = self.ALLOWED_SIZES[size]["estimated_load_time"]

        # Ajuster selon le dataset (LUBM plus structuré = plus lent)
        multipliers = {
            "DBpedia": 1.0,
            "LUBM": 1.3,
            "Generic": 0.7
        }

        return int(base_time * multipliers.get(dataset_name, 1.0))

    def load_to_virtuoso(self, file_path: str, endpoint: str, graph_uri: Optional[str] = None,
                        username: str = 'SPARQL', password: str = 'admin123') -> Tuple[bool, str]:
        """
        Charge un dataset dans Virtuoso via l'API de chargement de fichiers

        Args:
            file_path: Chemin vers le fichier .ttl
            endpoint: URL de l'endpoint Virtuoso
            graph_uri: URI du graphe (optionnel)
            username: Nom d'utilisateur Virtuoso (défaut: 'dba')
            password: Mot de passe Virtuoso (défaut: 'dba')

        Returns:
            Tuple (success, message)
        """
        try:
            # Extraire l'URL de base
            base_url = endpoint.replace('/sparql', '')

            if not graph_uri:
                graph_uri = f"http://example.org/dataset_{int(time.time())}"

            # Authentification pour Virtuoso
            auth = (username, password)

            # Méthode 1: Utiliser l'API Graph Store avec authentification
            try:
                load_url = f"{base_url}/sparql-graph-crud?graph-uri={graph_uri}"

                # Lire le fichier
                with open(file_path, 'rb') as f:
                    file_content = f.read()

                # Envoyer via PUT avec authentification
                response = requests.put(
                    load_url,
                    data=file_content,
                    headers={
                        'Content-Type': 'text/turtle; charset=utf-8'
                    },
                    auth=auth,
                    timeout=300
                )

                if response.status_code in [200, 201, 204]:
                    log_message(f"Dataset chargé avec succès via Graph Store Protocol", "info")
                    return True, f"Dataset chargé avec succès dans le graphe {graph_uri}"

                log_message(f"Méthode 1 échouée (code {response.status_code}): {response.text[:200]}", "warning")

            except Exception as e1:
                log_message(f"Méthode 1 échouée: {str(e1)}", "warning")

            # Méthode 2: Essayer avec l'endpoint UPDATE standard
            try:
                update_url = f"{base_url}/sparql"

                # Pour les petits fichiers, on peut essayer de charger tout en une fois
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Créer une requête INSERT DATA
                query = f"""
                INSERT DATA {{
                    GRAPH <{graph_uri}> {{
                        {content}
                    }}
                }}
                """

                response = requests.post(
                    update_url,
                    data={'query': query},
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    auth=auth,
                    timeout=300
                )

                if response.status_code in [200, 201, 204]:
                    log_message(f"Dataset chargé avec succès via INSERT DATA", "info")
                    return True, f"Dataset chargé avec succès dans le graphe {graph_uri}"

                log_message(f"Méthode 2 échouée (code {response.status_code})", "warning")

            except Exception as e2:
                log_message(f"Méthode 2 échouée: {str(e2)}", "warning")

            # Méthode 3: Charger par chunks avec authentification (dernier recours)
            log_message(f"Tentative de chargement par chunks avec authentification", "info")
            return self._load_by_chunks_virtuoso(file_path, endpoint, graph_uri, auth=auth)

        except Exception as e:
            log_message(f"Erreur lors du chargement dans Virtuoso: {str(e)}", "error")
            return False, f"Erreur: {str(e)}"

    def _load_by_chunks_virtuoso(self, file_path: str, endpoint: str, graph_uri: str,
                                 auth: tuple = ('SPARQL', 'admin123'), chunk_size: int = 1000) -> Tuple[bool, str]:
        """
        Charge un dataset par chunks dans Virtuoso

        Args:
            file_path: Chemin vers le fichier
            endpoint: Endpoint SPARQL
            graph_uri: URI du graphe
            auth: Tuple (username, password) pour authentification
            chunk_size: Nombre de lignes par chunk

        Returns:
            Tuple (success, message)
        """
        try:
            base_url = endpoint.replace('/sparql', '')
            update_endpoint = f"{base_url}/sparql"

            # D'abord, vider le graphe s'il existe
            clear_query = f"CLEAR GRAPH <{graph_uri}>"

            try:
                requests.post(
                    update_endpoint,
                    data={'query': clear_query},
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    auth=auth,
                    timeout=30
                )
                log_message(f"Graphe {graph_uri} vidé avec succès", "info")
            except Exception as e:
                log_message(f"Avertissement lors du nettoyage du graphe: {str(e)}", "warning")
                pass  # Le graphe n'existe peut-être pas encore

            # Lire et insérer par chunks
            log_message(f"Démarrage chargement par chunks de {file_path}", "info")

            with open(file_path, 'r', encoding='utf-8') as f:
                lines = []
                triplet_count = 0
                prefixes = []

                for line in f:
                    line = line.strip()

                    # Ignorer les lignes vides et les commentaires
                    if not line or line.startswith('#'):
                        continue

                    # Collecter les préfixes séparément (Turtle uniquement)
                    if line.startswith('@prefix') or line.startswith('@base'):
                        prefixes.append(line)
                        continue

                    # Ajouter les triplets (N-Triples ou Turtle)
                    lines.append(line)

                    # Insérer par chunks
                    if len(lines) >= chunk_size:
                        log_message(f"Insertion de {len(lines)} triplets (total: {triplet_count})", "info")
                        success = self._insert_chunk_virtuoso(update_endpoint, graph_uri, lines, auth)
                        if not success:
                            log_message(f"Échec d'insertion chunk à {triplet_count} triplets", "error")
                            return False, f"Échec d'insertion après {triplet_count} triplets"
                        triplet_count += len(lines)
                        lines = []

                # Insérer les lignes restantes
                if lines:
                    log_message(f"Insertion du dernier chunk de {len(lines)} triplets", "info")
                    success = self._insert_chunk_virtuoso(update_endpoint, graph_uri, lines, auth)
                    if not success:
                        log_message(f"Échec d'insertion du dernier chunk", "error")
                        return False, f"Échec d'insertion du dernier chunk"
                    triplet_count += len(lines)

            log_message(f"Chargement terminé : {triplet_count} triplets insérés", "info")
            return True, f"Dataset chargé avec succès : ~{triplet_count} triplets dans {graph_uri}"

        except Exception as e:
            log_message(f"Erreur chargement par chunks: {str(e)}", "error")
            return False, f"Erreur chargement par chunks: {str(e)}"

    def _insert_chunk_virtuoso(self, endpoint: str, graph_uri: str, lines: List[str],
                              auth: tuple = ('SPARQL', 'admin123')) -> bool:
        """
        Insère un chunk de triplets dans Virtuoso

        Args:
            endpoint: Endpoint UPDATE
            graph_uri: URI du graphe
            lines: Lignes de triplets à insérer
            auth: Tuple (username, password) pour authentification

        Returns:
            True si succès
        """
        try:
            # Joindre les lignes en nettoyant la syntaxe Turtle
            # Retirer les points-virgules et points finaux qui causent des conflits
            cleaned_lines = []
            for line in lines:
                # Retirer les ; . qui causent l'erreur SP030 dans Virtuoso
                line = line.replace('; .', '.')
                # Retirer les espaces multiples
                line = ' '.join(line.split())
                if line:
                    cleaned_lines.append(line)

            data = ' '.join(cleaned_lines)

            # Créer la requête INSERT DATA
            insert_query = f"""
            INSERT DATA {{
                GRAPH <{graph_uri}> {{
                    {data}
                }}
            }}
            """

            response = requests.post(
                endpoint,
                data={'query': insert_query},
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                auth=auth,
                timeout=60
            )

            if response.status_code not in [200, 201, 204]:
                log_message(f"Échec insertion chunk: HTTP {response.status_code} - {response.text[:500]}", "error")
                return False

            return True

        except Exception as e:
            log_message(f"Exception insertion chunk: {str(e)}", "error")
            return False

    def load_to_fuseki(self, file_path: str, endpoint: str, graph_uri: Optional[str] = None,
                      username: Optional[str] = None, password: Optional[str] = None) -> Tuple[bool, str]:
        """
        Charge un dataset dans Jena Fuseki via l'API de chargement de fichiers

        Args:
            file_path: Chemin vers le fichier .ttl
            endpoint: URL de l'endpoint Fuseki
            graph_uri: URI du graphe (optionnel)
            username: Nom d'utilisateur Fuseki (optionnel)
            password: Mot de passe Fuseki (optionnel)

        Returns:
            Tuple (success, message)
        """
        try:
            # Extraire l'URL de base et le nom du dataset
            # http://localhost:3030/dataset/query -> http://localhost:3030/dataset
            base_url = endpoint.replace('/query', '').replace('/sparql', '')

            if not graph_uri:
                graph_uri = f"http://example.org/dataset_{int(time.time())}"

            # Authentification optionnelle pour Fuseki
            auth = (username, password) if username and password else None

            # Méthode 1: API /data avec graph parameter
            try:
                load_url = f"{base_url}/data?graph={graph_uri}"

                with open(file_path, 'rb') as f:
                    file_content = f.read()

                response = requests.post(
                    load_url,
                    data=file_content,
                    headers={'Content-Type': 'text/turtle; charset=utf-8'},
                    auth=auth,
                    timeout=300
                )

                if response.status_code in [200, 201, 204]:
                    log_message(f"Dataset chargé avec succès via API /data", "info")
                    return True, f"Dataset chargé avec succès dans le graphe {graph_uri}"

                log_message(f"Méthode 1 échouée (code {response.status_code}): {response.text[:200]}", "warning")

            except Exception as e1:
                log_message(f"Méthode 1 échouée: {str(e1)}", "warning")

            # Méthode 2: Utiliser l'endpoint UPDATE
            try:
                update_url = f"{base_url}/update"

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                query = f"""
                INSERT DATA {{
                    GRAPH <{graph_uri}> {{
                        {content}
                    }}
                }}
                """

                response = requests.post(
                    update_url,
                    data={'update': query},
                    headers={'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'},
                    auth=auth,
                    timeout=300
                )

                if response.status_code in [200, 201, 204]:
                    log_message(f"Dataset chargé avec succès via UPDATE endpoint", "info")
                    return True, f"Dataset chargé avec succès dans le graphe {graph_uri}"

                log_message(f"Méthode 2 échouée (code {response.status_code})", "warning")

            except Exception as e2:
                log_message(f"Méthode 2 échouée: {str(e2)}", "warning")

            # Méthode 3: Charger par chunks
            log_message(f"Tentative de chargement par chunks", "info")
            return self._load_by_chunks_fuseki(file_path, endpoint, graph_uri, auth=auth)

        except Exception as e:
            log_message(f"Erreur lors du chargement dans Fuseki: {str(e)}", "error")
            return False, f"Erreur: {str(e)}"

    def _load_by_chunks_fuseki(self, file_path: str, endpoint: str, graph_uri: str,
                               auth: Optional[tuple] = None, chunk_size: int = 1000) -> Tuple[bool, str]:
        """
        Charge un dataset par chunks dans Fuseki

        Args:
            file_path: Chemin vers le fichier
            endpoint: Endpoint SPARQL
            graph_uri: URI du graphe
            auth: Tuple (username, password) pour authentification optionnelle
            chunk_size: Nombre de lignes par chunk

        Returns:
            Tuple (success, message)
        """
        try:
            base_url = endpoint.replace('/query', '').replace('/sparql', '')
            update_endpoint = f"{base_url}/update"

            # D'abord, vider le graphe s'il existe
            clear_query = f"CLEAR GRAPH <{graph_uri}>"

            try:
                response = requests.post(
                    update_endpoint,
                    data={'update': clear_query},
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    auth=auth,
                    timeout=30
                )
                log_message(f"Graphe {graph_uri} vidé avec succès", "info")
            except Exception as e:
                log_message(f"Avertissement lors du nettoyage du graphe: {str(e)}", "warning")
                pass  # Le graphe n'existe peut-être pas encore

            # Lire et insérer par chunks
            log_message(f"Démarrage chargement par chunks de {file_path}", "info")

            with open(file_path, 'r', encoding='utf-8') as f:
                lines = []
                triplet_count = 0
                prefixes = []

                for line in f:
                    line = line.strip()

                    # Ignorer les lignes vides et les commentaires
                    if not line or line.startswith('#'):
                        continue

                    # Collecter les préfixes séparément (Turtle uniquement)
                    if line.startswith('@prefix') or line.startswith('@base'):
                        prefixes.append(line)
                        continue

                    # Ajouter les triplets (N-Triples ou Turtle)
                    lines.append(line)

                    # Insérer par chunks
                    if len(lines) >= chunk_size:
                        log_message(f"Insertion de {len(lines)} triplets (total: {triplet_count})", "info")
                        success = self._insert_chunk_fuseki(update_endpoint, graph_uri, lines, auth)
                        if not success:
                            log_message(f"Échec d'insertion chunk à {triplet_count} triplets", "error")
                            return False, f"Échec d'insertion après {triplet_count} triplets"
                        triplet_count += len(lines)
                        lines = []

                # Insérer les lignes restantes
                if lines:
                    log_message(f"Insertion du dernier chunk de {len(lines)} triplets", "info")
                    success = self._insert_chunk_fuseki(update_endpoint, graph_uri, lines, auth)
                    if not success:
                        log_message(f"Échec d'insertion du dernier chunk", "error")
                        return False, f"Échec d'insertion du dernier chunk"
                    triplet_count += len(lines)

            log_message(f"Chargement terminé : {triplet_count} triplets insérés", "info")
            return True, f"Dataset chargé avec succès : ~{triplet_count} triplets dans {graph_uri}"

        except Exception as e:
            return False, f"Erreur chargement par chunks: {str(e)}"

    def _insert_chunk_fuseki(self, endpoint: str, graph_uri: str, lines: List[str],
                            auth: Optional[tuple] = None) -> bool:
        """
        Insère un chunk de triplets dans Fuseki

        Args:
            endpoint: Endpoint UPDATE
            graph_uri: URI du graphe
            lines: Lignes de triplets à insérer
            auth: Tuple (username, password) pour authentification optionnelle

        Returns:
            True si succès
        """
        try:
            # Joindre les lignes en nettoyant la syntaxe Turtle
            cleaned_lines = []
            for line in lines:
                # Retirer les ; . qui peuvent causer des problèmes
                line = line.replace('; .', '.')
                # Retirer les espaces multiples
                line = ' '.join(line.split())
                if line:
                    cleaned_lines.append(line)

            data = ' '.join(cleaned_lines)

            # Créer la requête INSERT DATA
            insert_query = f"""
            INSERT DATA {{
                GRAPH <{graph_uri}> {{
                    {data}
                }}
            }}
            """

            response = requests.post(
                endpoint,
                data={'update': insert_query},
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                auth=auth,
                timeout=60
            )

            if response.status_code not in [200, 201, 204]:
                log_message(f"Échec insertion chunk: HTTP {response.status_code} - {response.text[:500]}", "error")
                return False

            return True

        except Exception as e:
            log_message(f"Exception insertion chunk: {str(e)}", "error")
            return False

    def check_virtuoso_permissions(self, endpoint: str, username: str = 'SPARQL', password: str = 'admin123') -> Tuple[bool, str, dict]:
        """
        Vérifie si l'utilisateur a les permissions nécessaires pour charger des données

        Args:
            endpoint: Endpoint Virtuoso
            username: Nom d'utilisateur à vérifier
            password: Mot de passe

        Returns:
            Tuple (has_permissions, message, permissions_details)
        """
        try:
            base_url = endpoint.replace('/sparql-auth', '').replace('/sparql', '')
            test_endpoint = f"{base_url}/sparql"

            # Test 1: Vérifier si l'authentification fonctionne
            test_query = "SELECT COUNT(*) as ?count WHERE { ?s ?p ?o } LIMIT 1"

            response = requests.post(
                test_endpoint,
                data={'query': test_query},
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                auth=(username, password),
                timeout=10
            )

            auth_works = response.status_code in [200, 201, 204]

            # Test 2: Vérifier les permissions d'écriture avec un graphe temporaire
            test_graph = f"http://test.permissions.{int(time.time())}"
            test_insert = f"""
            INSERT DATA {{
                GRAPH <{test_graph}> {{
                    <http://test.subject> <http://test.predicate> "test" .
                }}
            }}
            """

            response = requests.post(
                test_endpoint,
                data={'query': test_insert},
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                auth=(username, password),
                timeout=10
            )

            insert_works = response.status_code in [200, 201, 204]

            # Nettoyer le graphe de test
            if insert_works:
                clear_query = f"CLEAR GRAPH <{test_graph}>"
                requests.post(
                    test_endpoint,
                    data={'query': clear_query},
                    auth=(username, password),
                    timeout=10
                )

            permissions = {
                'authentication': auth_works,
                'sparql_update': insert_works,
                'username': username
            }

            if auth_works and insert_works:
                message = f"✅ Utilisateur '{username}' a toutes les permissions nécessaires"
                log_message(message, "info")
                return True, message, permissions
            elif auth_works and not insert_works:
                message = f"⚠️ Authentification OK mais pas de permissions SPARQL_UPDATE pour '{username}'"
                log_message(message, "warning")
                return False, message, permissions
            else:
                message = f"❌ Échec d'authentification pour l'utilisateur '{username}'"
                log_message(message, "error")
                return False, message, permissions

        except Exception as e:
            log_message(f"Erreur vérification permissions: {str(e)}", "error")
            return False, f"Erreur: {str(e)}", {}

    def validate_dataset_coherence(self, dataset_name: str, size: str) -> Tuple[bool, str, dict]:
        """
        Valide la cohérence d'un dataset avant chargement

        Vérifie:
        - Existence du fichier
        - Format du fichier (Turtle, N-Triples)
        - Cohérence du contenu
        - Préfixes corrects

        Args:
            dataset_name: Nom du dataset (DBpedia, LUBM, Generic)
            size: Taille du dataset (10K, 100K)

        Returns:
            Tuple (is_coherent, message, validation_details)
        """
        try:
            file_path = self.datasets_path / dataset_name / f"{size}.ttl"

            if not file_path.exists():
                return False, f"Fichier non trouvé: {file_path}", {}

            # Informations sur le fichier
            file_size = file_path.stat().st_size
            file_size_mb = file_size / (1024 ** 2)

            validation_details = {
                'file_exists': True,
                'file_size_mb': round(file_size_mb, 2),
                'format': None,
                'has_prefixes': False,
                'sample_triplets': [],
                'estimated_triplets': 0,
                'errors': []
            }

            # Lire les premières lignes pour analyser le format
            prefixes = []
            sample_triplets = []
            line_count = 0
            triplet_count = 0

            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i > 100:  # Analyser seulement les 100 premières lignes
                        break

                    line = line.strip()
                    line_count += 1

                    if not line or line.startswith('#'):
                        continue

                    if line.startswith('@prefix') or line.startswith('@base'):
                        prefixes.append(line)
                        validation_details['has_prefixes'] = True
                    elif line:
                        triplet_count += 1
                        if len(sample_triplets) < 3:
                            sample_triplets.append(line[:100])  # Premier 100 caractères

            # Détecter le format
            expected_format = self.DATASET_INFO[dataset_name]['format']
            detected_format = 'Turtle' if prefixes else 'N-Triples'

            validation_details['format'] = detected_format
            validation_details['expected_format'] = expected_format
            validation_details['sample_triplets'] = sample_triplets
            validation_details['prefixes_found'] = len(prefixes)

            # Estimer le nombre total de triplets
            if triplet_count > 0:
                avg_bytes_per_triplet = file_size / max(line_count, 1)
                validation_details['estimated_triplets'] = int(file_size / max(avg_bytes_per_triplet, 1))

            # Vérifications de cohérence
            issues = []

            # 1. Vérifier format cohérent
            if detected_format != expected_format:
                issues.append(f"Format détecté ({detected_format}) différent de l'attendu ({expected_format})")

            # 2. Vérifier cohérence des ontologies pour LUBM et DBpedia
            if dataset_name == "LUBM" and not any("univ-bench.owl" in p for p in prefixes):
                issues.append("Ontologie LUBM manquante (univ-bench.owl)")

            if dataset_name == "DBpedia" and not any("dbpedia.org" in t for t in sample_triplets):
                issues.append("URIs DBpedia non détectées dans les triplets")

            # 3. Vérifier taille cohérente
            expected_size_range = self.ALLOWED_SIZES[size]
            max_triplets = expected_size_range['max_triplets']

            if validation_details['estimated_triplets'] > max_triplets * 1.5:
                issues.append(f"Fichier trop volumineux: ~{validation_details['estimated_triplets']} triplets (max attendu: {max_triplets})")

            validation_details['errors'] = issues

            # Résultat final
            if not issues:
                message = f"✅ Dataset {dataset_name} {size} cohérent ({detected_format}, ~{validation_details['estimated_triplets']} triplets)"
                log_message(message, "info")
                return True, message, validation_details
            else:
                message = f"⚠️ Problèmes détectés dans {dataset_name} {size}: {'; '.join(issues)}"
                log_message(message, "warning")
                return False, message, validation_details

        except Exception as e:
            log_message(f"Erreur validation cohérence: {str(e)}", "error")
            return False, f"Erreur: {str(e)}", {}

    def validate_loaded_dataset(self, endpoint: str, dataset_name: str, graph_uri: Optional[str] = None) -> Tuple[bool, str, int]:
        """
        Valide qu'un dataset a bien été chargé en exécutant une requête de validation

        Args:
            endpoint: URL de l'endpoint SPARQL
            dataset_name: Nom du dataset (pour obtenir la requête de validation)
            graph_uri: URI du graphe à valider (optionnel)

        Returns:
            Tuple (is_valid, message, triplet_count)
        """
        try:
            # Si on a un graph_uri, compter les triplets dans ce graphe spécifique
            if graph_uri:
                count_query = f"SELECT (COUNT(*) AS ?count) WHERE {{ GRAPH <{graph_uri}> {{ ?s ?p ?o }} }}"
            else:
                # Compter uniquement le graphe par défaut
                count_query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o . }"

            sparql = SPARQLWrapper(endpoint)
            sparql.setQuery(count_query)
            sparql.setReturnFormat('json')
            result = sparql.query().convert()

            triplet_count = 0
            if 'results' in result and 'bindings' in result['results']:
                bindings = result['results']['bindings']
                if bindings and 'count' in bindings[0]:
                    triplet_count = int(bindings[0]['count']['value'])

            # Vérifier la cohérence avec le dataset attendu
            if triplet_count > 0:
                # Essayer la validation spécifique au dataset si possible
                try:
                    validation_query = self.DATASET_INFO[dataset_name]["validation_query"]

                    # Adapter la requête pour le graphe nommé si nécessaire
                    if graph_uri:
                        # Modifier la requête ASK pour cibler le graphe
                        validation_query = validation_query.replace(
                            "ASK { ",
                            f"ASK {{ GRAPH <{graph_uri}> {{ "
                        ).replace(" }", " } }")

                    sparql.setQuery(validation_query)
                    ask_result = sparql.query().convert()
                    is_valid = ask_result.get('boolean', False)

                    if is_valid:
                        return True, f"Dataset validé : {triplet_count} triplets chargés", triplet_count
                    else:
                        # Les triplets sont là mais ne correspondent pas au type attendu
                        return True, f"Dataset chargé : {triplet_count} triplets (validation partielle)", triplet_count
                except:
                    # Validation spécifique échouée, mais on a des triplets
                    return True, f"Dataset chargé : {triplet_count} triplets", triplet_count
            else:
                return False, "Aucun triplet trouvé dans le graphe", 0

        except Exception as e:
            log_message(f"Erreur lors de la validation: {str(e)}", "error")
            return False, f"Erreur lors de la validation: {str(e)}", 0

    def get_loading_recommendations(self, dataset_name: str, size: str) -> Dict:
        """
        Retourne des recommandations pour le chargement d'un dataset

        Args:
            dataset_name: Nom du dataset
            size: Taille du dataset

        Returns:
            Dictionnaire avec les recommandations
        """
        info = self.get_dataset_file_info(dataset_name, size)

        if not info.get("exists"):
            return {"error": info.get("error")}

        # Vérifier la mémoire
        memory_check = self.check_memory_available(info["memory_required"])

        # Estimer le temps
        estimated_time = self.estimate_load_time(dataset_name, size)

        return {
            "dataset": dataset_name,
            "size": size,
            "file_size_mb": info["size_mb"],
            "estimated_time_seconds": estimated_time,
            "memory_required_mb": info["memory_required"],
            "memory_available": memory_check[0],
            "memory_message": memory_check[1],
            "recommended_for": info["recommended_for"],
            "description": info["description"],
            "format": info["format"],
            "can_load": memory_check[0]
        }

    # ========================================================================
    # NOUVELLES MÉTHODES POUR LA GESTION PERSISTANTE DES DATASETS
    # ========================================================================

    def save_dataset_metadata(self, dataset_name: str, size: str, target: str,
                              graph_uri: str, triplet_count: int = 0) -> bool:
        """
        Sauvegarde les métadonnées d'un dataset chargé dans un fichier JSON

        Args:
            dataset_name: Nom du dataset
            size: Taille du dataset
            target: Moteur cible ('virtuoso', 'fuseki', 'both')
            graph_uri: URI du graphe chargé
            triplet_count: Nombre de triplets chargés

        Returns:
            True si la sauvegarde a réussi
        """
        try:
            # Charger les métadonnées existantes
            metadata = self.load_all_metadata()

            # Ajouter/mettre à jour les nouvelles métadonnées
            timestamp = datetime.now().isoformat()

            if target in ['virtuoso', 'both']:
                metadata['virtuoso'] = {
                    'dataset_name': dataset_name,
                    'size': size,
                    'graph_uri': graph_uri,
                    'triplet_count': triplet_count,
                    'loaded_at': timestamp,
                    'file_path': str(self.datasets_path / dataset_name / f"{size}.ttl")
                }

            if target in ['fuseki', 'both']:
                metadata['fuseki'] = {
                    'dataset_name': dataset_name,
                    'size': size,
                    'graph_uri': graph_uri,
                    'triplet_count': triplet_count,
                    'loaded_at': timestamp,
                    'file_path': str(self.datasets_path / dataset_name / f"{size}.ttl")
                }

            # Sauvegarder dans le fichier JSON
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            log_message(f"Métadonnées sauvegardées: {dataset_name} ({size}) dans {target}", "info")
            return True

        except Exception as e:
            log_message(f"Erreur sauvegarde métadonnées: {str(e)}", "error")
            return False

    def load_all_metadata(self) -> Dict:
        """
        Charge toutes les métadonnées des datasets depuis le fichier JSON

        Returns:
            Dictionnaire avec les métadonnées de tous les datasets chargés
        """
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            log_message(f"Erreur chargement métadonnées: {str(e)}", "warning")
            return {}

    def get_loaded_dataset_info(self, target: str = 'virtuoso') -> Optional[Dict]:
        """
        Récupère les informations du dataset actuellement chargé

        Args:
            target: Moteur cible ('virtuoso' ou 'fuseki')

        Returns:
            Dictionnaire avec les infos du dataset ou None
        """
        metadata = self.load_all_metadata()
        return metadata.get(target)

    def update_env_file(self, dataset_name: str, size: str, target: str) -> bool:
        """
        Met à jour le fichier .env avec les informations du dataset chargé

        Args:
            dataset_name: Nom du dataset
            size: Taille du dataset
            target: Moteur cible ('virtuoso', 'fuseki', 'both')

        Returns:
            True si la mise à jour a réussi
        """
        try:
            # Lire le fichier .env existant
            env_lines = []
            if self.env_file.exists():
                with open(self.env_file, 'r', encoding='utf-8') as f:
                    env_lines = f.readlines()

            # Variables à mettre à jour
            updates = {
                'CURRENT_DATASET_NAME': dataset_name,
                'CURRENT_DATASET_SIZE': size,
                'CURRENT_DATASET_TARGET': target,
                'DATASET_LOADED_AT': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'DATASETS_PATH': str(self.datasets_path)
            }

            # Mettre à jour ou ajouter les variables
            updated_vars = set()
            for i, line in enumerate(env_lines):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                for key, value in updates.items():
                    if line.startswith(f"{key}="):
                        env_lines[i] = f"{key}={value}\n"
                        updated_vars.add(key)
                        break

            # Ajouter les variables manquantes à la fin
            new_section = False
            for key, value in updates.items():
                if key not in updated_vars:
                    if not new_section:
                        env_lines.append("\n# ==============================================================================\n")
                        env_lines.append("# CONFIGURATION DES DATASETS CHARGÉS (Auto-généré)\n")
                        env_lines.append("# ==============================================================================\n\n")
                        new_section = True
                    env_lines.append(f"{key}={value}\n")

            # Écrire le fichier .env mis à jour
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.writelines(env_lines)

            log_message(f"Fichier .env mis à jour avec {dataset_name} ({size})", "info")
            return True

        except Exception as e:
            log_message(f"Erreur mise à jour .env: {str(e)}", "error")
            return False

    def clear_dataset(self, target: str, endpoint: str,
                     username: Optional[str] = None, password: Optional[str] = None) -> Tuple[bool, str]:
        """
        Vide les données d'un dataset chargé

        Args:
            target: Moteur cible ('virtuoso' ou 'fuseki')
            endpoint: URL de l'endpoint
            username: Nom d'utilisateur (optionnel)
            password: Mot de passe (optionnel)

        Returns:
            Tuple (success, message)
        """
        try:
            # Récupérer les métadonnées du dataset chargé
            metadata = self.get_loaded_dataset_info(target)

            if not metadata:
                return False, f"Aucun dataset chargé dans {target}"

            graph_uri = metadata.get('graph_uri')
            if not graph_uri:
                return False, "URI du graphe non trouvée dans les métadonnées"

            # Préparer l'authentification
            auth = None
            if username and password:
                auth = (username, password)
            elif target == 'virtuoso':
                auth = ('SPARQL', 'admin123')

            # Construire l'URL de l'endpoint UPDATE
            if target == 'virtuoso':
                base_url = endpoint.replace('/sparql', '')
                update_endpoint = f"{base_url}/sparql"
            else:  # fuseki
                base_url = endpoint.replace('/query', '').replace('/sparql', '')
                update_endpoint = f"{base_url}/update"

            # Exécuter la requête CLEAR GRAPH
            clear_query = f"CLEAR GRAPH <{graph_uri}>"

            # Timeout augmenté pour les gros datasets (100K+ triplets)
            timeout = 180  # 3 minutes pour permettre la suppression de gros volumes

            response = requests.post(
                update_endpoint,
                data={'query': clear_query} if target == 'virtuoso' else {'update': clear_query},
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                auth=auth,
                timeout=timeout
            )

            if response.status_code in [200, 201, 204]:
                # Supprimer les métadonnées
                all_metadata = self.load_all_metadata()
                if target in all_metadata:
                    del all_metadata[target]
                    with open(self.metadata_file, 'w', encoding='utf-8') as f:
                        json.dump(all_metadata, f, indent=2, ensure_ascii=False)

                log_message(f"Dataset vidé avec succès de {target}", "info")
                return True, f"Dataset supprimé avec succès de {target}"
            else:
                return False, f"Erreur HTTP {response.status_code}: {response.text[:200]}"

        except Exception as e:
            log_message(f"Erreur suppression dataset: {str(e)}", "error")
            return False, f"Erreur: {str(e)}"

    def get_dataset_statistics(self) -> Dict:
        """
        Récupère les statistiques des datasets chargés

        Returns:
            Dictionnaire avec les statistiques
        """
        try:
            metadata = self.load_all_metadata()

            stats = {
                'virtuoso': None,
                'fuseki': None,
                'total_datasets_loaded': 0,
                'total_triplets': 0
            }

            for target in ['virtuoso', 'fuseki']:
                if target in metadata:
                    info = metadata[target]
                    stats[target] = {
                        'dataset': f"{info['dataset_name']} ({info['size']})",
                        'triplets': info.get('triplet_count', 0),
                        'loaded_at': info.get('loaded_at', 'Unknown'),
                        'graph_uri': info.get('graph_uri', 'Unknown')
                    }
                    stats['total_datasets_loaded'] += 1
                    stats['total_triplets'] += info.get('triplet_count', 0)

            return stats

        except Exception as e:
            log_message(f"Erreur récupération statistiques: {str(e)}", "error")
            return {}

    def get_dataset_info(self, dataset_name: str) -> Dict:
        """
        Récupère les informations détaillées d'un dataset

        Args:
            dataset_name: Nom du dataset

        Returns:
            Dictionnaire avec les informations du dataset
        """
        return self.DATASET_INFO.get(dataset_name, self.DATASET_INFO["Generic"])
