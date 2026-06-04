# ⚡ Simulador de Planificación de Procesos

Simulador interactivo que permite visualizar y comparar el comportamiento de diversos algoritmos de planificación de procesos utilizados en sistemas operativos.

Construido con **Python** y **Streamlit**.

## Algoritmos Implementados

### No Expulsivos
- Primero en llegar, primero en ejecutar (FCFS)
- Primero el trabajo más corto (SJF)
- Selección aleatoria
- Planificación basada en prioridades

### Expulsivos
- Turno rotativo (Round Robin)
- Primero el menor tiempo restante (SRTF)
- Planificación basada en prioridades

## Requisitos Previos

- **Python 3.10+**
- **pip** (gestor de paquetes de Python)
- Se recomienda un entorno **Linux** o **WSL** (Windows Subsystem for Linux)

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/schweb04/process-scheduling-sim.git
cd process-scheduling-sim
```

### 2. Crear un entorno virtual

Un entorno virtual es una carpeta aislada donde se instalan las dependencias del proyecto sin afectar las bibliotecas globales de tu sistema.

```bash
python3 -m venv .venv
```

### 3. Activar el entorno virtual

```bash
source .venv/bin/activate
```

> Al activarse, verás `(.venv)` al inicio de tu línea de comandos. Esto indica que cualquier paquete que instales quedará dentro de esa carpeta y no en tu sistema.

### 4. Instalar las dependencias

```bash
pip install -r requirements.txt
```

Esto instalará automáticamente `streamlit`, `pandas` y todas sus sub-dependencias.

## Ejecución

Asegúrate de tener el entorno virtual activado y ejecuta:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
streamlit run src/app.py
```

Streamlit abrirá automáticamente tu navegador en `http://localhost:8501`.

## Estructura del Proyecto

```
process-scheduling-sim/
├── .streamlit/
│   └── config.toml          # Tema visual de la aplicación
├── docs/
│   ├── specs.md              # Especificaciones del proyecto
│   └── technical_decisions.md # Decisiones técnicas y de diseño
├── src/
│   ├── core/
│   │   ├── process.py        # Clase Process y estados
│   │   └── process_generator.py # Generador aleatorio de procesos
│   └── app.py                # Punto de entrada (Streamlit)
├── tests/
│   └── test_processes.py     # Pruebas de la lógica de procesos
├── .gitignore
├── requirements.txt
└── README.md
```

## Documentación

Las decisiones arquitectónicas y técnicas del proyecto están detalladas en [`docs/technical_decisions.md`](docs/technical_decisions.md).
