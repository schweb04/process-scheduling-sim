# Decisiones Técnicas y de Diseño

Este documento sirve como registro central de las decisiones arquitectónicas y tecnológicas tomadas durante el desarrollo del Simulador de Planificación de Procesos.

## 1. Lenguaje y Entorno de Desarrollo
*   **Lenguaje**: Python.
    *   *Justificación*: Python es un lenguaje altamente versátil con una sintaxis limpia y expresiva que facilita la implementación de lógica de simulación compleja (como el manejo de múltiples colas de estado y tiempos de los algoritmos).
*   **Entorno**: WSL (Windows Subsystem for Linux).
    *   *Justificación*: Permite un entorno nativo de Linux dentro de Windows, lo cual se alinea muy bien con los conceptos de sistemas operativos, y evita problemas de compatibilidad con librerías o scripts al ejecutar simulaciones.

## 2. Interfaz Gráfica (GUI)
*   **Biblioteca**: Streamlit.
    *   *Justificación*: Streamlit permite desarrollar interfaces web interactivas (dashboards) usando puramente Python. Esto es ideal para un simulador donde necesitaremos actualizar el estado visual en "tiempo real" (o paso a paso) y mostrar métricas. Facilita la creación de paneles laterales para la configuración de la simulación y gráficas en la vista principal para resultados.

## 3. Arquitectura del Proyecto
Se ha optado por separar claramente la lógica del negocio de la interfaz de usuario:
*   **`src/core/`**: Contendrá toda la lógica interna del simulador: procesos (`process.py`), los distintos algoritmos de planificación (`schedulers/`) y las métricas. Estas clases no tendrán dependencia alguna con la interfaz.
*   **`src/gui/`**: Se encargará de consumir los objetos y resultados de `core` para representarlos visualmente a través de Streamlit.

## 4. Modelado del Proceso
Para representar fielmente la ejecución de un proceso, se utiliza un **modelo de ráfagas CPU-E/S-CPU**.
*   *Justificación*: Un proceso no suele consumir CPU de principio a fin sin interrupciones. Frecuentemente necesita operaciones de E/S (lectura de disco, entrada del usuario). Modelar los requerimientos de un proceso como una secuencia alternada de tiempos de CPU y de E/S (ej. `[Ráfaga_CPU, Ráfaga_IO, Ráfaga_CPU]`) permite evaluar los algoritmos (especialmente los expulsivos y SRTF) de forma más realista, evidenciando cómo el tiempo de espera por E/S afecta el rendimiento del procesador y las colas.

## 5. Generación Aleatoria de Procesos
*   **Módulo Independiente**: Se aislará la lógica de creación aleatoria en `src/core/process_generator.py`.
    *   *Justificación*: Mantener la clase `Process` pura (sin depender de bibliotecas como `random`). Esto permite construir escenarios tanto aleatorios como predefinidos fácilmente para pruebas.
*   **Distribución de Ráfagas**: Se generará primero un total de tiempo CPU y un total de tiempo E/S por cada proceso. Luego, el tiempo CPU se dividirá intentando mantener equidad antes y después de la(s) ráfaga(s) de E/S (creando la estructura `[CPU, IO, CPU]`).
    *   *Justificación*: Asegura que los procesos sigan el ciclo natural de ejecución en sistemas operativos, donde siempre inician haciendo uso de CPU para luego hacer peticiones de E/S, y al volver requieren otra pequeña o gran fracción de CPU antes de finalizar.

## 6. Diseño de la Interfaz Gráfica (Streamlit)
*   **Separación de Lógica Visual**: El archivo `src/app.py` será el único punto de entrada de la aplicación y coordinará la interfaz.
    *   *Justificación*: Mantiene el desacoplamiento de la lógica (`core`) de su presentación.
*   **Panel Lateral (Sidebar) para Configuración**: Se utilizará el panel lateral de Streamlit (`st.sidebar`) exclusivamente para los controles y parámetros de entrada (número de procesos, rangos de ráfagas, etc.).
    *   *Justificación*: Permite al usuario mantener siempre visibles los controles sin invadir el espacio principal donde se renderizará el estado de la simulación.
*   **Estética Premium y Tema Global**: La configuración visual de la aplicación se centralizará en `.streamlit/config.toml` usando un tema oscuro con color de acento Verde.
    *   *Justificación*: Ofrece una experiencia moderna y fluida. Tener la configuración en un archivo `toml` permite cambiar el color de acento o el tema completo (ej. cambiar de Verde a Azul o de Oscuro a Claro) fácilmente modificando una sola línea, sin alterar el código fuente.

## 7. Gestión de Dependencias
*   **Entorno Virtual (`venv`)**: Se utiliza el módulo estándar `python3 -m venv` para crear un entorno aislado (`.venv/`) donde se instalan las dependencias del proyecto.
    *   *Justificación*: Evita conflictos con paquetes instalados globalmente en el sistema y garantiza que cualquier persona que clone el repositorio pueda reproducir exactamente el mismo entorno de ejecución.
*   **`requirements.txt`**: Archivo que lista las dependencias externas del proyecto (`streamlit` y `pandas`). Todas las demás librerías utilizadas (`enum`, `random`, `os`, `sys`, `typing`) pertenecen a la biblioteca estándar de Python y no requieren instalación.
    *   *Justificación*: Es el mecanismo estándar en Python para declarar dependencias de forma explícita y reproducible (`pip install -r requirements.txt`).

## 8. Diseño del Planificador (Scheduler)
*   **Clase Base Abstracta con Herencia**: Se implementa una clase `Scheduler` en `src/core/simulator.py` que contiene toda la maquinaria común de la simulación (colas, reloj, estadísticas). Los algoritmos específicos (FCFS, SJF, Round Robin, etc.) heredan de esta clase y solo implementan el método abstracto `select_next_process()`.
    *   *Justificación*: Evita la duplicación de código. La lógica de mover procesos entre colas, avanzar el reloj y calcular métricas es idéntica para todos los algoritmos; lo único que cambia es la política de selección. Este patrón (Template Method) permite añadir un nuevo algoritmo en pocas líneas.
*   **Ciclo de Vida de las Colas**: Los procesos transitan por los estados `NEW → READY → RUNNING → BLOCKED → READY → RUNNING → FINISHED` siguiendo el modelo de ráfagas CPU-E/S-CPU. El `Scheduler` administra cuatro colas (`ready_queue`, `blocked_queue`, `finished_queue`) más una referencia al proceso en CPU (`running_process`).
*   **Orden de Ejecución del Tick**: Cada tick ejecuta operaciones en un orden estricto: (1) admitir nuevos procesos, (2) avanzar E/S de bloqueados, (3) avanzar CPU del proceso activo, (4) asignar CPU si está libre, (5) acumular espera de la cola de listos, (6) registrar historial, (7) verificar finalización, (8) avanzar reloj.
    *   *Justificación*: Un orden determinístico garantiza resultados reproducibles y evita condiciones de carrera lógica (ej. que un proceso recién llegado sea seleccionado antes de procesar a los que ya estaban esperando).
*   **Soporte de Quantum**: El `Scheduler` incluye un atributo `quantum` y un contador `quantum_remaining` para soportar algoritmos expulsivos como Round Robin. Cuando el quantum se agota, el proceso en ejecución es devuelto a la cola de listos.
*   **Historial de Ticks**: Se registra una instantánea (`snapshot`) del estado del sistema en cada tick, almacenando qué proceso está en CPU, cuáles están en cada cola y cuántos llegaron ese tick. Este historial es la fuente de datos para la visualización paso a paso en la interfaz gráfica.
*   **Estadísticas**: El método `get_statistics()` calcula todas las métricas requeridas por las especificaciones del proyecto: % de uso del procesador, tiempo promedio de espera, tiempo promedio de bloqueo, tiempo promedio de ejecución (turnaround), total de procesos completados, arribo promedio de nuevos procesos por paso y tiempo total de simulación.

## 9. Algoritmos No Expulsivos
Todos los algoritmos no expulsivos se implementan en `src/core/algorithms/non_preemptive.py` como subclases de `Scheduler`, implementando únicamente el método `select_next_process()`.
*   **Convención de Prioridades**: Un número de prioridad **menor** indica **mayor** prioridad (ej. prioridad 1 es más urgente que prioridad 5).
    *   *Justificación*: Esta es la convención utilizada por la mayoría de sistemas operativos reales (Linux, por ejemplo). Resulta intuitiva al pensar en prioridad como "orden de importancia": el #1 es el primero.
*   **SJF evalúa la ráfaga actual, no el total**: En SJF se compara `remaining_current_burst` (el tiempo restante de la ráfaga de CPU que el proceso está a punto de ejecutar), no el tiempo total de CPU que le queda al proceso.
    *   *Justificación*: SJF clásico selecciona basándose en la próxima ráfaga de CPU. Usar el tiempo total restante correspondería más bien a SRTF (Shortest Remaining Time First), que además es expulsivo.
*   **Criterio de Desempate**: Cuando dos o más procesos tienen el mismo valor de selección (misma ráfaga, misma prioridad), se desempata por `arrival_time` (el que llegó primero tiene preferencia).
    *   *Justificación*: Garantiza un comportamiento determinístico y justo ante empates, evitando resultados arbitrarios que dificulten el análisis.

## 10. Algoritmos Expulsivos
Todos los algoritmos expulsivos se implementan en `src/core/algorithms/preemptive.py` como subclases de `Scheduler`.
*   **Hook de Expulsión (`_check_preemption()`)**: Se añadió un método hook al ciclo del `tick()` del Scheduler base (paso 3.5) que por defecto no hace nada. Los algoritmos expulsivos lo sobrescriben para comparar el proceso en CPU contra la cola de listos y decidir si debe ser interrumpido.
    *   *Justificación*: Este patrón permite que los algoritmos no expulsivos existentes sigan funcionando sin modificación alguna, mientras que los expulsivos añaden su lógica de interrupción de forma limpia.
*   **Dos tipos de expulsión**: Round Robin usa expulsión por quantum (ya integrada en el Scheduler base). SRTF y Prioridad Expulsiva usan expulsión por comparación (sobrescribiendo `_check_preemption()`).
*   **Relación entre pares de algoritmos**:
    *   SJF ↔ SRTF: Mismo criterio (`remaining_current_burst`), pero SRTF puede interrumpir.
    *   Prioridad NP ↔ Prioridad Expulsiva: Mismo criterio (`priority`), pero la versión expulsiva puede interrumpir.
    *   FCFS ↔ Round Robin: Mismo orden (FIFO), pero Round Robin limita el tiempo con un quantum.
