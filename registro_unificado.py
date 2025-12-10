import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# Inicializa archivos si no existen
def inicializar_archivo(nombre):
    if not os.path.exists(nombre):
        with open(nombre, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=4, ensure_ascii=False)

# Validaciones comunes
def validar_si(valor):
    return valor.strip().lower() in ["sí", "si", "ok", "vigente", "al día", "bueno"]

# -------------------- CLIENTES --------------------
def registrar_cliente(nombre, identificacion, tarjeta):
    nombre = nombre.strip()
    identificacion = identificacion.strip().upper()
    tarjeta_limpia = tarjeta.replace(" ", "").replace("-", "")

    if len(nombre) < 3:
        messagebox.showerror("Error", "El nombre debe tener al menos 3 caracteres")
        return
    if len(identificacion) < 5:
        messagebox.showerror("Error", "La identificación debe tener al menos 5 caracteres")
        return
    if not tarjeta_limpia.isdigit() or len(tarjeta_limpia) != 16:
        messagebox.showerror("Error", "La tarjeta debe tener 16 dígitos")
        return

    tarjeta_enmascarada = f"**** **** **** {tarjeta_limpia[-4:]}"
    cliente = {
        "nombre": nombre,
        "identificacion": identificacion,
        "tarjeta": tarjeta_limpia,
        "tarjeta_enmascarada": tarjeta_enmascarada,
        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "estado": "activo"
    }

    with open("clientes_registrados.json", 'r+', encoding='utf-8') as f:
        clientes = json.load(f)
        clientes.append(cliente)
        f.seek(0)
        json.dump(clientes, f, indent=4, ensure_ascii=False)

    messagebox.showinfo("Registro exitoso", f"Cliente {nombre} registrado correctamente")

def ver_clientes():
    """Muestra ventana con clientes registrados"""
    if not os.path.exists("clientes_registrados.json"):
        messagebox.showinfo("Sin registros", "No hay clientes registrados aún")
        return

    with open("clientes_registrados.json", 'r', encoding='utf-8') as f:
        clientes = json.load(f)

    if not clientes:
        messagebox.showinfo("Sin registros", "No hay clientes registrados aún")
        return

    ventana = tk.Toplevel()
    ventana.title("Clientes Registrados")
    ventana.geometry("700x400")

    tree = ttk.Treeview(ventana, columns=("Nombre", "ID", "Tarjeta", "Fecha"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    for c in clientes:
        tree.insert("", "end", values=(c["nombre"], c["identificacion"], c["tarjeta_enmascarada"], c["fecha_registro"]))

    tree.pack(fill="both", expand=True, padx=10, pady=10)
    tk.Label(ventana, text=f"Total de clientes: {len(clientes)}", font=("Arial", 10, "bold")).pack(pady=5)

# -------------------- TAXISTAS --------------------
def registrar_taxista(campos):
    for campo, valor in campos.items():
        if not valor.strip():
            messagebox.showerror("Error", f"El campo '{campo}' no puede estar vacío")
            return
        if "Nombre" not in campo and "Identificación" not in campo and "Placa" not in campo:
            if not validar_si(valor):
                messagebox.showerror("Error", f"El campo '{campo}' debe estar en regla (ej: 'Sí')")
                return

    taxista = {
        "nombre": campos["Nombre Completo:"],
        "identificacion": campos["Identificación (DNI/Pasaporte):"],
        "licencia": campos["Licencia vigente:"],
        "antecedentes": campos["Antecedentes penales al día:"],
        "certificado_medico": campos["Certificado médico vigente:"],
        "infracciones": campos["Pago de infracciones al día:"],
        "placa": campos["Placa del vehículo:"],
        "seguro": campos["Seguro vigente:"],
        "impuestos": campos["Impuestos al día:"],
        "placa_estado": campos["Placa en buen estado:"],
        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "estado": "activo"
    }

    with open("taxis_registrados.json", 'r+', encoding='utf-8') as f:
        taxis = json.load(f)
        taxis.append(taxista)
        f.seek(0)
        json.dump(taxis, f, indent=4, ensure_ascii=False)

    messagebox.showinfo("Registro exitoso", f"Taxista {taxista['nombre']} registrado correctamente")

def ver_taxistas():
    """Muestra ventana con taxistas registrados"""
    if not os.path.exists("taxis_registrados.json"):
        messagebox.showinfo("Sin registros", "No hay taxistas registrados aún")
        return

    with open("taxis_registrados.json", 'r', encoding='utf-8') as f:
        taxis = json.load(f)

    if not taxis:
        messagebox.showinfo("Sin registros", "No hay taxistas registrados aún")
        return

    ventana = tk.Toplevel()
    ventana.title("Taxistas Registrados")
    ventana.geometry("700x400")

    tree = ttk.Treeview(ventana, columns=("Nombre", "ID", "Placa", "Fecha"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    for t in taxis:
        tree.insert("", "end", values=(t["nombre"], t["identificacion"], t["placa"], t["fecha_registro"]))

    tree.pack(fill="both", expand=True, padx=10, pady=10)
    tk.Label(ventana, text=f"Total de taxistas: {len(taxis)}", font=("Arial", 10, "bold")).pack(pady=5)

# -------------------- INTERFAZ --------------------
def crear_interfaz():
    root = tk.Tk()
    root.title("UNIETAXI - Registro Unificado")
    root.geometry("650x750")
    root.resizable(False, False)

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # Pestaña Cliente
    tab_cliente = tk.Frame(notebook)
    notebook.add(tab_cliente, text="🧍 Cliente")

    tk.Label(tab_cliente, text="Nombre Completo:").pack(pady=5)
    entry_nombre = tk.Entry(tab_cliente, width=40)
    entry_nombre.pack()

    tk.Label(tab_cliente, text="Identificación (DNI/Pasaporte):").pack(pady=5)
    entry_id = tk.Entry(tab_cliente, width=40)
    entry_id.pack()

    tk.Label(tab_cliente, text="Tarjeta de Crédito (16 dígitos):").pack(pady=5)
    entry_tarjeta = tk.Entry(tab_cliente, width=40)
    entry_tarjeta.pack()

    # ✅ Botón Registrar Cliente
    tk.Button(
        tab_cliente,
        text="✅ Registrar Cliente",
        command=lambda: registrar_cliente(entry_nombre.get(), entry_id.get(), entry_tarjeta.get()),
        bg="#27ae60",
        fg="white",
        font=("Arial", 12, "bold"),
        padx=10,
        pady=5
    ).pack(pady=10)

    # 📋 Botón Ver Clientes Registrados
    tk.Button(
        tab_cliente,
        text="📋 Ver Clientes Registrados",
        command=ver_clientes,
        bg="#3498db",
        fg="white",
        font=("Arial", 10),
        padx=10,
        pady=5
    ).pack(pady=5)

    # Pestaña Taxista
    tab_taxista = tk.Frame(notebook)
    notebook.add(tab_taxista, text="🚖 Taxista")

    campos_taxista = [
        "Nombre Completo:",
        "Identificación (DNI/Pasaporte):",
        "Licencia vigente:",
        "Antecedentes penales al día:",
        "Certificado médico vigente:",
        "Pago de infracciones al día:",
        "Placa del vehículo:",
        "Seguro vigente:",
        "Impuestos al día:",
        "Placa en buen estado:"
    ]

    entradas_taxista = {}

    for campo in campos_taxista:
        tk.Label(tab_taxista, text=campo).pack(pady=3)
        entrada = tk.Entry(tab_taxista, width=40)
        entrada.pack()
        entradas_taxista[campo] = entrada

    # ✅ Botón Registrar Taxista
    tk.Button(
        tab_taxista,
        text="✅ Registrar Taxista",
        command=lambda: registrar_taxista({k: v.get() for k, v in entradas_taxista.items()}),
        bg="#1d1f21",
        fg="white",
        font=("Arial", 12, "bold"),
        padx=10,
        pady=5
    ).pack(pady=10)

    # 📋 Botón Ver Taxistas Registrados
    tk.Button(
        tab_taxista,
        text="📋 Ver Taxistas Registrados",
        command=ver_taxistas,
        bg="#3498db",
        fg="white",
        font=("Arial", 10),
        padx=10,
        pady=5
    ).pack(pady=5)

    root.mainloop()

# Inicializar archivos
inicializar_archivo("clientes_registrados.json")
inicializar_archivo("taxis_registrados.json")

# Lanzar interfaz
crear_interfaz()