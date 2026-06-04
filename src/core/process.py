from enum import Enum
from typing import List

class ProcessState(Enum):
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    FINISHED = "FINISHED"

class Process:
    """
    Representa un proceso en el simulador de planificación.
    Utiliza un modelo de ráfagas CPU-E/S-CPU.
    """
    def __init__(self, pid: int, arrival_time: int, bursts: List[int], priority: int = 0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.bursts = bursts  # Ej: [CPU1, IO1, CPU2]
        self.priority = priority
        
        self.state = ProcessState.NEW
        self.current_burst_index = 0
        
        # Tiempo restante de la ráfaga actual (CPU o IO)
        self.remaining_current_burst = self.bursts[self.current_burst_index] if self.bursts else 0
        
        # Métricas
        self.wait_time = 0
        self.cpu_time = 0
        self.io_time = 0
        self.completion_time = -1
        
    @property
    def total_burst_time(self) -> int:
        """Suma de todos los tiempos de CPU."""
        return sum(self.bursts[i] for i in range(0, len(self.bursts), 2))
        
    @property
    def total_io_burst_time(self) -> int:
        """Suma de todos los tiempos de IO."""
        return sum(self.bursts[i] for i in range(1, len(self.bursts), 2))

    @property
    def turnaround_time(self) -> int:
        """Tiempo total desde que llega hasta que finaliza."""
        if self.completion_time == -1:
            return -1
        return self.completion_time - self.arrival_time
        
    def is_finished(self) -> bool:
        """Retorna True si el proceso completó todas sus ráfagas."""
        return self.current_burst_index >= len(self.bursts)
        
    def is_current_burst_io(self) -> bool:
        """Retorna True si la ráfaga actual es de Entrada/Salida (E/S)."""
        # Las ráfagas de E/S están en índices impares (1, 3, 5, ...)
        return self.current_burst_index % 2 != 0

    def _advance_burst(self):
        """Avanza al siguiente burst (si existe) e ignora bursts de tamaño 0."""
        self.current_burst_index += 1
        
        # Saltar bursts vacíos de manera recursiva/iterativa (en caso de haber CPU de 0 o IO de 0 intencional)
        while not self.is_finished() and self.bursts[self.current_burst_index] == 0:
            self.current_burst_index += 1
            
        if not self.is_finished():
            self.remaining_current_burst = self.bursts[self.current_burst_index]

    def tick_cpu(self) -> bool:
        """
        Simula 1 tick de ejecución en CPU.
        Retorna True si la ráfaga actual de CPU ha finalizado con este tick.
        """
        if self.is_finished() or self.is_current_burst_io():
            raise ValueError(f"Proceso {self.pid} no puede ejecutar CPU en este momento.")
            
        self.remaining_current_burst -= 1
        self.cpu_time += 1
        
        if self.remaining_current_burst == 0:
            self._advance_burst()
            return True
            
        return False

    def tick_io(self) -> bool:
        """
        Simula 1 tick de ejecución en E/S (bloqueado).
        Retorna True si la ráfaga actual de E/S ha finalizado con este tick.
        """
        if self.is_finished() or not self.is_current_burst_io():
            raise ValueError(f"Proceso {self.pid} no puede ejecutar E/S en este momento.")
            
        self.remaining_current_burst -= 1
        self.io_time += 1
        
        if self.remaining_current_burst == 0:
            self._advance_burst()
            return True
            
        return False

    def tick_wait(self):
        """Simula 1 tick esperando en la cola de listos (READY)."""
        if self.state == ProcessState.READY:
            self.wait_time += 1

    def finish(self, current_tick: int):
        """Marca el proceso como terminado y calcula sus métricas."""
        self.state = ProcessState.FINISHED
        self.completion_time = current_tick

    def __str__(self):
        return (f"Process(PID={self.pid}, State={self.state.value}, "
                f"BurstIdx={self.current_burst_index}, Rem={self.remaining_current_burst})")
    
    def __repr__(self):
        return self.__str__()
