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
*   **`src/ui/`**: Se encargará de consumir los objetos y resultados de `core` para representarlos visualmente a través de Streamlit.

## 4. Modelado del Proceso
Para representar fielmente la ejecución de un proceso, se utiliza un **modelo de ráfagas CPU-E/S-CPU**.
*   *Justificación*: Un proceso no suele consumir CPU de principio a fin sin interrupciones. Frecuentemente necesita operaciones de E/S (lectura de disco, entrada del usuario). Modelar los requerimientos de un proceso como una secuencia alternada de tiempos de CPU y de E/S (ej. `[Ráfaga_CPU, Ráfaga_IO, Ráfaga_CPU]`) permite evaluar los algoritmos (especialmente los expulsivos y SRTF) de forma más realista, evidenciando cómo el tiempo de espera por E/S afecta el rendimiento del procesador y las colas.
