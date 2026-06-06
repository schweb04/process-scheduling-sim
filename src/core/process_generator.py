import random
from typing import List, Tuple
from core.process import Process

class ProcessGenerator:
    """
    Clase encargada de generar procesos aleatoriamente basados en rangos configurables.
    """
    
    def __init__(self, 
                 num_processes: int = 5,
                 arrival_time_range: Tuple[int, int] = (0, 10),
                 cpu_burst_range: Tuple[int, int] = (2, 10),
                 io_burst_range: Tuple[int, int] = (1, 5),
                 priority_levels: Tuple[int, int] = (1, 5)):
        """
        Inicializa los parámetros del generador.
        """
        self.num_processes = num_processes
        self.arrival_time_range = arrival_time_range
        self.cpu_burst_range = cpu_burst_range
        self.io_burst_range = io_burst_range
        self.priority_levels = priority_levels

    def _generate_bursts(self) -> List[int]:
        """
        Genera la secuencia de ráfagas [CPU, IO, CPU] dividiendo el total
        del tiempo de CPU de forma equitativa antes y después del IO.
        """
        total_cpu = random.randint(*self.cpu_burst_range)
        total_io = random.randint(*self.io_burst_range)
        
        # Si no hay I/O, es solo una gran ráfaga de CPU
        if total_io == 0:
            return [total_cpu]
            
        # Dividir CPU
        half_cpu = total_cpu // 2
        remainder = total_cpu % 2
        
        # Si es impar, decidimos aleatoriamente dónde poner el tick extra
        extra_first = random.choice([True, False])
        
        cpu_1 = half_cpu + (1 if extra_first and remainder else 0)
        cpu_2 = half_cpu + (1 if not extra_first and remainder else 0)
        
        bursts = []
        if cpu_1 > 0:
            bursts.append(cpu_1)
        else:
            bursts.append(0) # Mantenemos la estructura para respetar que índice impar es I/O
            
        bursts.append(total_io)
        
        if cpu_2 > 0:
            bursts.append(cpu_2)
            
        return bursts

    def generate(self) -> List[Process]:
        """
        Genera y retorna la lista de procesos.
        """
        processes = []
        for i in range(1, self.num_processes + 1):
            arrival_time = random.randint(*self.arrival_time_range)
            priority = random.randint(*self.priority_levels)
            bursts = self._generate_bursts()
            
            p = Process(pid=i, arrival_time=arrival_time, bursts=bursts, priority=priority)
            processes.append(p)
            
        return processes
