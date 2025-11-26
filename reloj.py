import tkinter as tk
from datetime import datetime, timedelta

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Reloj Acelerado")

# Tiempo inicial simulado
tiempo_simulado = datetime.now()

def actualizar_reloj():
    global tiempo_simulado
    # Incrementar el tiempo simulado en 10 horas cada 5 minutos reales
    tiempo_simulado += timedelta(seconds=30)  # 30 segundos simulados por cada actualización (500 ms)
    tiempo_formateado = tiempo_simulado.strftime("%H:%M:%S")
    etiqueta_reloj.config(text=tiempo_formateado)
    ventana.after(500, actualizar_reloj)  # Actualizar cada 500 ms (medio segundo)

# Crear y configurar la etiqueta del reloj
etiqueta_reloj = tk.Label(ventana, font=("Helvetica", 48), fg="black")
etiqueta_reloj.pack(anchor="center")

# Iniciar la actualización del reloj
actualizar_reloj()

# Iniciar el bucle principal de la ventana
ventana.mainloop()