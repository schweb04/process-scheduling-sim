import random
from typing import Optional, List
from core.process import Process
from core.simulator import Scheduler


class FCFSScheduler(Scheduler):
    """
    Primero en llegar, primero en ejecutar (First Come, First Served).
    
    Selecciona el proceso que lleva más tiempo en la cola de listos,
    es decir, el primero que fue insertado (FIFO).
    """
    
    def select_next_process(self) -> Optional[Process]:
        if self.ready_queue:
            return self.ready_queue.pop(0)
        return None


class SJFScheduler(Scheduler):
    """
    Primero el trabajo más corto (Shortest Job First).
    
    Selecciona el proceso cuya ráfaga de CPU actual (remaining_current_burst)
    sea la más corta. En caso de empate, se desempata por orden de llegada
    (arrival_time).
    
    Nota: Se evalúa la ráfaga de CPU actual, no el tiempo total restante
    del proceso. Evaluar el tiempo total restante correspondería a SRTF
    (que además es expulsivo).
    """
    
    def select_next_process(self) -> Optional[Process]:
        if not self.ready_queue:
            return None
        
        # Ordenar por ráfaga actual más corta, desempate por llegada
        self.ready_queue.sort(
            key=lambda p: (p.remaining_current_burst, p.arrival_time)
        )
        return self.ready_queue.pop(0)


class RandomScheduler(Scheduler):
    """
    Selección aleatoria.
    
    Selecciona un proceso al azar de la cola de listos.
    """
    
    def select_next_process(self) -> Optional[Process]:
        if not self.ready_queue:
            return None
        
        index = random.randint(0, len(self.ready_queue) - 1)
        return self.ready_queue.pop(index)


class PriorityNPScheduler(Scheduler):
    """
    Planificación basada en prioridades (No Expulsiva).
    
    Selecciona el proceso con el menor número de prioridad
    (menor número = mayor prioridad, convención estándar de SO).
    En caso de empate, se desempata por orden de llegada (arrival_time).
    """
    
    def select_next_process(self) -> Optional[Process]:
        if not self.ready_queue:
            return None
        
        # Ordenar por prioridad (menor = más urgente), desempate por llegada
        self.ready_queue.sort(
            key=lambda p: (p.priority, p.arrival_time)
        )
        return self.ready_queue.pop(0)
