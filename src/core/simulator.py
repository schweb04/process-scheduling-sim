from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from core.process import Process, ProcessState

class Scheduler(ABC):
    """
    Clase base abstracta para los algoritmos de planificación de procesos.
    
    Administra las colas de estado (NEW → READY → RUNNING → BLOCKED → FINISHED),
    el reloj del sistema y la recolección de estadísticas.
    
    Las subclases solo necesitan implementar el método `select_next_process()`
    para definir la política de selección del algoritmo.
    """
    
    def __init__(self, processes: List[Process], quantum: int = 0):
        """
        Inicializa el Scheduler con la lista de procesos a simular.
        
        Args:
            processes: Lista de procesos generados (serán ordenados por arrival_time).
            quantum: Quantum de tiempo para algoritmos expulsivos (ej. Round Robin).
                     Si es 0, se ignora (algoritmos no expulsivos).
        """
        # Ordenar por tiempo de llegada para procesarlos cronológicamente
        self.processes: List[Process] = sorted(processes, key=lambda p: p.arrival_time)
        self.quantum: int = quantum
        
        # Colas de estado
        self.ready_queue: List[Process] = []
        self.blocked_queue: List[Process] = []
        self.finished_queue: List[Process] = []
        
        # CPU
        self.running_process: Optional[Process] = None
        self.quantum_remaining: int = quantum  # Contador del quantum actual
        
        # Reloj del sistema
        self.current_tick: int = 0
        
        # Estadísticas
        self.cpu_busy_ticks: int = 0
        self.arrivals_per_tick: List[int] = []  # Cuántos procesos llegaron en cada tick
        
        # Estado de la simulación
        self.is_complete: bool = False
        
        # Historial de eventos por tick (útil para la visualización en Streamlit)
        self.history: List[Dict[str, Any]] = []
    
    # ─────────────────────────────────────────────
    #  MÉTODO ABSTRACTO (a implementar por cada algoritmo)
    # ─────────────────────────────────────────────
    
    @abstractmethod
    def select_next_process(self) -> Optional[Process]:
        """
        Selecciona el siguiente proceso de la ready_queue para asignarle la CPU.
        
        Debe retornar el proceso seleccionado y ELIMINARLO de la ready_queue.
        Retorna None si la cola está vacía.
        
        Cada algoritmo implementa su propia lógica:
          - FCFS: el primero de la cola (índice 0).
          - SJF: el de menor remaining_burst_time.
          - Prioridad: el de mayor prioridad (menor número).
          - Aleatorio: uno al azar.
        """
        pass
    
    # ─────────────────────────────────────────────
    #  MÉTODO CENTRAL: tick()
    # ─────────────────────────────────────────────
    
    def tick(self):
        """
        Ejecuta un paso completo de la simulación.
        
        Orden de operaciones:
          1. Admitir procesos nuevos que llegan en este tick.
          2. Avanzar E/S de los procesos bloqueados.
          3. Avanzar CPU del proceso en ejecución.
          4. Asignar la CPU si está libre.
          5. Acumular tiempo de espera de los procesos en la cola de listos.
          6. Registrar el estado del tick actual en el historial.
          7. Verificar si la simulación ha terminado.
          8. Avanzar el reloj.
        """
        if self.is_complete:
            return
        
        # 1. Admitir procesos nuevos
        self._admit_new_processes()
        
        # 2. Procesar cola de bloqueados (E/S)
        self._process_blocked_queue()
        
        # 3. Procesar CPU
        self._process_running()
        
        # 4. Asignar CPU si está libre
        self._assign_cpu()
        
        # 5. Acumular espera en la cola de listos
        self._process_ready_queue()
        
        # 6. Registrar estado del tick
        self._record_tick()
        
        # 7. Verificar si la simulación terminó
        self._check_completion()
        
        # 8. Avanzar el reloj
        self.current_tick += 1
    
    def run_all(self):
        """Ejecuta la simulación completa hasta que todos los procesos terminen."""
        while not self.is_complete:
            self.tick()
    
    # ─────────────────────────────────────────────
    #  MÉTODOS AUXILIARES (privados)
    # ─────────────────────────────────────────────
    
    def _admit_new_processes(self):
        """
        Revisa qué procesos tienen arrival_time == current_tick
        y los mueve a la cola de listos (READY).
        """
        arrivals = 0
        for process in self.processes:
            if process.state == ProcessState.NEW and process.arrival_time == self.current_tick:
                process.state = ProcessState.READY
                self.ready_queue.append(process)
                arrivals += 1
        self.arrivals_per_tick.append(arrivals)
    
    def _process_blocked_queue(self):
        """
        Avanza 1 tick de E/S en cada proceso bloqueado.
        Si un proceso termina su ráfaga de E/S, lo mueve a la cola de listos.
        """
        still_blocked = []
        for process in self.blocked_queue:
            io_finished = process.tick_io()
            if io_finished:
                # La ráfaga de E/S terminó
                if process.is_finished():
                    process.finish(self.current_tick)
                    self.finished_queue.append(process)
                else:
                    process.state = ProcessState.READY
                    self.ready_queue.append(process)
            else:
                still_blocked.append(process)
        self.blocked_queue = still_blocked
    
    def _process_running(self):
        """
        Si hay un proceso en la CPU, avanza 1 tick de CPU.
        Si termina su ráfaga de CPU, lo mueve a bloqueados o terminados.
        También maneja la expiración del quantum (para algoritmos expulsivos).
        """
        if self.running_process is None:
            return
        
        cpu_burst_finished = self.running_process.tick_cpu()
        self.cpu_busy_ticks += 1
        
        if cpu_burst_finished:
            # La ráfaga de CPU terminó
            if self.running_process.is_finished():
                self.running_process.finish(self.current_tick)
                self.finished_queue.append(self.running_process)
            else:
                # Le queda E/S por hacer
                self.running_process.state = ProcessState.BLOCKED
                self.blocked_queue.append(self.running_process)
            self.running_process = None
            self.quantum_remaining = self.quantum
        elif self.quantum > 0:
            # Verificar expiración del quantum (Round Robin, etc.)
            self.quantum_remaining -= 1
            if self.quantum_remaining <= 0:
                # Expulsión: devolver a la cola de listos
                self.running_process.state = ProcessState.READY
                self.ready_queue.append(self.running_process)
                self.running_process = None
                self.quantum_remaining = self.quantum
    
    def _assign_cpu(self):
        """
        Si la CPU está libre y hay procesos listos, selecciona uno
        usando el método abstracto `select_next_process()`.
        """
        if self.running_process is None and self.ready_queue:
            selected = self.select_next_process()
            if selected is not None:
                selected.state = ProcessState.RUNNING
                self.running_process = selected
                self.quantum_remaining = self.quantum
    
    def _process_ready_queue(self):
        """Acumula 1 tick de espera en cada proceso que sigue en la cola de listos."""
        for process in self.ready_queue:
            process.tick_wait()
    
    def _record_tick(self):
        """
        Registra una instantánea del estado actual del sistema.
        Útil para la visualización paso a paso en la interfaz gráfica.
        """
        snapshot = {
            "tick": self.current_tick,
            "running": self.running_process.pid if self.running_process else None,
            "ready": [p.pid for p in self.ready_queue],
            "blocked": [p.pid for p in self.blocked_queue],
            "finished": [p.pid for p in self.finished_queue],
            "arrivals": self.arrivals_per_tick[-1] if self.arrivals_per_tick else 0,
        }
        self.history.append(snapshot)
    
    def _check_completion(self):
        """Verifica si todos los procesos han terminado."""
        if len(self.finished_queue) == len(self.processes):
            self.is_complete = True
    
    # ─────────────────────────────────────────────
    #  ESTADÍSTICAS
    # ─────────────────────────────────────────────
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Calcula y retorna las métricas de rendimiento de la simulación.
        
        Métricas (según specs.md):
          - % de uso del procesador
          - Tiempo promedio de espera
          - Tiempo promedio de bloqueo (E/S)
          - Tiempo promedio de ejecución (turnaround)
          - Total de procesos completados
          - Arribo de nuevos procesos por paso
          - Tiempo total de la simulación
        """
        total_ticks = self.current_tick if self.current_tick > 0 else 1
        completed = self.finished_queue
        num_completed = len(completed)
        
        if num_completed > 0:
            avg_wait = sum(p.wait_time for p in completed) / num_completed
            avg_io = sum(p.io_time for p in completed) / num_completed
            avg_turnaround = sum(p.turnaround_time for p in completed) / num_completed
        else:
            avg_wait = 0
            avg_io = 0
            avg_turnaround = 0
        
        cpu_usage = (self.cpu_busy_ticks / total_ticks) * 100
        
        avg_arrivals = (
            sum(self.arrivals_per_tick) / len(self.arrivals_per_tick)
            if self.arrivals_per_tick else 0
        )
        
        return {
            "cpu_usage_percent": round(cpu_usage, 2),
            "avg_wait_time": round(avg_wait, 2),
            "avg_io_time": round(avg_io, 2),
            "avg_turnaround_time": round(avg_turnaround, 2),
            "total_completed": num_completed,
            "avg_arrivals_per_tick": round(avg_arrivals, 2),
            "total_ticks": total_ticks,
        }
