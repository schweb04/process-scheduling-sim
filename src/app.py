import streamlit as st
import pandas as pd
from core.process_generator import ProcessGenerator

# Configuración básica de la página
st.set_page_config(
    page_title="Simulador de Planificación",
    page_icon="⚡",
    layout="wide"
)

def render_sidebar():
    st.sidebar.header("⚙️ Configuración del Generador")
    st.sidebar.markdown("Ajusta los parámetros para generar los procesos de prueba.")
    
    num_processes = st.sidebar.slider("Cantidad de Procesos", min_value=1, max_value=20, value=5)
    
    st.sidebar.subheader("Rangos de Llegada")
    min_arr, max_arr = st.sidebar.slider("Llegada (Ticks)", 0, 50, (0, 10))
    
    st.sidebar.subheader("Rangos de Ráfagas")
    min_cpu, max_cpu = st.sidebar.slider("Total CPU (Ticks)", 1, 20, (2, 8))
    min_io, max_io = st.sidebar.slider("Total E/S (Ticks)", 0, 10, (1, 3))
    
    st.sidebar.subheader("Prioridades")
    min_prio, max_prio = st.sidebar.slider("Rango de Prioridad", 1, 10, (1, 5))
    
    # Botón principal
    generate_btn = st.sidebar.button("Generar Procesos", type="primary", use_container_width=True)
    
    return {
        "num_processes": num_processes,
        "arrival_time_range": (min_arr, max_arr),
        "cpu_burst_range": (min_cpu, max_cpu),
        "io_burst_range": (min_io, max_io),
        "priority_levels": (min_prio, max_prio),
        "generate_btn": generate_btn
    }

def main():
    st.title("⚡ Simulador de Planificación de Procesos")
    st.markdown("Genera procesos aleatorios y visualiza su estructura interna basada en el modelo **CPU-E/S-CPU**.")
    
    # Renderizar panel lateral
    config = render_sidebar()
    
    # Estado de la sesión para guardar los procesos generados
    if "procesos" not in st.session_state:
        st.session_state.procesos = []
        
    if config["generate_btn"]:
        generator = ProcessGenerator(
            num_processes=config["num_processes"],
            arrival_time_range=config["arrival_time_range"],
            cpu_burst_range=config["cpu_burst_range"],
            io_burst_range=config["io_burst_range"],
            priority_levels=config["priority_levels"]
        )
        st.session_state.procesos = generator.generate()
        
    # Mostrar resultados si hay procesos generados
    if st.session_state.procesos:
        st.subheader(f"📊 Procesos Generados ({len(st.session_state.procesos)})")
        
        # Transformar los objetos Process a un diccionario para mostrarlos en Pandas
        data = []
        for p in st.session_state.procesos:
            data.append({
                "PID": p.pid,
                "Llegada": p.arrival_time,
                "Prioridad": p.priority,
                "Secuencia de Ráfagas (Ticks)": str(p.bursts),
                "Total CPU": p.total_burst_time,
                "Total E/S": p.total_io_burst_time
            })
            
        df = pd.DataFrame(data)
        
        # Ocultar el índice predeterminado de pandas y usar la configuración nativa de tabla de Streamlit
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "PID": st.column_config.NumberColumn(format="%d"),
            }
        )
    else:
        st.info("👈 Utiliza el panel lateral para configurar y generar los procesos.")

if __name__ == "__main__":
    main()
