"""
Port - Browser Worker Pool Interface

Define o contrato para um pool de workers que processam URLs em paralelo
usando múltiplas páginas do Playwright.
"""

from abc import ABC, abstractmethod
from typing import List, Callable, Any, Optional
from dataclasses import dataclass


@dataclass
class WorkerResult:
    """Resultado do processamento de uma URL por um worker"""
    url: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    worker_id: int = -1
    duration_seconds: float = 0.0


class IBrowserWorkerPool(ABC):
    """
    Interface para pool de workers que processa URLs em paralelo.
    
    Permite scraping concorrente com múltiplas páginas Playwright,
    gerenciando lifecycle, distribuição de URLs e coleta de resultados.
    """
    
    @abstractmethod
    async def initialize(self, num_workers: int) -> None:
        """
        Inicializa o pool com número especificado de workers.
        
        Args:
            num_workers: Número de páginas Playwright paralelas
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Fecha todas as páginas e contexto do Playwright"""
        pass
    
    @abstractmethod
    async def process_urls(
        self,
        urls: List[str],
        worker_func: Callable[[str, int], Any],
        show_progress: bool = True
    ) -> List[WorkerResult]:
        """
        Processa lista de URLs em paralelo.
        
        Args:
            urls: Lista de URLs para processar
            worker_func: Função async que processa cada URL (recebe url, worker_id)
            show_progress: Se deve mostrar barra de progresso
            
        Returns:
            Lista de WorkerResult com resultados de cada URL
        """
        pass
    
    @abstractmethod
    async def process_urls_with_retry(
        self,
        urls: List[str],
        worker_func: Callable[[str, int], Any],
        max_retries: int = 3,
        show_progress: bool = True
    ) -> List[WorkerResult]:
        """
        Processa URLs com retry automático em caso de falha.
        
        Args:
            urls: Lista de URLs para processar
            worker_func: Função async que processa cada URL
            max_retries: Número máximo de tentativas por URL
            show_progress: Se deve mostrar barra de progresso
            
        Returns:
            Lista de WorkerResult
        """
        pass
    
    @abstractmethod
    def get_num_workers(self) -> int:
        """Retorna número de workers ativos"""
        pass
    
    @abstractmethod
    def get_queue_size(self) -> int:
        """Retorna número de URLs ainda na fila"""
        pass
