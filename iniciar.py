"""
iniciar.py - Script de Inicio Automático UNIETAXI

Este script configura e inicia automáticamente todo el sistema:
1. Verifica la instalación
2. Crea estructura de directorios
3. Genera datos de ejemplo si es necesario
4. Inicia la simulación web automáticamente

Uso:
    python iniciar.py
"""

import os
import sys
import json
import time
from datetime import datetime

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Imprime un encabezado con estilo"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"{text:^60}")
    print(f"{'='*60}{Colors.ENDC}\n")

def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_warning(text):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text):
    """Imprime mensaje de error"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text):
    """Imprime mensaje informativo"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.ENDC}")

# ==================== VERIFICACIÓN DEL SISTEMA ====================

def verificar_python():
    """Verifica la versión de Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print_error(f"Python 3.7+ requerido. Versión actual: {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro}")
    return True

def verificar_archivos():
    """Verifica que existan todos los archivos necesarios"""
    archivos_requeridos = [
        "config.py",
        "models.py",
        "sistema_central.py",
        "main.py",
        "simulacion_web.py",
        "exportador.py",
        "visualizacion_mapa.py",
        "registro_unificado.py",
        "reloj.py"
    ]
    
    print_info("Verificando archivos del sistema...")
    faltantes = []
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"   ✓ {archivo}")
        else:
            print(f"   ✗ {archivo} {Colors.FAIL}(FALTANTE){Colors.ENDC}")
            faltantes.append(archivo)
    
    if faltantes:
        print_error(f"Faltan {len(faltantes)} archivos")
        return False
    
    print_success("Todos los archivos presentes")
    return True

def crear_estructura_directorios():
    """Crea la estructura de directorios necesaria"""
    print_info("Creando estructura de directorios...")
    
    directorios = [
        "data",
        "data/reportes"
    ]
    
    for directorio in directorios:
        if not os.path.exists(directorio):
            os.makedirs(directorio)
            print(f"   📁 Creado: {directorio}")
        else:
            print(f"   ✓ Existe: {directorio}")
    
    print_success("Estructura de directorios lista")

# ==================== GENERACIÓN DE DATOS DE EJEMPLO ====================

def generar_clientes_ejemplo():
    """Genera clientes de ejemplo"""
    clientes = [
        {
            "nombre": "Juan Pérez García",
            "identificacion": "12345678A",
            "tarjeta": "4532123456789012",
            "tarjeta_enmascarada": "**** **** **** 9012",
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "activo"
        },
        {
            "nombre": "María López Sánchez",
            "identificacion": "87654321B",
            "tarjeta": "4532123456789013",
            "tarjeta_enmascarada": "**** **** **** 9013",
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "activo"
        },
        {
            "nombre": "Pedro Martínez Ruiz",
            "identificacion": "11223344C",
            "tarjeta": "4532123456789014",
            "tarjeta_enmascarada": "**** **** **** 9014",
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "activo"
        },
        {
            "nombre": "Laura Fernández Torres",
            "identificacion": "55667788D",
            "tarjeta": "4532123456789015",
            "tarjeta_enmascarada": "**** **** **** 9015",
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "activo"
        },
        {
            "nombre": "Carlos Gómez Díaz",
            "identificacion": "99887766E",
            "tarjeta": "4532123456789016",
            "tarjeta_enmascarada": "**** **** **** 9016",
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "activo"
        },
        {
            "nombre": "Ana Rodríguez Castro",
            "identificacion": "44556677F",
            "tarjeta": "4532123456789017",
            "tarjeta_enmascarada": "**** **** **** 9017",
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "activo"
        },
        {
            "nombre": "David Jiménez Moreno",
            "identificacion": "33445566G",
            "tarjeta": "4532123456789018",
            "tarjeta_enmascarada": "**** **** **** 9018",
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "activo"
        },
        {
            "nombre": "Isabel Navarro Herrera",
            "identificacion": "22334455H",
            "tarjeta": "4532123456789019",
            "tarjeta_enmascarada": "**** **** **** 9019",
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "activo"
        }
    ]
    
    archivo = "data/clientes_registrados.json"
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(clientes, f, indent=2, ensure_ascii=False)
    
    print_success(f"Generados {len(clientes)} clientes de ejemplo")
    return len(clientes)

def generar_taxis_ejemplo():
    """Genera taxis de ejemplo"""
    taxis = [
        {
            "nombre": "Carlos Ramírez López",
            "identificacion": "11111111A",
            "licencia": "Vigente",
            "antecedentes": "Al día",
            "certificado_medico": "Vigente",
            "infracciones": "Al día",
            "placa": "ABC123",
            "seguro": "Vigente",
            "impuestos": "Al día",
            "placa_estado": "Bueno",
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "activo"
        },
        {
            "nombre": "Lucía Fernández García",
            "identificacion": "22222222B",
            "licencia": "Vigente",
            "antecedentes": "Al día",
            "certificado_medico": "Vigente",
            "infracciones": "Al día",
            "placa": "XYZ789",
            "seguro": "Vigente",
            "impuestos": "Al día",
            "placa_estado": "Bueno",
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "activo"
        },
        {
            "nombre": "Juan Pérez Martín",
            "identificacion": "33333333C",
            "licencia": "Vigente",
            "antecedentes": "Al día",
            "certificado_medico": "Vigente",
            "infracciones": "Al día",
            "placa": "DEF456",
            "seguro": "Vigente",
            "impuestos": "Al día",
            "placa_estado": "Bueno",
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "activo"
        },
        {
            "nombre": "Miguel Torres Sánchez",
            "identificacion": "44444444D",
            "licencia": "Vigente",
            "antecedentes": "Al día",
            "certificado_medico": "Vigente",
            "infracciones": "Al día",
            "placa": "GHI789",
            "seguro": "Vigente",
            "impuestos": "Al día",
            "placa_estado": "Bueno",
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "activo"
        },
        {
            "nombre": "María López Ruiz",
            "identificacion": "55555555E",
            "licencia": "Vigente",
            "antecedentes": "Al día",
            "certificado_medico": "Vigente",
            "infracciones": "Al día",
            "placa": "JKL012",
            "seguro": "Vigente",
            "impuestos": "Al día",
            "placa_estado": "Bueno",
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "activo"
        }
    ]
    
    archivo = "data/taxis_registrados.json"
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(taxis, f, indent=2, ensure_ascii=False)
    
    print_success(f"Generados {len(taxis)} taxis de ejemplo")
    return len(taxis)

def verificar_o_generar_datos():
    """Verifica si existen datos o los genera"""
    print_info("Verificando datos de usuarios...")
    
    clientes_file = "data/clientes_registrados.json"
    taxis_file = "data/taxis_registrados.json"
    
    clientes_existen = os.path.exists(clientes_file)
    taxis_existen = os.path.exists(taxis_file)
    
    if clientes_existen and taxis_existen:
        print_success("Datos de usuarios encontrados")
        
        # Contar registros
        with open(clientes_file, 'r', encoding='utf-8') as f:
            clientes = json.load(f)
        with open(taxis_file, 'r', encoding='utf-8') as f:
            taxis = json.load(f)
        
        print(f"   📊 {len(clientes)} clientes registrados")
        print(f"   📊 {len(taxis)} taxis registrados")
        
        return True
    else:
        print_warning("No se encontraron datos de usuarios")
        print("\n¿Deseas generar datos de ejemplo?")
        print("   [1] Sí, generar datos de ejemplo")
        print("   [2] No, abrir registro manual")
        print("   [3] Cancelar")
        
        opcion = input("\nSelecciona una opción (1-3): ").strip()
        
        if opcion == "1":
            print_info("\nGenerando datos de ejemplo...")
            generar_clientes_ejemplo()
            generar_taxis_ejemplo()
            return True
        elif opcion == "2":
            print_info("Abriendo registro manual...")
            os.system("python registro_unificado.py")
            return verificar_o_generar_datos()  # Volver a verificar
        else:
            print_warning("Cancelado por el usuario")
            return False

# ==================== MENÚ PRINCIPAL ====================

def mostrar_menu():
    """Muestra el menú principal"""
    print_header("MENÚ PRINCIPAL")
    
    print(f"{Colors.BOLD}¿Qué deseas hacer?{Colors.ENDC}\n")
    print(f"{Colors.CYAN}[1]{Colors.ENDC} 🌐 Iniciar Simulación Web (Recomendado)")
    print(f"{Colors.CYAN}[2]{Colors.ENDC} 💻 Iniciar Simulación en Terminal")
    print(f"{Colors.CYAN}[3]{Colors.ENDC} 📝 Abrir Registro de Usuarios")
    print(f"{Colors.CYAN}[4]{Colors.ENDC} 🗺️  Generar Mapa Animado")
    print(f"{Colors.CYAN}[5]{Colors.ENDC} 🧪 Ejecutar Pruebas del Sistema")
    print(f"{Colors.CYAN}[6]{Colors.ENDC} ⏰ Ver Reloj Acelerado")
    print(f"{Colors.CYAN}[7]{Colors.ENDC} 📊 Ver Estadísticas")
    print(f"{Colors.CYAN}[0]{Colors.ENDC} ❌ Salir")
    
    return input(f"\n{Colors.BOLD}Selecciona una opción (0-7): {Colors.ENDC}").strip()

def ejecutar_opcion(opcion):
    """Ejecuta la opción seleccionada"""
    
    if opcion == "1":
        print_info("Iniciando simulación web...")
        dias = input("¿Cuántos días deseas simular? (Enter = 2): ").strip()
        if dias and dias.isdigit():
            os.system(f"python main.py --dias {dias}")
        else:
            os.system("python main.py")
    
    elif opcion == "2":
        print_info("Iniciando simulación en terminal...")
        dias = input("¿Cuántos días deseas simular? (Enter = 2): ").strip()
        if dias and dias.isdigit():
            os.system(f"python main.py --terminal --dias {dias}")
        else:
            os.system("python main.py --terminal")
    
    elif opcion == "3":
        print_info("Abriendo registro de usuarios...")
        os.system("python registro_unificado.py")
    
    elif opcion == "4":
        print_info("Generando mapa animado...")
        os.system("python visualizacion_mapa.py")
    
    elif opcion == "5":
        print_info("Ejecutando pruebas...")
        os.system("python test_sistema.py")
    
    elif opcion == "6":
        print_info("Abriendo reloj acelerado...")
        os.system("python reloj.py")
    
    elif opcion == "7":
        print_info("Mostrando estadísticas...")
        mostrar_estadisticas()
    
    elif opcion == "0":
        print_success("¡Hasta luego!")
        return False
    
    else:
        print_error("Opción inválida")
    
    input(f"\n{Colors.BOLD}Presiona ENTER para continuar...{Colors.ENDC}")
    return True

def mostrar_estadisticas():
    """Muestra estadísticas del sistema"""
    archivo_stats = "data/estadisticas.json"
    
    if not os.path.exists(archivo_stats):
        print_warning("No hay estadísticas disponibles")
        print_info("Ejecuta primero una simulación")
        return
    
    with open(archivo_stats, 'r', encoding='utf-8') as f:
        stats = json.load(f)
    
    print_header("ESTADÍSTICAS DEL SISTEMA")
    
    print(f"{Colors.BOLD}General:{Colors.ENDC}")
    print(f"   Total Taxis: {stats['total_taxis']}")
    print(f"   Total Clientes: {stats['total_clientes']}")
    print(f"   Total Servicios: {stats['total_servicios']}")
    print(f"   Ganancia Empresa: ${stats['ganancia_total_empresa']:.2f}")
    
    if stats.get('taxi_mejor_calificado'):
        print(f"\n{Colors.BOLD}Mejor Taxista:{Colors.ENDC}")
        mejor = stats['taxi_mejor_calificado']
        print(f"   {mejor['nombre']} ({mejor['placa']})")
        print(f"   ⭐ Calificación: {mejor['calificacion']:.2f}")
    
    if stats.get('taxi_mas_servicios'):
        print(f"\n{Colors.BOLD}Más Activo:{Colors.ENDC}")
        activo = stats['taxi_mas_servicios']
        print(f"   {activo['nombre']} ({activo['placa']})")
        print(f"   📊 Servicios: {activo['servicios']}")

# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """Función principal del script de inicio"""
    
    # Banner
    print(f"""
{Colors.HEADER}{Colors.BOLD}
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║                   🚖 SISTEMA UNIETAXI                     ║
║              Script de Inicio Automático                   ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
{Colors.ENDC}""")
    
    print(f"{Colors.CYAN}Versión: 2.0.0")
    print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{Colors.ENDC}")
    
    # Verificaciones
    print_header("VERIFICACIÓN DEL SISTEMA")
    
    if not verificar_python():
        return
    
    if not verificar_archivos():
        print_error("Sistema incompleto. Verifica que tengas todos los archivos.")
        return
    
    crear_estructura_directorios()
    
    if not verificar_o_generar_datos():
        return
    
    # Menú principal
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"""
{Colors.HEADER}{Colors.BOLD}
╔════════════════════════════════════════════════════════════╗
║                   🚖 SISTEMA UNIETAXI                     ║
╚════════════════════════════════════════════════════════════╝
{Colors.ENDC}""")
        
        opcion = mostrar_menu()
        
        if not ejecutar_opcion(opcion):
            break
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}¡Gracias por usar UNIETAXI!{Colors.ENDC}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Programa interrumpido por el usuario{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)