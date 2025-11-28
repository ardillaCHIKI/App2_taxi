"""
main.py - Orquestador Principal del Sistema UNIETAXI

Este archivo inicia automáticamente:
1. Carga de datos desde JSON
2. Simulación web en tiempo real
3. Visualización en navegador
4. Generación de reportes

Uso:
    python main.py              # Modo web (por defecto)
    python main.py --terminal   # Modo terminal
    python main.py --dias 3     # Especificar días
"""

import sys
import os
import threading
import time
import webbrowser

import config
from simulacion_web import iniciar_simulacion_web, SistemaCentralWeb, SimulacionWebGenerator
from sistema_central import cargar_clientes_desde_json, cargar_taxis_desde_json

# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """
    Función principal que inicia el sistema UNIETAXI.
    Por defecto, inicia la simulación web.
    """
    
    # Analizar argumentos
    modo_terminal = "--terminal" in sys.argv
    num_dias = config.SIMULACION["DIAS_POR_DEFECTO"]
    
    # Buscar argumento de días
    for i, arg in enumerate(sys.argv):
        if arg == "--dias" and i + 1 < len(sys.argv):
            try:
                num_dias = int(sys.argv[i + 1])
            except ValueError:
                print(f"⚠️ Valor inválido para días: {sys.argv[i + 1]}")
    
    # Mostrar banner
    print(config.MENSAJES["BIENVENIDA"])
    print(f"Versión: {config.VERSION}")
    print(f"Fecha: {config.obtener_fecha_legible()}")
    print(config.MENSAJES["SEPARADOR"])
    
    print(f"\n🎮 MODO: {'Terminal' if modo_terminal else 'Web Interactivo'}")
    print(f"📅 Días a simular: {num_dias}")
    print(config.MENSAJES["SEPARADOR"])
    
    # Verificar datos
    verificar_y_preparar_datos()
    
    if modo_terminal:
        # Modo terminal (antiguo)
        iniciar_modo_terminal(num_dias)
    else:
        # Modo web (por defecto)
        iniciar_modo_web(num_dias)


def verificar_y_preparar_datos():
    """Verifica que existan datos o crea ejemplos"""
    
    print("\n📂 VERIFICANDO DATOS...\n")
    
    # Verificar clientes
    clientes_existen = os.path.exists(config.CLIENTES_JSON)
    taxis_existen = os.path.exists(config.TAXIS_JSON)
    
    if not clientes_existen or not taxis_existen:
        print("⚠️ No se encontraron datos registrados")
        print("\n💡 OPCIONES:")
        print("   1. Ejecuta 'python registro_unificado.py' para registrar usuarios")
        print("   2. El sistema usará datos de ejemplo automáticamente")
        print()
        
        respuesta = input("¿Deseas continuar con datos de ejemplo? (S/n): ").strip().lower()
        if respuesta and respuesta != 's' and respuesta != 'si':
            print("\n❌ Ejecuta primero: python registro_unificado.py")
            sys.exit(0)
    else:
        print("✅ Datos encontrados:")
        if clientes_existen:
            print(f"   - {config.CLIENTES_JSON}")
        if taxis_existen:
            print(f"   - {config.TAXIS_JSON}")


def iniciar_modo_web(num_dias: int):
    """Inicia el modo web interactivo"""
    
    print("\n" + "="*60)
    print("🌐 INICIANDO SIMULACIÓN WEB EN TIEMPO REAL")
    print("="*60)
    
    print("\n📋 CARACTERÍSTICAS:")
    print("   ✅ Mapa interactivo de Madrid")
    print("   ✅ Taxis moviéndose en tiempo real")
    print("   ✅ Eventos y estadísticas actualizadas")
    print("   ✅ Visualización de rutas y asignaciones")
    print("   ✅ Panel de control y monitoreo")
    
    print("\n⏳ Preparando simulación...")
    
    try:
        # Iniciar simulación web
        iniciar_simulacion_web(num_dias)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Simulación interrumpida por el usuario")
        print("✅ Datos guardados correctamente")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n" + "="*60)
        print("SIMULACIÓN FINALIZADA")
        print("="*60)
        mostrar_archivos_generados()


def iniciar_modo_terminal(num_dias: int):
    """Inicia el modo terminal (antiguo)"""
    
    print("\n" + "="*60)
    print("💻 MODO TERMINAL")
    print("="*60)
    
    from sistema_central import SistemaCentral
    from main import hilo_cliente, hilo_sistema_principal
    
    # Crear sistema
    sistema = SistemaCentral(num_dias=num_dias)
    
    # Cargar datos
    num_taxis = cargar_taxis_desde_json(sistema)
    num_clientes = cargar_clientes_desde_json(sistema)
    
    # Si no hay datos, usar ejemplos
    if num_taxis == 0:
        print("\n⚠️ Usando taxis de ejemplo...")
        for i in range(5):
            sistema.afiliar_taxi(
                100000 + i, f"Taxi{i+1}", "Driver", f"TX{i+1:03d}",
                "Toyota", "Corolla", 60
            )
    
    if num_clientes == 0:
        print("\n⚠️ Usando clientes de ejemplo...")
        for i in range(8):
            sistema.afiliar_cliente(
                200000 + i, f"Cliente{i+1}", "Test", "4532123456789012"
            )
    
    print(f"\n✅ Sistema listo:")
    print(f"   🚖 Taxis: {len(sistema.taxis)}")
    print(f"   🧍 Clientes: {len(sistema.clientes)}")
    
    # Confirmar inicio
    input("\n🎬 Presiona ENTER para iniciar...")
    
    print("\n🚀 INICIANDO SIMULACIÓN...\n")
    
    # Iniciar hilos
    hilo_sistema = threading.Thread(target=hilo_sistema_principal, args=(sistema,))
    hilo_sistema.start()
    
    # Crear hilos de clientes
    time.sleep(0.5)
    hilos_clientes = []
    for cliente in sistema.clientes[:10]:
        import random
        num_solicitudes = random.randint(1, 2)
        hilo = threading.Thread(target=hilo_cliente, args=(sistema, cliente, num_solicitudes))
        hilos_clientes.append(hilo)
        hilo.start()
        time.sleep(0.1)
    
    # Esperar finalización
    for hilo in hilos_clientes:
        hilo.join()
    
    hilo_sistema.join()
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN FINAL")
    print("="*60)
    print(f"✅ Servicios realizados: {len(sistema.servicios_completados)}")
    print(f"💰 Ganancia empresa: ${sistema.ganancia_total_empresa:.2f}")
    print(f"🚖 Taxis activos: {len([t for t in sistema.taxis if t.cantidad_servicios > 0])}")
    print("="*60)
    
    mostrar_archivos_generados()


def mostrar_archivos_generados():
    """Muestra los archivos generados por la simulación"""
    
    print("\n📁 ARCHIVOS GENERADOS:")
    
    archivos = [
        ("Servicios completados", config.SERVICIOS_JSON),
        ("Ubicaciones tiempo real", config.UBICACIONES_TIEMPO_REAL),
        ("Simulación web", os.path.join(config.BASE_DIR, "simulacion_tiempo_real.html")),
        ("Mapa animado", config.MAPA_HTML),
        ("Estadísticas", os.path.join(config.DATA_DIR, "estadisticas.json")),
        ("Reportes", config.REPORTES_DIR)
    ]
    
    for nombre, ruta in archivos:
        if os.path.exists(ruta):
            print(f"   ✅ {nombre}: {ruta}")
        else:
            print(f"   ⚠️  {nombre}: No generado")
    
    print("\n💡 PRÓXIMOS PASOS:")
    print("   1. Abre 'simulacion_tiempo_real.html' para ver la simulación")
    print("   2. Ejecuta 'python visualizacion_mapa.py' para el mapa animado")
    print("   3. Ejecuta 'python test_sistema.py' para verificar el sistema")
    print("   4. Revisa la carpeta 'data/reportes/' para ver informes detallados")


def mostrar_ayuda():
    """Muestra la ayuda del sistema"""
    
    print("""
╔════════════════════════════════════════════════════════════╗
║                  UNIETAXI - SISTEMA DE AYUDA               ║
╚════════════════════════════════════════════════════════════╝

USO:
    python main.py                    # Modo web (por defecto)
    python main.py --terminal         # Modo terminal
    python main.py --dias 3           # Simular 3 días
    python main.py --help             # Mostrar esta ayuda

MODOS:

    🌐 Modo Web (Recomendado)
       - Visualización en tiempo real en navegador
       - Mapa interactivo con taxis moviéndose
       - Estadísticas y eventos actualizados
       - Interfaz gráfica intuitiva
    
    💻 Modo Terminal
       - Salida en consola
       - Útil para debugging
       - Más rápido para pruebas

EJEMPLOS:

    # Simulación web de 5 días
    python main.py --dias 5
    
    # Modo terminal con 2 días
    python main.py --terminal --dias 2

ARCHIVOS NECESARIOS:

    📂 data/clientes_registrados.json
    📂 data/taxis_registrados.json
    
    Si no existen, ejecuta primero:
    python registro_unificado.py

OTROS COMANDOS:

    python registro_unificado.py      # Registrar usuarios
    python visualizacion_mapa.py      # Generar mapa animado
    python test_sistema.py            # Ejecutar pruebas
    python reloj.py                   # Ver reloj acelerado

Para más información, revisa README.md
""")


# ==================== PUNTO DE ENTRADA ====================

if __name__ == "__main__":
    # Verificar ayuda
    if "--help" in sys.argv or "-h" in sys.argv:
        mostrar_ayuda()
        sys.exit(0)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Programa interrumpido por el usuario")
        print("✅ Datos guardados correctamente")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)