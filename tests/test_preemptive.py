import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from core.process import Process
from core.algorithms.preemptive import (
    RoundRobinScheduler,
    SRTFScheduler,
    PriorityPScheduler,
)

def create_test_processes():
    """
    Escenario diseñado para evidenciar la expulsión:
    
      P1: llega tick 0, bursts=[5, 1, 1], prioridad 3  (largo, baja prioridad)
      P2: llega tick 2, bursts=[2, 1, 1], prioridad 1  (corto, alta prioridad)
      P3: llega tick 3, bursts=[1, 1, 2], prioridad 2
      
    En tick 2, P2 llega con ráfaga más corta (2 vs 3 restantes de P1)
    y prioridad más alta (1 vs 3). Los algoritmos expulsivos deberían
    interrumpir a P1 en ese momento.
    """
    return [
        Process(pid=1, arrival_time=0, bursts=[5, 1, 1], priority=3),
        Process(pid=2, arrival_time=2, bursts=[2, 1, 1], priority=1),
        Process(pid=3, arrival_time=3, bursts=[1, 1, 2], priority=2),
    ]

def run_algorithm(name, scheduler_class, **kwargs):
    """Ejecuta un algoritmo y muestra el historial tick a tick más estadísticas."""
    processes = create_test_processes()
    scheduler = scheduler_class(processes=processes, **kwargs)
    
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    print(f"  P1: llegada=0, bursts=[5,1,1], prioridad=3 (largo)")
    print(f"  P2: llegada=2, bursts=[2,1,1], prioridad=1 (urgente)")
    print(f"  P3: llegada=3, bursts=[1,1,2], prioridad=2")
    print(f"{'-'*60}")
    print(f"  {'Tick':<6} {'CPU':<10} {'Ready':<18} {'Blocked':<12} {'Finished'}")
    print(f"  {'-'*4:<6} {'-'*7:<10} {'-'*13:<18} {'-'*8:<12} {'-'*8}")
    
    scheduler.run_all()
    
    for snap in scheduler.history:
        cpu = f"P{snap['running']}" if snap['running'] else "idle"
        ready = [f"P{pid}" for pid in snap['ready']]
        blocked = [f"P{pid}" for pid in snap['blocked']]
        finished = [f"P{pid}" for pid in snap['finished']]
        
        print(f"  {snap['tick']:<6} {cpu:<10} {str(ready):<18} {str(blocked):<12} {finished}")
    
    stats = scheduler.get_statistics()
    print(f"\n  Estadísticas:")
    print(f"    % Uso CPU:           {stats['cpu_usage_percent']}%")
    print(f"    Promedio espera:     {stats['avg_wait_time']} ticks")
    print(f"    Promedio bloqueo:    {stats['avg_io_time']} ticks")
    print(f"    Promedio turnaround: {stats['avg_turnaround_time']} ticks")
    print(f"    Total completados:   {stats['total_completed']}")
    print(f"    Tiempo total:        {stats['total_ticks']} ticks")

if __name__ == "__main__":
    print("PRUEBAS DE ALGORITMOS EXPULSIVOS")
    print("Escenario: P1 largo empieza, P2 más corto/urgente llega en tick 2")
    
    run_algorithm("Round Robin (quantum=2)", RoundRobinScheduler, quantum=2)
    run_algorithm("SRTF (Menor Tiempo Restante)", SRTFScheduler)
    run_algorithm("Prioridad Expulsiva", PriorityPScheduler)
    
    print(f"\n{'='*60}")
    print("✅ Todas las pruebas completadas.")
