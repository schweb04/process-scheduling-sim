from typing import Optional, List
from core.process import Process, ProcessState
from core.simulator import Scheduler


class RoundRobinScheduler(Scheduler):
    """
    Turno Rotativo (Round Robin).
    
    Selecciona procesos en orden FIFO (como FCFS), pero cada proceso
    solo puede ejecutar durante un máximo de `quantum` ticks consecutivos.
    Si no termina su ráfaga en ese tiempo, es expulsado y devuelto al
    final de la cola de listos.
    
    La expulsión por quantum ya está implementada en el Scheduler base
    (en _process_running()), por lo que esta clase solo necesita definir
    select_next_process() y asegurar que se pase un quantum > 0.
    """
    
    def select_next_process(self) -> Optional[Process]:
        if self.ready_queue:
            return self.ready_queue.pop(0)
        return None


class SRTFScheduler(Scheduler):
    """
    Primero el Menor Tiempo Restante (Shortest Remaining Time First).
    
    Versión expulsiva de SJF. Selecciona el proceso con el menor
    `remaining_current_burst`. Si llega un proceso con menos tiempo
    restante que el que está en CPU, lo interrumpe.
    
    Usa el mismo criterio que SJF (remaining_current_burst), pero
    al ser expulsivo, evalúa en cada tick si debe interrumpir.
    Desempate por arrival_time.
    """
    
    def select_next_process(self) -> Optional[Process]:
        if not self.ready_queue:
            return None
        
        self.ready_queue.sort(
            key=lambda p: (p.remaining_current_burst, p.arrival_time)
        )
        return self.ready_queue.pop(0)
    
    def _check_preemption(self):
        """
        Compara el tiempo restante del proceso en CPU contra el menor
        de la cola de listos. Si hay uno con menos tiempo, expulsa.
        """
        if self.running_process is None or not self.ready_queue:
            return
        
        # Encontrar el menor remaining_current_burst en la cola de listos
        shortest_ready = min(
            self.ready_queue,
            key=lambda p: (p.remaining_current_burst, p.arrival_time)
        )
        
        running_metric = (self.running_process.remaining_current_burst, self.running_process.arrival_time)
        ready_metric = (shortest_ready.remaining_current_burst, shortest_ready.arrival_time)
        
        # Expulsar si el de la cola tiene menor tiempo restante, o igual tiempo pero llegó antes
        if ready_metric < running_metric:
            self.running_process.state = ProcessState.READY
            self.ready_queue.append(self.running_process)
            self.running_process = None


class PriorityPScheduler(Scheduler):
    """
    Planificación basada en Prioridades (Expulsiva).
    
    Versión expulsiva de PriorityNP. Selecciona el proceso con el menor
    número de prioridad (menor = más urgente). Si llega un proceso con
    mayor prioridad que el que está en CPU, lo interrumpe.
    
    Desempate por arrival_time.
    """
    
    def select_next_process(self) -> Optional[Process]:
        if not self.ready_queue:
            return None
        
        self.ready_queue.sort(
            key=lambda p: (p.priority, p.arrival_time)
        )
        return self.ready_queue.pop(0)
    
    def _check_preemption(self):
        """
        Compara la prioridad del proceso en CPU contra la mayor prioridad
        (menor número) de la cola de listos. Si hay uno más urgente, expulsa.
        """
        if self.running_process is None or not self.ready_queue:
            return
        
        # Encontrar la mayor prioridad (menor número) en la cola de listos
        highest_priority_ready = min(
            self.ready_queue,
            key=lambda p: (p.priority, p.arrival_time)
        )
        
        running_metric = (self.running_process.priority, self.running_process.arrival_time)
        ready_metric = (highest_priority_ready.priority, highest_priority_ready.arrival_time)
        
        # Expulsar si el de la cola tiene mayor prioridad, o igual prioridad pero llegó antes
        if ready_metric < running_metric:
            self.running_process.state = ProcessState.READY
            self.ready_queue.append(self.running_process)
            self.running_process = None
