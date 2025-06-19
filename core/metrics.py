"""
Module de collecte des métriques système
"""

import psutil
import time
from typing import Dict, Any
from utils.helpers import log_message

class MetricsCollector:
    """Classe responsable de la collecte des métriques système"""
    
    def __init__(self):
        """Initialise le collecteur de métriques"""
        self.baseline_metrics = self.collect_system_metrics()
    
    def collect_system_metrics(self) -> Dict[str, float]:
        """
        Collecte les métriques système actuelles
        
        Returns:
            Dictionnaire contenant les métriques système
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory_info = psutil.virtual_memory()
            memory_used_mb = memory_info.used / (1024 * 1024)  # Conversion en MB
            
            return {
                "cpu": cpu_percent,
                "memory": memory_used_mb,
                "memory_percent": memory_info.percent,
                "timestamp": time.time()
            }
            
        except Exception as e:
            log_message(f"Erreur lors de la collecte des métriques: {str(e)}")
            return {
                "cpu": 0.0,
                "memory": 0.0,
                "memory_percent": 0.0,
                "timestamp": time.time()
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Récupère les informations détaillées du système
        
        Returns:
            Dictionnaire contenant les informations système
        """
        try:
            # Informations CPU
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False)
            cpu_freq = psutil.cpu_freq()
            
            # Informations mémoire
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Informations disque
            disk_usage = psutil.disk_usage('/')
            
            # Informations réseau
            network_stats = psutil.net_io_counters()
            
            return {
                "cpu": {
                    "logical_cores": cpu_count_logical,
                    "physical_cores": cpu_count_physical,
                    "max_frequency": cpu_freq.max if cpu_freq else None,
                    "current_frequency": cpu_freq.current if cpu_freq else None
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": memory.percent
                },
                "swap": {
                    "total_gb": round(swap.total / (1024**3), 2),
                    "used_percent": swap.percent
                },
                "disk": {
                    "total_gb": round(disk_usage.total / (1024**3), 2),
                    "free_gb": round(disk_usage.free / (1024**3), 2),
                    "used_percent": round((disk_usage.used / disk_usage.total) * 100, 2)
                },
                "network": {
                    "bytes_sent": network_stats.bytes_sent,
                    "bytes_recv": network_stats.bytes_recv,
                    "packets_sent": network_stats.packets_sent,
                    "packets_recv": network_stats.packets_recv
                }
            }
            
        except Exception as e:
            log_message(f"Erreur lors de la récupération des informations système: {str(e)}")
            return {}
    
    def calculate_resource_usage(self, start_metrics: Dict[str, float], 
                               end_metrics: Dict[str, float]) -> Dict[str, float]:
        """
        Calcule l'utilisation des ressources entre deux points de mesure
        
        Args:
            start_metrics: Métriques au début
            end_metrics: Métriques à la fin
            
        Returns:
            Dictionnaire contenant l'utilisation des ressources
        """
        return {
            "cpu_usage": end_metrics["cpu"] - start_metrics["cpu"],
            "memory_usage": end_metrics["memory"] - start_metrics["memory"],
            "duration": end_metrics["timestamp"] - start_metrics["timestamp"]
        }
    
    def get_baseline_metrics(self) -> Dict[str, float]:
        """
        Retourne les métriques de base du système
        
        Returns:
            Métriques de base collectées à l'initialisation
        """
        return self.baseline_metrics.copy()
    
    def update_baseline(self):
        """Met à jour les métriques de base"""
        self.baseline_metrics = self.collect_system_metrics()
        log_message("Métriques de base mises à jour")
    
    def monitor_resources(self, duration: int = 60, interval: int = 1) -> Dict[str, Any]:
        """
        Surveille les ressources pendant une durée donnée
        
        Args:
            duration: Durée de surveillance en secondes
            interval: Intervalle entre les mesures en secondes
            
        Returns:
            Dictionnaire contenant l'historique des métriques
        """
        metrics_history = []
        start_time = time.time()
        
        while (time.time() - start_time) < duration:
            metrics = self.collect_system_metrics()
            metrics_history.append(metrics)
            time.sleep(interval)
        
        return {
            "history": metrics_history,
            "duration": duration,
            "samples": len(metrics_history),
            "average_cpu": sum(m["cpu"] for m in metrics_history) / len(metrics_history),
            "average_memory": sum(m["memory"] for m in metrics_history) / len(metrics_history),
            "max_cpu": max(m["cpu"] for m in metrics_history),
            "max_memory": max(m["memory"] for m in metrics_history)
        }