# App2_taxi
📋 Tabla de Contenidos

Características
Arquitectura
Requisitos
Instalación
Uso
Estructura del Proyecto
Sincronización y Recursos Críticos
Casos de Prueba
Configuración
API y Módulos
Contribución
Licencia


✨ Características
🎯 Funcionalidades Principales

Sistema de matching inteligente: Asignación automática del taxi más cercano basado en distancia euclidiana
Desempate por calificación: Cuando múltiples taxis están a la misma distancia, se elige el mejor calificado
Simulación multi-día: Soporte para simular operaciones durante múltiples días
Sincronización robusta: 8 semáforos binarios protegen recursos críticos
Visualización en tiempo real: Interfaz web con actualización dinámica de servicios
Sistema de calificaciones: Rating de 1 a 5 estrellas para conductores
Reportes automáticos: Generación de reportes diarios y mensuales
Gestión de comisiones: Cálculo automático del 20% para UNIETAXI y 80% para taxistas

🔒 Recursos Críticos Protegidos

Lista de Taxis (mutex_taxis)
Lista de Clientes (mutex_clientes)
Función Match (mutex_match) - Sección crítica más importante
Control de Fin del Día (mutex_fin_del_dia)
Servicios de Seguimiento (mutex_servicios_seguimiento)
Servicios Completados (mutex_servicios_completados)
Cola de Solicitudes (mutex_solicitudes)
Afiliaciones (mutex_afiliacion)


🏗️ Arquitectura
┌─────────────────────────────────────────────────────────────┐
│                     SISTEMA UNIETAXI                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐  │
│  │   Cliente 1   │   │   Cliente 2   │   │   Cliente N   │  │
│  │   (Hilo)     │   │   (Hilo)     │   │   (Hilo)     │  │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘  │
│         │                   │                   │          │
│         └───────────────────┼───────────────────┘          │
│                             │                               │
│                    ┌────────▼────────┐                     │
│                    │ Sistema Central │                     │
│                    │  (8 Semáforos)  │                     │
│                    └────────┬────────┘                     │
│                             │                               │
│         ┌───────────────────┼───────────────────┐          │
│         │                   │                   │          │
│  ┌──────▼───────┐   ┌──────▼───────┐   ┌──────▼───────┐  │
│  │    Taxi 1     │   │    Taxi 2     │   │    Taxi M     │  │
│  │  (Disponible) │   │  (Ocupado)    │   │  (Disponible) │  │
│  └──────────────┘   └──────────────┘   └──────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
Modelo de Hilos

Hilo del Sistema Principal: Gestiona días de simulación, reportes y cierres contables
Hilos de Clientes: Cada cliente ejecuta en su propio hilo (solicitud → asignación → servicio → calificación)
Sincronización: Semáforos binarios garantizan exclusión mutua en secciones críticas


📦 Requisitos
Software Necesario

Python 3.12 o superior
pip (gestor de paquetes de Python)

Dependencias Python
bash# Ninguna dependencia externa requerida
# El sistema usa solo bibliotecas estándar de Python:
# - threading (para hilos y semáforos)
# - json (para almacenamiento de datos)
# - datetime (para timestamps)
# - math (para cálculos de distancia)
# - http.server (para servidor web)

🚀 Instalación
1. Clonar el Repositorio
bashgit clone https://github.com/tu-usuario/unietaxi.git
cd unietaxi
2. Verificar Python
bashpython --version
# Debe mostrar Python 3.12 o superior
3. Estructura de Directorios
El sistema creará automáticamente los directorios necesarios:
unietaxi/
├── data/
│   ├── reportes/          # Reportes generados automáticamente
│   ├── servicios_completados.json
│   ├── simulacion_live.json
│   └── ubicaciones_tiempo_real.json
├── clientes_registrados.json
└── taxis_registrados.json

💻 Uso
Modo 1: Interfaz Web (Recomendado)
Inicia la simulación con visualización web en tiempo real:
bash# Simulación de 1 día (por defecto)
python main.py

# Simulación de 3 días
python main.py --dias 3

# Simulación de 7 días
python main.py --dias 7
Luego abre tu navegador en: http://localhost:8000
Modo 2: Terminal
Ejecuta la simulación en modo consola:
bash# Simulación de 2 días en terminal
python main.py --terminal --dias 2
Modo 3: Registro de Usuarios
Registra nuevos clientes y taxis de forma interactiva:
bashpython registro_unificado.py
Opciones:

1 - Registrar nuevo cliente
2 - Registrar nuevo taxi
3 - Ver clientes registrados
4 - Ver taxis registrados
5 - Salir

Modo 4: Ejecutar Tests
Valida el sistema con 15 casos de prueba automatizados:
bashpython test_sistema.py
Resultado esperado:
Total de pruebas: 15
✅ Exitosas: 15
❌ Fallidas: 0
🎉 ¡Todas las pruebas pasaron exitosamente!

📁 Estructura del Proyecto
unietaxi/
│
├── 📄 main.py                      # Punto de entrada principal
├── 📄 sistema_central.py           # Núcleo del sistema (8 semáforos)
├── 📄 models.py                    # Clases Cliente, Taxi, Servicio
├── 📄 hilos.py                     # Implementación de hilos
├── 📄 config.py                    # Configuración centralizada
├── 📄 simulacion_web.py            # Servidor web y lógica de simulación
├── 📄 registro_unificado.py        # Sistema de registro interactivo
├── 📄 test_sistema.py              # Suite de 15 pruebas automatizadas
├── 📄 exportador.py                # Exportación de reportes
├── 📄 visualizacion_mapa.py        # Visualización de mapas
├── 📄 reloj.py                     # Sistema de tiempo simulado
├── 📄 iniciar.py                   # Script de inicialización
│
├── 🌐 simulacion_tiempo_real.html  # Interfaz web principal
├── 🌐 taxi_animado.html            # Visualización animada de taxis
│
├── 📊 data/
│   ├── reportes/                   # Reportes diarios y mensuales
│   ├── servicios_completados.json # Historial de servicios
│   ├── simulacion_live.json       # Estado en tiempo real
│   └── ubicaciones_tiempo_real.json # Posiciones de taxis
│
├── 📋 clientes_registrados.json    # Base de datos de clientes
├── 📋 taxis_registrados.json       # Base de datos de taxis
│
└── 📖 README.md                    # Este archivo
Descripción de Módulos Principales
MóduloResponsabilidadsistema_central.pyGestión de sincronización, asignaciones, reportes (659 líneas)models.pyDefinición de clases Cliente, Taxi, Serviciohilos.pyHilos de clientes y sistema principalsimulacion_web.pyServidor HTTP y actualización en tiempo realtest_sistema.py15 casos de prueba automatizadosconfig.pyConfiguraciones (tarifas, tiempos, radios)

🔐 Sincronización y Recursos Críticos
Semáforos Implementados
El sistema utiliza 8 semáforos binarios para proteger recursos críticos:
1️⃣ mutex_taxis

Protege: Lista de taxis
Previene: Race conditions al modificar disponibilidad de taxis

2️⃣ mutex_clientes

Protege: Lista de clientes
Previene: Conflictos en registro/modificación de clientes

3️⃣ mutex_match ⭐ MÁS IMPORTANTE

Protege: Función de asignación de taxis
Previene: Asignación del mismo taxi a múltiples clientes
Crítico: Solo un cliente puede ejecutar asignar_taxi() a la vez

4️⃣ mutex_fin_del_dia

Protege: Control de servicios activos y fin del día
Previene: Problemas con servicios_activos y fin_del_dia

5️⃣ mutex_servicios_seguimiento

Protege: Arreglo de 5 servicios diarios de seguimiento
Previene: Desbordamiento y reemplazo de servicios

6️⃣ mutex_servicios_completados

Protege: Lista de servicios completados y contador
Previene: IDs duplicados y pérdida de información

7️⃣ mutex_solicitudes

Protege: Cola de solicitudes
Previene: Conflictos al agregar/extraer solicitudes

8️⃣ mutex_afiliacion

Protege: Proceso de afiliación de clientes y taxis
Previene: Pérdida de afiliaciones pendientes

Primitivas de Sincronización
python# Inicialización
semaforo = threading.Semaphore(1)  # Semáforo binario

# Uso en sección crítica
semaforo.acquire()  # Wait/P - Entrar a sección crítica
try:
    # ... código protegido ...
finally:
    semaforo.release()  # Signal/V - Salir de sección crítica

🧪 Casos de Prueba
El sistema incluye 15 casos de prueba organizados en 5 categorías:
🔒 Pruebas de Sincronización (4 tests)
IDNombreValidaciónCP-SC-01Race Condition en Lista de Taxismutex_match y mutex_taxisCP-SC-02Modificación Concurrente de Serviciosmutex_servicios_completadosCP-SC-03Asignación Simultánea de Mismo Taximutex_matchCP-SC-04Actualización Concurrente de CalificacionesSemáforos de calificación
⚠️ Pruebas de Casos Extremos (4 tests)
IDNombreValidaciónCP-EXT-01No Hay Taxis DisponiblesMensaje apropiadoCP-EXT-02Taxis Fuera de RadioRadio de 2 kmCP-EXT-03Todos los Taxis OcupadosEstado de ocupaciónCP-EXT-04Tarjeta de Crédito InválidaValidación de 16 dígitos
⚙️ Pruebas de Funcionalidad Básica (4 tests)
IDNombreValidaciónCP-FUN-01Registro de Cliente VálidoAfiliación correctaCP-FUN-02Registro de Taxi VálidoAfiliación correctaCP-FUN-03Cálculo de DistanciaTeorema de PitágorasCP-FUN-04Desempate por CalificaciónMejor calificado gana
💼 Pruebas de Lógica de Negocio (2 tests)
IDNombreValidaciónCP-NEG-01Cálculo de Tarifadistancia × $2.5/kmCP-NEG-02Comisión de la Empresa20% UNIETAXI, 80% taxista
🔄 Pruebas de Integración (1 test)
IDNombreValidaciónCP-INT-01Flujo Completo de ServicioCiclo completo: solicitud → calificación

⚙️ Configuración
Todos los parámetros del sistema se encuentran en config.py:
Parámetros Principales
python# Tarifa y Distancias
TARIFA_POR_KM = 2.5              # $2.5 por kilómetro
RADIO_BUSQUEDA_KM = 2.0          # Radio de búsqueda de taxis
VELOCIDAD_PROMEDIO_KMH = 60      # Velocidad promedio

# Comisiones
COMISION_EMPRESA = 0.20          # 20% para UNIETAXI
GANANCIA_TAXISTA = 0.80          # 80% para el taxista

# Calificaciones
CALIFICACION_MINIMA = 1
CALIFICACION_MAXIMA = 5

# Simulación
TIEMPO_SIMULACION_DIA = 6.0      # Segundos reales por día simulado
SERVICIOS_POR_DIA = 5            # Servicios a seguir diariamente
DIAS_POR_DEFECTO = 1             # Días de simulación por defecto

# Coordenadas de Madrid (Zona de Operación)
PUNTOS_INICIO_TAXIS = [
    (40.4168, -3.7038),  # Puerta del Sol
    (40.4200, -3.6887),  # Puerta de Alcalá
    (40.4379, -3.6795),  # Estadio Santiago Bernabéu
    # ... más puntos
]
Modificar Configuración
Para cambiar parámetros, edita config.py:
python# Ejemplo: Cambiar tarifa a $3/km
TARIFA_POR_KM = 3.0

# Ejemplo: Simular días más largos (10 segundos)
SIMULACION["TIEMPO_SIMULACION_DIA"] = 10.0

📚 API y Módulos
Sistema Central
pythonfrom sistema_central import SistemaCentral

# Crear sistema para 3 días
sistema = SistemaCentral(num_dias=3)

# Afiliar taxi
sistema.afiliar_taxi(
    cedula=123456789,
    nombre="Juan Pérez",
    apellido="García",
    placa="ABC123",
    marca="Toyota",
    modelo="Corolla",
    velocidad=60
)

# Afiliar cliente
sistema.afiliar_cliente(
    cedula=987654321,
    nombre="María",
    apellido="López",
    tarjeta="1234567890123456"
)

# Asignar taxi a cliente
cliente = sistema.clientes[0]
taxi = sistema.asignar_taxi(cliente)

# Realizar servicio
if taxi:
    sistema.realizar_servicio(cliente, taxi)
Modelos
pythonfrom models import Cliente, Taxi, Servicio

# Crear cliente
cliente = Cliente(
    cedula=123456,
    nombre="Ana",
    apellido="Martínez",
    tarjeta="1234567890123456"
)

# Crear taxi
taxi = Taxi(
    id_taxi=1,
    cedula=789012,
    nombre="Carlos",
    apellido="Rodríguez",
    placa="XYZ789",
    marca="Honda",
    modelo="Civic",
    velocidad=60,
    ubicacion=(40.4168, -3.7038)
)

# Calcular distancia
distancia = taxi.calcular_distancia(
    origen=(40.4168, -3.7038),
    destino=(40.4200, -3.6887)
)

📊 Reportes Generados
Reporte Diario
Generado al final de cada día en data/reportes/dia_X.txt:
============================================================
REPORTE DÍA 1 - 2024-12-13 14:30:00
============================================================

📊 SERVICIOS DE SEGUIMIENTO (5 servicios aleatorios):

1. Servicio #123
   Taxi: ABC123 - Juan Pérez
   Cliente: María López (CI: 987654321)
   Origen: (40.4168, -3.7038) → Destino: (40.4200, -3.6887)
   Distancia: 0.38 km | Costo: $0.95
   Calificación: 5⭐

...

💰 GANANCIA TOTAL DEL DÍA: $45.50
Cierre Contable Diario
Generado a las 12:00 PM en data/reportes/cierre_dia_X.txt:
============================================================
CIERRE CONTABLE DÍA 1
============================================================

Taxi ABC123 - Juan Pérez
  Total Generado: $12.50
  Comisión UNIETAXI (20%): $2.50
  Ganancia Taxista (80%): $10.00

...

💰 GANANCIA EMPRESA DEL DÍA: $9.10
💰 GANANCIA ACUMULADA EMPRESA: $9.10
Reporte Mensual
Generado al final de la simulación en data/reportes/reporte_mensual.txt:
============================================================
REPORTE MENSUAL FINAL
============================================================

Taxi ABC123 - Juan Pérez
  Placa: ABC123 | Marca: Toyota | Modelo: Corolla
  Total Generado: $125.50
  Comisión UNIETAXI (20%): $25.10
  Ganancia Taxista (80%): $100.40
  Servicios: 25 | Calificación Promedio: 4.8⭐

...

💰 GANANCIA TOTAL EMPRESA: $91.40

🎨 Interfaz Web
Características

Actualización en tiempo real (cada 2 segundos)
Mapa de Madrid con ubicaciones de taxis
Indicadores visuales:

🟢 Verde: Taxi disponible
🔴 Rojo: Taxi ocupado


Panel de estadísticas:

Servicios completados
Ganancia total
Taxis activos
Clientes registrados



Tecnologías

HTML5 + CSS3
JavaScript (ES6+)
Fetch API para comunicación con servidor
Canvas para visualizaciones