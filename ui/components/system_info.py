"""
Composant pour afficher les informations système
"""

import psutil
import os
import sys
import platform
from datetime import datetime
from typing import Dict, Any
from core.metrics import MetricsCollector
from utils.helpers import format_memory_size, log_message

class SystemInfoDisplay:
    """Classe pour afficher les informations système"""
    
    def __init__(self):
        """Initialise l'afficheur d'informations système"""
        self.metrics_collector = MetricsCollector()
    
    def _get_detailed_os_info(self) -> Dict[str, str]:
        """
        Récupère des informations détaillées sur le système d'exploitation
        
        Returns:
            Dictionnaire avec les informations détaillées de l'OS
        """
        os_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "detailed_name": ""
        }
        
        try:
            if platform.system() == "Windows":
                # Utilisation de WMI pour Windows pour plus de précision
                try:
                    import wmi
                    c = wmi.WMI()
                    
                    # Informations détaillées sur l'OS
                    for os_info_wmi in c.Win32_OperatingSystem():
                        os_info["detailed_name"] = os_info_wmi.Caption
                        os_info["version"] = os_info_wmi.Version
                        os_info["build"] = os_info_wmi.BuildNumber
                        os_info["architecture"] = os_info_wmi.OSArchitecture
                        break
                        
                except ImportError:
                    # Fallback si WMI n'est pas disponible
                    try:
                        import winreg
                        
                        # Lecture du registre Windows pour les informations détaillées
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                           r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                        
                        try:
                            product_name = winreg.QueryValueEx(key, "ProductName")[0]
                            current_build = winreg.QueryValueEx(key, "CurrentBuild")[0]
                            display_version = winreg.QueryValueEx(key, "DisplayVersion")[0]
                            
                            os_info["detailed_name"] = f"{product_name}"
                            os_info["build"] = current_build
                            os_info["display_version"] = display_version
                            
                        except FileNotFoundError:
                            pass
                        finally:
                            winreg.CloseKey(key)
                            
                    except Exception:
                        # Utiliser les informations de base de platform
                        os_info["detailed_name"] = f"{platform.system()} {platform.release()}"
            else:
                # Pour Linux/Mac
                os_info["detailed_name"] = f"{platform.system()} {platform.release()}"
                
        except Exception as e:
            log_message(f"Erreur lors de la récupération des infos OS détaillées: {str(e)}", "warning")
            os_info["detailed_name"] = f"{platform.system()} {platform.release()}"
        
        return os_info
    
    def _get_detailed_cpu_info(self) -> Dict[str, str]:
        """
        Récupère des informations détaillées sur le processeur
        
        Returns:
            Dictionnaire avec les informations détaillées du CPU
        """
        cpu_info = {
            "name": platform.processor() or "Information non disponible",
            "architecture": platform.machine(),
            "cores_physical": psutil.cpu_count(logical=False),
            "cores_logical": psutil.cpu_count(logical=True),
            "frequency": "Non disponible"
        }
        
        try:
            if platform.system() == "Windows":
                # Utilisation de WMI pour Windows
                try:
                    import wmi
                    c = wmi.WMI()
                    
                    for processor in c.Win32_Processor():
                        cpu_info["name"] = processor.Name.strip()
                        cpu_info["max_clock_speed"] = f"{processor.MaxClockSpeed} MHz"
                        cpu_info["manufacturer"] = processor.Manufacturer
                        cpu_info["description"] = processor.Description
                        break
                        
                except ImportError:
                    # Fallback avec le registre Windows
                    try:
                        import winreg
                        
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                           r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
                        
                        try:
                            cpu_name = winreg.QueryValueEx(key, "ProcessorNameString")[0]
                            cpu_info["name"] = cpu_name.strip()
                            
                            # Fréquence du processeur
                            try:
                                cpu_mhz = winreg.QueryValueEx(key, "~MHz")[0]
                                cpu_info["frequency"] = f"{cpu_mhz} MHz"
                            except FileNotFoundError:
                                pass
                                
                        except FileNotFoundError:
                            pass
                        finally:
                            winreg.CloseKey(key)
                            
                    except Exception:
                        pass
            
            # Informations de fréquence via psutil (disponible sur tous les OS)
            try:
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    cpu_info["current_freq"] = f"{cpu_freq.current:.0f} MHz"
                    cpu_info["max_freq"] = f"{cpu_freq.max:.0f} MHz" if cpu_freq.max else "Non disponible"
                    cpu_info["min_freq"] = f"{cpu_freq.min:.0f} MHz" if cpu_freq.min else "Non disponible"
            except Exception:
                pass
                
        except Exception as e:
            log_message(f"Erreur lors de la récupération des infos CPU détaillées: {str(e)}", "warning")
        
        return cpu_info
    
    def get_system_summary(self) -> Dict[str, str]:
        """
        Récupère un résumé des informations système avec détection précise
        
        Returns:
            Dictionnaire formaté des informations système
        """
        try:
            # Informations détaillées de l'OS
            os_info = self._get_detailed_os_info()
            
            # Informations détaillées du CPU
            cpu_info = self._get_detailed_cpu_info()
            
            # Informations de base
            info = {
                "Système d'exploitation": os_info.get("detailed_name", f"{platform.system()} {platform.release()}"),
                "Architecture": platform.machine(),
                "Processeur": cpu_info["name"],
                "Python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "Date et heure": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Ajout des informations supplémentaires si disponibles
            if "build" in os_info:
                info["Build OS"] = os_info["build"]
            
            if "display_version" in os_info:
                info["Version OS"] = os_info["display_version"]
            
            # Informations CPU détaillées
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False)
            cpu_percent = psutil.cpu_percent(interval=1)
            
            info["CPU"] = f"{cpu_count_physical} cœurs physiques, {cpu_count_logical} cœurs logiques"
            info["Utilisation CPU"] = f"{cpu_percent:.1f}%"
            
            # Ajout de la fréquence si disponible
            if "current_freq" in cpu_info:
                info["Fréquence CPU"] = cpu_info["current_freq"]
            elif "max_clock_speed" in cpu_info:
                info["Fréquence CPU"] = cpu_info["max_clock_speed"]
            
            # Informations mémoire
            memory = psutil.virtual_memory()
            info["Mémoire totale"] = format_memory_size(memory.total)
            info["Mémoire disponible"] = format_memory_size(memory.available)
            info["Utilisation mémoire"] = f"{memory.percent:.1f}%"
            
            # Informations disque
            disk = psutil.disk_usage('/')
            disk_used_percent = (disk.used / disk.total) * 100
            info["Espace disque total"] = format_memory_size(disk.total)
            info["Espace disque libre"] = format_memory_size(disk.free)
            info["Utilisation disque"] = f"{disk_used_percent:.1f}%"
            
            return info
            
        except Exception as e:
            log_message(f"Erreur lors de la récupération des informations système: {str(e)}", "error")
            return {"Erreur": "Impossible de récupérer les informations système"}
    
    def get_detailed_system_info(self) -> Dict[str, Any]:
        """
        Récupère des informations système détaillées
        
        Returns:
            Dictionnaire détaillé des informations système
        """
        try:
            detailed_info = self.metrics_collector.get_system_info()
            
            # Ajout des informations détaillées de l'OS et du CPU
            os_info = self._get_detailed_os_info()
            cpu_info = self._get_detailed_cpu_info()
            
            # Ajout d'informations supplémentaires
            detailed_info["platform"] = {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": cpu_info["name"],
                "python_version": sys.version,
                "python_implementation": platform.python_implementation(),
                "detailed_os": os_info,
                "detailed_cpu": cpu_info
            }
            
            # Informations sur les processus
            try:
                process_count = len(psutil.pids())
                detailed_info["processes"] = {
                    "total_count": process_count,
                    "current_process_memory": psutil.Process().memory_info().rss / (1024**2),  # MB
                    "current_process_cpu": psutil.Process().cpu_percent()
                }
            except Exception:
                detailed_info["processes"] = {"error": "Impossible d'obtenir les informations de processus"}
            
            # Informations sur l'environnement Python
            detailed_info["python_environment"] = {
                "executable": sys.executable,
                "path": sys.path[:3],  # Premiers éléments du path
                "modules_count": len(sys.modules)
            }
            
            return detailed_info
            
        except Exception as e:
            log_message(f"Erreur lors de la récupération des informations détaillées: {str(e)}", "error")
            return {"error": f"Impossible de récupérer les informations détaillées: {str(e)}"}
    
    def get_performance_baseline(self) -> Dict[str, Any]:
        """
        Établit une baseline de performance système
        
        Returns:
            Métriques de baseline
        """
        try:
            import time
            
            # Collecte de métriques sur une courte période
            baseline_metrics = []
            
            for i in range(5):
                metrics = self.metrics_collector.collect_system_metrics()
                baseline_metrics.append(metrics)
                time.sleep(0.5)
            
            # Calcul des moyennes
            avg_cpu = sum(m["cpu"] for m in baseline_metrics) / len(baseline_metrics)
            avg_memory = sum(m["memory"] for m in baseline_metrics) / len(baseline_metrics)
            
            baseline = {
                "timestamp": datetime.now().isoformat(),
                "avg_cpu_percent": round(avg_cpu, 2),
                "avg_memory_mb": round(avg_memory, 2),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_io": self._get_disk_io_baseline(),
                "network_io": self._get_network_io_baseline()
            }
            
            return baseline
            
        except Exception as e:
            log_message(f"Erreur lors de l'établissement de la baseline: {str(e)}", "error")
            return {"error": f"Impossible d'établir la baseline: {str(e)}"}
    
    def _get_disk_io_baseline(self) -> Dict[str, Any]:
        """Récupère les métriques de base des I/O disque"""
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                return {
                    "read_bytes": disk_io.read_bytes,
                    "write_bytes": disk_io.write_bytes,
                    "read_count": disk_io.read_count,
                    "write_count": disk_io.write_count
                }
        except Exception:
            pass
        return {"error": "Métriques I/O disque non disponibles"}
    
    def _get_network_io_baseline(self) -> Dict[str, Any]:
        """Récupère les métriques de base des I/O réseau"""
        try:
            net_io = psutil.net_io_counters()
            if net_io:
                return {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv
                }
        except Exception:
            pass
        return {"error": "Métriques I/O réseau non disponibles"}
    
    def check_system_readiness(self) -> Dict[str, Any]:
        """
        Vérifie si le système est prêt pour les tests de performance
        
        Returns:
            Résultat de la vérification
        """
        readiness = {
            "ready": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        try:
            # Vérification de la mémoire disponible
            memory = psutil.virtual_memory()
            if memory.percent > 80:
                readiness["warnings"].append("Utilisation mémoire élevée (>80%)")
                readiness["recommendations"].append("Fermez des applications pour libérer de la mémoire")
            
            if memory.available < 1024**3:  # Moins de 1GB disponible
                readiness["errors"].append("Mémoire disponible insuffisante (<1GB)")
                readiness["ready"] = False
            
            # Vérification CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 70:
                readiness["warnings"].append("Utilisation CPU élevée (>70%)")
                readiness["recommendations"].append("Attendez que la charge CPU diminue")
            
            # Vérification de l'espace disque
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > 90:
                readiness["warnings"].append("Espace disque faible (<10% libre)")
                readiness["recommendations"].append("Libérez de l'espace disque")
            
            if disk.free < 500 * 1024**2:  # Moins de 500MB libre
                readiness["errors"].append("Espace disque critique (<500MB libre)")
                readiness["ready"] = False
            
            # Vérifications des dépendances Python
            required_modules = ['streamlit', 'pandas', 'plotly', 'SPARQLWrapper', 'psutil']
            missing_modules = []
            
            for module in required_modules:
                try:
                    __import__(module)
                except ImportError:
                    missing_modules.append(module)
            
            if missing_modules:
                readiness["errors"].append(f"Modules Python manquants: {', '.join(missing_modules)}")
                readiness["ready"] = False
            
            # Recommandations générales
            if readiness["ready"]:
                readiness["recommendations"].extend([
                    "Fermez les applications non nécessaires pour de meilleures mesures",
                    "Utilisez plusieurs itérations pour des résultats plus fiables",
                    "Considérez les itérations d'échauffement pour stabiliser les performances"
                ])
            
        except Exception as e:
            readiness["errors"].append(f"Erreur lors de la vérification: {str(e)}")
            readiness["ready"] = False
        
        return readiness
    
    def get_environment_variables(self) -> Dict[str, str]:
        """
        Récupère les variables d'environnement pertinentes
        
        Returns:
            Dictionnaire des variables d'environnement
        """
        relevant_vars = [
            'JAVA_HOME', 'PYTHONPATH', 'PATH', 'HOME', 'USER', 'USERNAME',
            'VIRTUOSO_ENDPOINT', 'FUSEKI_ENDPOINT', 'DEBUG_MODE',
            'PROCESSOR_IDENTIFIER', 'PROCESSOR_ARCHITECTURE'  # Variables Windows spécifiques
        ]
        
        env_vars = {}
        for var in relevant_vars:
            value = os.environ.get(var)
            if value:
                # Tronquer les valeurs trop longues
                if len(value) > 100:
                    value = value[:97] + "..."
                env_vars[var] = value
        
        return env_vars