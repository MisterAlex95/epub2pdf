"""
Module d'optimisation des performances pour epub2pdf
"""

import time
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import List, Dict, Any, Optional, Callable
import logging

try:
    import numba
    from numba import jit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class PerformanceOptimizer:
    """Optimiseur de performances pour epub2pdf"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self._cache = {}
        self._max_cache_size = 100
        self._performance_stats = {}
        
    def get_system_info(self) -> Dict[str, Any]:
        """Récupère les informations système pour l'optimisation"""
        info = {
            'cpu_count': 0,
            'memory_gb': 0,
            'disk_space_gb': 0,
            'numba_available': NUMBA_AVAILABLE,
            'psutil_available': PSUTIL_AVAILABLE
        }
        
        try:
            import multiprocessing
            info['cpu_count'] = multiprocessing.cpu_count()
        except:
            info['cpu_count'] = 4  # Valeur par défaut
        
        if PSUTIL_AVAILABLE:
            try:
                memory = psutil.virtual_memory()
                info['memory_gb'] = memory.total / (1024**3)
                
                disk = psutil.disk_usage('/')
                info['disk_space_gb'] = disk.free / (1024**3)
            except Exception as e:
                self.logger.warning(f"⚠️ Erreur récupération infos système: {e}")
        
        return info
    
    def optimize_worker_count(self, task_type: str = "conversion") -> int:
        """Optimise le nombre de workers selon le système"""
        system_info = self.get_system_info()
        cpu_count = system_info['cpu_count']
        memory_gb = system_info['memory_gb']
        
        # Optimisation selon le type de tâche
        if task_type == "conversion":
            # Pour la conversion d'images, optimiser selon la mémoire
            if memory_gb >= 16:
                workers = min(cpu_count, 8)
            elif memory_gb >= 8:
                workers = min(cpu_count, 6)
            else:
                workers = min(cpu_count, 4)
        elif task_type == "scan":
            # Pour le scan de fichiers, plus de workers
            workers = min(cpu_count * 2, 12)
        else:
            workers = min(cpu_count, 6)
        
        self.logger.info(f"🔧 Workers optimisés: {workers} (CPU: {cpu_count}, RAM: {memory_gb:.1f}GB)")
        return workers
    
    def optimize_memory_usage(self, target_mb: int = 512) -> Dict[str, Any]:
        """Optimise l'utilisation mémoire"""
        if not PSUTIL_AVAILABLE:
            return {'optimized': False, 'reason': 'psutil non disponible'}
        
        try:
            memory = psutil.virtual_memory()
            available_mb = memory.available / (1024**2)
            
            if available_mb < target_mb:
                # Forcer le garbage collection
                import gc
                gc.collect()
                
                # Vérifier à nouveau
                memory = psutil.virtual_memory()
                available_mb = memory.available / (1024**2)
            
            return {
                'optimized': available_mb >= target_mb,
                'available_mb': available_mb,
                'target_mb': target_mb
            }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur optimisation mémoire: {e}")
            return {'optimized': False, 'reason': str(e)}
    
    @staticmethod
    def fast_image_processing(image_data, width, height):
        """Traitement d'image optimisé avec numba"""
        if not NUMBA_AVAILABLE:
            return image_data
        
        # Algorithme de traitement optimisé
        result = image_data.copy()
        
        for i in prange(width):
            for j in prange(height):
                # Exemple d'optimisation: ajustement de contraste
                pixel = image_data[i, j]
                result[i, j] = min(255, max(0, pixel * 1.1))
        
        return result
    
    async def async_file_processing(self, file_paths: List[str], 
                                  processor: Callable, 
                                  max_workers: int = 4) -> List[Any]:
        """Traitement asynchrone de fichiers"""
        semaphore = asyncio.Semaphore(max_workers)
        
        async def process_file(file_path):
            async with semaphore:
                try:
                    return await asyncio.to_thread(processor, file_path)
                except Exception as e:
                    self.logger.error(f"❌ Erreur traitement {file_path}: {e}")
                    return None
        
        tasks = [process_file(path) for path in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrer les résultats None
        return [r for r in results if r is not None]
    
    def parallel_batch_processing(self, items: List[Any], 
                                processor: Callable,
                                batch_size: int = 10,
                                max_workers: int = 4) -> List[Any]:
        """Traitement parallèle par lots"""
        results = []
        
        # Diviser en lots
        batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Traiter chaque lot en parallèle
            future_to_batch = {
                executor.submit(self._process_batch, batch, processor): batch 
                for batch in batches
            }
            
            for future in future_to_batch:
                try:
                    batch_results = future.result()
                    results.extend(batch_results)
                except Exception as e:
                    self.logger.error(f"❌ Erreur traitement lot: {e}")
        
        return results
    
    def _process_batch(self, batch: List[Any], processor: Callable) -> List[Any]:
        """Traite un lot d'éléments"""
        results = []
        for item in batch:
            try:
                result = processor(item)
                if result is not None:
                    results.append(result)
            except Exception as e:
                self.logger.warning(f"⚠️ Erreur traitement item: {e}")
        return results
    
    def cache_optimization(self, key: str, data: Any, ttl_seconds: int = 300):
        """Optimisation du cache avec TTL"""
        if len(self._cache) >= self._max_cache_size:
            # Supprimer les éléments expirés
            current_time = time.time()
            expired_keys = [
                k for k, v in self._cache.items() 
                if current_time - v['timestamp'] > v['ttl']
            ]
            for k in expired_keys:
                del self._cache[k]
            
            # Si toujours plein, supprimer le plus ancien
            if len(self._cache) >= self._max_cache_size:
                oldest_key = min(self._cache.keys(), 
                               key=lambda k: self._cache[k]['timestamp'])
                del self._cache[oldest_key]
        
        self._cache[key] = {
            'data': data,
            'timestamp': time.time(),
            'ttl': ttl_seconds
        }
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """Récupère des données du cache"""
        if key not in self._cache:
            return None
        
        cache_entry = self._cache[key]
        if time.time() - cache_entry['timestamp'] > cache_entry['ttl']:
            del self._cache[key]
            return None
        
        return cache_entry['data']
    
    def start_performance_monitoring(self, task_name: str):
        """Démarre le monitoring de performance"""
        self._performance_stats[task_name] = {
            'start_time': time.time(),
            'memory_start': self._get_memory_usage(),
            'cpu_start': self._get_cpu_usage()
        }
    
    def end_performance_monitoring(self, task_name: str) -> Dict[str, Any]:
        """Termine le monitoring et retourne les statistiques"""
        if task_name not in self._performance_stats:
            return {}
        
        start_stats = self._performance_stats[task_name]
        end_time = time.time()
        
        stats = {
            'duration_seconds': end_time - start_stats['start_time'],
            'memory_peak': self._get_memory_usage(),
            'cpu_peak': self._get_cpu_usage()
        }
        
        # Calculer les différences
        if PSUTIL_AVAILABLE:
            memory_diff = stats['memory_peak'] - start_stats['memory_start']
            stats['memory_increase_mb'] = memory_diff
            stats['cpu_increase_percent'] = stats['cpu_peak'] - start_stats['cpu_start']
        
        # Nettoyer
        del self._performance_stats[task_name]
        
        return stats
    
    def _get_memory_usage(self) -> float:
        """Récupère l'utilisation mémoire en MB"""
        if not PSUTIL_AVAILABLE:
            return 0.0
        
        try:
            process = psutil.Process()
            return process.memory_info().rss / (1024**2)
        except:
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Récupère l'utilisation CPU en pourcentage"""
        if not PSUTIL_AVAILABLE:
            return 0.0
        
        try:
            return psutil.cpu_percent(interval=0.1)
        except:
            return 0.0
    
    def optimize_for_large_files(self, file_size_mb: float) -> Dict[str, Any]:
        """Optimise les paramètres pour les gros fichiers"""
        optimizations = {
            'batch_size': 5,
            'max_workers': 2,
            'memory_limit_mb': 1024,
            'use_numba': False,
            'use_async': False
        }
        
        if file_size_mb > 500:
            # Très gros fichiers
            optimizations.update({
                'batch_size': 2,
                'max_workers': 1,
                'memory_limit_mb': 2048,
                'use_numba': True,
                'use_async': False
            })
        elif file_size_mb > 100:
            # Gros fichiers
            optimizations.update({
                'batch_size': 3,
                'max_workers': 2,
                'memory_limit_mb': 1024,
                'use_numba': True,
                'use_async': True
            })
        elif file_size_mb > 50:
            # Fichiers moyens
            optimizations.update({
                'batch_size': 5,
                'max_workers': 3,
                'memory_limit_mb': 512,
                'use_numba': True,
                'use_async': True
            })
        else:
            # Petits fichiers
            optimizations.update({
                'batch_size': 10,
                'max_workers': 4,
                'memory_limit_mb': 256,
                'use_numba': False,
                'use_async': True
            })
        
        return optimizations
    
    def clear_cache(self):
        """Nettoie le cache"""
        self._cache.clear()
        self.logger.info("🧹 Cache d'optimisation nettoyé")


# Instance globale pour utilisation dans l'application
performance_optimizer = PerformanceOptimizer()
