"""
Module de métriques avancées pour analyse de performance
Inclut percentiles (P50/P95/P99), métriques CPU par-core, analyse statistique
"""

import psutil
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
from config.settings import METRICS_CPU_INTERVAL, METRICS_MAX_HISTORY_SIZE
from utils.logging_config import get_logger


logger = get_logger("advanced_metrics")


@dataclass
class PercentileMetrics:
    """Métriques de percentiles pour une série de valeurs"""
    p50: float  # Médiane
    p75: float
    p90: float
    p95: float
    p99: float
    min: float
    max: float
    mean: float
    std: float
    count: int

    def to_dict(self) -> Dict[str, float]:
        """Convertit en dictionnaire"""
        return asdict(self)


@dataclass
class CPUCoreMetrics:
    """Métriques détaillées par cœur CPU"""
    core_id: int
    usage_percent: float
    frequency_mhz: Optional[float]
    is_physical: bool


@dataclass
class AdvancedSystemMetrics:
    """Métriques système complètes"""
    timestamp: float
    cpu_overall: float
    cpu_per_core: List[CPUCoreMetrics]
    memory_used_mb: float
    memory_percent: float
    memory_available_mb: float
    disk_read_mb: float
    disk_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    process_count: int


class AdvancedMetricsCollector:
    """Collecteur de métriques avancées avec analyse statistique"""

    def __init__(self):
        """Initialise le collecteur de métriques"""
        self.metrics_history: List[Dict[str, Any]] = []
        self.query_execution_times: Dict[str, List[float]] = defaultdict(list)

        # Baseline pour métriques différentielles
        self.baseline_disk_io = psutil.disk_io_counters()
        self.baseline_network_io = psutil.net_io_counters()

        logger.info("Collecteur de métriques avancées initialisé")

    def collect_cpu_per_core(self) -> List[CPUCoreMetrics]:
        """
        Collecte les métriques détaillées par cœur CPU

        Returns:
            Liste de métriques par cœur
        """
        try:
            # Usage par cœur - Utiliser la constante configurée
            per_core_usage = psutil.cpu_percent(interval=METRICS_CPU_INTERVAL, percpu=True)

            # Fréquences par cœur (si disponible)
            try:
                per_core_freq = psutil.cpu_freq(percpu=True)
            except:
                per_core_freq = None

            # Informations topologie
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False)
            is_hyperthreading = cpu_count_logical > cpu_count_physical

            cores_metrics = []

            for i, usage in enumerate(per_core_usage):
                # Fréquence pour ce cœur
                freq = None
                if per_core_freq and i < len(per_core_freq):
                    freq = per_core_freq[i].current if hasattr(per_core_freq[i], 'current') else None

                # Détermine si c'est un cœur physique
                is_physical = (i < cpu_count_physical) if is_hyperthreading else True

                cores_metrics.append(CPUCoreMetrics(
                    core_id=i,
                    usage_percent=usage,
                    frequency_mhz=freq,
                    is_physical=is_physical
                ))

            logger.debug(f"Collecté métriques pour {len(cores_metrics)} cœurs CPU")
            return cores_metrics

        except Exception as e:
            logger.error(f"Erreur collecte métriques CPU par-core: {str(e)}")
            return []

    def collect_memory_details(self) -> Dict[str, float]:
        """
        Collecte les détails mémoire avancés

        Returns:
            Dictionnaire de métriques mémoire
        """
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()

            return {
                "total_mb": mem.total / (1024 ** 2),
                "available_mb": mem.available / (1024 ** 2),
                "used_mb": mem.used / (1024 ** 2),
                "free_mb": mem.free / (1024 ** 2),
                "percent": mem.percent,
                "swap_total_mb": swap.total / (1024 ** 2),
                "swap_used_mb": swap.used / (1024 ** 2),
                "swap_percent": swap.percent
            }

        except Exception as e:
            logger.error(f"Erreur collecte métriques mémoire: {str(e)}")
            return {}

    def collect_disk_io(self) -> Dict[str, float]:
        """
        Collecte les métriques I/O disque

        Returns:
            Dictionnaire de métriques disque
        """
        try:
            current_io = psutil.disk_io_counters()

            if self.baseline_disk_io:
                read_mb = (current_io.read_bytes - self.baseline_disk_io.read_bytes) / (1024 ** 2)
                write_mb = (current_io.write_bytes - self.baseline_disk_io.write_bytes) / (1024 ** 2)
            else:
                read_mb = current_io.read_bytes / (1024 ** 2)
                write_mb = current_io.write_bytes / (1024 ** 2)

            return {
                "read_mb": read_mb,
                "write_mb": write_mb,
                "read_count": current_io.read_count,
                "write_count": current_io.write_count
            }

        except Exception as e:
            logger.error(f"Erreur collecte I/O disque: {str(e)}")
            return {}

    def collect_network_io(self) -> Dict[str, float]:
        """
        Collecte les métriques I/O réseau

        Returns:
            Dictionnaire de métriques réseau
        """
        try:
            current_io = psutil.net_io_counters()

            if self.baseline_network_io:
                sent_mb = (current_io.bytes_sent - self.baseline_network_io.bytes_sent) / (1024 ** 2)
                recv_mb = (current_io.bytes_recv - self.baseline_network_io.bytes_recv) / (1024 ** 2)
            else:
                sent_mb = current_io.bytes_sent / (1024 ** 2)
                recv_mb = current_io.bytes_recv / (1024 ** 2)

            return {
                "sent_mb": sent_mb,
                "recv_mb": recv_mb,
                "packets_sent": current_io.packets_sent,
                "packets_recv": current_io.packets_recv
            }

        except Exception as e:
            logger.error(f"Erreur collecte I/O réseau: {str(e)}")
            return {}

    def collect_advanced_system_metrics(self) -> AdvancedSystemMetrics:
        """
        Collecte toutes les métriques système avancées

        Returns:
            Objet AdvancedSystemMetrics complet
        """
        try:
            cpu_per_core = self.collect_cpu_per_core()
            memory = self.collect_memory_details()
            disk_io = self.collect_disk_io()
            network_io = self.collect_network_io()

            # Calculer cpu_overall depuis cpu_per_core pour éviter double collecte
            cpu_overall = sum(c.usage_percent for c in cpu_per_core) / len(cpu_per_core) if cpu_per_core else 0.0

            metrics = AdvancedSystemMetrics(
                timestamp=time.time(),
                cpu_overall=cpu_overall,
                cpu_per_core=cpu_per_core,
                memory_used_mb=memory.get("used_mb", 0),
                memory_percent=memory.get("percent", 0),
                memory_available_mb=memory.get("available_mb", 0),
                disk_read_mb=disk_io.get("read_mb", 0),
                disk_write_mb=disk_io.get("write_mb", 0),
                network_sent_mb=network_io.get("sent_mb", 0),
                network_recv_mb=network_io.get("recv_mb", 0),
                process_count=len(psutil.pids())
            )

            # Stocker dans l'historique avec rotation automatique
            self.metrics_history.append({
                "timestamp": metrics.timestamp,
                "cpu_overall": metrics.cpu_overall,
                "memory_percent": metrics.memory_percent,
                "disk_read_mb": metrics.disk_read_mb,
                "network_sent_mb": metrics.network_sent_mb
            })

            # Limiter la taille de l'historique pour éviter débordement mémoire
            if len(self.metrics_history) > METRICS_MAX_HISTORY_SIZE:
                self.metrics_history = self.metrics_history[-METRICS_MAX_HISTORY_SIZE:]
                logger.debug(f"Historique tronqué à {METRICS_MAX_HISTORY_SIZE} entrées")

            logger.debug("Métriques système avancées collectées")
            return metrics

        except Exception as e:
            logger.exception(f"Erreur collecte métriques avancées: {str(e)}")
            raise

    def record_query_execution(self, query_name: str, execution_time: float):
        """
        Enregistre le temps d'exécution d'une requête pour analyse statistique

        Args:
            query_name: Nom de la requête
            execution_time: Temps d'exécution en secondes
        """
        self.query_execution_times[query_name].append(execution_time)
        logger.debug(f"Enregistré: {query_name} = {execution_time:.3f}s")

    def calculate_percentiles(
        self,
        values: List[float],
        percentiles: List[int] = [50, 75, 90, 95, 99]
    ) -> PercentileMetrics:
        """
        Calcule les percentiles pour une série de valeurs

        Args:
            values: Liste de valeurs
            percentiles: Percentiles à calculer

        Returns:
            Objet PercentileMetrics avec toutes les statistiques
        """
        if not values:
            logger.warning("Calcul percentiles sur liste vide")
            return PercentileMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        arr = np.array(values)

        metrics = PercentileMetrics(
            p50=float(np.percentile(arr, 50)),
            p75=float(np.percentile(arr, 75)),
            p90=float(np.percentile(arr, 90)),
            p95=float(np.percentile(arr, 95)),
            p99=float(np.percentile(arr, 99)),
            min=float(np.min(arr)),
            max=float(np.max(arr)),
            mean=float(np.mean(arr)),
            std=float(np.std(arr)),
            count=len(values)
        )

        logger.debug(f"Percentiles calculés: P50={metrics.p50:.3f}, P95={metrics.p95:.3f}, P99={metrics.p99:.3f}")
        return metrics

    def get_query_percentiles(self, query_name: str) -> Optional[PercentileMetrics]:
        """
        Récupère les percentiles pour une requête spécifique

        Args:
            query_name: Nom de la requête

        Returns:
            PercentileMetrics ou None si pas de données
        """
        if query_name not in self.query_execution_times:
            logger.warning(f"Aucune donnée pour la requête: {query_name}")
            return None

        return self.calculate_percentiles(self.query_execution_times[query_name])

    def get_all_queries_percentiles(self) -> Dict[str, PercentileMetrics]:
        """
        Calcule les percentiles pour toutes les requêtes enregistrées

        Returns:
            Dictionnaire {query_name: PercentileMetrics}
        """
        results = {}

        for query_name, times in self.query_execution_times.items():
            if times:
                results[query_name] = self.calculate_percentiles(times)

        logger.info(f"Percentiles calculés pour {len(results)} requêtes")
        return results

    def generate_performance_report(self) -> Dict[str, Any]:
        """
        Génère un rapport complet de performance

        Returns:
            Dictionnaire contenant toutes les analyses
        """
        report = {
            "timestamp": time.time(),
            "total_queries_executed": sum(len(times) for times in self.query_execution_times.values()),
            "unique_queries": len(self.query_execution_times),
            "percentiles_by_query": {},
            "system_metrics_summary": {},
            "top_slowest_queries": [],
            "top_fastest_queries": []
        }

        # Percentiles par requête
        all_percentiles = self.get_all_queries_percentiles()
        report["percentiles_by_query"] = {
            name: metrics.to_dict()
            for name, metrics in all_percentiles.items()
        }

        # Top 5 plus lentes (P95)
        sorted_by_p95 = sorted(
            all_percentiles.items(),
            key=lambda x: x[1].p95,
            reverse=True
        )
        report["top_slowest_queries"] = [
            {"query": name, "p95": metrics.p95, "mean": metrics.mean}
            for name, metrics in sorted_by_p95[:5]
        ]

        # Top 5 plus rapides (P50)
        sorted_by_p50 = sorted(
            all_percentiles.items(),
            key=lambda x: x[1].p50
        )
        report["top_fastest_queries"] = [
            {"query": name, "p50": metrics.p50, "mean": metrics.mean}
            for name, metrics in sorted_by_p50[:5]
        ]

        # Résumé métriques système
        if self.metrics_history:
            history_df = pd.DataFrame(self.metrics_history)
            report["system_metrics_summary"] = {
                "cpu_mean": float(history_df["cpu_overall"].mean()),
                "cpu_max": float(history_df["cpu_overall"].max()),
                "memory_mean": float(history_df["memory_percent"].mean()),
                "memory_max": float(history_df["memory_percent"].max()),
                "samples_collected": len(self.metrics_history)
            }

        logger.info("Rapport de performance généré")
        return report

    def clear_history(self):
        """Efface l'historique des métriques"""
        self.metrics_history.clear()
        self.query_execution_times.clear()
        logger.info("Historique des métriques effacé")

    def export_to_dataframe(self) -> pd.DataFrame:
        """
        Exporte toutes les données en DataFrame pour analyse

        Returns:
            DataFrame avec toutes les métriques
        """
        rows = []

        for query_name, times in self.query_execution_times.items():
            for i, exec_time in enumerate(times):
                rows.append({
                    "query_name": query_name,
                    "iteration": i + 1,
                    "execution_time": exec_time
                })

        df = pd.DataFrame(rows)
        logger.info(f"DataFrame exporté: {len(df)} lignes")
        return df
