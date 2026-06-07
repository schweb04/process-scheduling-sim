import time
import copy
import streamlit as st
import pandas as pd
from core.process_generator import ProcessGenerator
from core.algorithms.non_preemptive import (
    FCFSScheduler,
    SJFScheduler,
    RandomScheduler,
    PriorityNPScheduler,
)
from core.algorithms.preemptive import (
    RoundRobinScheduler,
    SRTFScheduler,
    PriorityPScheduler,
)

# ─────────────────────────────────────────────
#  Configuración de la página
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Simulador de Planificación",
    page_icon="⚡",
    layout="wide"
)

# ─────────────────────────────────────────────
#  Catálogo de algoritmos
# ─────────────────────────────────────────────

ALGORITHMS = {
    "FCFS (Primero en llegar)": {
        "class": FCFSScheduler,
        "needs_quantum": False,
        "preemptive": False,
        "description": (
            "**Primero en llegar, primero en ejecutar (FCFS)**. "
            "Selecciona el proceso que lleva más tiempo esperando en la cola de listos (FIFO). "
            "No expulsivo: una vez que un proceso obtiene la CPU, la conserva hasta terminar su ráfaga."
        ),
    },
    "SJF (Trabajo más corto)": {
        "class": SJFScheduler,
        "needs_quantum": False,
        "preemptive": False,
        "description": (
            "**Primero el trabajo más corto (SJF)**. "
            "Selecciona el proceso con la ráfaga de CPU actual más corta. "
            "No expulsivo: no interrumpe al proceso en ejecución aunque llegue uno más corto."
        ),
    },
    "Aleatorio": {
        "class": RandomScheduler,
        "needs_quantum": False,
        "preemptive": False,
        "description": (
            "**Selección aleatoria**. "
            "Elige un proceso al azar de la cola de listos. "
            "No expulsivo: el proceso seleccionado termina su ráfaga sin interrupciones."
        ),
    },
    "Prioridad (No Expulsiva)": {
        "class": PriorityNPScheduler,
        "needs_quantum": False,
        "preemptive": False,
        "description": (
            "**Prioridad no expulsiva**. "
            "Selecciona el proceso con mayor prioridad (menor número). "
            "No expulsivo: no interrumpe al proceso en ejecución aunque llegue uno más prioritario."
        ),
    },
    "Round Robin": {
        "class": RoundRobinScheduler,
        "needs_quantum": True,
        "preemptive": True,
        "description": (
            "**Turno rotativo (Round Robin)**. "
            "Cada proceso ejecuta durante un máximo de *quantum* ticks. "
            "Si no termina, es expulsado y enviado al final de la cola de listos."
        ),
    },
    "SRTF (Menor tiempo restante)": {
        "class": SRTFScheduler,
        "needs_quantum": False,
        "preemptive": True,
        "description": (
            "**Primero el menor tiempo restante (SRTF)**. "
            "Versión expulsiva de SJF. Si llega un proceso con menor tiempo de ráfaga restante "
            "que el que está en CPU, lo interrumpe inmediatamente."
        ),
    },
    "Prioridad (Expulsiva)": {
        "class": PriorityPScheduler,
        "needs_quantum": False,
        "preemptive": True,
        "description": (
            "**Prioridad expulsiva**. "
            "Si llega un proceso con mayor prioridad (menor número) que el que está en CPU, "
            "lo interrumpe inmediatamente."
        ),
    },
}

# ─────────────────────────────────────────────
#  Inicialización del estado de sesión
# ─────────────────────────────────────────────

def init_session_state():
    """Inicializa las variables de sesión si no existen."""
    if "procesos" not in st.session_state:
        st.session_state.procesos = []
    if "scheduler" not in st.session_state:
        st.session_state.scheduler = None
    if "auto_mode" not in st.session_state:
        st.session_state.auto_mode = False
    if "procesos_backup" not in st.session_state:
        st.session_state.procesos_backup = []

init_session_state()

# ─────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────

def render_sidebar():
    """Renderiza el panel lateral con las 3 secciones de configuración."""
    
    # ── Sección 1: Parámetros de Generación ──
    with st.sidebar.expander("📋 Parámetros de Generación", expanded=True):
        st.caption(
            "Configura los rangos para generar procesos aleatorios. "
            "Cada proceso tendrá un tiempo de llegada, ráfagas de CPU y E/S, "
            "y una prioridad dentro de estos rangos."
        )
        num_processes = st.slider(
            "Cantidad de Procesos", 1, 20, 5,
            help="Número total de procesos que se simularán."
        )
        min_arr, max_arr = st.slider(
            "Rango de Llegada (Ticks)", 0, 50, (0, 10),
            help="El tiempo en el que un proceso entra al sistema. 0 significa que está disponible desde el inicio."
        )
        min_cpu, max_cpu = st.slider(
            "Rango de CPU (Ticks)", 1, 20, (2, 8),
            help="Tiempo total de procesamiento requerido por el proceso en la CPU, el cual se dividirá en múltiples ráfagas."
        )
        min_io, max_io = st.slider(
            "Rango de E/S (Ticks)", 0, 10, (1, 3),
            help="Tiempo total que el proceso pasará bloqueado realizando operaciones de Entrada/Salida."
        )
        min_prio, max_prio = st.slider(
            "Rango de Prioridad", 1, 10, (1, 5),
            help="Nivel de urgencia del proceso. Los valores más bajos indican mayor prioridad (ej. 1 es más urgente que 5)."
        )
        
        generate_btn = st.button(
            "🎲 Generar Procesos",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.get("auto_mode", False)
        )
    
    # ── Sección 2: Configuración del Algoritmo ──
    with st.sidebar.expander("🧠 Algoritmo de Planificación", expanded=True):
        algo_name = st.selectbox(
            "Selecciona un algoritmo",
            list(ALGORITHMS.keys()),
        )
        algo_info = ALGORITHMS[algo_name]
        
        st.markdown(algo_info["description"])
        
        tag = "🔴 Expulsivo" if algo_info["preemptive"] else "🟢 No Expulsivo"
        st.caption(tag)
        
        quantum = 0
        if algo_info["needs_quantum"]:
            quantum = st.number_input(
                "Quantum (ticks)",
                min_value=1,
                max_value=20,
                value=3,
            )
    
    # ── Sección 3: Controles de Simulación ──
    with st.sidebar.expander("▶️ Controles de Simulación", expanded=True):
        speed = st.slider(
            "Velocidad (ms/tick)",
            min_value=100,
            max_value=2000,
            value=500,
            step=100,
            help="Tiempo de espera entre ticks en el modo automático."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            step_btn = st.button("⏭ Siguiente Tick", use_container_width=True, disabled=st.session_state.get("auto_mode", False))
        with col2:
            run_all_btn = st.button("⏩ Ejecutar Todo", use_container_width=True, disabled=st.session_state.get("auto_mode", False))
        
        if st.session_state.get("auto_mode", False):
            auto_btn = st.button("⏸ Pausar Automático", use_container_width=True)
        else:
            auto_btn = st.button("▶️ Modo Automático", use_container_width=True)
            
        reset_btn = st.button("🔄 Reiniciar Simulación", use_container_width=True, disabled=st.session_state.get("auto_mode", False))
    
    return {
        "num_processes": num_processes,
        "arrival_time_range": (min_arr, max_arr),
        "cpu_burst_range": (min_cpu, max_cpu),
        "io_burst_range": (min_io, max_io),
        "priority_levels": (min_prio, max_prio),
        "generate_btn": generate_btn,
        "algo_name": algo_name,
        "algo_info": algo_info,
        "quantum": quantum,
        "speed": speed,
        "step_btn": step_btn,
        "run_all_btn": run_all_btn,
        "auto_btn": auto_btn,
        "reset_btn": reset_btn,
    }

# ─────────────────────────────────────────────
#  Funciones de creación del Scheduler
# ─────────────────────────────────────────────

def create_scheduler(config):
    """Crea una nueva instancia del Scheduler con los procesos y algoritmo configurados."""
    # Usar copias profundas de los procesos para no mutar los originales
    processes_copy = copy.deepcopy(st.session_state.procesos_backup)
    algo_class = config["algo_info"]["class"]
    
    kwargs = {}
    if config["algo_info"]["needs_quantum"]:
        kwargs["quantum"] = config["quantum"]
    
    return algo_class(processes=processes_copy, **kwargs)

# ─────────────────────────────────────────────
#  Funciones de renderizado
# ─────────────────────────────────────────────

def render_process_table():
    """Muestra la tabla de procesos generados."""
    if not st.session_state.procesos:
        return
    
    st.subheader(f"📊 Procesos Generados ({len(st.session_state.procesos)})")
    
    data = []
    for p in st.session_state.procesos:
        data.append({
            "PID": p.pid,
            "Llegada": p.arrival_time,
            "Prioridad": p.priority,
            "Ráfagas (Ticks)": str(p.bursts),
            "Total CPU": p.total_burst_time,
            "Total E/S": p.total_io_burst_time,
        })
    
    df = pd.DataFrame(data)
    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
        column_config={"PID": st.column_config.NumberColumn(format="%d")},
    )

def render_simulation_state(scheduler):
    """Muestra el estado actual de las colas y la CPU."""
    st.subheader(f"🕐 Tick Actual: {scheduler.current_tick}")
    
    if scheduler.is_complete:
        render_history(scheduler)
        st.write("")
        
    col_ready, col_cpu, col_blocked, col_finished = st.columns(4)
    
    with col_ready:
        st.markdown("### 🟢 Listos")
        if scheduler.ready_queue:
            for p in scheduler.ready_queue:
                st.markdown(f"- **P{p.pid}** (espera: {p.wait_time}t)")
        else:
            st.caption("Cola vacía")
    
    with col_cpu:
        st.markdown("### 🔵 CPU")
        if scheduler.running_process:
            p = scheduler.running_process
            st.markdown(
                f"**P{p.pid}**\n\n"
                f"Ráfaga restante: `{p.remaining_current_burst}t`"
            )
            if scheduler.quantum > 0:
                st.caption(f"Quantum restante: {scheduler.quantum_remaining}t")
        else:
            st.caption("Ociosa")
    
    with col_blocked:
        st.markdown("### 🟡 Bloqueados")
        if scheduler.blocked_queue:
            for p in scheduler.blocked_queue:
                st.markdown(f"- **P{p.pid}** (E/S rest: {p.remaining_current_burst}t)")
        else:
            st.caption("Cola vacía")
    
    with col_finished:
        st.markdown("### ✅ Terminados")
        if scheduler.finished_queue:
            for p in scheduler.finished_queue:
                st.markdown(f"- **P{p.pid}** (Tiempo de ejecución: {p.turnaround_time}t)")
        else:
            st.caption("Ninguno aún")

def render_history(scheduler):
    """Muestra el historial tick a tick como tabla."""
    if not scheduler.history:
        return
    
    with st.expander("📜 Historial Tick a Tick", expanded=False):
        history_data = []
        for snap in scheduler.history:
            history_data.append({
                "Tick": snap["tick"],
                "CPU": f"P{snap['running']}" if snap["running"] else "Ociosa",
                "Listos": [f"P{pid}" for pid in snap["ready"]],
                "Bloqueados": [f"P{pid}" for pid in snap["blocked"]],
                "Finalizados": [f"P{pid}" for pid in snap["finished"]],
                "Llegadas": snap["arrivals"],
            })
        
        df = pd.DataFrame(history_data)
        st.dataframe(df, hide_index=True, use_container_width=True)

def render_statistics(scheduler):
    """Muestra las estadísticas finales de la simulación."""
    if not scheduler.is_complete:
        return
    
    st.subheader("📈 Estadísticas Finales")
    stats = scheduler.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("% Uso CPU", f"{stats['cpu_usage_percent']}%", help="Porcentaje del tiempo total en el que la CPU estuvo ejecutando algún proceso.")
        st.metric("Tiempo Total", f"{stats['total_ticks']} ticks", help="Cantidad de ticks transcurridos desde el inicio hasta terminar el último proceso.")
    with col2:
        st.metric("Promedio Espera", f"{stats['avg_wait_time']} ticks", help="Tiempo promedio que los procesos pasaron en la cola de Listos esperando la CPU.")
        st.metric("Promedio Bloqueo", f"{stats['avg_io_time']} ticks", help="Tiempo promedio que los procesos pasaron bloqueados por Entrada/Salida.")
    with col3:
        st.metric("Promedio Ejecución", f"{stats['avg_turnaround_time']} ticks", help="Tiempo promedio desde que el proceso llega al sistema hasta que finaliza.")
        st.metric("Arribo Prom./Tick", f"{stats['avg_arrivals_per_tick']}", help="Promedio de procesos que llegaron al sistema por cada tick de tiempo.")
    with col4:
        st.metric("Total Completados", f"{stats['total_completed']}", help="Número total de procesos que finalizaron exitosamente.")

# ─────────────────────────────────────────────
#  Función principal
# ─────────────────────────────────────────────

def main():
    st.title("⚡ Simulador de Planificación de Procesos")
    st.markdown(
        "Genera procesos aleatorios, selecciona un algoritmo de planificación "
        "y observa paso a paso cómo gestiona las colas y la CPU."
    )
    
    config = render_sidebar()
    
    # ── Generar procesos ──
    if config["generate_btn"]:
        generator = ProcessGenerator(
            num_processes=config["num_processes"],
            arrival_time_range=config["arrival_time_range"],
            cpu_burst_range=config["cpu_burst_range"],
            io_burst_range=config["io_burst_range"],
            priority_levels=config["priority_levels"],
        )
        st.session_state.procesos = generator.generate()
        st.session_state.procesos_backup = copy.deepcopy(st.session_state.procesos)
        st.session_state.scheduler = None  # Resetear simulación
    
    # ── Reiniciar simulación ──
    if config["reset_btn"] and st.session_state.procesos_backup:
        st.session_state.scheduler = None
        st.session_state.auto_mode = False
    
    # ── Mostrar tabla de procesos ──
    render_process_table()
    
    # ── Verificar que hay procesos antes de simular ──
    if not st.session_state.procesos:
        st.info("👈 Utiliza el panel lateral para generar procesos y comenzar.")
        return
    
    st.divider()
    
    # ── Crear scheduler si no existe ──
    if st.session_state.scheduler is None:
        st.session_state.scheduler = create_scheduler(config)
    
    scheduler = st.session_state.scheduler
    
    # ── Controles de simulación ──
    if config["auto_btn"]:
        st.session_state.auto_mode = not st.session_state.auto_mode
        st.rerun()

    if config["step_btn"] and not scheduler.is_complete:
        scheduler.tick()
    
    if config["run_all_btn"] and not scheduler.is_complete:
        scheduler.run_all()
    
    # ── Mostrar estado actual ──
    if st.session_state.get("auto_mode", False) and not scheduler.is_complete:
        total = len(scheduler.processes)
        completed = len(scheduler.finished_queue)
        st.progress(completed / total if total > 0 else 1.0)

    render_simulation_state(scheduler)
    
    # ── Estadísticas finales ──
    render_statistics(scheduler)
    
    if scheduler.is_complete:
        if st.session_state.get("auto_mode", False):
            st.session_state.auto_mode = False
            st.rerun()
        st.success("✅ Simulación completada.")
    else:
        if st.session_state.get("auto_mode", False):
            time.sleep(config["speed"] / 1000.0)
            scheduler.tick()
            st.rerun()

if __name__ == "__main__":
    main()
