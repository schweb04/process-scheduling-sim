# Documentación Técnica y de Diseño

Este documento describe la arquitectura, el modelado y las decisiones técnicas tomadas durante el desarrollo del **Simulador de Planificación de Procesos**. Su propósito es servir como el informe detallado del proyecto, explicando *cómo* se construyó el simulador y *por qué* se tomaron ciertas decisiones de diseño.

---

## 1. Arquitectura General y Tecnologías

El proyecto fue construido en **Python** debido a su sintaxis limpia y su capacidad para modelar simulaciones lógicas de forma orientada a objetos de manera muy legible.

Para asegurar un código escalable y fácil de mantener, se adoptó una arquitectura que **desacopla completamente la lógica de negocio de la interfaz gráfica**:

*   **`src/core/` (Lógica Pura)**: Contiene todas las reglas matemáticas y estructurales de la simulación. El `Scheduler`, los `Process` y los algoritmos no saben nada de cómo se van a mostrar en pantalla.
*   **`src/app.py` (Interfaz Gráfica)**: Actúa como el controlador visual utilizando la biblioteca **Streamlit**. Consume los objetos de `core/` y los renderiza de forma interactiva.

**¿Por qué Streamlit?**
Streamlit fue elegido por su capacidad de construir dashboards web modernos y reactivos exclusivamente con Python, lo cual es ideal para un simulador que requiere paneles de control dinámicos, visualización de estados en tiempo real y tablas de métricas.

---

## 2. Modelado de Procesos (Modelo CPU-E/S-CPU)

En lugar de tratar a los procesos como bloques monolíticos de tiempo, el simulador utiliza un modelo realista basado en ráfagas (bursts) alternadas. 

Cada proceso se representa internamente con una lista de enteros `bursts = [CPU, E/S, CPU, ...]`.
*   *Justificación*: En un sistema operativo real, un proceso rara vez usa el procesador ininterrumpidamente. Constantemente solicita acceso a memoria secundaria o dispositivos, entrando en estado bloqueado. Modelar esto permite evaluar verdaderamente la eficiencia de la CPU frente a cuellos de botella de Entrada/Salida, y pone a prueba cómo los algoritmos reaccionan cuando un proceso se bloquea y libera la CPU voluntariamente.

**Estados del Proceso**:
El ciclo de vida se controla mediante la enumeración `ProcessState`: `NEW → READY → RUNNING → BLOCKED → FINISHED`.

---

## 3. El Motor del Simulador: La clase `Scheduler`

El núcleo del proyecto radica en la clase abstracta `Scheduler` (`src/core/simulator.py`). Esta clase base maneja toda la fontanería de la simulación:
1.  **Las Colas**: Administra las listas físicas de procesos (`ready_queue`, `blocked_queue`, `finished_queue`).
2.  **El Reloj Global (`current_tick`)**: Controla el tiempo del sistema.
3.  **El Recolector de Estadísticas**: Suma los tiempos de espera, uso de CPU y turnaround.

### El Ciclo Estricto del Tick
Para garantizar que la simulación sea determinista (siempre produce el mismo resultado ante los mismos procesos), el método `tick()` ejecuta las operaciones en un orden estricto inalterable:
1.  **Admitir**: Mover procesos con `arrival_time == current_tick` a Listos.
2.  **E/S**: Avanzar la ráfaga de los procesos Bloqueados. Si terminan, regresan a Listos.
3.  **CPU**: Avanzar la ráfaga del proceso en Ejecución.
4.  **Evaluar Expulsión**: (Paso hook para algoritmos expulsivos).
5.  **Asignar**: Si la CPU quedó o está libre, elegir el siguiente proceso.
6.  **Esperar**: Incrementar el contador de espera a los procesos que se quedaron en Listos.

*Justificación*: Este patrón (Template Method) permite que los distintos algoritmos de planificación solo tengan que heredar de `Scheduler` e implementar un solo método: `select_next_process()`.

---

## 4. Algoritmos de Planificación Implementados

El simulador implementa 7 políticas de planificación, divididas en no expulsivas y expulsivas.

### Algoritmos No Expulsivos
*(Una vez que toman la CPU, no la sueltan hasta que terminan su ráfaga actual o solicitan E/S).*

1.  **FCFS (First-Come, First-Served)**: Implementación FIFO basada en sacar siempre el índice `0` de la `ready_queue`.
2.  **SJF (Shortest Job First)**: Ordena la cola de listos buscando el menor `remaining_current_burst`.
    *   *Nota de diseño*: Evalúa la longitud de la *ráfaga actual*, no el tiempo total restante del proceso, emulando el comportamiento estándar de SJF predictivo.
3.  **Random (Aleatorio)**: Selecciona un índice al azar de la cola de listos usando la librería estándar `random`.
4.  **Priority NP (Prioridad)**: Ordena la cola buscando el número de prioridad más bajo.
    *   *Convención*: El número menor representa la prioridad más alta (ej. 1 es más importante que 5), alineándose con estándares como Linux.

### Algoritmos Expulsivos
*(Pueden interrumpir al proceso en ejecución si las condiciones lo ameritan).*

Se implementó un método hook `_check_preemption()` en el ciclo base que es sobrescrito por estos algoritmos:

5.  **Round Robin**: Cada proceso recibe un límite de tiempo (quantum). La lógica de expiración de quantum se integró directamente en el Scheduler base.
6.  **SRTF (Shortest Remaining Time First)**: Compara el tiempo restante del proceso en CPU contra el de la cola de listos. Si llega uno más corto (o igual de corto, pero que llegó antes), expulsa al actual.
7.  **Priority Preemptive (Prioridad Expulsiva)**: Similar a SRTF, pero expulsa si llega un proceso con mejor prioridad (o misma prioridad, pero menor `arrival_time`).

### Criterio General de Desempate
En todos los algoritmos, si el atributo de selección principal empata (ej. dos procesos con prioridad 2, o dos procesos con 3 ticks restantes), se utiliza el **`arrival_time` como segundo criterio de ordenamiento**. El proceso que entró al sistema primero tiene la preferencia, garantizando justicia y evitando inanición arbitraria.

---

## 5. Diseño de la Experiencia de Usuario (Streamlit)

La interfaz gráfica se diseñó bajo una filosofía de **flujo secuencial de 3 pasos**, utilizando el panel lateral para mantener limpio el panel principal:

1.  **Generación de Procesos**: El usuario define los rangos matemáticos (Llegada, CPU, E/S, Prioridad) de forma parametrizada. 
2.  **Selección de Algoritmo**: Un catálogo claro explica el funcionamiento y la naturaleza (expulsiva/no expulsiva) de cada algoritmo.
3.  **Controles de Simulación**: Múltiples formas de observar el comportamiento:
    *   **Paso a paso**: Útil con fines educativos para auditar decisiones en ticks conflictivos.
    *   **Automático**: Para visualizar dinámicamente cómo las colas se vacían y llenan a una velocidad controlable por el usuario.
    *   **Ejecutar todo**: Para simular directamente y ver las estadísticas finales de rendimiento (turnaround, espera, etc.).

**Manejo de Estado (`st.session_state`)**
Para lograr que la interfaz permitiera pausar, dar pasos, y reiniciar la simulación usando los mismos procesos exactos generados, se utilizó copias profundas (`copy.deepcopy()`) de los objetos originales en la memoria de la sesión de Streamlit. Esto evita que las mutaciones inherentes a la simulación corrompan los datos para una segunda pasada.

---

## 6. Pruebas y Aseguramiento de Calidad

Para garantizar que la lógica central fuera robusta antes de acoplarla a la interfaz gráfica, se desarrollaron scripts de pruebas (`tests/test_non_preemptive.py` y `tests/test_preemptive.py`).
Estos tests inyectan procesos duros (hardcoded) diseñados específicamente para forzar casos límite, como:
*   Empates de prioridades simultáneas.
*   Llegadas de procesos cortos interrumpiendo procesos largos justo en el medio de una ráfaga de CPU.

El uso de un reloj centralizado y colas estrictas permitió que estas pruebas de consola predijeran el mismo historial tick a tick que finalmente se muestra en la web.
