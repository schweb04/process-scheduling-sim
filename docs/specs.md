# Proyecto 03: Simulador de Planificación de Procesos

En este proyecto, **deben desarrollar** un Simulador de Planificación de Procesos, una herramienta de software que simula varios algoritmos de planificación de procesos comúnmente utilizados en sistemas operativos. El objetivo del proyecto es obtener experiencia práctica en entender, implementar y analizar el comportamiento de diferentes algoritmos de planificación de procesos.

Deben implementar varios algoritmos de planificación de procesos, estos son:

No expulsivos:

* Primero en llegar primero en ejecutar (FCFS)  
* Primero el trabajo más corto (SJF)  
* Selección aleatoria  
* Planificación basada en prioridades

Expulsivos:

* Turno rotativo (round robin)  
* Primero el menor tiempo restante (SRTF)  
* Planificación basada en prioridades

El simulador debe contar con una interfaz fácil de usar que permitirá a los usuarios:

* Generar de manera aleatoria detalles de procesos como tiempo de procesamiento (burst time), tiempo de procesamiento de E/S (IO burst time) y prioridad.  
* Seleccionar y configurar diferentes algoritmos de planificación para observar su comportamiento.  
* Definir el tiempo de cada paso (tick) del procesador y el tiempo de llegada.  
* Explicar brevemente los parámetros para generar los detalles de cada proceso.  
* Explicar brevemente el algoritmo en cuestión.

 

El simulador proporcionará visualizaciones para ayudar a los usuarios a comprender mejor el proceso de planificación, estas visualizaciones deben mostrar las actualizaciones en tiempo real sobre el estado de los procesos en la cola de listos, bloqueados, terminados y la CPU.

El simulador incluirá estadísticas para analizar el rendimiento de los algoritmos de planificación, para ello deben calcular % de uso del procesador, tiempo promedio de espera, tiempo promedio de bloqueo, tiempo promedio de ejecución, total de procesos completados, arribo de nuevos procesos por paso y tiempo total. 

* El simulador se implementará en un lenguaje de programación de su elección, preferiblemente C o C++, para alinearse estrechamente con los conceptos de sistemas operativos. La selección del lenguaje no afecta la nota.  
* Se pueden utilizar bibliotecas de interfaz gráfica de usuario (GUI) como Qt o Tkinter para desarrollar la interfaz de usuario, o cualquier otra biblioteca que ustedes prefieran y les facilite la implementación gráfica. Pueden usar tecnologías webs si así lo desean.  
* Se utilizarán estructuras de datos como colas y matrices para representar procesos y gestionar la planificación.

Los estudiantes presentarán un código fuente bien documentado que implemente el simulador de planificación de procesos y los algoritmos de planificación. Un informe detallado . **ENTREGA**: un video donde se realice una demostración del proyecto además de se que discuta las decisiones de diseño, los desafíos de implementación y el análisis de rendimiento de diferentes algoritmos de planificación según su apreciación.

* Corrección y funcionalidad del simulador.  
* Claridad y usabilidad de la interfaz de usuario.  
* Precisión de las métricas de rendimiento y análisis.  
* Calidad de la documentación y redacción del informe.  
* Manejo de conceptos en la demostración.

Al completar este proyecto, ustedes:

* Obtendrán un mayor entendimiento de los algoritmos de planificación de procesos.  
* Desarrollarán competencia en programación y estructuras de datos.  
* Mejorarán sus habilidades de modelado y simulación, analíticas y de resolución de problemas a través del análisis de rendimiento.  
* Mejorarán sus habilidades de comunicación a través de la documentación y la redacción de informes.

**Nota 01**: el video debe estar en drive o youtube.

**Nota 02**: el código fuente debe estar en un repositorio público.

**Nota 03**: la entrega es aquí y deben agregar ambos enlaces. 