import sys
import os

# Agregamos la carpeta src al path para que Python encuentre el módulo core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from core.process import Process, ProcessState

def test_processes():
    # Simularemos un proceso con PID 1, que llega en el tick 0.
    # Sus ráfagas serán: 2 ticks en CPU, 1 tick de I/O, y 1 tick final en CPU.
    p = Process(pid=1, arrival_time=0, bursts=[2, 1, 1], priority=5)
    
    print("--- Estado Inicial ---")
    print(p)
    print(f"Total CPU requerido: {p.total_burst_time}, Total I/O requerido: {p.total_io_burst_time}\n")
    
    # Simulemos que el Scheduler lo pasa a estado RUNNING y ejecuta el Tick 1
    print("--- Tick 1 (CPU) ---")
    p.state = ProcessState.RUNNING
    p.tick_cpu()
    print(p)
    
    # Tick 2 - El proceso terminará su primera ráfaga de CPU en este tick
    print("--- Tick 2 (CPU) ---")
    termino_rafaga = p.tick_cpu()
    print(p)
    print(f"¿Terminó su ráfaga actual? {'Sí' if termino_rafaga else 'No'}\n")
    
    # Como terminó su ráfaga de CPU y ahora le toca I/O, el Scheduler lo pondría en BLOCKED
    print("--- Tick 3 (I/O) ---")
    p.state = ProcessState.BLOCKED
    termino_rafaga = p.tick_io()
    print(p)
    print(f"¿Terminó su ráfaga actual de I/O? {'Sí' if termino_rafaga else 'No'}\n")
    
    # Digamos que en el Tick 4 el procesador estuvo ocupado con otro proceso y este tuvo que esperar
    print("--- Tick 4 (Espera) ---")
    p.state = ProcessState.READY
    p.tick_wait()
    print(p)
    print(f"Tiempo de espera acumulado: {p.wait_time}\n")
    
    # Tick 5 - Vuelve al CPU para su última ráfaga
    print("--- Tick 5 (CPU Final) ---")
    p.state = ProcessState.RUNNING
    termino_rafaga = p.tick_cpu()
    print(p)
    print(f"¿Terminó por completo el proceso? {'Sí' if p.is_finished() else 'No'}\n")
    
    # Le indicamos al proceso que terminó en el tick actual (Tick 5)
    p.finish(current_tick=5)
    print("--- Resultados Finales ---")
    print(f"Tiempo de retorno (Turnaround Time): {p.turnaround_time} ticks")
    print(f"Tiempo total en CPU: {p.cpu_time} ticks")
    print(f"Tiempo total en I/O: {p.io_time} ticks")

if __name__ == "__main__":
    test_processes()
