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
