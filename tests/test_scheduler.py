import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from typing import Optional
from core.process import Process, ProcessState
from core.simulator import Scheduler

# ─────────────────────────────────────────────
#  Subclase concreta mínima para probar el Scheduler (FCFS)
# ─────────────────────────────────────────────

class FCFSTest(Scheduler):
    """FCFS simple: selecciona el primer proceso de la cola de listos."""
    def select_next_process(self) -> Optional[Process]:
        if self.ready_queue:
            return self.ready_queue.pop(0)
        return None

# ─────────────────────────────────────────────
#  Test del ciclo de vida completo
# ─────────────────────────────────────────────

def test_scheduler_lifecycle():
    """
    Escenario controlado con 2 procesos predefinidos:
    
      P1: llega en tick 0, bursts=[2, 1, 1]  (2 CPU, 1 IO, 1 CPU)
      P2: llega en tick 1, bursts=[1, 1, 1]  (1 CPU, 1 IO, 1 CPU)
    
    Se ejecuta manualmente tick a tick para verificar cada transición de estado.
    """
    p1 = Process(pid=1, arrival_time=0, bursts=[2, 1, 1], priority=1)
    p2 = Process(pid=2, arrival_time=1, bursts=[1, 1, 1], priority=2)
    
    scheduler = FCFSTest(processes=[p1, p2])
    
    print("="*50)
    print("TEST: Ciclo de vida del Scheduler (FCFS)")
    print("="*50)
    
    # Ejecutar tick a tick y mostrar el estado
    while not scheduler.is_complete:
        tick = scheduler.current_tick
        scheduler.tick()
        snapshot = scheduler.history[-1]
        
        print(f"\nTick {tick}:")
        print(f"  CPU:        PID {snapshot['running']}")
        print(f"  Ready:      {snapshot['ready']}")
        print(f"  Blocked:    {snapshot['blocked']}")
        print(f"  Finished:   {snapshot['finished']}")
        print(f"  Llegadas:   {snapshot['arrivals']}")
    
    # Mostrar estadísticas
    stats = scheduler.get_statistics()
    print("\n" + "="*50)
    print("ESTADÍSTICAS FINALES")
    print("="*50)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Verificaciones básicas
    assert scheduler.is_complete, "La simulación debería haber terminado"
    assert len(scheduler.finished_queue) == 2, "Ambos procesos deberían estar terminados"
    assert stats["total_completed"] == 2
    assert stats["cpu_usage_percent"] > 0
    
    print("\n✅ Todas las verificaciones pasaron exitosamente.")

if __name__ == "__main__":
    test_scheduler_lifecycle()
