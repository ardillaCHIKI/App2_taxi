"""
config.py - Configuración Global del Sistema UNIETAXI

Este archivo contiene todas las configuraciones centralizadas del sistema.
"""

import os
from datetime import datetime

# ==================== RUTAS DE ARCHIVOS ====================

# Directorio base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORTES_DIR = os.path.join(DATA_DIR, "reportes")

# Crear directorios si no existen
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTES_DIR, exist_ok=True)

# Archivos JSON
CLIENTES_JSON = os.path.join(DATA_DIR, "clientes_registrados.json")
TAXIS_JSON = os.path.join(DATA_DIR, "taxis_registrados.json")
SERVICIOS_JSON = os.path.join(DATA_DIR, "servicios_completados.json")
UBICACIONES_TIEMPO_REAL = os.path.join(DATA_DIR, "ubicaciones_tiempo_real.json")

# Archivos de reportes
REPORTE_DIARIO_TEMPLATE = os.path.join(REPORTES_DIR, "reporte_dia_{dia}_{fecha}.txt")
REPORTE_MENSUAL = os.path.join(REPORTES_DIR, "reporte_mensual_{fecha}.txt")

# Archivo HTML del mapa
MAPA_HTML = os.path.join(BASE_DIR, "taxi_animado.html")

# ==================== PARÁMETROS DEL SISTEMA ====================

# Simulación de tiempo
TIEMPO_REAL = {
    "ACELERACION": 60,  # 1 segundo real = 60 segundos simulados
    "UPDATE_INTERVAL_MS": 500,  # Actualización cada 500ms
    "SEGUNDOS_POR_UPDATE": 30  # 30 segundos simulados por update
}

# Operación de taxis
TAXI_CONFIG = {
    "RADIO_BUSQUEDA_KM": 2.0,  # Radio de búsqueda en kilómetros
    "TARIFA_POR_KM": 2.5,  # Dólares por kilómetro
    # Nueva tarifa por metro (dólares por metro). Si se configura, tiene prioridad
    # sobre `TARIFA_POR_KM` y se aplicará a todos los clientes.
    "TARIFA_POR_METRO": 1.0,
    "VELOCIDAD_PROMEDIO_KMH": 60,  # Velocidad promedio
    "COMISION_EMPRESA": 0.20  # 20% de comisión para UNIETAXI
}

# Sistema de calificaciones
CALIFICACIONES = {
    "MINIMA": 1,
    "MAXIMA": 5,
    "INICIAL": 5.0
}

# Seguimiento diario
SEGUIMIENTO = {
    "SERVICIOS_POR_DIA": 5  # Servicios aleatorios a seguir por día
}

# Cierre contable
CIERRE_CONTABLE = {
    "HORA": 12,  # 12:00 PM
    "MINUTO": 0
}

# Validaciones
VALIDACIONES = {
    "NOMBRE_MIN_CHARS": 3,
    "IDENTIFICACION_MIN_CHARS": 5,
    "TARJETA_DIGITOS": 16,
    "PLACA_MIN_CHARS": 5
}

# ==================== COORDENADAS DE MADRID ====================

# Punto central (Sol)
CENTRO_MADRID = {
    "lat": 40.4168,
    "lng": -3.7034,
    "nombre": "Puerta del Sol"
}

# Ruta principal para visualización
RUTA_PRINCIPAL = [
    (40.4168, -3.7034, "Sol"),
    (40.4193, -3.6931, "Fuente de Cibeles"),
    (40.4200, -3.6887, "Puerta de Alcalá"),
    (40.4216, -3.6800, "Calle O'Donnell"),
    (40.4142, -3.6772, "Hospital Niño Jesús"),
    (40.4113, -3.6763, "Puerta Niño Jesús"),
    (40.4075, -3.6789, "Av. Menéndez Pelayo"),
    (40.4044, -3.6807, "Menéndez Pelayo")
]

# Puntos de inicio para taxis (simulación)
PUNTOS_INICIO_TAXIS = [
    (40.4178, -3.7094, "Ópera"),
    (40.4234, -3.7109, "Plaza de España"),
    (40.4153, -3.6840, "Parque del Retiro"),
    (40.4050, -3.7026, "Embajadores"),
    (40.4306, -3.7162, "Argüelles"),
    (40.4200, -3.7100, "Gran Vía"),
    (40.4100, -3.6900, "Atocha"),
    (40.4250, -3.6850, "Salamanca")
]

# ==================== CONFIGURACIÓN DE SIMULACIÓN ====================

SIMULACION = {
    "DIAS_POR_DEFECTO": 2,
    "CLIENTES_ACTIVOS_MAX": 20,
    "TAXIS_ACTIVOS_MAX": 10,
    "SOLICITUDES_POR_CLIENTE": (1, 3),  # Min y max solicitudes
    "DELAY_ENTRE_SOLICITUDES": (0.1, 0.5),  # Segundos
    "TIEMPO_SIMULACION_DIA": 6.0  # Segundos reales por día simulado (aumentado para más actividad)
}

# ==================== COLORES PARA VISUALIZACIÓN ====================

COLORES_TAXIS = [
    {"color": "orange", "bg": "orange", "nombre": "Naranja"},
    {"color": "purple", "bg": "purple", "nombre": "Violeta"},
    {"color": "red", "bg": "red", "nombre": "Rojo"},
    {"color": "darkgreen", "bg": "green", "nombre": "Verde"},
    {"color": "gray", "bg": "gray", "nombre": "Gris"},
    {"color": "blue", "bg": "blue", "nombre": "Azul"},
    {"color": "pink", "bg": "pink", "nombre": "Rosa"},
    {"color": "brown", "bg": "brown", "nombre": "Café"}
]

# ==================== MENSAJES DEL SISTEMA ====================

MENSAJES = {
    "BIENVENIDA": """
╔════════════════════════════════════════════════════════════╗
║           SISTEMA UNIETAXI - VERSIÓN 2.0                  ║
║      Sincronización y Comunicación entre Procesos          ║
╚════════════════════════════════════════════════════════════╝
""",
    "SEPARADOR": "=" * 60,
    "SEPARADOR_MENOR": "-" * 60
}

# ==================== CONFIGURACIÓN DE LOGS ====================

LOG_CONFIG = {
    "NIVEL": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "FORMATO": "[%(asctime)s] %(levelname)s: %(message)s",
    "FECHA_FORMATO": "%Y-%m-%d %H:%M:%S"
}

# ==================== FUNCIONES AUXILIARES ====================

def obtener_timestamp():
    """Retorna timestamp formateado"""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def obtener_fecha_legible():
    """Retorna fecha en formato legible"""
    return datetime.now().strftime("%d de %B de %Y, %H:%M:%S")

def crear_nombre_reporte_diario(dia):
    """Crea nombre de archivo para reporte diario"""
    return REPORTE_DIARIO_TEMPLATE.format(
        dia=dia,
        fecha=obtener_timestamp()
    )

def crear_nombre_reporte_mensual():
    """Crea nombre de archivo para reporte mensual"""
    return REPORTE_MENSUAL.format(fecha=obtener_timestamp())

# ==================== VALIDACIONES DE CONFIGURACIÓN ====================

def validar_configuracion():
    """Valida que la configuración sea coherente"""
    errores = []
    
    if TAXI_CONFIG["RADIO_BUSQUEDA_KM"] <= 0:
        errores.append("El radio de búsqueda debe ser positivo")
    
    if TAXI_CONFIG["TARIFA_POR_KM"] <= 0:
        errores.append("La tarifa por km debe ser positiva")
    
    if not (0 <= TAXI_CONFIG["COMISION_EMPRESA"] <= 1):
        errores.append("La comisión debe estar entre 0 y 1")
    
    if SEGUIMIENTO["SERVICIOS_POR_DIA"] < 0:
        errores.append("Los servicios de seguimiento deben ser >= 0")
    
    if errores:
        raise ValueError("Errores en configuración:\n" + "\n".join(errores))
    
    return True

# Validar al importar
validar_configuracion()

# ==================== INFORMACIÓN DEL SISTEMA ====================

VERSION = "2.0.0"
AUTOR = "Equipo UNIETAXI"
FECHA_VERSION = "2024-12-10"

if __name__ == "__main__":
    print(MENSAJES["BIENVENIDA"])
    print(f"Versión: {VERSION}")
    print(f"Autor: {AUTOR}")
    print(f"\nDirectorios configurados:")
    print(f"  - Base: {BASE_DIR}")
    print(f"  - Datos: {DATA_DIR}")
    print(f"  - Reportes: {REPORTES_DIR}")
    print(f"\nArchivos JSON:")
    print(f"  - Clientes: {CLIENTES_JSON}")
    print(f"  - Taxis: {TAXIS_JSON}")
    print(f"  - Servicios: {SERVICIOS_JSON}")
    print(f"\n✅ Configuración validada correctamente")
