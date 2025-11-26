"""
exportador.py - Exportación de Datos para Visualización

Este módulo maneja la exportación de datos del sistema a formatos
adecuados para visualización en mapas y reportes.
"""

import json
import os
from datetime import datetime
from typing import List

import config
from models import Cliente, Taxi, Servicio

# ==================== EXPORTACIÓN A JSON ====================

def exportar_taxis_para_mapa(taxis: List[Taxi], archivo_salida: str = None) -> str:
    """
    Exporta los taxis a formato JSON para visualización en mapa.
    
    Args:
        taxis: Lista de taxis del sistema
        archivo_salida: Ruta del archivo de salida (opcional)
    
    Returns:
        Ruta del archivo generado
    """
    if archivo_salida is None:
        archivo_salida = config.TAXIS_JSON
    
    taxis_data = []
    for i, taxi in enumerate(taxis):
        taxi_dict = taxi.to_dict()
        
        # Agregar información adicional para el mapa
        taxi_dict.update({
            "taxi_id": f"taxi{i+1}",
            "color": config.COLORES_TAXIS[i % len(config.COLORES_TAXIS)]["color"],
            "icono": "🚕"
        })
        
        taxis_data.append(taxi_dict)
    
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(taxis_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Exportados {len(taxis_data)} taxis a {archivo_salida}")
    return archivo_salida


def exportar_clientes_para_mapa(clientes: List[Cliente], archivo_salida: str = None) -> str:
    """
    Exporta los clientes a formato JSON para visualización en mapa.
    
    Args:
        clientes: Lista de clientes del sistema
        archivo_salida: Ruta del archivo de salida (opcional)
    
    Returns:
        Ruta del archivo generado
    """
    if archivo_salida is None:
        archivo_salida = config.CLIENTES_JSON
    
    clientes_data = []
    for cliente in clientes:
        cliente_dict = cliente.to_dict()
        
        # Agregar información adicional para el mapa
        cliente_dict.update({
            "icono": "📍" if not cliente.en_servicio else "🚶",
            "visible_en_mapa": cliente.en_servicio
        })
        
        clientes_data.append(cliente_dict)
    
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(clientes_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Exportados {len(clientes_data)} clientes a {archivo_salida}")
    return archivo_salida


def exportar_servicios(servicios: List[Servicio], archivo_salida: str = None) -> str:
    """
    Exporta los servicios completados a JSON.
    
    Args:
        servicios: Lista de servicios del sistema
        archivo_salida: Ruta del archivo de salida (opcional)
    
    Returns:
        Ruta del archivo generado
    """
    if archivo_salida is None:
        archivo_salida = config.SERVICIOS_JSON
    
    servicios_data = [s.to_dict() for s in servicios]
    
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(servicios_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Exportados {len(servicios_data)} servicios a {archivo_salida}")
    return archivo_salida


def exportar_ubicaciones_tiempo_real(taxis: List[Taxi], clientes: List[Cliente], 
                                     servicios_activos: List[Servicio] = None,
                                     archivo_salida: str = None) -> str:
    """
    Exporta las ubicaciones actuales de taxis y clientes para actualización en tiempo real.
    
    Args:
        taxis: Lista de taxis
        clientes: Lista de clientes
        servicios_activos: Lista de servicios en curso (opcional)
        archivo_salida: Ruta del archivo de salida (opcional)
    
    Returns:
        Ruta del archivo generado
    """
    if archivo_salida is None:
        archivo_salida = config.UBICACIONES_TIEMPO_REAL
    
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "taxis": [],
        "clientes": [],
        "servicios_activos": []
    }
    
    # Exportar taxis
    for taxi in taxis:
        data["taxis"].append({
            "id_taxi": taxi.id_taxi,
            "placa": taxi.placa,
            "nombre": taxi.nombre_completo(),
            "ubicacion": taxi.ubicacion,
            "disponible": taxi.disponible,
            "cliente_actual": taxi.cliente_actual,
            "color": taxi.color_mapa
        })
    
    # Exportar clientes en servicio
    for cliente in clientes:
        if cliente.en_servicio:
            data["clientes"].append({
                "cedula": cliente.cedula,
                "nombre": cliente.nombre_completo(),
                "ubicacion_actual": cliente.ubicacion_actual,
                "destino": cliente.destino,
                "taxi_asignado": cliente.taxi_asignado
            })
    
    # Exportar servicios activos
    if servicios_activos:
        for servicio in servicios_activos:
            if not servicio.completado:
                data["servicios_activos"].append(servicio.to_dict())
    
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return archivo_salida


# ==================== GENERACIÓN DE REPORTES ====================

def generar_reporte_texto(sistema, tipo: str = "diario", dia: int = None) -> str:
    """
    Genera un reporte en formato texto.
    
    Args:
        sistema: Instancia del sistema central
        tipo: "diario" o "mensual"
        dia: Número de día (solo para reportes diarios)
    
    Returns:
        Ruta del archivo generado
    """
    if tipo == "diario" and dia is None:
        dia = sistema.dia_actual - 1
    
    # Crear nombre de archivo
    if tipo == "diario":
        archivo = config.crear_nombre_reporte_diario(dia)
    else:
        archivo = config.crear_nombre_reporte_mensual()
    
    with open(archivo, 'w', encoding='utf-8') as f:
        if tipo == "diario":
            _escribir_reporte_diario(f, sistema, dia)
        else:
            _escribir_reporte_mensual(f, sistema)
    
    print(f"✅ Reporte {tipo} generado: {archivo}")
    return archivo


def _escribir_reporte_diario(f, sistema, dia: int):
    """Escribe el contenido del reporte diario"""
    f.write("=" * 70 + "\n")
    f.write(f"REPORTE DIARIO - DÍA {dia}\n")
    f.write(f"Fecha: {config.obtener_fecha_legible()}\n")
    f.write("=" * 70 + "\n\n")
    
    f.write("SERVICIOS EN SEGUIMIENTO:\n")
    f.write("-" * 70 + "\n\n")
    
    servicios_dia = [s for s in sistema.servicios_completados if s.dia == dia and s.en_seguimiento]
    
    if servicios_dia:
        ganancia_total = 0
        for i, servicio in enumerate(servicios_dia, 1):
            f.write(f"{i}. Servicio #{servicio.id_servicio}\n")
            f.write(f"   Taxi ID: {servicio.id_taxi}\n")
            f.write(f"   Cliente ID: {servicio.id_cliente}\n")
            f.write(f"   Origen: ({servicio.origen[0]:.4f}, {servicio.origen[1]:.4f})\n")
            f.write(f"   Destino: ({servicio.destino[0]:.4f}, {servicio.destino[1]:.4f})\n")
            f.write(f"   Distancia: {servicio.distancia_km:.2f} km\n")
            f.write(f"   Costo: ${servicio.costo:.2f}\n")
            f.write(f"   Calificación: {servicio.calificacion}⭐\n")
            f.write(f"   Hora: {servicio.timestamp}\n")
            f.write("\n")
            ganancia_total += servicio.costo
        
        f.write("-" * 70 + "\n")
        f.write(f"GANANCIA TOTAL DEL DÍA: ${ganancia_total:.2f}\n")
    else:
        f.write("No hubo servicios en seguimiento este día.\n")
    
    f.write("\n" + "=" * 70 + "\n")


def _escribir_reporte_mensual(f, sistema):
    """Escribe el contenido del reporte mensual"""
    f.write("=" * 70 + "\n")
    f.write("REPORTE MENSUAL FINAL\n")
    f.write(f"Fecha: {config.obtener_fecha_legible()}\n")
    f.write("=" * 70 + "\n\n")
    
    f.write("DESEMPEÑO DE TAXISTAS:\n")
    f.write("-" * 70 + "\n\n")
    
    for taxi in sistema.taxis:
        if taxi.cantidad_servicios > 0:
            f.write(f"ID Taxista: {taxi.id_taxi} :: {taxi.nombre_completo()}\n")
            f.write(f"Placa: {taxi.placa} :: {taxi.marca} {taxi.modelo}\n")
            f.write(f"Total Generado: ${taxi.ganancia_total:.2f}\n")
            f.write(f"Comisión UNIETAXI (20%): ${taxi.calcular_comision_empresa():.2f}\n")
            f.write(f"Ganancia del Taxista (80%): ${taxi.calcular_ganancia_neta():.2f}\n")
            f.write(f"Servicios Realizados: {taxi.cantidad_servicios}\n")
            f.write(f"Calificación Promedio: {taxi.calcular_calificacion_promedio():.2f}⭐\n")
            f.write("-" * 70 + "\n\n")
    
    f.write("=" * 70 + "\n")
    f.write("RESUMEN GENERAL:\n")
    f.write("-" * 70 + "\n")
    f.write(f"Ganancia Total Empresa: ${sistema.ganancia_total_empresa:.2f}\n")
    f.write(f"Total Servicios Realizados: {len(sistema.servicios_completados)}\n")
    f.write(f"Total Taxis Activos: {len([t for t in sistema.taxis if t.cantidad_servicios > 0])}\n")
    f.write(f"Total Clientes Atendidos: {len(set(s.id_cliente for s in sistema.servicios_completados))}\n")
    f.write("=" * 70 + "\n")


# ==================== EXPORTACIÓN PARA MAPA HTML ====================

def preparar_datos_para_mapa_animado(taxis: List[Taxi]) -> dict:
    """
    Prepara los datos de taxis en el formato que espera el mapa animado.
    
    Args:
        taxis: Lista de taxis del sistema
    
    Returns:
        Diccionario con datos formateados para el mapa
    """
    taxi_taxista_map = {}
    
    for i, taxi in enumerate(taxis, 1):
        taxi_id = f"taxi{i}"
        taxi_taxista_map[taxi_id] = {
            "nombre": taxi.nombre_completo(),
            "identificacion": str(taxi.cedula),
            "placa": taxi.placa,
            "marca": taxi.marca,
            "modelo": taxi.modelo,
            "estado": "disponible" if taxi.disponible else "ocupado",
            "fecha_registro": taxi.fecha_registro,
            "ubicacion": list(taxi.ubicacion),
            "calificacion": round(taxi.calcular_calificacion_promedio(), 2),
            "servicios_realizados": taxi.cantidad_servicios
        }
    
    return taxi_taxista_map


def exportar_configuracion_mapa(taxis: List[Taxi], archivo_salida: str = None) -> str:
    """
    Exporta la configuración específica para el mapa animado.
    
    Args:
        taxis: Lista de taxis
        archivo_salida: Ruta del archivo de salida
    
    Returns:
        Ruta del archivo generado
    """
    if archivo_salida is None:
        archivo_salida = os.path.join(config.DATA_DIR, "config_mapa.json")
    
    config_mapa = {
        "centro": config.CENTRO_MADRID,
        "radio_busqueda_km": config.TAXI_CONFIG["RADIO_BUSQUEDA_KM"],
        "ruta_principal": config.RUTA_PRINCIPAL,
        "taxis": preparar_datos_para_mapa_animado(taxis),
        "colores": config.COLORES_TAXIS,
        "timestamp": config.obtener_fecha_legible()
    }
    
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(config_mapa, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Configuración del mapa exportada a {archivo_salida}")
    return archivo_salida


# ==================== ESTADÍSTICAS ====================

def generar_estadisticas(sistema) -> dict:
    """
    Genera estadísticas completas del sistema.
    
    Args:
        sistema: Instancia del sistema central
    
    Returns:
        Diccionario con estadísticas
    """
    stats = {
        "total_taxis": len(sistema.taxis),
        "total_clientes": len(sistema.clientes),
        "total_servicios": len(sistema.servicios_completados),
        "servicios_por_dia": {},
        "ganancia_total_empresa": round(sistema.ganancia_total_empresa, 2),
        "ganancia_promedio_por_servicio": 0,
        "calificacion_promedio_general": 0,
        "taxi_mejor_calificado": None,
        "taxi_mas_servicios": None,
        "taxi_mayor_ganancia": None,
        "taxis_activos": 0,
        "taxis_inactivos": 0,
        "clientes_atendidos": len(set(s.id_cliente for s in sistema.servicios_completados))
    }
    
    # Servicios por día
    for servicio in sistema.servicios_completados:
        dia = f"dia_{servicio.dia}"
        if dia not in stats["servicios_por_dia"]:
            stats["servicios_por_dia"][dia] = 0
        stats["servicios_por_dia"][dia] += 1
    
    # Ganancia promedio
    if sistema.servicios_completados:
        total_ganancias = sum(s.costo for s in sistema.servicios_completados)
        stats["ganancia_promedio_por_servicio"] = round(
            total_ganancias / len(sistema.servicios_completados), 2
        )
    
    # Estadísticas de taxis
    taxis_con_servicios = [t for t in sistema.taxis if t.cantidad_servicios > 0]
    stats["taxis_activos"] = len(taxis_con_servicios)
    stats["taxis_inactivos"] = len(sistema.taxis) - len(taxis_con_servicios)
    
    if taxis_con_servicios:
        # Calificación promedio general
        calificaciones = [t.calcular_calificacion_promedio() for t in taxis_con_servicios]
        stats["calificacion_promedio_general"] = round(sum(calificaciones) / len(calificaciones), 2)
        
        # Mejor calificado
        mejor_taxi = max(taxis_con_servicios, key=lambda t: t.calcular_calificacion_promedio())
        stats["taxi_mejor_calificado"] = {
            "id": mejor_taxi.id_taxi,
            "nombre": mejor_taxi.nombre_completo(),
            "placa": mejor_taxi.placa,
            "calificacion": round(mejor_taxi.calcular_calificacion_promedio(), 2)
        }
        
        # Más servicios
        mas_servicios = max(taxis_con_servicios, key=lambda t: t.cantidad_servicios)
        stats["taxi_mas_servicios"] = {
            "id": mas_servicios.id_taxi,
            "nombre": mas_servicios.nombre_completo(),
            "placa": mas_servicios.placa,
            "servicios": mas_servicios.cantidad_servicios
        }
        
        # Mayor ganancia
        mayor_ganancia = max(taxis_con_servicios, key=lambda t: t.ganancia_total)
        stats["taxi_mayor_ganancia"] = {
            "id": mayor_ganancia.id_taxi,
            "nombre": mayor_ganancia.nombre_completo(),
            "placa": mayor_ganancia.placa,
            "ganancia": round(mayor_ganancia.ganancia_total, 2)
        }
    
    return stats


def exportar_estadisticas(sistema, archivo_salida: str = None) -> str:
    """
    Exporta las estadísticas del sistema a JSON.
    
    Args:
        sistema: Instancia del sistema central
        archivo_salida: Ruta del archivo de salida
    
    Returns:
        Ruta del archivo generado
    """
    if archivo_salida is None:
        archivo_salida = os.path.join(config.DATA_DIR, "estadisticas.json")
    
    stats = generar_estadisticas(sistema)
    
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Estadísticas exportadas a {archivo_salida}")
    return archivo_salida


# ==================== FUNCIÓN PRINCIPAL ====================

def exportar_todo(sistema):
    """
    Exporta todos los datos del sistema.
    
    Args:
        sistema: Instancia del sistema central
    """
    print("\n📤 EXPORTANDO TODOS LOS DATOS...")
    print(config.MENSAJES["SEPARADOR_MENOR"])
    
    exportar_taxis_para_mapa(sistema.taxis)
    exportar_clientes_para_mapa(sistema.clientes)
    exportar_servicios(sistema.servicios_completados)
    exportar_configuracion_mapa(sistema.taxis)
    exportar_estadisticas(sistema)
    
    print(config.MENSAJES["SEPARADOR_MENOR"])
    print("✅ Todos los datos exportados correctamente\n")


if __name__ == "__main__":
    print("Este módulo debe ser importado desde main.py o sistema_central.py")
    print("No debe ejecutarse directamente.")