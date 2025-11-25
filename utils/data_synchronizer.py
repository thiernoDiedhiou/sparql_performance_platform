"""
Module de synchronisation optimisé avec support chunking pour gros datasets
Version 2.0 - Améliorations majeures pour performance
"""

import streamlit as st
import requests
import time
from SPARQLWrapper import SPARQLWrapper, TURTLE, CSV, JSON
from typing import Dict, Any, Optional, Callable, List
from utils.helpers import log_message, format_memory_size
from utils.logging_config import get_logger, log_sync, ContextLogger
from core.executor import QueryExecutor
from config.settings import CONNECTIVITY_TIMEOUT, SYNC_CHUNK_SIZE, MAX_SYNC_TRIPLETS


logger = get_logger("data_synchronizer")


class ChunkedDataSynchronizer:
    """
    Synchroniseur de données optimisé avec support de chunking
    Gère efficacement les gros datasets (> 1M triplets)
    """

    def __init__(self, virtuoso_endpoint: str, fuseki_endpoint: str):
        """
        Initialise le synchroniseur optimisé

        Args:
            virtuoso_endpoint: URL de l'endpoint Virtuoso
            fuseki_endpoint: URL de l'endpoint Jena Fuseki
        """
        self.virtuoso_endpoint = virtuoso_endpoint
        self.fuseki_endpoint = fuseki_endpoint
        self.fuseki_base_url = self._extract_fuseki_base_url(fuseki_endpoint)
        self.executor = QueryExecutor(timeout=CONNECTIVITY_TIMEOUT)

        # Configuration chunking
        self.chunk_size = SYNC_CHUNK_SIZE
        self.max_triplets = MAX_SYNC_TRIPLETS

        logger.info(f"Synchroniseur initialisé - Chunk: {self.chunk_size:,}, Max: {self.max_triplets:,}")

    def _extract_fuseki_base_url(self, fuseki_endpoint: str) -> str:
        """Extrait l'URL de base Fuseki"""
        if '/query' in fuseki_endpoint:
            return fuseki_endpoint.replace('/query', '')
        elif '/sparql' in fuseki_endpoint:
            return fuseki_endpoint.replace('/sparql', '')
        return fuseki_endpoint

    def count_triplets(self, endpoint_url: str, graph_uri: Optional[str] = None) -> int:
        """
        Compte le nombre de triplets dans un endpoint SPARQL

        Args:
            endpoint_url: URL de l'endpoint SPARQL
            graph_uri: URI du graphe nommé (None = TOUS les triplets, y compris graphes nommés)

        Returns:
            Nombre de triplets (0 en cas d'erreur)
        """
        if graph_uri:
            # Compter dans un graphe spécifique
            count_query = f"SELECT (COUNT(*) AS ?count) WHERE {{ GRAPH <{graph_uri}> {{ ?s ?p ?o }} }}"
        else:
            # Compter uniquement le graphe par défaut (correspond à ce qui est exporté)
            count_query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o . }"

        try:
            result = self.executor.execute_query(endpoint_url, count_query)

            if result["success"] and result["results"]:
                bindings = result["results"].get("results", {}).get("bindings", [])
                if bindings and "count" in bindings[0]:
                    count = int(bindings[0]["count"]["value"])
                    graph_info = f" (graphe: {graph_uri})" if graph_uri else ""
                    logger.debug(f"Triplets comptés: {count:,} dans {endpoint_url}{graph_info}")
                    return count

            return 0

        except Exception as e:
            logger.error(f"Erreur comptage triplets {endpoint_url}: {str(e)}")
            return 0

    def export_chunk_from_virtuoso(
        self,
        offset: int,
        limit: int,
        graph_uri: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> Optional[str]:
        """
        Exporte un chunk de données depuis Virtuoso

        Args:
            offset: Décalage de début
            limit: Nombre de triplets à exporter
            graph_uri: URI du graphe source (None = graphe par défaut)
            progress_callback: Fonction de callback pour progression

        Returns:
            Données RDF au format TURTLE ou None
        """
        try:
            sparql = SPARQLWrapper(self.virtuoso_endpoint)

            if graph_uri:
                query = f"""
                CONSTRUCT {{ ?s ?p ?o }}
                WHERE {{ GRAPH <{graph_uri}> {{ ?s ?p ?o }} }}
                LIMIT {limit}
                OFFSET {offset}
                """
            else:
                query = f"""
                CONSTRUCT {{ ?s ?p ?o }}
                WHERE {{ ?s ?p ?o }}
                LIMIT {limit}
                OFFSET {offset}
                """

            sparql.setQuery(query)
            sparql.setReturnFormat(TURTLE)
            sparql.setTimeout(300)  # 5 minutes par chunk

            graph_info = f" (graphe: {graph_uri})" if graph_uri else ""
            logger.debug(f"Export chunk: offset={offset:,}, limit={limit:,}{graph_info}")

            if progress_callback:
                progress_callback(offset, limit, f"Export du chunk {offset:,}-{offset+limit:,}")

            results = sparql.query().convert()

            # Conversion en string
            if isinstance(results, bytes):
                turtle_data = results.decode('utf-8')
            else:
                turtle_data = str(results)

            lines = len(turtle_data.splitlines())
            logger.info(f"Chunk exporté: {lines} lignes RDF")

            return turtle_data

        except Exception as e:
            logger.error(f"Erreur export chunk offset={offset}: {str(e)}")
            return None

    def export_data_chunked(
        self,
        total_triplets: Optional[int] = None,
        graph_uri: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> List[str]:
        """
        Exporte toutes les données par chunks

        Args:
            total_triplets: Nombre total de triplets (détecté auto si None)
            graph_uri: URI du graphe source (None = graphe par défaut)
            progress_callback: Fonction de callback pour progression

        Returns:
            Liste de chunks RDF en format TURTLE
        """
        chunks = []

        try:
            # Compter les triplets si non fourni
            if total_triplets is None:
                total_triplets = self.count_triplets(self.virtuoso_endpoint, graph_uri)

            if total_triplets == 0:
                logger.warning("Aucun triplet à exporter")
                return chunks

            # Limiter au maximum configuré
            triplets_to_export = min(total_triplets, self.max_triplets)

            if total_triplets > self.max_triplets:
                logger.warning(
                    f"Dataset trop large ({total_triplets:,}), "
                    f"limité à {self.max_triplets:,} triplets"
                )
                st.warning(
                    f"⚠️ Dataset limité à {self.max_triplets:,} triplets "
                    f"(total: {total_triplets:,})"
                )

            # Calculer le nombre de chunks
            num_chunks = (triplets_to_export + self.chunk_size - 1) // self.chunk_size

            graph_info = f" (graphe: {graph_uri})" if graph_uri else ""
            logger.info(
                f"Export chunked démarré: {triplets_to_export:,} triplets "
                f"en {num_chunks} chunks de {self.chunk_size:,}{graph_info}"
            )

            st.info(
                f"🔄 Export de {triplets_to_export:,} triplets "
                f"en {num_chunks} chunks..."
            )

            # Exporter chaque chunk
            for i in range(num_chunks):
                offset = i * self.chunk_size
                limit = min(self.chunk_size, triplets_to_export - offset)

                logger.debug(f"Traitement chunk {i+1}/{num_chunks}")

                chunk_data = self.export_chunk_from_virtuoso(
                    offset=offset,
                    limit=limit,
                    graph_uri=graph_uri,
                    progress_callback=progress_callback
                )

                if chunk_data:
                    chunks.append(chunk_data)
                    logger.info(f"Chunk {i+1}/{num_chunks} exporté avec succès")
                else:
                    logger.error(f"Échec export chunk {i+1}/{num_chunks}")

            logger.info(f"Export chunked terminé: {len(chunks)}/{num_chunks} chunks réussis")
            return chunks

        except Exception as e:
            logger.exception(f"Erreur lors de l'export chunked: {str(e)}")
            st.error(f"❌ Erreur export chunked: {str(e)}")
            return chunks

    def upload_chunk_to_fuseki(
        self,
        chunk_data: str,
        chunk_number: int,
        graph_uri: Optional[str] = None
    ) -> bool:
        """
        Upload un chunk de données vers Fuseki

        Args:
            chunk_data: Données RDF au format TURTLE
            chunk_number: Numéro du chunk (pour logging)
            graph_uri: URI du graphe cible (None = graphe par défaut)

        Returns:
            True si l'upload a réussi
        """
        try:
            # Construire l'URL avec le graphe cible si spécifié
            if graph_uri:
                upload_url = f"{self.fuseki_base_url}/data?graph={graph_uri}"
            else:
                upload_url = f"{self.fuseki_base_url}/data"

            headers = {
                'Content-Type': 'text/turtle; charset=utf-8'
            }

            graph_info = f" (graphe: {graph_uri})" if graph_uri else ""
            logger.debug(f"Upload chunk {chunk_number} vers Fuseki{graph_info}...")

            response = requests.post(
                upload_url,
                data=chunk_data.encode('utf-8'),
                headers=headers,
                timeout=300  # 5 minutes
            )

            if response.status_code in [200, 201, 204]:
                logger.info(f"Chunk {chunk_number} uploadé avec succès")
                return True
            else:
                logger.error(
                    f"Échec upload chunk {chunk_number}: "
                    f"HTTP {response.status_code}"
                )
                return False

        except Exception as e:
            logger.exception(f"Erreur upload chunk {chunk_number}: {str(e)}")
            return False

    def clear_fuseki_dataset(self, graph_uri: Optional[str] = None) -> bool:
        """
        Vide complètement le dataset Fuseki ou un graphe spécifique

        Args:
            graph_uri: URI du graphe à vider (None = tout le dataset)

        Returns:
            True si le nettoyage a réussi
        """
        try:
            update_url = f"{self.fuseki_base_url}/update"

            if graph_uri:
                delete_query = f"CLEAR GRAPH <{graph_uri}>"
                st.info(f"🧹 Nettoyage du graphe {graph_uri}...")
                logger.info(f"Nettoyage du graphe {graph_uri}...")
            else:
                delete_query = "DELETE WHERE { ?s ?p ?o }"
                st.info("🧹 Nettoyage du dataset Fuseki...")
                logger.info("Nettoyage du dataset Fuseki...")

            response = requests.post(
                update_url,
                data={'update': delete_query},
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=120
            )

            if response.status_code in [200, 204]:
                logger.info("Nettoyage Fuseki réussi")
                return True
            else:
                logger.warning(f"Erreur nettoyage: HTTP {response.status_code}")
                return False

        except Exception as e:
            logger.exception(f"Impossible de vider Fuseki: {str(e)}")
            return False

    def synchronize_datasets_chunked(
        self,
        clear_target: bool = True,
        limit_triplets: Optional[int] = None,
        show_progress: bool = True,
        source_graph_uri: Optional[str] = None,
        target_graph_uri: Optional[str] = None
    ) -> bool:
        """
        Synchronise les données de Virtuoso vers Fuseki avec chunking

        Args:
            clear_target: Vider Fuseki avant synchronisation
            limit_triplets: Limiter le nombre de triplets (None = auto)
            show_progress: Afficher la progression dans l'UI
            source_graph_uri: URI du graphe source dans Virtuoso (None = graphe par défaut)
            target_graph_uri: URI du graphe cible dans Fuseki (None = graphe par défaut)

        Returns:
            True si la synchronisation a réussi
        """
        with ContextLogger(logger, "Synchronisation chunked", level="INFO"):

            st.subheader("🔄 Synchronisation Optimisée (Chunking)")

            # Étape 1: Vérification initiale
            virtuoso_count = self.count_triplets(self.virtuoso_endpoint, source_graph_uri)
            fuseki_count = self.count_triplets(self.fuseki_endpoint, target_graph_uri)

            st.write("📊 **État initial:**")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Virtuoso", f"{virtuoso_count:,} triplets")
            with col2:
                st.metric("Jena Fuseki", f"{fuseki_count:,} triplets")

            if virtuoso_count == 0:
                st.warning("⚠️ Virtuoso ne contient aucune donnée")
                logger.warning("Virtuoso vide, synchronisation annulée")
                return False

            if virtuoso_count == fuseki_count and fuseki_count > 0:
                st.success("✅ Les datasets sont déjà synchronisés !")
                logger.info("Datasets déjà synchronisés")
                return True

            # Étape 2: Nettoyage optionnel (confirmation déjà effectuée dans l'UI)
            if clear_target and fuseki_count > 0:
                st.info(f"🗑️ Suppression de {fuseki_count:,} triplets existants dans Fuseki...")
                if not self.clear_fuseki_dataset(target_graph_uri):
                    st.warning("⚠️ Échec nettoyage, mais on continue...")
                else:
                    st.success("✅ Données Fuseki supprimées avec succès")

            # Étape 3: Export chunked avec progression
            st.info("📦 Export des données par chunks...")

            progress_bar = st.progress(0.0)
            status_text = st.empty()

            def progress_callback(offset, limit, message):
                if show_progress:
                    total = limit_triplets if limit_triplets else virtuoso_count
                    progress = min((offset + limit) / total, 1.0)
                    progress_bar.progress(progress)
                    status_text.text(message)

            start_time = time.time()

            chunks = self.export_data_chunked(
                total_triplets=limit_triplets,
                graph_uri=source_graph_uri,
                progress_callback=progress_callback
            )

            export_duration = time.time() - start_time

            if not chunks:
                st.error("❌ Aucun chunk exporté")
                logger.error("Export chunked échoué")
                return False

            st.success(
                f"✅ Export réussi: {len(chunks)} chunks en {export_duration:.1f}s"
            )

            # Étape 4: Upload chunked
            st.info("📤 Upload des chunks vers Fuseki...")
            upload_progress = st.progress(0.0)

            successful_uploads = 0
            start_time = time.time()

            for i, chunk in enumerate(chunks):
                if self.upload_chunk_to_fuseki(chunk, i + 1, target_graph_uri):
                    successful_uploads += 1

                upload_progress.progress((i + 1) / len(chunks))

            upload_duration = time.time() - start_time

            if successful_uploads < len(chunks):
                st.warning(
                    f"⚠️ Upload partiel: {successful_uploads}/{len(chunks)} chunks"
                )
                logger.warning(
                    f"Upload partiel: {successful_uploads}/{len(chunks)}"
                )

            # Étape 5: Vérification finale
            st.info("🔍 Vérification de la synchronisation...")
            time.sleep(3)  # Attendre que Fuseki traite

            final_fuseki_count = self.count_triplets(self.fuseki_endpoint, target_graph_uri)

            st.write("📊 **État final:**")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Virtuoso", f"{virtuoso_count:,} triplets")
            with col2:
                delta = final_fuseki_count - fuseki_count
                st.metric(
                    "Jena Fuseki",
                    f"{final_fuseki_count:,} triplets",
                    delta=f"+{delta:,}" if delta > 0 else None
                )

            # Résultat
            success_rate = (
                (final_fuseki_count / virtuoso_count) * 100
                if virtuoso_count > 0 else 0
            )

            total_duration = export_duration + upload_duration

            if success_rate >= 95:
                st.success(
                    f"✅ Synchronisation réussie ! "
                    f"{final_fuseki_count:,} triplets ({success_rate:.1f}%) "
                    f"en {total_duration:.1f}s"
                )

                log_sync(
                    logger,
                    "Chunked sync",
                    virtuoso_count,
                    final_fuseki_count,
                    True,
                    total_duration
                )

                return True
            else:
                st.warning(
                    f"⚠️ Synchronisation partielle: {success_rate:.1f}% "
                    f"des données transférées"
                )

                log_sync(
                    logger,
                    "Chunked sync (partial)",
                    virtuoso_count,
                    final_fuseki_count,
                    False,
                    total_duration
                )

                return success_rate > 50  # Succès si > 50%

    def estimate_sync_time(self, triplet_count: int) -> Dict[str, Any]:
        """
        Estime le temps de synchronisation

        Args:
            triplet_count: Nombre de triplets à synchroniser

        Returns:
            Dictionnaire avec estimations
        """
        # Estimation basée sur 1000 triplets/seconde
        # (ajuster selon benchmark réel)
        triplets_per_second = 1000

        estimated_seconds = triplet_count / triplets_per_second
        num_chunks = (triplet_count + self.chunk_size - 1) // self.chunk_size

        return {
            "triplets": triplet_count,
            "estimated_duration": estimated_seconds,
            "estimated_minutes": estimated_seconds / 60,
            "num_chunks": num_chunks,
            "chunk_size": self.chunk_size
        }


# Compatibilité avec l'ancienne API
class DataSynchronizer(ChunkedDataSynchronizer):
    """Alias pour compatibilité ascendante"""

    def synchronize_datasets(
        self,
        clear_target: bool = True,
        limit_triplets: Optional[int] = None,
        source_graph_uri: Optional[str] = None,
        target_graph_uri: Optional[str] = None
    ) -> bool:
        """
        Méthode compatible avec l'ancienne API avec support des graphes nommés

        Args:
            clear_target: Vider Fuseki avant synchronisation
            limit_triplets: Limiter le nombre de triplets
            source_graph_uri: URI du graphe source dans Virtuoso
            target_graph_uri: URI du graphe cible dans Fuseki

        Returns:
            True si la synchronisation a réussi
        """
        return self.synchronize_datasets_chunked(
            clear_target=clear_target,
            limit_triplets=limit_triplets,
            show_progress=True,
            source_graph_uri=source_graph_uri,
            target_graph_uri=target_graph_uri
        )
