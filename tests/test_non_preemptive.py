import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from core.process import Process
from core.algorithms.non_preemptive import (
    FCFSScheduler,
    SJFScheduler,
    RandomScheduler,
    PriorityNPScheduler,
)

def create_test_processes():
    """
    Crea 3 procesos con valores controlados para comparar algoritmos.
    
      P1: llega tick 0, bursts=[3, 1, 1], prioridad 3
      P2: llega tick 0, bursts=[1, 1, 2], prioridad 1 (más urgente)
      P3: llega tick 1, bursts=[2, 1, 1], prioridad 2
    """
    return [
        Process(pid=1, arrival_time=0, bursts=[3, 1, 1], priority=3),
        Process(pid=2, arrival_time=0, bursts=[1, 1, 2], priority=1),
        Process(pid=3, arrival_time=1, bursts=[2, 1, 1], priority=2),
    ]

def run_algorithm(name, scheduler_class):
    """Ejecuta un algoritmo y muestra el historial tick a tick más estadísticas."""
    processes = create_test_processes()
    scheduler = scheduler_class(processes=processes)
    
    print(f"\n{'='*55}")
    print(f"  {name}")
    print(f"{'='*55}")
    print(f"  P1: llegada=0, bursts=[3,1,1], prioridad=3")
    print(f"  P2: llegada=0, bursts=[1,1,2], prioridad=1")
    print(f"  P3: llegada=1, bursts=[2,1,1], prioridad=2")
    print(f"{'-'*55}")
    print(f"  {'Tick':<6} {'CPU':<8} {'Ready':<15} {'Blocked':<12} {'Finished'}")
    print(f"  {'-'*4:<6} {'-'*5:<8} {'-'*10:<15} {'-'*8:<12} {'-'*8}")
    
    scheduler.run_all()
    
    for snap in scheduler.history:
        cpu = f"P{snap['running']}" if snap['running'] else "idle"
        ready = [f"P{pid}" for pid in snap['ready']]
        blocked = [f"P{pid}" for pid in snap['blocked']]
        finished = [f"P{pid}" for pid in snap['finished']]
        
        print(f"  {snap['tick']:<6} {cpu:<8} {str(ready):<15} {str(blocked):<12} {finished}")
    
    stats = scheduler.get_statistics()
    print(f"\n  Estadísticas:")
    print(f"    % Uso CPU:           {stats['cpu_usage_percent']}%")
    print(f"    Promedio espera:     {stats['avg_wait_time']} ticks")
    print(f"    Promedio bloqueo:    {stats['avg_io_time']} ticks")
    print(f"    Promedio turnaround: {stats['avg_turnaround_time']} ticks")
    print(f"    Total completados:   {stats['total_completed']}")
    print(f"    Tiempo total:        {stats['total_ticks']} ticks")

if __name__ == "__main__":
    print("PRUEBAS DE ALGORITMOS NO EXPULSIVOS")
    print("Escenario: 3 procesos con tiempos y prioridades controlados")
    
    run_algorithm("FCFS (Primero en llegar, primero en ejecutar)", FCFSScheduler)
    run_algorithm("SJF (Primero el trabajo más corto)", SJFScheduler)
    run_algorithm("Random (Selección aleatoria)", RandomScheduler)
    run_algorithm("Priority NP (Prioridad no expulsiva)", PriorityNPScheduler)
    
    print(f"\n{'='*55}")
    print("✅ Todas las pruebas completadas.")
