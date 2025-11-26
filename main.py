"""
main.py - Orquestador Principal del Sistema UNIETAXI

Este archivo coordina todos los componentes del sistema:
- Carga datos desde JSON
- Inicia hilos de clientes y sistema
- Gestiona el flujo de días
- Exporta datos para visualización
"""

import threading
import time
import random
import sys

import config
from models import Cliente, Taxi
from sistema_central import SistemaCentral, cargar_clientes_desde_json, cargar_taxis_desde_json

# ==================== HILOS ====================

def hilo_cliente(sistema: SistemaCentral, cliente: Cliente, num_solicitudes: int = 1):
    """
    Hilo que simula el comportamiento de un cliente.
    
    Flujo:
    1. Verifica si el sistema está activo
    2. Activa un servicio
    3. Genera ubicación y destino aleatorios
    4. Solicita taxi
    5. Si obtiene taxi, realiza el servicio
    6. Desactiva el servicio
    
    Args:
        sistema: Instancia del sistema central
        cliente: Cliente que realiza las solicitudes
        num_solicitudes: Número de solicitudes a realizar
    """
    for i in range(num_solicitudes):
        # Verificar si el sistema sigue activo
        if sistema.fin_sistema:
            break
        
        # Activar servicio
        if not sistema.activar_servicio():
            print(f"⚠️ {cliente}: Sistema cerrado, no se puede solicitar taxi")
            break
        
        try:
            # Generar ubicación y destino aleatorios dentro de Madrid
            # Rango: cerca del centro de Madrid
            cliente.ubicacion_actual = (
                random.uniform(40.39, 40.45),  # Latitud Madrid
                random.uniform(-3.75, -3.65)   # Longitud Madrid
            )
            cliente.destino = (
                random.uniform(40.39, 40.45),
                random.uniform(-3.75, -3.65)
            )
            cliente.en_servicio = True
            
            print(f"\n📱 {cliente} solicita taxi")
            print(f"   Ubicación: ({cliente.ubicacion_actual[0]:.4f}, {cliente.ubicacion_actual[1]:.4f})")
            print(f"   Destino: ({cliente.destino[0]:.4f}, {cliente.destino[1]:.4f})")
            
            # Buscar y asignar taxi
            taxi = sistema.asignar_taxi(cliente)
            
            if taxi:
                # Realizar el servicio
                sistema.realizar_servicio(cliente, taxi)
            else:
                print(f"⚠️ {cliente}: No se pudo asignar taxi")
                cliente.en_servicio = False
            
            # Pequeña pausa entre solicitudes
            delay = random.uniform(*config.SIMULACION["DELAY_ENTRE_SOLICITUDES"])
            time.sleep(delay)
            
        finally:
            # Desactivar servicio
            sistema.desactivar_servicio()


def hilo_sistema_principal(sistema: SistemaCentral):
    """
    Hilo principal que controla el flujo de días del sistema.
    
    Flujo:
    1. Inicia un nuevo día
    2. Espera la duración del día
    3. Finaliza el día (genera reportes y cierre contable)
    4. Repite para cada día configurado
    5. Genera reporte final mensual
    
    Args:
        sistema: Instancia del sistema central
    """
    for dia in range(sistema.num_dias):
        sistema.iniciar_nuevo_dia()
        
        # Simular duración del día
        time.sleep(config.SIMULACION["TIEMPO_SIMULACION_DIA"])
        
        sistema.finalizar_dia()
    
    # Marcar fin del sistema
    sistema.fin_sistema = True
    
    # Generar reporte final
    print(f"\n\n{'#'*60}")
    print(f"🏁 FIN DE SIMULACIÓN")
    print(f"{'#'*60}")
    sistema.generar_reporte_mensual()
    
    # Exportar datos finales
    sistema.exportar_datos_json()


# ==================== FUNCIONES DE INICIALIZACIÓN ====================

def cargar_datos_o_ejemplos(sistema: SistemaCentral):
    """
    Carga datos desde JSON o usa ejemplos si no hay datos.
    
    Args:
        sistema: Instancia del sistema central
    """
    print("\n📂 CARGANDO DATOS...\n")
    
    # Cargar taxis
    num_taxis = cargar_taxis_desde_json(sistema)
    
    # Si no hay taxis, usar ejemplos
    if num_taxis == 0:
        print("⚠️ No hay taxis en JSON, usando datos de ejemplo...\n")
        ejemplos_taxis = [
            (111111, "Carlos", "Rodríguez", "ABC123", "Toyota", "Corolla", 60),
            (222222, "María", "González", "XYZ789", "Honda", "Civic", 55),
            (333333, "José", "Martínez", "DEF456", "Nissan", "Sentra", 65),
            (444444, "Ana", "López", "GHI789", "Chevrolet", "Cruze", 58),
            (555555, "Luis", "Pérez", "JKL012", "Ford", "Focus", 62)
        ]
        
        for taxi_data in ejemplos_taxis:
            sistema.afiliar_taxi(*taxi_data)
        print()
    
    # Cargar clientes
    num_clientes = cargar_clientes_desde_json(sistema)
    
    # Si no hay clientes, usar ejemplos
    if num_clientes == 0:
        print("⚠️ No hay clientes en JSON, usando datos de ejemplo...\n")
        ejemplos_clientes = [
            (10001, "Juan", "Ramírez", "4532123456789012"),
            (10002, "Pedro", "Silva", "4532123456789013"),
            (10003, "Laura", "Torres", "4532123456789014"),
            (10004, "Sofia", "Méndez", "4532123456789015"),
            (10005, "Diego", "Castro", "4532123456789016"),
            (10006, "Carmen", "Ruiz", "4532123456789017"),
            (10007, "Miguel", "Flores", "4532123456789018"),
            (10008, "Isabel", "Vargas", "4532123456789019")
        ]
        
        for cliente_data in ejemplos_clientes:
            sistema.afiliar_cliente(*cliente_data)
        print()


def crear_hilos_clientes(sistema: SistemaCentral):
    """
    Crea e inicia los hilos de clientes.
    
    Args:
        sistema: Instancia del sistema central
    
    Returns:
        Lista de hilos creados
    """
    hilos_clientes = []
    
    # Limitar el número de clientes activos
    clientes_activos = sistema.clientes[:config.SIMULACION["CLIENTES_ACTIVOS_MAX"]]
    
    print(f"\n🚀 INICIANDO {len(clientes_activos)} CLIENTES...\n")
    
    for cliente in clientes_activos:
        # Cada cliente hará entre 1 y 3 solicitudes
        num_solicitudes = random.randint(*config.SIMULACION["SOLICITUDES_POR_CLIENTE"])
        
        hilo = threading.Thread(
            target=hilo_cliente,
            args=(sistema, cliente, num_solicitudes),
            name=f"Cliente-{cliente.cedula}"
        )
        hilos_clientes.append(hilo)
        hilo.start()
        
        # Pequeño delay entre inicios para escalonar solicitudes
        time.sleep(0.05)
    
    return hilos_clientes


# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """
    Función principal del sistema UNIETAXI.
    
    Flujo:
    1. Muestra mensaje de bienvenida
    2. Crea el sistema central
    3. Carga datos desde JSON o usa ejemplos
    4. Inicia hilo principal del sistema
    5. Crea e inicia hilos de clientes
    6. Espera a que terminen todos los hilos
    7. Muestra resumen final
    """
    
    # Mensaje de bienvenida
    print(config.MENSAJES["BIENVENIDA"])
    print(f"Versión: {config.VERSION}")
    print(f"Fecha: {config.obtener_fecha_legible()}")
    print(config.MENSAJES["SEPARADOR"])
    
    # Crear sistema central
    num_dias = config.SIMULACION["DIAS_POR_DEFECTO"]
    
    # Permitir configurar días por línea de comandos
    if len(sys.argv) > 1:
        try:
            num_dias = int(sys.argv[1])
            print(f"📅 Días configurados: {num_dias}")
        except ValueError:
            print(f"⚠️ Argumento inválido, usando {num_dias} días por defecto")
    
    sistema = SistemaCentral(num_dias=num_dias)
    
    # Cargar datos
    cargar_datos_o_ejemplos(sistema)
    
    # Verificar que hay datos suficientes
    if len(sistema.taxis) == 0:
        print("❌ ERROR: No hay taxis registrados en el sistema")
        return
    
    if len(sistema.clientes) == 0:
        print("❌ ERROR: No hay clientes registrados en el sistema")
        return
    
    print(f"📊 SISTEMA LISTO:")
    print(f"   🚖 Taxis disponibles: {len(sistema.taxis)}")
    print(f"   🧍 Clientes registrados: {len(sistema.clientes)}")
    print(f"   📅 Días a simular: {num_dias}")
    print(f"   ⏱️  Duración por día: {config.SIMULACION['TIEMPO_SIMULACION_DIA']} segundos reales")
    print()
    
    # Confirmar inicio
    print("🎬 Presiona ENTER para iniciar la simulación o CTRL+C para cancelar...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\n❌ Simulación cancelada por el usuario")
        return
    
    print("\n" + "="*60)
    print("🚀 INICIANDO SIMULACIÓN UNIETAXI")
    print("="*60 + "\n")
    
    # Iniciar hilo principal del sistema
    hilo_sistema = threading.Thread(
        target=hilo_sistema_principal,
        args=(sistema,),
        name="Sistema-Principal"
    )
    hilo_sistema.start()
    
    # Crear e iniciar hilos de clientes
    hilos_clientes = crear_hilos_clientes(sistema)
    
    # Esperar a que terminen todos los hilos de clientes
    print("\n⏳ Esperando finalización de servicios...\n")
    for hilo in hilos_clientes:
        hilo.join()
    
    print("✅ Todos los clientes finalizaron sus solicitudes")
    
    # Esperar al hilo principal
    hilo_sistema.join()
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN FINAL DE LA SIMULACIÓN")
    print("="*60)
    print(f"✅ Sistema UNIETAXI finalizado correctamente")
    print(f"📈 Total de servicios realizados: {len(sistema.servicios_completados)}")
    print(f"💰 Ganancia total de la empresa: ${sistema.ganancia_total_empresa:.2f}")
    print(f"🚖 Taxis que trabajaron: {len([t for t in sistema.taxis if t.cantidad_servicios > 0])}/{len(sistema.taxis)}")
    print(f"🧍 Clientes atendidos: {len(set(s.id_cliente for s in sistema.servicios_completados))}/{len(sistema.clientes)}")
    
    # Estadísticas de calificaciones
    if sistema.taxis:
        calificaciones = [t.calcular_calificacion_promedio() for t in sistema.taxis if t.cantidad_servicios > 0]
        if calificaciones:
            print(f"⭐ Calificación promedio general: {sum(calificaciones)/len(calificaciones):.2f}")
    
    print("="*60)
    
    # Información de archivos generados
    print("\n📁 ARCHIVOS GENERADOS:")
    print(f"   - {config.SERVICIOS_JSON}")
    print(f"   - {config.UBICACIONES_TIEMPO_REAL}")
    print(f"   - Reportes en: {config.REPORTES_DIR}")
    
    print("\n💡 PRÓXIMOS PASOS:")
    print("   1. Ejecuta 'python visualizacion_mapa.py' para ver el mapa animado")
    print("   2. Ejecuta 'python reloj.py' para ver el reloj acelerado")
    print("   3. Ejecuta 'python registro_unificado.py' para registrar más usuarios")
    
    print("\n🎉 ¡Gracias por usar UNIETAXI!")


# ==================== MODO RÁPIDO ====================

def modo_rapido():
    """
    Modo rápido sin confirmación, útil para pruebas automatizadas.
    """
    print(config.MENSAJES["BIENVENIDA"])
    print("⚡ MODO RÁPIDO ACTIVADO\n")
    
    sistema = SistemaCentral(num_dias=1)
    cargar_datos_o_ejemplos(sistema)
    
    if len(sistema.taxis) == 0 or len(sistema.clientes) == 0:
        print("❌ ERROR: Datos insuficientes")
        return
    
    # Iniciar simulación sin confirmación
    hilo_sistema = threading.Thread(target=hilo_sistema_principal, args=(sistema,))
    hilo_sistema.start()
    
    # Solo 5 clientes en modo rápido
    hilos_clientes = []
    for cliente in sistema.clientes[:5]:
        hilo = threading.Thread(target=hilo_cliente, args=(sistema, cliente, 1))
        hilos_clientes.append(hilo)
        hilo.start()
    
    for hilo in hilos_clientes:
        hilo.join()
    
    hilo_sistema.join()
    
    print(f"\n✅ Simulación rápida completada: {len(sistema.servicios_completados)} servicios")


# ==================== PUNTO DE ENTRADA ====================

if __name__ == "__main__":
    try:
        # Si se pasa --rapido como argumento, usar modo rápido
        if len(sys.argv) > 1 and sys.argv[1] == "--rapido":
            modo_rapido()
        else:
            main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Simulación interrumpida por el usuario")
        print("❌ Finalizando...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)